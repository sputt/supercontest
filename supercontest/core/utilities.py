"""Utilites for use across the package. This should not import any
other supercontest modules.
"""
from __future__ import print_function

import requests
import datetime
import bs4
import xlrd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from decorator import decorator
from flask import current_app
from flask_mail import Message

from supercontest import mail, db
from supercontest.models import User, Pick


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
    as its only argument. This is a selenium webdriver for Chrome (headless).
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(30)
    try:
        return function(driver)
    finally:
        driver.quit()


def send_mail(subject, body, recipient):
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    mail.send(msg)


def add_user(email, password, **kwargs):
    user = User(email=email,
                password=current_app.user_manager.password_manager.hash_password(password),
                active=True,
                email_confirmed_at=datetime.datetime.utcnow(),
                **kwargs)
    db.session.add(user)
    db.session.commit()


def get_team_abv(team):
    map = {
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
        'PATRIOTS': 'NEP',
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
        'REDSKINS': 'WAS'
    }
    return map.get(team, team)


def commit_users_from_excel(path):
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_name('Main')
    for row_index in range(1, sheet.nrows):  # skip first row of headers
        name = sheet.cell_value(row_index, 0).replace(u'\u2019', "'")  # replace unicode with right single quote
        email = sheet.cell_value(row_index, 2)
        print('Registering "{}" with "{}"'.format(name, email))
        add_user(email=email, password='sbsc19', first_name=name)


def commit_picks_from_excel(path):
    wb = xlrd.open_workbook(path)
    for week in range(1, 18):  # this goes 1-17
        print('Week {}'.format(week))
        sheet = wb.sheet_by_name('week{}picks'.format(week))
        for row_index in range(1, sheet.nrows):  # skip first row of headers
            cut_last_cols = 1 if week in [8, 9, 10] else 2  # cut the last two cols, question and count mostly
            row_values = sheet.row_values(row_index, end_colx=sheet.ncols-cut_last_cols)
            user = row_values.pop(0).replace(u'\u2019', "'")  # first col is user, replace unicode with right single quote
            # ignore empty strings and take the first five. This is the only place which has a discrepancy with Petty's
            # spreadsheet. Taking the first or last five did not match scores. He was taking some random collection
            # of them and I don't have his script to check. Therefore, weeks where people had >5 picks MIGHT
            # be off by a point or two.
            picks = [pick for pick in row_values if pick][:5]
            user_id = db.session.query(User.id).filter_by(first_name=user).first()[0]
            # Petty's spreadsheet kept people with multiple submissions (harner week 17, grdich week 13,
            # freie week 7). The only one with a DIFFERENCE in picks was Grdich. Petty kept the first entry
            # (assuming bc submission timestamp was most recent), so I'll keep that one.
            if db.session.query(Pick).filter_by(week=week, user_id=user_id).all():
                print('Duplicate pick rows detected for {}, keeping the previous'.format(user))
            elif user_id is None:
                print('"{}" does not match any first names in the db, '
                      'moving to next user'.format(user))
            else:
                print('Committing picks for {}: {}'.format(user, picks))
                picks = [Pick(week=week, team=pick, user_id=user_id) for pick in picks]
                db.session.add_all(picks)
                db.session.commit()