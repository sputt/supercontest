from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import bs4
import requests


def get_soup_from_url(url):
    """Helper function to save boilerplate in URL fetching/parsing.
    Takes in a URL and returns a Soup object.
    """
    resp = requests.get(url)
    html = resp.text
    soup = bs4.BeautifulSoup(html, 'html.parser')

    return soup


class PickForm(Form):
    name = TextField('Name:', validators=[validators.required()])
    pick = TextField('Pick:', validators=[validators.required()])

    def reset(self):
        blankData = MultiDict([('csrf', self.reset_csrf())])
        self.process(blankData)
