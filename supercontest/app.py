from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user
from supercontest.forms import EmailPasswordForm

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

# Must be after db definition and before creation.
from supercontest import models


@app.route('/')
def index():
    week = 2
    matchups = models.Matchup.query.filter_by(week=week).all()
    return render_template('table.html', week=week, matchups=matchups)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = EmailPasswordForm()
    # if form.validate_on_submit():
    #    # check password here later
    #    return redirect(url_for('index'))
    return render_template('login.html', form=form)


def create_db():
    db.create_all()


def run_app():
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    run_app()
