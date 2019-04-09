from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from threading import Thread
from time import sleep
import logging
import cache

app = Flask(__name__)

''' Database '''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scouting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
cache.models.db.init_app(app)

''' Web Routes '''
@app.route('/')
@app.route('/index')
@app.route('/leaderboards')
def leaderboards():
	return render_template('leaderboards.html', title='Leaderboards', leaderboards={'defence': cache.defence_sorted, 'cargo': cache.cargo_sorted, 'hatch': cache.hatch_sorted, 'rankings': cache.rankings_sorted})

@app.route('/teams')
def teams():
	return render_template('teams.html', title='Teams', teams=cache.teams)

@app.route('/team/<int:team_number>')
def team(team_number):
	return render_template('team.html', title="Team {}".format(team_number), team=cache.get_team_by_number(team_number))

def update_cache():
	while True:
		with app.app_context():
			cache.sort_teams()
			cache.ask_for_official_rankings()
			sleep(120)

cache.models.db.create_all(app=app)
cache.ask_for_teams_at_event()
cache_update_thread = Thread(target=update_cache)
cache_update_thread.start()
app.run(host='0.0.0.0')