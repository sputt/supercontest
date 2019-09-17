"""Logic for fetching NFL scores and committing them to the database.
"""
import sys

from supercontest.dbsession import commits
from supercontest.core.utilities import get_soup_from_url


def fetch_scores():
    """Hits the NFL API for live score updates and the time status
    of the game (quarter, final, etc).

    Returns:
        scores (list of dicts): Each score dict has home_team, home_team_score,
            visiting_team, visiting_team_score, status
        week (int)
    """
    url = 'http://www.nfl.com/liveupdate/scorestrip/ss.xml'
    soup = get_soup_from_url(url)
    week = int(soup.gms['w'])
    games = soup.gms.find_all('g')
    scores = []
    for game in games:
        score = {}
        home_team = game['hnn'].upper()
        visiting_team = game['vnn'].upper()
        score[u'home_team'] = home_team
        score[u'home_team_score'] = game['hs']
        score[u'visiting_team'] = visiting_team
        score[u'visiting_team_score'] = game['vs']
        score[u'status'] = game['q']
        scores.append(score)

    return scores, week


def commit_scores(season, week):
    """Python wrapper for all score committing. Requires
    that the week be passed through Python.

    Args:
        week (int)
    """
    scores, week_from_nfl = fetch_scores()
    if week != week_from_nfl:
        sys.stderr.write(
            'You are requesting scores for week {} but the NFL is '
            'returning scores for week {}.\n'.format(week, week_from_nfl))
        return
    commits._commit_scores(season=season, week=week, scores=scores)  # pylint: disable=protected-access
