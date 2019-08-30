import datetime
import json
from itertools import accumulate
from flask import Blueprint, render_template, request, redirect, url_for, Response, g
from flask_user import current_user, login_required
import plotly

from supercontest import db
from supercontest.core.scores import commit_scores
from supercontest.core.picks import commit_picks, InvalidPicks, PICK_DAYS
from supercontest.core.utilities import get_team_abv
from supercontest.core.results import calculate_leaderboard, commit_winners_and_points
from supercontest.models import Matchup, Pick, User

main_blueprint = Blueprint('main',  # pylint: disable=invalid-name
                           __name__,
                           template_folder='templates',
                           static_folder='static')


@main_blueprint.route('/')
@login_required
def home():
    return redirect(url_for('week.week_matchups'))


@main_blueprint.route('/leaderboard')
@login_required
def leaderboard():
    # Calculate and commit results, returning them to be rendered
    weeks, results, totals = calculate_leaderboard()
    # All three are necessary for the table, but 'results' contains
    # everything necessary for the line graph by itself. Structure:
    #   {user: {week: score, week: score...}
    # `totals` has the user as ID, and we'll want to map that to actual names
    # or emails for display, so let's do that now.
    display_map = {r.id: (' '.join([r.first_name, r.last_name]) if
                          r.first_name or r.last_name else r.email)
                   for r in db.session.query(User).all()}
    data = [
        plotly.graph_objs.Scatter(x=[0]+list(results[user[0]].keys()),
                                  y=list(accumulate([0]+list(results[user[0]].values()))),
                                  name=display_map[user[0]],
                                  visible=(True if current_user.id == user[0] else 'legendonly'))
        for user in totals  # user[0] is id, used as key for results dict
    ]
    # Note that a zero week with zero points is prepended to both arrays
    # to make the visualization better around the origin.
    dataJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)  # pylint: disable=invalid-name
    # Layout (titles, axes, etc) is handled in JS.
    return render_template('main/leaderboard.html',
                           weeks=weeks,
                           results=results,
                           totals=totals,
                           display_map=display_map,
                           dataJSON=dataJSON)


@main_blueprint.route('/feedback')
@login_required
def feedback():
    return render_template('main/feedback.html')


@main_blueprint.route('/pick', methods=['POST'])
@login_required
def pick():
    try:
        commit_picks(user=current_user,
                     week=request.json.get('week'),
                     teams=request.json.get('picks'))
    except InvalidPicks as msg:
        return Response(status=400, response=msg)
    else:
        return Response(status=200)


week_blueprint = Blueprint('week',  # pylint: disable=invalid-name
                           __name__,
                           template_folder='templates',
                           static_folder='static',
                           url_prefix='/week<week>')


@week_blueprint.url_defaults
def define_week(endpoint, values):  # pylint: disable=unused-argument
    """If the user goes to the website's home / without any week specification,
    query the database for the most recent matchups and go to that page.
    """
    if 'week' not in values:
        values['week'] = db.session.query(db.func.max(Matchup.week)).scalar() or 0  # pylint: disable=no-member


@week_blueprint.url_value_preprocessor
def get_week(endpoint, values):  # pylint: disable=unused-argument
    """Attributes 'available_weeks' and 'week' to the g object for
    use in subsequent routes. url_defaults obviously executes before this.
    """
    g.available_weeks = [
        result.week
        for result
        in db.session.query(Matchup.week).distinct().order_by(Matchup.week).all()  # pylint: disable=no-member
    ]
    g.week = int(values.pop('week'))


@week_blueprint.route('/')
@login_required
def week_matchups():
    if g.week == max(g.available_weeks or [0]):  # only check/commit scores if on the latest week
        # TODO: this should be changed to happen periodically! It's slow.
        commit_scores(week=g.week)  # pylint:disable=no-member
    matchups = db.session.query(Matchup).filter_by(week=g.week).all()  # pylint: disable=no-member
    # get the picks to overlay, then extract the single-element tuples
    picks = [pick[0] for pick in db.session.query(  # pylint: disable=no-member
        Pick.team).filter_by(week=g.week, user_id=current_user.id).all()]
    return render_template('week/week_matchups.html',
                           week=g.week,
                           available_weeks=g.available_weeks,
                           matchups=matchups,
                           picks=picks,
                           week_link_prefix='week.week_matchups',
                           switch_link=('week.week_picks', 'Picks'))


@week_blueprint.route('/picks')
@login_required
def week_picks():
    commit_winners_and_points(week=g.week)
    favored_teams = db.session.query(Matchup.favored_team).filter_by(week=g.week).all()  # pylint: disable=no-member
    favored_teams = [get_team_abv(team[0]) for team in favored_teams]
    underdog_teams = db.session.query(Matchup.underdog_team).filter_by(week=g.week).all()  # pylint: disable=no-member
    underdog_teams = [get_team_abv(team[0]) for team in underdog_teams]
    user_emails = db.session.query(User.email).all()  # pylint: disable=no-member
    all_picks = db.session.query(  # pylint: disable=no-member
        User.email, Pick.team, Pick.points).filter(
            Pick.week == g.week, Pick.user_id == User.id).all()
    all_picks = [(pick[0], get_team_abv(pick[1]), pick[2]) for pick in all_picks]
    if (datetime.datetime.today().isoweekday() in PICK_DAYS and
        max(g.available_weeks) == g.week):
        msg = ('Other user picks are hidden until lockdown on Saturday night '
               'at midnight.<br>You may see your own picks for this week '
               'on the <a href={}>{}</a> tab.'.format(
                   url_for('week.week_matchups'), 'Matchups'))
        return render_template('week/week_header.html',
                               week=g.week,
                               available_weeks=g.available_weeks,
                               message=msg,
                               week_link_prefix='week.week_picks',
                               switch_link=('week.week_matchups', 'Matchups'))
    return render_template('week/week_picks.html',
                           week=g.week,
                           available_weeks=g.available_weeks,
                           matchups=list(zip(favored_teams, underdog_teams)),
                           user_emails=user_emails,
                           all_picks=all_picks,
                           week_link_prefix='week.week_picks',
                           switch_link=('week.week_matchups', 'Matchups'))
