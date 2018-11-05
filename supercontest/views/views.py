from flask import Blueprint, render_template
from flask_user import current_user, login_required

from supercontest import db
from supercontest.scores import commit_scores
from supercontest.models import Matchup

main_blueprint = Blueprint('main', __name__, template_folder='templates')


@main_blueprint.route('/', defaults={'week': None})
@main_blueprint.route('/week<week>')
def home(week=None):
    """Main route for basic app interaction.
    """
    weeks = [result.week for result
             in db.session.query(Matchup.week).distinct().all()]  # pylint: disable=no-member
    max_week = max(weeks) if weeks else 0
    week = int(week) if week is not None else max_week
    if week == max_week:  # only check/commit scores if on the latest week
        commit_scores(week=week)
    matchups = db.session.query(Matchup).filter_by(week=week).all()
    return render_template('main/table.html',
                           week=week,
                           available_weeks=weeks,
                           matchups=matchups)


@main_blueprint.route('/members')
@login_required
def auth_route():
    return current_user.username
