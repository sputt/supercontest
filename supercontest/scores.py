from utilities import get_soup_from_url
from models import Matchup
from backend import session_scope


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

    return scores


def spoof_scores():
    """Just returns fake scores for testing purposes.
    """
    scores = [
        {u'home_team': u'LIONS',      u'home_team_score': u'35', u'visiting_team': u'PACKERS',   u'visiting_team_score': u'11', u'status': u'F'},
        {u'home_team': u'COLTS',      u'home_team_score': u'22', u'visiting_team': u'TEXANS',    u'visiting_team_score': u'13', u'status': u'F'},
        {u'home_team': u'VIKINGS',    u'home_team_score': u'23', u'visiting_team': u'BEARS',     u'visiting_team_score': u'10', u'status': u'F'},
        {u'home_team': u'PATRIOTS',   u'home_team_score': u'26', u'visiting_team': u'JETS',      u'visiting_team_score': u'6',  u'status': u'F'},
        {u'home_team': u'GIANTS',     u'home_team_score': u'18', u'visiting_team': u'REDSKINS',  u'visiting_team_score': u'10', u'status': u'F'},
        {u'home_team': u'EAGLES',     u'home_team_score': u'0',  u'visiting_team': u'COWBOYS',   u'visiting_team_score': u'6',  u'status': u'F'},
        {u'home_team': u'STEELERS',   u'home_team_score': u'28', u'visiting_team': u'BROWNS',    u'visiting_team_score': u'24', u'status': u'F'},
        {u'home_team': u'FALCONS',    u'home_team_score': u'22', u'visiting_team': u'PANTHERS',  u'visiting_team_score': u'10', u'status': u'F'},
        {u'home_team': u'RAVENS',     u'home_team_score': u'27', u'visiting_team': u'BENGALS',   u'visiting_team_score': u'31', u'status': u'F'},
        {u'home_team': u'BRONCOS',    u'home_team_score': u'24', u'visiting_team': u'CHIEFS',    u'visiting_team_score': u'27', u'status': u'F'},
        {u'home_team': u'RAMS',       u'home_team_score': u'13', u'visiting_team': u'49ERS',     u'visiting_team_score': u'0',  u'status': u'F'},
        {u'home_team': u'CHARGERS',   u'home_team_score': u'30', u'visiting_team': u'RAIDERS',   u'visiting_team_score': u'10', u'status': u'F'},
        {u'home_team': u'DOLPHINS',   u'home_team_score': u'16', u'visiting_team': u'BILLS',     u'visiting_team_score': u'22', u'status': u'F'},
        {u'home_team': u'SEAHAWKS',   u'home_team_score': u'24', u'visiting_team': u'CARDINALS', u'visiting_team_score': u'26', u'status': u'F'},
        {u'home_team': u'BUCCANEERS', u'home_team_score': u'31', u'visiting_team': u'SAINTS',    u'visiting_team_score': u'24', u'status': u'F'},
        {u'home_team': u'TITANS',     u'home_team_score': u'15', u'visiting_team': u'JAGUARS',   u'visiting_team_score': u'10', u'status': u'F'},
    ]

    return scores


def commit_scores(week, scores):
    with session_scope() as session:
        matchups = session.query(Matchup).filter_by(week=week).all()
        for game in scores:
            # could use home or visiting team, this is an arbitrary binary
            visiting_team = game['visiting_team']
            for matchup in matchups:
                if visiting_team == matchup.favored_team:
                    matchup.favored_team_score = game['visiting_team_score']
                    matchup.unfavored_team_score = game['home_team_score']
                    matchup.status = game['status']
                    break
                elif visiting_team == matchup.unfavored_team:
                    matchup.unfavored_team_score = game['visiting_team_score']
                    matchup.favored_team_score = game['home_team_score']
                    matchup.status = game['status']
                    break
