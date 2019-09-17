"""Logic for fetching the lines.
"""
from supercontest.core.utilities import with_webdriver
from supercontest.dbsession import commits, queries


# pylint: disable=too-many-locals
@with_webdriver
def fetch_lines(driver=None):  # driver is passed by decorator
    """Hits the official Westgate site and returns its line table as an html string,
    then coerces it into the proper format..

    Example Westgate return:
        [[u'1 SEAHAWKS', u'2 CARDINALS*', u'+6', u'THURSDAY, NOVEMBER 9, 2017 5:25 PM'],
         [u'23 GIANTS', u'24 49ERS*', u'+2.5', u'SUNDAY, NOVEMBER 12, 2017 1:25 PM'],...]

    Returns:
        lines (list): [FAVORED_TEAM, UNDERDOG_TEAM, DATETIME, LINE]
    """
    # Fetch the lines as WebElements
    url = 'https://www.westgateresorts.com/hotels/nevada/las-vegas/westgate-las-vegas-resort-casino/supercontest-weekly-card/'  # pylint: disable=line-too-long
    driver.get(url)
    iframe = driver.find_element_by_css_selector('iframe')
    driver.switch_to_frame(iframe)
    table = driver.find_element_by_css_selector('table')
    rows = table.find_elements_by_css_selector('tr')
    # Extract the text into Python objects
    date = ''
    lines = []
    for row in rows:
        cells = row.find_elements_by_css_selector('td')
        data = [cell.text for cell in cells if cell.text != '']
        # if only the first cell is populated, it's just a date row,
        # which is concatenated for subsequent iterations until it changes
        if len(data) == 1:
            date = cells[0].text  # reuse for next rows until overwritten with new date
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
    return lines


def commit_lines(season, week):
    """Python wrapper for all line committing. Requires
    that the week be passed through Python.

    Args:
        season (int)
        week (int)
    """
    lines = fetch_lines()
    week_id = queries.get_week_id(season=season, week=week)
    commits._commit_lines(week_id=week_id, lines=lines)  # pylint: disable=protected-access
