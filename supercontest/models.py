from . import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    picks = db.relationship('Pick', back_populates='user')


class Pick(db.Model):
    __tablename__ = 'picks'
    id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer, nullable=False)
    team = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='picks')
    points = db.Column(db.Float)


class Matchup(db.Model):
    __tablename__ = 'matchups'
    id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer, nullable=False)
    favored_team = db.Column(db.String, nullable=False)
    underdog_team = db.Column(db.String, nullable=False)
    datetime = db.Column(db.String, nullable=False)
    line = db.Column(db.Float, nullable=False)
    home_team = db.Column(db.String)
    favored_team_score = db.Column(db.Integer)
    underdog_team_score = db.Column(db.Integer)
    status = db.Column(db.String)  # quarter, "F"inal, etc
