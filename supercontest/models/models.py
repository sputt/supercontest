"""Contains the tables for the applications.
"""
# pylint: disable=no-member
from flask_user import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators

from supercontest import db


class User(db.Model, UserMixin):
    """The table for users.
    """
    # UniqueConstraints should be explicit (instead of implicit and unnamed)
    # so that Alembic can autogenerate the migrations properly.
    __table_args__ = (
        db.UniqueConstraint('email', name='email_constraint'),
    )
    __seq__ = db.Sequence('user_id_seq', start=43)
    id = db.Column(db.Integer, __seq__, server_default=__seq__.next_value(), primary_key=True)
    # UserMixin doesn't provide this property, for some reason?
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    email = db.Column(db.String(225, collation='NOCASE'), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    first_name = db.Column(db.String(50, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(50, collation='NOCASE'), nullable=False, server_default='')


class Pick(db.Model):
    """The table for user picks.
    """
    __seq__ = db.Sequence('pick_id_seq', start=3106)
    id = db.Column(db.Integer, __seq__, server_default=__seq__.next_value(), primary_key=True)
    week = db.Column(db.Integer, nullable=False)
    team = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    points = db.Column(db.Float)


class Matchup(db.Model):
    """The main table for lines and scores.
    Here are the "status" enumerations:
        P = has not started
        H = halftime
        F/FO = game is over
        1/2/3/4 = quarter
    """
    __seq__ = db.Sequence('matchup_id_seq', start=263)
    id = db.Column(db.Integer, __seq__, server_default=__seq__.next_value(), primary_key=True)
    week = db.Column(db.Integer, nullable=False)
    favored_team = db.Column(db.String, nullable=False)
    underdog_team = db.Column(db.String, nullable=False)
    datetime = db.Column(db.String, nullable=False)
    line = db.Column(db.Float, nullable=False)
    home_team = db.Column(db.String)
    favored_team_score = db.Column(db.Integer)
    underdog_team_score = db.Column(db.Integer)
    status = db.Column(db.String)
    winner = db.Column(db.String)


class UserProfileForm(FlaskForm):
    first_name = StringField(
        'First name',
        validators=[validators.DataRequired('First name is required')]
    )
    last_name = StringField(
        'Last name',
        validators=[validators.DataRequired('Last name is required')]
    )
    submit = SubmitField('Save')
