"""Utilites for use across the package. This should not import any
other supercontest modules.
"""
import datetime
import calendar
import requests
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from decorator import decorator
from flask_mail import Message
from dateutil import parser as dateutil_parser

from supercontest import mail


def get_soup_from_url(url):
    """Helper function to save boilerplate in URL fetching/parsing.
    Takes in a URL and returns a Soup object.
    """
    resp = requests.get(url)
    html = resp.text
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup


@decorator
def with_webdriver(function, *args, **kwargs):  # pylint: disable=unused-argument
    """Decorator. Requires that the decorated function accept the driver
    as its only argument.
    """
    driver = get_webdriver()
    try:
        return function(driver)
    finally:
        driver.quit()


def get_webdriver():
    """Instantiate and configure a selenium webdriver for chrome (headless).
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(30)
    return driver


def send_mail(subject, body, recipient):
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    mail.send(msg)


def is_today(allowable_days):
    """Provide allowable_days as an iterable of capitalized text
    (eg ['Monday', 'Friday']) and this will return a boolean if
    today is valid.
    """
    today_int = datetime.datetime.today().weekday()
    today_name = calendar.day_name[today_int]
    return today_name in allowable_days


def get_team_abv(team):
    return get_team_abv_map().get(team, team)


def get_team_abv_map():
    return {
        'CARDINALS': 'ARI',
        'FALCONS': 'ATL',
        'RAVENS': 'BAL',
        'BILLS': 'BUF',
        'PANTHERS': 'CAR',
        'BEARS': 'CHI',
        'BENGALS': 'CIN',
        'BROWNS': 'CLE',
        'COWBOYS': 'DAL',
        'BRONCOS': 'DEN',
        'LIONS': 'DET',
        'PACKERS': 'GB',
        'TEXANS': 'HOU',
        'COLTS': 'IND',
        'JAGUARS': 'JAX',
        'CHIEFS': 'KC',
        'CHARGERS': 'LAC',
        'RAMS': 'LAR',
        'DOLPHINS': 'MIA',
        'VIKINGS': 'MIN',
        'PATRIOTS': 'NE',
        'SAINTS': 'NO',
        'GIANTS': 'NYG',
        'JETS': 'NYJ',
        'RAIDERS': 'OAK',
        'EAGLES': 'PHI',
        'STEELERS': 'PIT',
        'SEAHAWKS': 'SEA',
        '49ERS': 'SF',
        'BUCCANEERS': 'TB',
        'TITANS': 'TEN',
        'REDSKINS': 'WAS',
    }


def convert_date(date_str):
    """Properly formats the strings for datetime in the database
    into python datetime objects.

    Args:
        date_str (str): the string from westgate, in our db

    Returns:
        (datetime obj): the python standard datetime obj for that str
    """
    return dateutil_parser.parse(date_str)
