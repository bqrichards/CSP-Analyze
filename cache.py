import json
import logging
import sys

import requests

import models

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

teams = []
defence_sorted = []
cargo_sorted = []
hatch_sorted = []
rankings_sorted = []

event_code = '2019wila'
tba_key = 'DzhuOimNqUcdpPEhDhFMoIFltbTNnIAner1f64b3aSSNrDTpZ1ZozPdN263iIV8L'
last_asked = {'teams_at_event': None, 'official_rankings': None}


def get_team_by_number(number):
    for team in teams:
        if team.number == number:
            return team
    return None


def ask_for_teams_at_event():
    global teams
    teams_filename = '{}-teams.json'.format(event_code)

    # Check if list of teams already exists
    try:
        with open(teams_filename, 'r') as f:
            teams_from_file = json.loads(f.read())
            teams = [models.Team(tba_dictionary=team_from_file, from_file=True) for team_from_file in teams_from_file]
            logger.info('Loaded teams from {}'.format(teams_filename))
            return
    except FileNotFoundError:
        logger.info('no previously saved base team info. fetching.')

    endpoint = 'https://www.thebluealliance.com/api/v3/event/{}/teams'.format(event_code)
    headers = {'X-TBA-Auth-Key': tba_key}
    logger.info('Asking for teams at event from {}'.format(endpoint))
    if last_asked['teams_at_event'] is not None:
        logger.info('Using If-Modified-Since: {}'.format(last_asked['teams_at_event']))
        headers['If-Modified-Since'] = last_asked['teams_at_event']

    r = requests.get(endpoint, headers=headers)

    logger.info('Status code: {}'.format(r.status_code))
    if r.status_code == 304:
        logger.info('No change in teams at event since last request')
    elif r.status_code != 200:
        return

    response_json = r.json()
    teams = []
    for team in response_json:
        team_object = models.Team(tbaDictionary=team)
        logger.info('Adding team with number {}'.format(team_object.number))
        teams.append(team_object)

    last_asked['teams_at_event'] = r.headers['Last-Modified']
    logger.info('Added {} teams'.format(len(teams)))

    teams_as_dicts = [team.__dict__ for team in teams]
    teams_filename = '{}-teams.json'.format(event_code)
    with open(teams_filename, 'w') as f:
        f.write(json.dumps(teams_as_dicts))


def ask_for_official_rankings():
    global teams

    if len(teams) == 0:
        logger.info('Aborting official rankings, we have no local team instances')
        return

    global rankings_sorted

    endpoint = 'https://www.thebluealliance.com/api/v3/event/{}/rankings'.format(event_code)
    headers = {'X-TBA-Auth-Key': tba_key}
    logger.info('Asking for official ranking from {}'.format(endpoint))
    if last_asked['official_rankings'] is not None:
        logger.info('Using If-Modified-Since: {}'.format(last_asked['official_rankings']))
        headers['If-Modified-Since'] = last_asked['official_rankings']
    else:
        logger.info('Using no If-Modified-Since')

    r = requests.get(endpoint, headers=headers)

    logger.info('Status code: {}'.format(r.status_code))
    if r.status_code == 304:
        logger.info('No change in rankings since last request')
        return
    elif r.status_code != 200:
        return

    response_json = r.json()
    if response_json is None:
        logger.info('No rankings yet')
        return

    response_json = response_json['rankings']

    for rank_index, rank_dict in enumerate(response_json):
        this_team = int(rank_dict['team_key'][3:])
        rankings_sorted.append(this_team)

        # Search for this team through our Team instances
        for team_index, team in enumerate(teams):
            if team.number == this_team:
                teams[team_index].rank = rank_index + 1

    last_asked['official_rankings'] = r.headers['Last-Modified']
    logger.info('Setting last asked for official rankings to {}'.format(last_asked['official_rankings']))


''' Query all match scouting results, recalculate averages, and sort '''


def sort_teams():
    global teams
    if len(teams) == 0:
        logger.warning('called sort_teams when 0 teams are present')
        return

    global defence_sorted
    global cargo_sorted
    global hatch_sorted

    # Query all match results
    rows = models.Match.query.all()
    logger.info('Sorting {} match results'.format(len(rows)))

    # Recalculate averages
    for team in teams:
        team.calculate_averages(models.Match.query.filter_by(idTeam=team.number).all())

    # Sort defence
    teams = sorted(teams, key=lambda team: team.avg_defence_rating, reverse=True)
    defence_sorted = [team.number for team in teams]

    # Sort cargo
    teams = sorted(teams, key=lambda team: team.avg_cargo_score, reverse=True)
    cargo_sorted = [team.number for team in teams]

    # Sort hatch
    teams = sorted(teams, key=lambda team: team.avg_hatch_score, reverse=True)
    hatch_sorted = [team.number for team in teams]
