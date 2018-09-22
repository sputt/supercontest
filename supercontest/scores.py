from __future__ import print_function
import sys
from supercontest.utilities import get_soup_from_url
from supercontest.models import Matchup
from supercontest.app import db


def fetch_scores():
    """Hits the NFL API for live score updates and the time status
    of the game (quarter, final, etc).
    """
    url = 'http://www.nfl.com/liveupdate/scorestrip/ss.xml'
    soup = get_soup_from_url(url)
    week = soup.gms['w']
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


def _commit_scores(week, scores):
    matchups = Matchup.query.filter_by(week=week).all()
    for game in scores:
        # could use home or visiting team, this is an arbitrary binary
        visiting_team = game['visiting_team']
        for matchup in matchups:
            if visiting_team == matchup.favored_team:
                matchup.favored_team_score = game['visiting_team_score']
                matchup.underdog_team_score = game['home_team_score']
                matchup.status = game['status']
                break
            elif visiting_team == matchup.underdog_team:
                matchup.underdog_team_score = game['visiting_team_score']
                matchup.favored_team_score = game['home_team_score']
                matchup.status = game['status']
                break
    db.session.commit()


def commit_scores(week):
    """Python wrapper for all score committing. Requires
    that the week be passed through Python.
    """
    scores, week_from_nfl = fetch_scores()
    if week != week_from_nfl:
        print('You are requested scores for week {} but the NFL is '
              'returning scores for week {}.'.format(week, week_from_nfl))
        return
    _commit_scores(week=week, scores=scores)


def main():
    """Command line entry point for all score committing. Requires
    that the week be passed through the CLI.
    """
    week = sys.argv[1]
    commit_scores(week=week)
