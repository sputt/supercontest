"""Contains the tables for the applications.
"""
# pylint: disable=no-member
from flask_user import UserMixin
from supercontest import db

class User(db.Model, UserMixin):
    """The table for users.
    """
    # UniqueConstraints should be explicit (instead of implicit and unnamed)
    # so that Alembic can autogenerate the migrations properly.
    __table_args__ = (
        db.UniqueConstraint('email', name='email_constraint'),
        db.UniqueConstraint('username', name='username_constraint'),
        db.UniqueConstraint('password', name='password_constraint'),
    )
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    email = db.Column(db.String(225, collation='NOCASE'), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    password = db.Column(db.String(255), nullable=False, server_default='')


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
    Here are the "status" enumerations:
        P = has not started
        H = halftime
        F/FO = game is over
        1/2/3/4 = quarter
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
