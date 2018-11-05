"""Utilites for use across the package. This should not import any
other supercontest modules.
"""
import requests
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from decorator import decorator
from flask_mail import Message
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
