from supercontest.models import Pick, Matchup
from supercontest.backend import session_scope


POINT_MAP = {
    'correct': 1.0,
    'incorrect': 0.0,
    'push': 0.5,
}


def compare_scores_to_lines(week):
    """Queries the matchups table for the week and compares the
    difference of the scores to the line, reporting the correct pick.
    This does not care about the games being done - if the current
    scores dictate a correct pick, it returns that.

    Returns:
        (dict): Results by team name and calculated points.

    Example:
        {'EAGLES': 1.0, 'BROWNS': 0.0,
         'JAGUARS': 0.5, 'JETS': 0.5',
         ...}
    """
    with session_scope() as session:
        matchups = session.query(Matchup).filter_by(week=week).all()
        results = {}
        for matchup in matchups:
            delta = float(matchup.favored_team_score - matchup.underdog_team_score)
            line = matchup.line
            if delta > line:
                results[matchup.favored_team] = POINT_MAP['correct']
                results[matchup.underdog_team] = POINT_MAP['incorrect']
            elif delta == line:
                results[matchup.favored_team] = POINT_MAP['push']
                results[matchup.underdog_team] = POINT_MAP['push']
            else:
                results[matchup.favored_team] = POINT_MAP['incorrect']
                results[matchup.underdog_team] = POINT_MAP['correct']

    return results


def commit_results(week, results):
    """Using the results from compare_scores_to_lines(), writes the points
    to the Picks table rows based on what the user selected.
    """
    with session_scope() as session:
        picks = session.query(Pick).filter_by(week=week).all()
        for pick in picks:
            pick.points = results[pick.team]
