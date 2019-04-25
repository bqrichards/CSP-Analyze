from threading import Thread
from time import sleep
from datetime import datetime
import re

from flask import Flask, render_template, request, redirect, url_for

import cache

app = Flask(__name__)

''' Database '''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scouting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
cache.models.db.init_app(app)

event_codes = ['2019arc']
unique_ips = []


def has_been_on_level(level_number, team):
    """
    Checks to see if a team has reached a certain HAB level in any of their matches
    :param level_number: level HAB level
    :param team: the team
    :return: Whether the team has been on this HAB level
    """
    for match in team.matches:
        if match.auto_idStartLevel == level_number or match.tele_idClimbLevel == level_number:
            return True
    return False


''' Web Routes '''
@app.route('/')
@app.route('/index')
@app.route('/leaderboards')
def leaderboards():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if ip not in unique_ips:
        unique_ips.append(ip)
        with open('unique_ips.txt', 'a+') as f:
            cache.logger.info('Appending unique ip {} to file'.format(ip))
            f.write(ip + '\n')

    return render_template('leaderboards.html', title='Leaderboards',
                           leaderboards={'defence': cache.defence_sorted, 'cargo': cache.cargo_sorted,
                                         'hatch': cache.hatch_sorted, 'rankings': cache.rankings_sorted})


@app.route('/teams', methods=['GET', 'POST'])
def teams():
    if request.method == 'GET':
        return render_template('teams.html', title='Teams', teams=cache.teams)

    # POST - trying to filter
    if 'hab-climb-select' not in request.form:
        cache.logger.warning('Submitting POST request without select options in form')
        return render_template('error.html', title='Error', error_message='POST request could not be handled')

    if request.form['hab-climb-select'] == 'No Preference':
        cache.logger.info('Attempting to filter with no preference, giving default list')
        return render_template('teams.html', title='Teams', teams=cache.teams)

    # Filter teams
    filtered_teams = []

    # Filter by HAB climb
    at_least_level = int(request.form['hab-climb-select'][-1])
    cache.logger.info('Filtering robots by HAB level {}'.format(at_least_level))
    filtered_teams.extend([team for team in cache.teams if has_been_on_level(at_least_level, team)])

    return render_template('teams.html', title='Teams', teams=filtered_teams)


@app.route('/team/<int:team_number>')
def team(team_number):
    return render_template('team.html', title="Team {}".format(team_number), team=cache.get_team_by_number(team_number))


@app.route('/edit/<int:row_id>', methods=['GET', 'POST'])
def edit(row_id):
    if request.method == 'POST':
        # Make changes
        date_pattern = re.compile('^(\d+)-(\d+)-(\d+)$')
        old_match = cache.models.Match.query.filter_by(id=row_id).first()
        for key in request.form:
            matches = date_pattern.match(request.form[key])
            if matches is not None:
                new_date = datetime.strptime(matches[0], '%Y-%m-%d')
                setattr(old_match, key, new_date)
            elif request.form[key] in ('True', 'False'):
                setattr(old_match, key, request.form[key] == 'True')
            else:
                try:
                    # Insert as integer
                    int_value = int(request.form[key])
                    setattr(old_match, key, int_value)
                except ValueError:
                    # Insert as original value
                    setattr(old_match, key, request.form[key])

        cache.models.db.session.add(old_match)
        cache.models.db.session.commit()

        # Send back to recent
        return redirect(url_for('latest'))

    column_names = [column.name for column in cache.models.Match.__mapper__.columns]
    match_obj = cache.models.Match.query.filter_by(id=row_id).first()
    match = []
    for column_name in column_names:
        match.append(getattr(match_obj, column_name))
    match = zip(column_names, match)
    return render_template('edit.html', title='Edit', match=match)


@app.route('/latest')
def latest():
    column_names = [column.name for column in cache.models.Match.__mapper__.columns]
    queried_matches = cache.models.Match.query.all()[::-1]
    matches = []
    for match in queried_matches:
        matches.append([getattr(match, column_name) for column_name in column_names])

    return render_template('latest.html', title='Latest', columns=column_names, matches=matches)


@app.route('/submit', methods=['POST'])
def submit():
    form = request.form
    if form is None:
        return 'no data posted'

    data = None
    try:
        data = form['csvdata']
    except KeyError:
        return 'no csvdata'

    columns = [column.name for column in cache.models.Match.__mapper__.columns]
    split = data.split('~~~~~')
    split = [text.split(',') for text in split]

    date_pattern = re.compile('^(\d+)\/(\d+)\/(\d+) (\d+):(\d+):(\d+)$')
    imports = 0
    for split_result in split:
        # Convert datatypes to Python
        for i, subresult in enumerate(split_result):
            # Boolean
            if subresult == 'TRUE':
                split_result[i] = True
            elif subresult == 'FALSE':
                split_result[i] = False

            # Date
            matches = date_pattern.match(subresult)
            if matches is None:
                continue

            # Parse Date
            date_str = datetime.strptime(matches[0], '%Y/%m/%d %H:%M:%S')
            split_result[i] = date_str

        if len(split_result) == 76:
            together = {key: value for (key, value) in zip(columns, split_result)}
            del together['id']
            cache.models.db.session.add(cache.models.Match(**together))
            cache.logger.info('Added match result')
            imports += 1
        else:
            cache.logger.info('Ignoring result, has length of {}'.format(len(split_result)))
            continue

    cache.models.db.session.commit()

    return str(imports)


def update_cache():
    while True:
        with app.app_context():
            cache.sort_teams()
            #cache.ask_for_official_rankings()
            sleep(120)


cache.models.db.create_all(app=app)
cache.teams = []
for event_code in event_codes:
    cache.teams.extend(cache.ask_for_teams_at_event(event_code))
cache_update_thread = Thread(target=update_cache)
cache_update_thread.start()
app.run(host='0.0.0.0')
