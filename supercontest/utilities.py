import requests
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_soup_from_url(url):
    """Helper function to save boilerplate in URL fetching/parsing.
    Takes in a URL and returns a Soup object.
    """
    resp = requests.get(url)
    html = resp.text
    soup = bs4.BeautifulSoup(html, 'html.parser')

    return soup


def with_webdriver(function):
    """Decorator. Requires that the decorated function accept "driver"
    as its first argument. This is a selenium webdriver for Chrome (headless).
    """
    def wrapper(*args, **kwargs):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.implicitly_wait(30)
        try:
            return function(driver, *args, **kwargs)
        finally:
            driver.quit()
    
    return wrapper
