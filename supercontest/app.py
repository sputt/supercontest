from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

# Must be after db definition and before creation.
from supercontest import models, scores


@app.route('/', defaults={'week': None})
@app.route('/week<week>')
def home(week=None):
    if week is not None:
        # Use the week requested in the route, but cast str to int.
        week = int(week)
    else:
        # Look up the most recent week in the db (already an int).
        week = db.session.query(db.func.max(models.Matchup.week)).scalar()
    scores.commit_scores(week=week)
    matchups = models.Matchup.query.filter_by(week=week).all()
    return render_template('table.html', week=week, matchups=matchups)


def create_db():
    db.create_all()


def run_app():
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    run_app()
