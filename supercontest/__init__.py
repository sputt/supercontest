import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)

app.config.from_object('config.default')
app.config.from_pyfile('config.py')
if 'APP_CONFIG_FILE' in os.environ:
    app.config.from_envvar('APP_CONFIG_FILE')

db = SQLAlchemy(app)

from . import models 

def create_db():
    # this lazy import of the models must be after db
    # instantiation and before creation.
    from . import models
    db.create_all()


def run_app():
    app.run(host='0.0.0.0')
