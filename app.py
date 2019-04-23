from threading import Thread
from time import sleep
from datetime import datetime
import re

from flask import Flask, render_template, request

import cache

app = Flask(__name__)

''' Database '''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scouting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
cache.models.db.init_app(app)

event_codes = ['2019carv', '2019gal', '2019hop', '2019new', '2019roe', '2019tur']
unique_ips = []

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


@app.route('/teams')
def teams():
    return render_template('teams.html', title='Teams', teams=cache.teams)


@app.route('/team/<int:team_number>')
def team(team_number):
    return render_template('team.html', title="Team {}".format(team_number), team=cache.get_team_by_number(team_number))


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
