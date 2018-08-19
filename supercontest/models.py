from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    picks = relationship('Pick', back_populates='user')


class Pick(Base):
    __tablename__ = 'picks'
    id = Column(Integer, primary_key=True)
    week = Column(Integer, nullable=False)
    team = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='picks')
    points = Column(Integer)


class Matchup(Base):
    __tablename__ = 'matchups'
    id = Column(Integer, primary_key=True)
    week = Column(Integer, nullable=False)
    favored_team = Column(String, nullable=False)
    unfavored_team = Column(String, nullable=False)
    datetime = Column(String, nullable=False)
    line = Column(Float, nullable=False)
    favored_team_score = Column(Integer)
    unfavored_team_score = Column(Integer)
    status = Column(String)  # quarter, "F"inal, etc
