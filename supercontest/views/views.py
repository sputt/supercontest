import json
from itertools import accumulate
from flask import Blueprint, render_template, request, redirect, url_for, Response, g
from flask_user import current_user, login_required
import plotly

from supercontest import db
from supercontest.core.scores import commit_scores
from supercontest.core.picks import commit_picks, InvalidPicks, PICK_DAYS
from supercontest.core.utilities import get_team_abv, get_id_name_map, is_today
from supercontest.core.results import calculate_leaderboard, commit_winners_and_points
from supercontest.models import Matchup, Pick, User

# This is the primary blueprint of the application. If flask supported nested
# blueprints, I'd do one for season and one for week, but they're both here.
# Many routes in the supercontest are data-specific to the season and week.
season_week_blueprint = Blueprint('season_week',  # pylint: disable=invalid-name
                                  __name__,
                                  template_folder='templates',
                                  static_folder='static')
only_season_endpoints = ['season_week.leaderboard', 'season_week.graph']  # pylint: disable=invalid-name


@season_week_blueprint.url_defaults
def define_week(endpoint, values):  # pylint: disable=unused-argument
    """If the user goes to the website's home / without any week or season
    specification, query the database for the most recent matchups and go
    to that page.
    """
    if not values.get('season'):
        values['season'] = db.session.query(db.func.max(Matchup.season)).scalar() or 0  # pylint: disable=no-member
    if not values.get('week') and endpoint not in only_season_endpoints:
        values['week'] = db.session.query(db.func.max(Matchup.week)).filter_by(  # pylint: disable=no-member
            season=values['season']).scalar() or 0


@season_week_blueprint.url_value_preprocessor
def get_week(endpoint, values):  # pylint: disable=unused-argument
    """Attributes current and available weeks and seasons to the g object for
    use in subsequent routes. url_defaults obviously executes before this.

    This also adds the useful is_current_week, which is a logical condition for
    many other actions.
    """
    g.available_seasons = [
        result.season
        for result
        in db.session.query(Matchup.season).distinct().order_by(Matchup.season).all()  # pylint: disable=no-member
    ]
    g.season = int(values.pop('season'))

    if endpoint not in only_season_endpoints:
        g.available_weeks = [
            result.week
            for result
            in db.session.query(Matchup.week).filter_by(  # pylint: disable=no-member
                season=g.season).distinct().order_by(Matchup.week).all()
        ]
        g.week = int(values.pop('week'))

        g.is_current_week = (g.season == max(g.available_seasons or [0]) and
                             g.week == max(g.available_weeks or [0]))


@season_week_blueprint.route('/season<season>/week<week>/matchups')
@login_required
def matchups():
    # If you are on the most recent week of the most recent season, this
    # fetches and commits scores every time the site is visited/refreshed.
    # It's not the slowest thing in the world, and is ok for now. It is
    # restricted to Thursday/Sunday/Monday, because those are the only
    # days scores would change, as well as Wednesday because we want to
    # commit scores when we fetch lines.
    if g.is_current_week and is_today(['Wednesday',
                                       'Thursday', 'Sunday', 'Monday']):
        commit_scores(season=g.season, week=g.week)  # pylint: disable=no-member
    _matchups = db.session.query(Matchup).filter_by(  # pylint: disable=no-member
        season=g.season, week=g.week).all()
    # get the picks to overlay, then extract the single-element tuples
    _picks = [pick[0] for pick in db.session.query(Pick.team).filter_by(  # pylint: disable=no-member
        season=g.season, week=g.week, user_id=current_user.id).all()]
    return render_template('matchups.html',
                           matchups=_matchups,
                           picks=_picks)


@season_week_blueprint.route('/season<season>/week<week>/picks')
@login_required
def picks():
    commit_winners_and_points(season=g.season, week=g.week)
    results = db.session.query(  # pylint: disable=no-member
        Matchup.favored_team, Matchup.underdog_team).filter_by(
            season=g.season, week=g.week).all()
    favs, dogs = zip(*results)
    favored_teams = [get_team_abv(team) for team in favs]
    underdog_teams = [get_team_abv(team) for team in dogs]
    _matchups = list(zip(favored_teams, underdog_teams))
    user_ids = [str(ident[0]) for ident in db.session.query(User.id).all()]  # pylint: disable=no-member
    display_map = get_id_name_map()
    all_picks = db.session.query(  # pylint: disable=no-member
        User.id, Pick.team, Pick.points).filter(
            Pick.season == g.season, Pick.week == g.week, Pick.user_id == User.id).all()
    all_picks = [(str(pick[0]), get_team_abv(pick[1]), pick[2]) for pick in all_picks]
    if is_today(PICK_DAYS) and g.is_current_week:
        msg = ('Other user picks are hidden until lockdown on Saturday night '
               'at midnight.<br>You may see your own picks for this week '
               'on the <a href={}>{}</a> tab.'.format(
                   url_for('season_week.matchups'), 'Matchups'))
        return render_template('pick_restriction.html', message=msg)
    return render_template('picks.html',
                           matchups=_matchups,
                           user_ids=user_ids,
                           display_map=display_map,
                           all_picks=all_picks)


@season_week_blueprint.route('/season<season>/leaderboard')
@login_required
def leaderboard():
    # Calculate and commit results, returning them to be rendered
    weeks, results, totals = calculate_leaderboard(season=g.season)
    display_map = get_id_name_map()
    return render_template('leaderboard.html',
                           weeks=weeks,
                           results=results,
                           totals=totals,
                           display_map=display_map)


@season_week_blueprint.route('/season<season>/graph')
@login_required
def graph():
    # Calculate and commit results, returning them to be rendered
    _, results, totals = calculate_leaderboard(season=g.season)
    # All three are necessary for the table, but 'results' contains
    # everything necessary for the line graph by itself. Structure:
    #   {user: {week: score, week: score...}
    # `totals` has the user as ID, and we'll want to map that to actual names
    # or emails for display, so let's do that now.
    display_map = get_id_name_map()
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
    return render_template('graph.html', dataJSON=dataJSON)


# The "main" blueprint is the collection of all other views, the ones that
# don't require a season or week to be specified.
main_blueprint = Blueprint('main',  # pylint: disable=invalid-name
                           __name__,
                           template_folder='templates',
                           static_folder='static')


@main_blueprint.route('/')
@login_required
def home():
    return redirect(url_for('season_week.matchups'))


@main_blueprint.route('/feedback')
@login_required
def feedback():
    return render_template('feedback.html')


@main_blueprint.route('/rules')
@login_required
def rules():
    return render_template('rules.html')


@main_blueprint.route('/pick', methods=['POST'])
@login_required
def pick():
    try:
        commit_picks(user=current_user,
                     season=request.json.get('season'),
                     week=request.json.get('week'),
                     teams=request.json.get('picks'))
    except InvalidPicks as msg:
        return Response(status=400, response=msg)
    else:
        return Response(status=200)
