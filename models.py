from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
teams = []

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

	start_level = None
	end_level = None
	has_been_highlighted = False
	has_been_issued_warning = False

	def __init__(self):
		pass

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