# pylint: disable=too-few-public-methods
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from supercontest import db
from supercontest.models import User, Pick, Line, Score, Season, Week


class UserObject(SQLAlchemyObjectType):
    class Meta:
        model = User


class PickObject(SQLAlchemyObjectType):
    class Meta:
        model = Pick


class LineObject(SQLAlchemyObjectType):
    class Meta:
        model = Line

class ScoreObject(SQLAlchemyObjectType):
    class Meta:
        model = Score


class SeasonObject(SQLAlchemyObjectType):
    class Meta:
        model = Season


class WeekObject(SQLAlchemyObjectType):
    class Meta:
        model = Week


class Query(graphene.ObjectType):
    users = graphene.List(UserObject)
    picks = graphene.List(PickObject)
    lines = graphene.List(LineObject)
    scores = graphene.List(ScoreObject)
    seasons = graphene.List(SeasonObject)
    weeks = graphene.List(WeekObject)

    # pylint: disable=no-member,unused-argument,no-self-use
    def resolve_users(self, *args, **kwargs):
        return db.session.query(User).all()

    def resolve_picks(self, *args, **kwargs):
        return db.session.query(Pick).all()

    def resolve_lines(self, *args, **kwargs):
        return db.session.query(Line).all()

    def resolve_scores(self, *args, **kwargs):
        return db.session.query(Score).all()

    def resolve_seasons(self, *args, **kwargs):
        return db.session.query(Season).all()

    def resolve_weeks(self, *args, **kwargs):
        return db.session.query(Week).all()
    # pylint: enable=no-member,unused-argument,no-self-use


schema = graphene.Schema(query=Query)  # pylint: disable=invalid-name
