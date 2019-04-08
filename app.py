import logging
import models
import cache
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)
app = Flask(__name__)

''' Database '''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scouting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
with app.app_context():
	models.db.init_app(app)

''' Web Routes '''
@app.route('/')
@app.route('/index')
@app.route('/leaderboards')
def leaderboards():
	return render_template('leaderboards.html', title='Leaderboards')

@app.route('/teams')
def teams():
	return render_template('teams.html', title='Teams')

models.db.create_all(app=app)
app.run(host='0.0.0.0')