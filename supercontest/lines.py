from utilities import get_soup_from_url
from models import Matchup
from backend import session_scope


def fetch_lines():
    """Hits the official Westgate site and returns its line table as an html string,
    then coerces it into the following format: [FAVORED_TEAM, UNDERDOG_TEAM, DATETIME, LINE]

    Example Westgate return:
        [[u'1 SEAHAWKS', u'2 CARDINALS*', u'+6', u'THURSDAY, NOVEMBER 9, 2017 5:25 PM'],
         [u'23 GIANTS', u'24 49ERS*', u'+2.5', u'SUNDAY, NOVEMBER 12, 2017 1:25 PM'],...]
    """
    url = ('https://www.westgatedestinations.com/nevada/las-vegas/westgate-las-vegas-'
           'hotel-casino/casino/supercontest-weekly-card')
    soup = get_soup_from_url(url)
    table = soup.find('table')
    date = ''
    lines = []
    for _tr in table.find_all('tr'):
        tds = _tr.find_all('td')
        # if only the first cell is populated, it's just a date row,
        # which is concatenated for subsequent iterations until it changes
        if len([td for td in tds if td.text]) == 1:
            date = tds[0].text
        else:
            line = [td.text for td in tds]
            date_time = date + ' ' + line.pop(1)  # remove the time and add to date
            line.append(date_time)
            if line[2] == 'PK':  # if it's a draw pick, set the line to zero for math
                line[2] = '+0'
            line.append(line.pop(2))  # move the line to the end
            # remove the team number and whitespace, we only care about name
            for cell_index in [0, 1]:
                line[cell_index] = line[cell_index].split(None, 1)[-1].strip()
            # strip the + in the predicted line, it's always positive for the first col winner
            line[-1] = line[-1].replace('+', '')
            lines.append(line)

    return lines


def spoof_lines():
    """Just returns fake lines for testing purposes.
    """
    lines = [
        [u'LIONS*', u'PACKERS', u'SUNDAY, DECEMBER 31, 2017, 10:00 AM', u'1'],
        [u'COLTS*', u'TEXANS', u'SUNDAY, DECEMBER 31, 2017, 10:00 AM', u'2'],
        [u'VIKINGS*', u'BEARS', u'SUNDAY, DECEMBER 31, 2017, 10:00 AM', u'3'],
        [u'PATRIOTS*', u'JETS', u'SUNDAY, DECEMBER 31, 2017, 10:00 AM', u'4'],
        [u'GIANTS*', u'REDSKINS', u'SUNDAY, DECEMBER 31, 2017, 10:00 AM', u'5'],
        [u'EAGLES*', u'COWBOYS', u'SUNDAY, DECEMBER 31, 2017, 10:00 AM', u'6'],
        [u'STEELERS*', u'BROWNS', u'SUNDAY, DECEMBER 31, 2017, 10:00 AM', u'0'],
        [u'FALCONS*', u'PANTHERS', u'SUNDAY, DECEMBER 31, 2017, 1:25 PM', u'0'],
        [u'RAVENS*', u'BENGALS', u'SUNDAY, DECEMBER 31, 2017, 1:25 PM', u'7'],
        [u'BRONCOS*', u'CHIEFS', u'SUNDAY, DECEMBER 31, 2017, 1:25 PM', u'8'],
        [u'RAMS*', u'49ERS', u'SUNDAY, DECEMBER 31, 2017, 1:25 PM', u'3'],
        [u'CHARGERS*', u'RAIDERS', u'SUNDAY, DECEMBER 31, 2017, 1:25 PM', u'1'],
        [u'DOLPHINS*', u'BILLS', u'SUNDAY, DECEMBER 31, 2017, 1:25 PM', u'1'],
        [u'SEAHAWKS*', u'CARDINALS', u'SUNDAY, DECEMBER 31, 2017, 1:25 PM', u'4'],
        [u'BUCCANEERS*', u'SAINTS', u'SUNDAY, DECEMBER 31, 2017, 1:25 PM', u'0'],
        [u'TITANS*', u'JAGUARS', u'SUNDAY, DECEMBER 31, 2017, 1:25 PM', u'9'],
    ]

    return lines


def instantiate_rows_for_matchups(week, lines):
    """This function strips the asterisks (if any) from the team names
    so that they're pure before committing to the table. It adds that
    respective team to the home_team column.
    """
    matchups = []
    for line in lines:
        favored_team = line[0]
        underdog_team = line[1]
        if '*' in favored_team:
            favored_team = favored_team.replace('*', '')
            home_team = favored_team
        elif '*' in underdog_team:
            underdog_team = underdog_team.replace('*', '')
            home_team = underdog_team
        else:
            home_team = None
        matchup = Matchup(week=week,
                          favored_team=favored_team,
                          underdog_team=underdog_team,
                          datetime=line[2],
                          line=float(line[3]),
                          home_team=home_team)
        matchups.append(matchup)

    return matchups


def commit_lines(week, lines):
    """This is always done before commit_scores(). This function
    creates the rows for the matchups and adds the lines, then
    commit_scores() updates them later as the games are played.
    """
    with session_scope() as session:
        matchups = instantiate_rows_for_matchups(week=week, lines=lines)
        session.add_all(matchups)
