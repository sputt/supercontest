import operator
from sqlalchemy.sql import func

from supercontest import db
from supercontest.models import Pick, Matchup, User


def calculate_leaderboard():
    """returns
      results = {user: {week: score, week: score ... }
      weeks = [1, 2, ... ]
      totals = [(user, points), (user, points) ... ] (sorted)
    """
    user_emails = [result.email for result in db.session.query(User.email).all()]
    results = {user_email: {} for user_email in user_emails}
    weeks = [result.week for result in db.session.query(Matchup.week).distinct().all()]  # pylint: disable=no-member
    for week in weeks:
        # TODO - technically you only have to calc and commit the most recent week, since the others are done and static
        commit_winners_and_points(week)
        user_scores = count_points_for_week(week)
        for user_score in user_scores:
            results[user_score[0]][week] = user_score[1]
    totals = {}
    for user, scores in results.items():
        totals[user] = sum(scores.values())
    return weeks, results, sorted(totals.items(), key=operator.itemgetter(1), reverse=True)


def count_points_for_week(week):
    """returns tuples of [(email, points), (email, points), etc]
    """
    return db.session.query(User.email, func.sum(Pick.points)).filter(Pick.week == week, Pick.user_id == User.id).group_by(Pick.user_id).all()


def commit_winners_and_points(week):
    """Main entry point to calculate picks against matchups and write the
    results to the db.
    """
    commit_match_winners(week=week)
    commit_pick_points(week=week)


def commit_pick_points(week):
    picks = db.session.query(Pick).filter_by(week=week).all()
    winners = [result.winner for result in db.session.query(Matchup.winner).filter_by(week=week).all()]
    for pick in picks:
        if pick.team in winners:  # direct match
            pick.points = 1.0
        elif any(pick.team in winner for winner in winners):  # in a string like WINNERLOSER, for pushes
            pick.points = 0.5
        else:
            pick.points = 0
    db.session.commit()


def commit_match_winners(week):
    matchups = db.session.query(Matchup).filter_by(week=week).all()
    for matchup in matchups:
        delta = matchup.favored_team_score - matchup.underdog_team_score
        if delta > matchup.line:
            matchup.winner = matchup.favored_team
        elif delta == matchup.line:
            # if the line is a push, include both team names in string
            matchup.winner = matchup.favored_team + matchup.underdog_team
        else:
            matchup.winner = matchup.underdog_team
    db.session.commit()