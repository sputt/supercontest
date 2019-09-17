"""Contains the tables for the applications.

A few general notes here:
    - I'm leaning on the light side. Foreign keys are just IDs,
      not back-populating many-one relationships.
    - The many-many relationships are unidirectional.
    - Calculations and aggregations are not stored. They're
      recalculated on request by the app. This app has fairly
      dynamic data (nfl scores), so this design pattern is ok.
"""
# pylint: disable=no-member,too-few-public-methods,missing-docstring
from flask_user import UserMixin

from supercontest import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __seq__ = db.Sequence(__tablename__ + '_id_seq')
    # UniqueConstraints should be explicit (instead of implicit and unnamed)
    # so that Alembic can autogenerate the migrations properly.
    __table_args__ = (db.UniqueConstraint('email', name='email_constraint'),)
    id = db.Column(db.Integer, __seq__, server_default=__seq__.next_value(), primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False)
    email = db.Column(db.String, nullable=False)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)


class Season(db.Model):
    __tablename__ = 'seasons'
    __seq__ = db.Sequence(__tablename__ + '_id_seq')
    id = db.Column(db.Integer, __seq__, server_default=__seq__.next_value(), primary_key=True)
    season = db.Column(db.Integer, nullable=False)


class Week(db.Model):
    __tablename__ = 'weeks'
    __seq__ = db.Sequence(__tablename__ + '_id_seq')
    id = db.Column(db.Integer, __seq__, server_default=__seq__.next_value(), primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id'), nullable=False)
    week = db.Column(db.Integer, nullable=False)


class Line(db.Model):
    __tablename__ = 'lines'
    __seq__ = db.Sequence(__tablename__ + '_id_seq')
    id = db.Column(db.Integer, __seq__, server_default=__seq__.next_value(), primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=False)
    favored_team = db.Column(db.String, nullable=False)
    underdog_team = db.Column(db.String, nullable=False)
    datetime = db.Column(db.String, nullable=False)
    line = db.Column(db.Float, nullable=False)
    home_team = db.Column(db.String)  # nullable: some games are at neither's stadium


class Pick(db.Model):
    __tablename__ = 'picks'
    __seq__ = db.Sequence(__tablename__ + '_id_seq')
    id = db.Column(db.Integer, __seq__, server_default=__seq__.next_value(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=False)
    team = db.Column(db.String, nullable=False)


class Score(db.Model):
    __tablename__ = 'scores'
    __seq__ = db.Sequence(__tablename__ + '_id_seq')
    id = db.Column(db.Integer, __seq__, server_default=__seq__.next_value(), primary_key=True)
    line_id = db.Column(db.Integer, db.ForeignKey('lines.id'), nullable=False)
    favored_team_score = db.Column(db.Integer, nullable=False)
    underdog_team_score = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False)  # P 1 2 H 3 4 F FO
