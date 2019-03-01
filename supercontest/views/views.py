from flask import Blueprint, render_template, request, redirect, url_for
from flask_user import current_user, login_required

from supercontest import db
from supercontest.core.scores import commit_scores
from supercontest.models import Matchup, UserProfileForm

main_blueprint = Blueprint('main', __name__, template_folder='templates')


@main_blueprint.route('/', defaults={'week': None})
@main_blueprint.route('/week<week>')
@login_required
def home(week=None):
    """Main route for basic app interaction.
    """
    weeks = [result.week for result
             in db.session.query(Matchup.week).distinct().all()]  # pylint: disable=no-member
    max_week = max(weeks) if weeks else 0
    week = int(week) if week is not None else max_week
    if week == max_week:  # only check/commit scores if on the latest week
        # TODO: this should be changed to happen periodically! It's slow.
        commit_scores(week=week)
    matchups = db.session.query(Matchup).filter_by(week=week).all()
    return render_template('main/table.html',
                           week=week,
                           available_weeks=weeks,
                           matchups=matchups)


@main_blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    form = UserProfileForm(request.form, obj=current_user)
    if request.method == 'POST' and form.validate():
        form.populate_obj(current_user)
        db.session.commit()
        return redirect(url_for('main.home'))
    # Process GET or invalid POST
    return render_template('main/user_profile.html', form=form)
