# pylint: disable=too-few-public-methods
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from supercontest.models import User, Pick, Matchup
from supercontest import db


class UserObject(SQLAlchemyObjectType):
    class Meta:
        model = User


class PickObject(SQLAlchemyObjectType):
    class Meta:
        model = Pick


class MatchupObject(SQLAlchemyObjectType):
    class Meta:
        model = Matchup


class Query(graphene.ObjectType):
    users = graphene.List(UserObject)
    picks = graphene.List(PickObject)
    matchups = graphene.List(MatchupObject)

    # pylint: disable=no-member,unused-argument,no-self-use
    def resolve_users(self, *args, **kwargs):
        return db.session.query(User).all()

    def resolve_picks(self, *args, **kwargs):
        return db.session.query(Pick).all()

    def resolve_matchups(self, *args, **kwargs):
        return db.session.query(Matchup).all()
    # pylint: enable=no-member,unused-argument,no-self-use


schema = graphene.Schema(query=Query)  # pylint: disable=invalid-name
