"""The main application. Contains the app and db for import elsewhere.
"""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

app = Flask(__name__)  # pylint: disable=invalid-name
app.config.from_pyfile('config.py')
app.config.from_pyfile('gmail.py')
db = SQLAlchemy(app)  # pylint: disable=invalid-name
mail = Mail(app)  # pylint: disable=invalid-name

# Must be after db definition and before creation.
from supercontest import scores  # pylint: disable=wrong-import-position
from supercontest import models  # pylint: disable=wrong-import-position


@app.route('/', defaults={'week': None})
@app.route('/week<week>')
def home(week=None):
    """Main route for basic app interaction.
    """
    weeks = [res.week for res
             in db.session.query(models.Matchup.week).distinct().all()]
    if week is not None:
        week = int(week)
    else:
        week = max(weeks)
    scores.commit_scores(week=week)
    matchups = models.Matchup.query.filter_by(week=week).all()
    return render_template('table.html',
                           week=week,
                           available_weeks=weeks,
                           matchups=matchups)


def create_db():
    """Creates the db. Only called once, manually.
    """
    db.create_all()


def run_app():
    """Logic for starting the app. Most should be abstracted to config.
    """
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    run_app()
