import json
from itertools import accumulate
from flask import Blueprint, render_template, request, redirect, url_for, Response, g
from flask_user import current_user, login_required
import plotly

from supercontest.dbsession import queries
from supercontest.core.picks import PICK_DAYS, commit_picks, InvalidPicks
from supercontest.core.scores import commit_scores
from supercontest.core.utilities import is_today, get_team_abv_map
from supercontest.core.results import (
    RESULTS_DAYS,
    determine_current_pick_points,
    determine_current_coverer,
    get_week_teams,
    get_sorted_week_teams,
    get_all_week_totals,
    get_season_totals,
)

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
        values['season'] = queries.get_max_season()
    if not values.get('week') and endpoint not in only_season_endpoints:
        values['week'] = queries.get_max_week(season=values['season'])


@season_week_blueprint.url_value_preprocessor
def get_week(endpoint, values):  # pylint: disable=unused-argument
    """Attributes current and available weeks and seasons to the g object for
    use in subsequent routes. url_defaults obviously executes before this.

    This also adds the useful is_current_week, which is a logical condition for
    many other actions.
    """
    g.available_seasons = queries.get_sorted_seasons()
    g.season = int(values.pop('season'))
    g.is_current_season = g.season == max(g.available_seasons)
    if endpoint not in only_season_endpoints:
        g.available_weeks = queries.get_sorted_weeks(season=g.season)
        g.week = int(values.pop('week'))
        g.is_current_week = g.is_current_season and g.week == max(g.available_weeks)


@season_week_blueprint.route('/season<season>/week<week>/matchups')
@login_required
def matchups():
    if g.is_current_week and is_today(RESULTS_DAYS):
        commit_scores(season=g.season, week=g.week)
    sorted_matchups = queries.get_sorted_matchups(season=g.season, week=g.week)
    # Get the picks to overlay. We only need the team names.
    pick_teams = [row.team for row in queries.get_picks(season=g.season,
                                                        week=g.week,
                                                        user_id=current_user.id)]
    if g.is_current_week and is_today(PICK_DAYS):
        msg = ('Make your picks by clicking on the teams below, '
               'then click submit at the bottom.')
    else:
        msg = ''
    # Since we already need team names to highlight picks, determine which
    # teams are covering in order to colorize.
    cover_status = {matchup.line_id: determine_current_coverer(matchup)
                    for matchup in sorted_matchups}
    return render_template('matchups.html',
                           sorted_matchups=sorted_matchups,
                           pick_teams=pick_teams,
                           cover_status=cover_status,
                           message=msg)


@season_week_blueprint.route('/season<season>/week<week>/picks')
@login_required
def picks():
    if g.is_current_week and is_today(RESULTS_DAYS):
        commit_scores(season=g.season, week=g.week)
    sorted_matchups = queries.get_sorted_matchups(season=g.season, week=g.week)
    # The matchups will be the column headers in the frontend table. We now need
    # the rows (user IDs) mapped with picked teams. If picks aren't locked down
    # yet, you're only going to report the info for the active user.
    if g.is_current_week and is_today(PICK_DAYS):
        _picks = get_week_teams(season=g.season, week=g.week, user_id=current_user.id)
        msg = ('To make or modify your picks, go to the <a href={}>{}</a> tab.<br>'
               'You may do this as much as you want until lockdown on Saturday night '
               'at midnight.<br>Everyone\'s picks will publish here at that time.'.format(
                   url_for('season_week.matchups'), 'Matchups'))
    else:
        _picks = get_week_teams(season=g.season, week=g.week)
        msg = ''
    # Now we need the status and current points in order to sort and display the
    # picks properly.
    status_map = {}
    points_map = {}
    for _matchup in sorted_matchups:
        status_map[_matchup.favored_team] = _matchup.status
        status_map[_matchup.underdog_team] = _matchup.status
        points_map[_matchup.favored_team] = determine_current_pick_points(
            row=_matchup, team=_matchup.favored_team)
        points_map[_matchup.underdog_team] = determine_current_pick_points(
            row=_matchup, team=_matchup.underdog_team)
    # And then order the users by total week score for the picks view.
    sorted_picks = get_sorted_week_teams(_picks, points_map)
    # And lastly we want to display slightly different data than the raw.
    id_name_map = queries.get_id_name_map()
    team_abv_map = get_team_abv_map()
    return render_template('picks.html',
                           sorted_matchups=sorted_matchups,
                           sorted_picks=sorted_picks,
                           id_name_map=id_name_map,  # used in template
                           team_abv_map=team_abv_map,  # used in template
                           points_map=json.dumps(points_map),  # dumped for js use
                           status_map=json.dumps(status_map),  # dumped for js use
                           message=msg)


@season_week_blueprint.route('/season<season>/leaderboard')
@login_required
def leaderboard():
    # If the lb or graph is being requested for the most recent season,
    # then fetch/calc/commit results for the most recent week of that season.
    # Only color the completed weeks.
    max_week = queries.get_max_week(season=g.season)
    if g.is_current_season and is_today(RESULTS_DAYS):
        commit_scores(season=g.season, week=max_week)
        color_week = max_week - 1
    else:
        color_week = max_week
    all_week_totals = get_all_week_totals(season=g.season)  # unsorted
    season_totals = get_season_totals(all_week_totals=all_week_totals)  # sorted
    id_name_map = queries.get_id_name_map()
    id_email_map = queries.get_id_email_map()
    max_points = color_week*5  # for total percentage display
    return render_template('leaderboard.html',
                           all_week_totals=all_week_totals,
                           season_totals=season_totals,
                           color_week=color_week,
                           id_name_map=id_name_map,
                           id_email_map=id_email_map,
                           max_points=max_points)


@season_week_blueprint.route('/season<season>/graph')
@login_required
def graph():
    # If the lb or graph is being requested for the most recent season,
    # then fetch/calc/commit results for the most recent week of that season.
    # Only graph the completed weeks.
    max_week = queries.get_max_week(season=g.season)
    if g.is_current_season and is_today(RESULTS_DAYS):
        commit_scores(season=g.season, week=max_week)
        graph_week = max_week - 1
    else:
        graph_week = max_week
    all_week_totals = get_all_week_totals(season=g.season)  # unsorted
    season_totals = get_season_totals(all_week_totals=all_week_totals)  # sorted
    id_name_map = queries.get_id_name_map()
    # Iterate over the sorted season totals so the graph legend shows names
    # in the same order as the leaderboard. If we didn't care about the sorting,
    # we'd just need all_week_totals to accumulate.
    data = []
    for user_id, _ in season_totals:
        weekly_data = all_week_totals[user_id]
        sorted_weeks = list(sorted([week for week in weekly_data.keys()
                                    if week <= graph_week]))
        sorted_points = [weekly_data[week] for week in sorted_weeks]
        is_current_user = user_id == current_user.id
        _graph = plotly.graph_objs.Scatter(
            # Note that a zero week with zero points is prepended to both arrays
            # to make the visualization better around the origin.
            x=[0]+sorted_weeks,
            y=list(accumulate([0]+sorted_points)),
            name=id_name_map[user_id],
            visible=(True if is_current_user else 'legendonly')
        )
        data.append(_graph)
    data_json = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)
    # Layout (titles, axes, etc) is handled in JS.
    return render_template('graph.html', dataJSON=data_json)


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
        commit_picks(user_id=current_user.id,
                     season=request.json.get('season'),
                     week=request.json.get('week'),
                     teams=request.json.get('picks'))
    except InvalidPicks as msg:
        return Response(status=400, response=msg)
    else:
        return Response(status=200)
