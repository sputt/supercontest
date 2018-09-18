from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from supercontest.models import Matchup
from supercontest.app import db


def get_chrome_headless_driver():
    """Instantiates and returns a selenium webdriver for Chrome (headless).
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(30)

    return driver

def fetch_lines():
    """Hits the official Westgate site and returns its line table as an html string,
    then coerces it into the following format: [FAVORED_TEAM, UNDERDOG_TEAM, DATETIME, LINE]

    Example Westgate return:
        [[u'1 SEAHAWKS', u'2 CARDINALS*', u'+6', u'THURSDAY, NOVEMBER 9, 2017 5:25 PM'],
         [u'23 GIANTS', u'24 49ERS*', u'+2.5', u'SUNDAY, NOVEMBER 12, 2017 1:25 PM'],...]
    """
    # Fetch the lines as WebElements
    url = 'https://www.westgateresorts.com/hotels/nevada/las-vegas/westgate-las-vegas-resort-casino/supercontest-weekly-card/'
    driver = get_chrome_headless_driver()
    try:
        driver.get(url)
        iframe = driver.find_element_by_css_selector('iframe')
        driver.switch_to_frame(iframe)
        table = driver.find_element_by_css_selector('table')
        rows = table.find_elements_by_css_selector('tr')
        # Extract the text into Python objects
        date = ''
        lines = []
        for row in rows:
            cells  = row.find_elements_by_css_selector('td')
            data = [cell.text for cell in cells if cell.text != '']
            # if only the first cell is populated, it's just a date row,
            # which is concatenated for subsequent iterations until it changes
            if len(data) == 1:
                date = cells[0].text
            # if the row has 4 values, it's a line - extract the info
            elif len(data) == 4:
                line = [cell.text for cell in cells]
                date_time = date + ' ' + line.pop(1)  # remove the time and add to date
                line.append(date_time)
                if line[2] == 'PK':  # if it's a draw pick, set the line to zero for math
                    line[2] = u'+0'
                line.append(line.pop(2))  # move the line to the end
                # remove the team number and whitespace, we only care about name
                for cell_index in [0, 1]:
                    line[cell_index] = line[cell_index].split(None, 1)[-1].strip()
                # strip the + in the predicted line, it's always positive for the first col winner
                line[-1] = line[-1].replace('+', '')
                lines.append(line)
            # sometimes westgate will return empty rows in the table - ignore them
            else:
                continue
    finally:
        driver.quit()

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
    matchups = instantiate_rows_for_matchups(week=week, lines=lines)
    db.session.add_all(matchups)
    db.session.commit()
