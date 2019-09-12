import json
from itertools import accumulate
from dateutil import parser as dateutil_parser
from flask import Blueprint, render_template, request, redirect, url_for, Response, g
from flask_user import current_user, login_required
import plotly

from supercontest import db
from supercontest.core.picks import commit_picks, InvalidPicks, PICK_DAYS
from supercontest.core.utilities import get_team_abv, get_id_name_map, is_today
from supercontest.core.results import update_results, get_results
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
    if g.is_current_week:
        update_results(season=g.season, week=g.week)
    # The template uses all of the info in the matchup table.
    _matchups = db.session.query(Matchup).filter_by(  # pylint: disable=no-member
        season=g.season, week=g.week).all()
    # Convert the datetime strings to actual datetime objects
    for _matchup in _matchups:
        _matchup.datetime = dateutil_parser.parse(_matchup.datetime)
    # Sort matchups by the datetime attribute.
    sorted_matchups = sorted(_matchups, key=lambda _matchup: _matchup.datetime)
    # Get the picks to overlay. We only need the team names. Since we have
    # to highlight picks by name anyway, we just use a comparison to
    # matchup.winner rather than using pick.points to colorize.
    _picks = [pick.team for pick in db.session.query(Pick.team).filter_by(  # pylint: disable=no-member
        season=g.season, week=g.week, user_id=current_user.id).all()]
    return render_template('matchups.html',
                           matchups=sorted_matchups,
                           picks=_picks)


@season_week_blueprint.route('/season<season>/week<week>/picks')
@login_required
def picks():
    if g.is_current_week:
        update_results(season=g.season, week=g.week)
    # The template only uses matchup.favored_team and matchup.underdog_team
    # for the column headers, then status for the lookup.
    _matchups = db.session.query(Matchup).filter_by(  # pylint: disable=no-member
        season=g.season, week=g.week).all()
    # Extract the status into a simple lookup so that picks can know how to
    # color the unstarted games. While iterating, replace the full team names
    # with their abbreviations.
    status_map = {}
    for _matchup in _matchups:
        _matchup.favored_team = get_team_abv(_matchup.favored_team)
        _matchup.underdog_team = get_team_abv(_matchup.underdog_team)
        status_map[_matchup.favored_team] = _matchup.status
        status_map[_matchup.underdog_team] = _matchup.status
    display_map = get_id_name_map()
    # If picks aren't locked down yet, you're only going to report the info
    # for the active user.
    # This route uses pick.points to color the cells, not matchup.winner.
    only_me = is_today(PICK_DAYS) and g.is_current_week
    if only_me:
        user_ids = [str(current_user.id)]
        sorted_user_ids = user_ids
        _picks = [(str(pick.user_id), get_team_abv(pick.team), pick.points)
                  for pick in db.session.query(Pick).filter_by(  # pylint: disable=no-member
                      season=g.season, week=g.week, user_id=current_user.id).all()]
        msg = ('Other user picks are hidden until lockdown on Saturday night '
               'at midnight.<br>You may continue to modify your own picks for '
               'this week on the <a href={}>{}</a> tab until then.'.format(
                   url_for('season_week.matchups'), 'Matchups'))
    else:
        user_ids = [str(user.id) for user in db.session.query(User.id).all()]  # pylint: disable=no-member
        sorted_user_ids = sorted(user_ids,
                                 key=lambda user_id: display_map[int(user_id)])
        _picks = [(str(pick.user_id), get_team_abv(pick.team), pick.points)
                  for pick in db.session.query(Pick).filter_by(  # pylint: disable=no-member
                      season=g.season, week=g.week).all()]
        msg = ''
    return render_template(template_name_or_list='picks.html',
                           matchups=_matchups,
                           picks=_picks,
                           user_ids=sorted_user_ids,
                           display_map=display_map,
                           status_map=json.dumps(status_map),
                           message=msg)


@season_week_blueprint.route('/season<season>/leaderboard')
@login_required
def leaderboard():
    # If the leaderboard is being requested for the most recent season,
    # then fetch/calc/commit results for the most recent week of that season.
    max_week = db.session.query(db.func.max(Matchup.week)).filter_by(  # pylint: disable=no-member
        season=g.season).scalar()
    if g.season == max(g.available_seasons):
        update_results(season=g.season, week=max_week)
        color_week = max_week - 1
    else:
        color_week = max_week
    results, totals = get_results(g.season)
    display_map = get_id_name_map()
    return render_template('leaderboard.html',
                           results=results,
                           totals=totals,
                           color_week=color_week,
                           display_map=display_map)


@season_week_blueprint.route('/season<season>/graph')
@login_required
def graph():
    # If the lb graph is being requested for the most recent season,
    # then fetch/calc/commit results for the most recent week of that season.
    if g.season == max(g.available_seasons):
        max_week = db.session.query(db.func.max(Matchup.week)).filter_by(  # pylint: disable=no-member
            season=g.season).scalar()
        update_results(season=g.season, week=max_week)
    results, totals = get_results(season=g.season)
    # 'results' contains everything necessary for the line graph by itself.
    # Structure: {user: {week: score, week: score...}
    # `totals` has the user as ID, and we'll want to map that to actual names
    # or emails for display, so let's do that now.
    display_map = get_id_name_map()
    data = [
        plotly.graph_objs.Scatter(x=[0]+list(sorted(results[user[0]].keys())),
                                  y=list(accumulate([0]+[item[1]
                                         for item in sorted(results[user[0]].items(),
                                                            key=lambda kv: kv[0])])),
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
