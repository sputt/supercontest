"""Configuration for the flask app.
"""
SQLALCHEMY_DATABASE_URI = "sqlite:///../data/supercontest.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
DEBUG = True
