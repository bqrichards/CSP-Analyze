import logging
from flask import Flask, render_template

logger = logging.getLogger(__name__)
app = Flask(__name__)

@app.route('/')
@app.route('/index')
@app.route('/leaderboards')
def leaderboards():
	return render_template('leaderboards.html', title='Leaderboards')

@app.route('/teams')
def teams():
	return render_template('teams.html', title='Teams')

app.run(host='0.0.0.0')