from sqlalchemy import func

from supercontest import db
from supercontest.models import Pick, Matchup, User
from supercontest.core.utilities import is_today
from supercontest.core.scores import commit_scores

# The scores update Th, Sun, Mon, and then add Wednesday
# because we want to fetch scores on Wednesdays after the lines
# are update (they'll all be zero, but will fill the tables).
RESULTS_DAYS = ['Wednesday', 'Thursday', 'Sunday', 'Monday']


def update_results(season, week):
    """Helper function for all the view that require current scores
    and current results (teams who covered, points for each pick).
    You typically only want to call this if is_current_week=True.

    Args:
        season (int): g.season, from the flask global object or elsewhere
        week (int): g.week, from the flask global object or elswehere
    """
    if is_today(RESULTS_DAYS):
        commit_scores(season=season, week=week)
    # No matter the day, calculate the current winners to color picks.
    commit_winners_and_points(season=season, week=week)


def get_results(season):
    """Helper function for all the views that do the summing of
    user results for display. Basically just returns a formatted
    copy of the entire Pick.points column, grouped by week and user.

    Args:
        season (int)
    """
    # Get weekly scores grouped by user. Could do the User and Pick queries
    # in one, but we need to cast to easy Python dict format anyway.
    user_ids = [result.id for result in db.session.query(User.id).all()]  # pylint: disable=no-member
    results = {}  # {user_id: {week: score, week: score ... }
    for user_id in user_ids:
        scores_by_week = db.session.query(  # pylint:disable=no-member
            Pick.week, func.sum(Pick.points)).filter(
                Pick.season == season,
                Pick.user_id == user_id).group_by(Pick.week).all()
        results[user_id] = {item[0]: item[1] for item in scores_by_week}
    totals = {}  # [(user_id, points), (user_id, points) ... ] (sorted)
    for user, scores in results.items():
        totals[user] = sum(scores.values())
    sorted_totals = [(k, totals[k]) for k in sorted(totals, key=totals.get, reverse=True)]
    return results, sorted_totals


def commit_winners_and_points(season, week):
    """Main entry point to calculate picks against matchups and write the
    results to the db.
    """
    commit_match_winners(season=season, week=week)
    commit_pick_points(season=season, week=week)


def commit_match_winners(season, week):
    matchups = db.session.query(Matchup).filter(  # pylint: disable=no-member
        Matchup.season == season,
        Matchup.week == week,
        Matchup.status != 'P').all()
    for matchup in matchups:
        delta = matchup.favored_team_score - matchup.underdog_team_score
        if delta > matchup.line:
            matchup.winner = matchup.favored_team
        elif delta == matchup.line:
            # if the line is a push, include both team names in string
            matchup.winner = matchup.favored_team + matchup.underdog_team
        else:
            matchup.winner = matchup.underdog_team
    db.session.commit()  # pylint: disable=no-member


def commit_pick_points(season, week):
    picks = db.session.query(Pick).filter_by(season=season, week=week).all()  # pylint: disable=no-member
    winners = [result.winner for result in db.session.query(  # pylint: disable=no-member
        Matchup.winner).filter_by(season=season, week=week).all() if result.winner]
    for pick in picks:
        if pick.team in winners:  # direct match
            pick.points = 1.0
        # in a string like WINNERLOSER, for pushes
        elif any(pick.team in winner for winner in winners):
            pick.points = 0.5
        else:
            pick.points = 0
    db.session.commit()  # pylint: disable=no-member
