def fetch_lines():
    """Hits the official Westgate site and returns its line table as an html string,
    then coerces it into the following format: [# FAVORED_TEAM, # UNFAVORED_TEAM, LINE, DATETIME]

    Example:
        [[u'1 SEAHAWKS', u'2 CARDINALS*', u'+6', u'THURSDAY, NOVEMBER 9, 2017 5:25 PM'],
         [u'23 GIANTS', u'24 49ERS*', u'+2.5', u'SUNDAY, NOVEMBER 12, 2017 1:25 PM'],...]
    """
    url = ('https://www.westgatedestinations.com/nevada/las-vegas/westgate-las-vegas-'
           'hotel-casino/casino/supercontest-weekly-card')
    soup = _get_soup_from_url(url)
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


def fetch_scores():
    """Hits the NFL API for live score updates, the week number,
    the time status of the game, and all the team names.
    """
    url = 'http://www.nfl.com/liveupdate/scorestrip/ss.xml'
    soup = _get_soup_from_url(url)
    week = soup.gms['w']
    games = soup.gms.find_all('g')
    scores = {}
    statuses = {}
    teams = []
    for game in games:
        home_team = game['hnn'].upper()
        visiting_team = game['vnn'].upper()
        scores[home_team] = game['hs']
        scores[visiting_team] = game['vs']
        statuses[home_team] = game['q']
        statuses[visiting_team] = game['q']
        teams.extend([home_team, visiting_team])

    return week, scores, statuses, sorted(teams)


def compare_scores_to_lines():
    """Wrapper which analyzes score deltas and attributes them to
    the appropriate line. Returns a list of tuples, like fetch_lines, but
    adds a tuple each for each score delta.
    """
    lines = fetch_lines()
    week, scores, statuses, teams = fetch_scores()
    results = lines[:]
    for index, matchup in enumerate(lines):
        # remove the home team asterisk for analysis, if necessary
        favored_team = matchup[0].replace('*', '')
        unfavored_team = matchup[1].replace('*', '')
        delta = int(scores[favored_team]) - int(scores[unfavored_team])
        results[index].append(unicode(delta))
        results[index].append('game is over' if statuses[favored_team].startswith('F') else '')

    return week, results


def compare_results_to_picks():
    """Logic to determine how many points to write to the Picks table.
    Null = not over
    0    = Incorrect
    0.5  = Exact Line
    1    = Correct
    """
