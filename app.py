import logging
import cache
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

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
	return render_template('leaderboards.html', title='Leaderboards', leaderboards={'defence': cache.defence_sorted, 'cargo': cache.cargo_sorted, 'hatch': cache.hatch_sorted})

@app.route('/teams')
def teams():
	return render_template('teams.html', title='Teams')

cache.models.db.create_all(app=app)
cache.ask_for_team_at_event()
cache.sort_teams()
app.run(host='0.0.0.0')