import requests
import bs4


def get_soup_from_url(url):
    """Helper function to save boilerplate in URL fetching/parsing.
    Takes in a URL and returns a Soup object.
    """
    resp = requests.get(url)
    html = resp.text
    soup = bs4.BeautifulSoup(html, 'html.parser')

    return soup
