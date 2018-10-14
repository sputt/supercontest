"""Contains the tables for the applications.
"""
# pylint: disable=no-member,too-few-public-methods
from supercontest.app import db


class User(db.Model):
    """The table for users.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)


class Pick(db.Model):
    """The table for user picks.
    """
    id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer, nullable=False)
    team = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('picks'))
    points = db.Column(db.Float)


class Matchup(db.Model):
    """The main table for lines and scores.
    """
    id = db.Column(db.Integer, primary_key=True)
    week = db.Column(db.Integer, nullable=False)
    favored_team = db.Column(db.String, nullable=False)
    underdog_team = db.Column(db.String, nullable=False)
    datetime = db.Column(db.String, nullable=False)
    line = db.Column(db.Float, nullable=False)
    home_team = db.Column(db.String)
    favored_team_score = db.Column(db.Integer)
    underdog_team_score = db.Column(db.Integer)
    status = db.Column(db.String)
    # P = has not started
    # H = halftime
    # F/FO = game is over
    # 1/2/3/4 = quarter
