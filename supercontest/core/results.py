from sqlalchemy.sql import func

from supercontest import db
from supercontest.models import Pick, Matchup, User


def calculate_leaderboard(season):
    """returns
      results = {user_id: {week: score, week: score ... }
      weeks = [1, 2, ... ]
      totals = [(user_id, points), (user_id, points) ... ] (sorted)
    """
    user_ids = [result.id for result in db.session.query(User.id).all()]  # pylint: disable=no-member
    results = {user_id: {} for user_id in user_ids}
    # the 17 is only here because of the practice 18th week I added in 2018
    weeks = [result.week for result in db.session.query(  # pylint: disable=no-member
        Matchup.week
        ).filter(
            Matchup.season == season, Matchup.week <= 17
            ).distinct().order_by(Matchup.week).all()]
    for week in weeks:
        # Technically you only have to calc and commit the most recent
        # week, since the others are done and static, but we do it all every time
        # just in case it's never called during the week. You could infer which
        # ones weren't calculated and just do those efficiently, but this
        # extra computation isn't gonna kill us.
        commit_winners_and_points(season=season, week=week)
        user_scores = count_points_for_week(season=season, week=week)
        for user_score in user_scores:
            results[user_score[0]][week] = user_score[1]
    totals = {}
    for user, scores in results.items():
        totals[user] = sum(scores.values())
    sorted_totals = [(k, totals[k]) for k in sorted(totals, key=totals.get, reverse=True)]
    return weeks, results, sorted_totals


def count_points_for_week(season, week):
    """returns tuples of [(id, points), (id, points), etc]
    """
    results = db.session.query(  # pylint: disable=no-member
        User.id, func.sum(Pick.points)).filter(
            Pick.season == season,
            Pick.week == week,
            Pick.user_id == User.id).group_by(User.id).all()
    return results


def commit_winners_and_points(season, week):
    """Main entry point to calculate picks against matchups and write the
    results to the db.
    """
    commit_match_winners(season=season, week=week)
    commit_pick_points(season=season, week=week)


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
