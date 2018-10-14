"""Utilites for use across the package. This should not import any
other supercontest modules.
"""
import requests
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from decorator import decorator


def get_soup_from_url(url):
    """Helper function to save boilerplate in URL fetching/parsing.
    Takes in a URL and returns a Soup object.
    """
    resp = requests.get(url)
    html = resp.text
    soup = bs4.BeautifulSoup(html, 'html.parser')

    return soup


@decorator
def with_webdriver(function, *args, **kwargs):
    """Decorator. Requires that the decorated function accept "driver"
    as its first argument. This is a selenium webdriver for Chrome (headless).
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(30)
    try:
        return function(driver, *args, **kwargs)
    finally:
        driver.quit()
