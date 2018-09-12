import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask

from supercontest import models, lines, matchups, picks, scores, users, utilities, views


APP = Flask(__name__)
DB_NAME = 'supercontest.db'
DB_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(DB_DIR, DB_NAME)
engine = create_engine('sqlite:///' + DB_PATH, echo=True)
Session = sessionmaker(bind=engine)
models.Base.metadata.create_all(engine)


def main():
    # Start fresh, everytime (just for now)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    APP.run(host='0.0.0.0', debug=True)


if __name__ == '__main__':
    main()
