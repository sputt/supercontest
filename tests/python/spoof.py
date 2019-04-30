"""A testing module that contains fake lines and fake scores. Currently unused.
"""


def spoof_lines():
    """Just returns fake lines for testing purposes.
    """
    lines = [
        [u'LIONS*',      u'PACKERS',   u'SUNDAY, DECEMBER 31, 2017, 10:00 AM', u'1'],
        [u'COLTS*',      u'TEXANS',    u'SUNDAY, DECEMBER 31, 2017, 10:00 AM', u'2'],
        [u'VIKINGS*',    u'BEARS',     u'SUNDAY, DECEMBER 31, 2017, 10:00 AM', u'3'],
        [u'PATRIOTS*',   u'JETS',      u'SUNDAY, DECEMBER 31, 2017, 10:00 AM', u'4'],
        [u'GIANTS*',     u'REDSKINS',  u'SUNDAY, DECEMBER 31, 2017, 10:00 AM', u'5'],
        [u'EAGLES*',     u'COWBOYS',   u'SUNDAY, DECEMBER 31, 2017, 10:00 AM', u'6'],
        [u'STEELERS*',   u'BROWNS',    u'SUNDAY, DECEMBER 31, 2017, 10:00 AM', u'0'],
        [u'FALCONS*',    u'PANTHERS',  u'SUNDAY, DECEMBER 31, 2017, 1:25 PM',  u'0'],
        [u'RAVENS*',     u'BENGALS',   u'SUNDAY, DECEMBER 31, 2017, 1:25 PM',  u'7'],
        [u'BRONCOS*',    u'CHIEFS',    u'SUNDAY, DECEMBER 31, 2017, 1:25 PM',  u'8'],
        [u'RAMS*',       u'49ERS',     u'SUNDAY, DECEMBER 31, 2017, 1:25 PM',  u'3'],
        [u'CHARGERS*',   u'RAIDERS',   u'SUNDAY, DECEMBER 31, 2017, 1:25 PM',  u'1'],
        [u'DOLPHINS*',   u'BILLS',     u'SUNDAY, DECEMBER 31, 2017, 1:25 PM',  u'1'],
        [u'SEAHAWKS*',   u'CARDINALS', u'SUNDAY, DECEMBER 31, 2017, 1:25 PM',  u'4'],
        [u'BUCCANEERS*', u'SAINTS',    u'SUNDAY, DECEMBER 31, 2017, 1:25 PM',  u'0'],
        [u'TITANS*',     u'JAGUARS',   u'SUNDAY, DECEMBER 31, 2017, 1:25 PM',  u'9'],
    ]

    return lines


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
