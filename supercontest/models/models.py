"""Contains the tables for the applications.
"""
# pylint: disable=no-member,too-few-public-methods,missing-docstring
from flask_user import UserMixin

from supercontest import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    # UniqueConstraints should be explicit (instead of implicit and unnamed)
    # so that Alembic can autogenerate the migrations properly.
    __table_args__ = (db.UniqueConstraint('email', name='email_constraint'),)
    __seq__ = db.Sequence('users_id_seq')
    id = db.Column(db.Integer, __seq__, server_default=__seq__.next_value(), primary_key=True)
    # UserMixin doesn't provide this property, for some reason?
    active = db.Column('is_active', db.Boolean(), nullable=False)
    email = db.Column(db.String, nullable=False)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)


class Pick(db.Model):
    __tablename__ = 'picks'
    __seq__ = db.Sequence('picks_id_seq')
    id = db.Column(db.Integer, __seq__, server_default=__seq__.next_value(), primary_key=True)
    season = db.Column(db.Integer, nullable=False)
    week = db.Column(db.Integer, nullable=False)
    team = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    points = db.Column(db.Float)


class Matchup(db.Model):
    __tablename__ = 'matchups'
    __seq__ = db.Sequence('matchups_id_seq')
    id = db.Column(db.Integer, __seq__, server_default=__seq__.next_value(), primary_key=True)
    season = db.Column(db.Integer, nullable=False)
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
    winner = db.Column(db.String)
