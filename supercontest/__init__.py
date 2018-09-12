from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__, instance_relative_config=True)

app.config.from_object('config.default')
app.config.from_pyfile('config.py')
app.config.from_envvar('APP_CONFIG_FILE')

db = SQLAlchemy(app)


def create_db():
    db.create_all()


def run_app():
    app.run(host='0.0.0.0')
