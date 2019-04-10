from flask_sqlalchemy import SQLAlchemy
from collections import Counter
import logging
import sys

db = SQLAlchemy()

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Team(object):
	number = None
	name = None
	matches = []

	# Averages
	avg_cargo_score = 0.0
	avg_hatch_score = 0.0
	avg_drive_rating = 0.0
	avg_defence_rating = 0.0
	rocket_stats = {'cargo': {'low': 0.0, 'middle': 0.0, 'high': 0.0},
					'hatch': {'low': 0.0, 'middle': 0.0, 'high': 0.0}}

	start_level = []
	end_level = []
	has_been_highlighted = False
	has_been_issued_warning = False

	def __init__(self, tbaDictionary=None, from_file=False):
		if tbaDictionary is not None:
			# Unpack the dictionary into variables
			self.key = tbaDictionary['key']
			if from_file:
				self.number = tbaDictionary['number']
				self.name = tbaDictionary['name']
			else:
				self.number = tbaDictionary['team_number']
				self.name = tbaDictionary['nickname']

	''' Set variables to their default values '''
	def clear(self):
		self.matches = []
		self.avg_cargo_score = 0.0
		self.avg_hatch_score = 0.0
		self.avg_drive_rating = 0.0
		self.avg_defence_rating = 0.0
		self.rocket_stats = {'cargo': {'low': 0.0, 'middle': 0.0, 'high': 0.0},
					'hatch': {'low': 0.0, 'middle': 0.0, 'high': 0.0}}
		self.start_level = []
		self.end_level = []
		self.has_been_highlighted = False
		self.has_been_issued_warning = False
	
	def calculate_averages(self, rows):
		self.clear()
		self.matches = rows
		
		for row in rows:
			self.start_level.append(row.auto_idStartLevel)
			self.end_level.append(row.tele_idClimbLevel)
			self.avg_drive_rating += row.comm_idDriveRating
			self.avg_defence_rating += row.comm_idDefenseRating

			if row.comm_flHighlight:
				self.has_been_highlighted = True
			if row.comm_flWarning:
				self.has_been_issued_warning = True

			# Cargo Score
			self.avg_cargo_score += sum([
				row.auto_numShipFrontCargoSuccess,
				row.auto_numShipSideCargoSuccess,
				row.auto_numRocketLowCargoSuccess,
				row.auto_numRocketMidCargoSuccess,
				row.auto_numRocketHighCargoSuccess,
				row.tele_numShipFrontCargoSuccess,
				row.tele_numShipSideCargoSuccess,
				row.tele_numRocketLowCargoSuccess,
				row.tele_numRocketMidCargoSuccess,
				row.tele_numRocketHighCargoSuccess]
			)

			# Cargo Rocket L/M/H
			self.rocket_stats['cargo']['low'] += sum([
				row.auto_numRocketLowCargoSuccess, row.tele_numRocketLowCargoSuccess
			])
			self.rocket_stats['cargo']['middle'] += sum([
				row.auto_numRocketMidCargoSuccess, row.tele_numRocketMidCargoSuccess
			])
			self.rocket_stats['cargo']['high'] += sum([
				row.auto_numRocketHighCargoSuccess, row.tele_numRocketHighCargoSuccess
			])

			# Hatch Score
			self.avg_hatch_score += sum([
				row.auto_numShipFrontHatchSuccess,
				row.auto_numShipSideHatchSuccess,
				row.auto_numRocketLowHatchSuccess,
				row.auto_numRocketMidHatchSuccess,
				row.auto_numRocketHighHatchSuccess,
				row.tele_numShipFrontHatchSuccess,
				row.tele_numShipSideHatchSuccess,
				row.tele_numRocketLowHatchSuccess,
				row.tele_numRocketMidHatchSuccess,
				row.tele_numRocketHighHatchSuccess]
			)

			# Hatch Rocket L/M/H
			self.rocket_stats['hatch']['low'] += sum([
				row.auto_numRocketLowHatchSuccess, row.tele_numRocketLowHatchSuccess
			])
			self.rocket_stats['hatch']['middle'] += sum([
				row.auto_numRocketMidHatchSuccess, row.tele_numRocketMidHatchSuccess
			])
			self.rocket_stats['hatch']['high'] += sum([
				row.auto_numRocketHighHatchSuccess, row.tele_numRocketHighHatchSuccess
			])

		# Divide averages by number of rows
		if len(rows) > 0:
			self.cargo_rocket_lmh = '{}/{}/{}'.format(
				round(self.rocket_stats['cargo']['low']/float(len(rows)), 2),
				round(self.rocket_stats['cargo']['middle']/float(len(rows)), 2),
				round(self.rocket_stats['cargo']['high']/float(len(rows)), 2)
			)
			self.hatch_rocket_lmh = '{}/{}/{}'.format(
				round(self.rocket_stats['hatch']['low']/float(len(rows)), 2),
				round(self.rocket_stats['hatch']['middle']/float(len(rows)), 2),
				round(self.rocket_stats['hatch']['high']/float(len(rows)), 2)
			)

			self.avg_cargo_score = round(self.avg_cargo_score/float(len(rows)), 2)
			self.avg_hatch_score = round(self.avg_hatch_score/float(len(rows)), 2)

			self.avg_drive_rating = round(self.avg_drive_rating/float(len(rows)), 2)
			self.avg_defence_rating = round(self.avg_defence_rating/float(len(rows)), 2)

		# Start and end level
		self.start_level = ', '.join(['{} {} times'.format(k, v) for (k, v) in Counter(self.start_level).items()])
		self.end_level = ', '.join(['{} {} times'.format(k, v) for (k, v) in Counter(self.end_level).items()])

class Match(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	event = db.Column(db.String)
	match = db.Column(db.Integer)
	idTeam = db.Column(db.Integer)
	idAlliance = db.Column(db.Integer)
	idDriveStation = db.Column(db.Integer)
	scoutname = db.Column(db.String)
	crashed = db.Column(db.Boolean)
	yellow = db.Column(db.Boolean)
	red = db.Column(db.Boolean)
	auto_flState = db.Column(db.Boolean)
	auto_idStartLevel = db.Column(db.Integer)
	auto_idStartObject = db.Column(db.Integer)
	auto_numShipFrontHatchAttempt = db.Column(db.Integer)
	auto_numShipFrontHatchSuccess = db.Column(db.Integer)
	auto_numShipSideHatchAttempt = db.Column(db.Integer)
	auto_numShipSideHatchSuccess = db.Column(db.Integer)
	auto_numShipFrontCargoAttempt = db.Column(db.Integer)
	auto_numShipFrontCargoSuccess = db.Column(db.Integer)
	auto_numShipSideCargoAttempt = db.Column(db.Integer)
	auto_numShipSideCargoSuccess = db.Column(db.Integer)
	auto_numRocketLowHatchAttempt = db.Column(db.Integer)
	auto_numRocketLowHatchSuccess = db.Column(db.Integer)
	auto_numRocketMidHatchAttempt = db.Column(db.Integer)
	auto_numRocketMidHatchSuccess = db.Column(db.Integer)
	auto_numRocketHighHatchAttempt = db.Column(db.Integer)
	auto_numRocketHighHatchSuccess = db.Column(db.Integer)
	auto_numRocketLowCargoAttempt = db.Column(db.Integer)
	auto_numRocketLowCargoSuccess = db.Column(db.Integer)
	auto_numRocketMidCargoAttempt = db.Column(db.Integer)
	auto_numRocketMidCargoSuccess = db.Column(db.Integer)
	auto_numRocketHighCargoAttempt = db.Column(db.Integer)
	auto_numRocketHighCargoSuccess = db.Column(db.Integer)
	auto_flCrossOver = db.Column(db.Boolean)
	tele_numShipFrontHatchAttempt = db.Column(db.Integer)
	tele_numShipFrontHatchSuccess = db.Column(db.Integer)
	tele_numShipSideHatchAttempt = db.Column(db.Integer)
	tele_numShipSideHatchSuccess = db.Column(db.Integer)
	tele_numShipFrontCargoAttempt = db.Column(db.Integer)
	tele_numShipFrontCargoSuccess = db.Column(db.Integer)
	tele_numShipSideCargoAttempt = db.Column(db.Integer)
	tele_numShipSideCargoSuccess = db.Column(db.Integer)
	tele_numRocketLowHatchAttempt = db.Column(db.Integer)
	tele_numRocketLowHatchSuccess = db.Column(db.Integer)
	tele_numRocketMidHatchAttempt = db.Column(db.Integer)
	tele_numRocketMidHatchSuccess = db.Column(db.Integer)
	tele_numRocketHighHatchAttempt = db.Column(db.Integer)
	tele_numRocketHighHatchSuccess = db.Column(db.Integer)
	tele_numRocketLowCargoAttempt = db.Column(db.Integer)
	tele_numRocketLowCargoSuccess = db.Column(db.Integer)
	tele_numRocketMidCargoAttempt = db.Column(db.Integer)
	tele_numRocketMidCargoSuccess = db.Column(db.Integer)
	tele_numRocketHighCargoAttempt = db.Column(db.Integer)
	tele_numRocketHighCargoSuccess = db.Column(db.Integer)
	tele_idClimbLevel = db.Column(db.Integer)
	tele_climbAssisted = db.Column(db.Boolean)
	tele_flDefence = db.Column(db.Boolean)
	flIntakeHatchGround = db.Column(db.Boolean)
	flIntakeHatchStation = db.Column(db.Boolean)
	flIntakeCargoGround = db.Column(db.Boolean)
	flIntakeCargoStation = db.Column(db.Boolean)
	comm_txNotes = db.Column(db.String)
	comm_flHighlight = db.Column(db.Boolean)
	comm_flWarning = db.Column(db.Boolean)
	comm_idDriveRating = db.Column(db.Integer)
	comm_idDefenseRating = db.Column(db.Integer)
	comm_flAlliance = db.Column(db.Boolean)
	comm_flRecovery = db.Column(db.Boolean)
	comm_flStrategy = db.Column(db.Boolean)
	comm_flOwnThing = db.Column(db.Boolean)
	comm_flGoodDefence = db.Column(db.Boolean)
	dtCreation = db.Column(db.Date)
	dtModified = db.Column(db.Date)
	txComputerName = db.Column(db.String)
	flRanking1 = db.Column(db.Boolean)