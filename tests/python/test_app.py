import time
import requests
import bs4
from flask_testing import LiveServerTestCase
from flask import url_for

from supercontest import get_app, db
from supercontest.models import User, Matchup, Pick
from supercontest.core.utilities import add_user, get_webdriver, get_team_abv
from supercontest.core.lines import _commit_lines
from supercontest.core.scores import _commit_scores
from supercontest.core.picks import commit_picks

from spoof import spoof_lines, spoof_scores


class AppTests(LiveServerTestCase):
    """ *IMPORTANT* these tests require that a postgres server
    already be running on the host on port 4949 (modify the file
    /etc/postgresql/<ver>/main/postgresql.conf to check the port)
    and restart if you need to), with a supercontest_unittests
    database already created, as well as the standard user
    `supercontest` with the standard password (from the regular config
    for production).

    These tests also require that selenium/chromedriver be setup.
    Reference docker/app/Dockerfile.
    """
    def create_app(self):
        test_configs = dict(
            TESTING=True,  # propagate exceptions
            MAIL_SUPPRESS_SEND=True,  # don't send mail
            WTF_CSRF_ENABLED=False,  # disable csrf form validation
        )
        app = get_app(db_name='supercontest_unittests',
                      db_port='4949',
                      db_host='localhost',
                      extra_config_settings=test_configs)
        return app

    def setUp(self):
        # Some config attrs.
        self.week = 1
        self.creds = dict(email='test@nowhere.com', password='hello')
        # Create tables.
        db.session.remove()
        db.drop_all()
        db.create_all()
        # Add user.
        add_user(**self.creds)
        # Add lines.
        _commit_lines(week=self.week, lines=spoof_lines())
        # Add scores.
        _commit_scores(week=self.week, scores=spoof_scores())
        # Webdriver.
        if hasattr(self, 'webdriver'):
            self.webdriver.quit()
        else:
            self.webdriver = get_webdriver()

    def login(self):
        self.webdriver.get(self.get_server_url() + url_for('main.home'))
        email_input = self.webdriver.find_element_by_id('email')
        password_input = self.webdriver.find_element_by_id('password')
        email_input.send_keys(self.creds.get('email'))
        password_input.send_keys(self.creds.get('password'))
        self.webdriver.find_element_by_xpath('//input[@type="submit"]').click()
        time.sleep(1)

    def goto(self, route, **kwargs):
        self.webdriver.get(self.get_server_url() + url_for(route, **kwargs))

    def test_lines_setup(self):
        """Verifies setup lines exist in the db.
        """
        results = db.session.query(Matchup).all()
        self.assertEqual(len(results), 16)
        self.assertEqual(results[2].underdog_team, u'BEARS')

    def test_scores_setup(self):
        """Verifies setup scores exist in the db.
        """
        results = db.session.query(Matchup).all()
        self.assertEqual(len(results), 16)
        self.assertEqual(results[2].underdog_team_score, 10)

    def test_user_setup(self):
        """Verifies setup user exists in the db.
        """
        results = db.session.query(User).all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].email, self.creds.get('email'))

    def test_login_home(self):
        """Logs in via the frontend and then ensures data in the matchups table view.
        """
        # Make sure the main page requires login first.
        self.goto('main.home')
        self.assertIn('You must be signed in to access', self.webdriver.page_source)
        # Then attempt to login and reload home.
        self.login()
        self.goto('week.week_matchups', week=self.week)
        # Make sure a table of lines and scores is in the dom.
        self.assertEqual(len(self.webdriver.find_elements_by_class_name('favoredTeam')), 16)
        self.assertEqual(len(self.webdriver.find_elements_by_class_name('underdogTeamScore')), 16)

    def test_picks_scores(self):
        """Makes sure that committing picks works, the pick view updates, and
        the leaderboard can be calculated against picks/matchups.
        """
        color_map = {
            'palegreen': 'rgba(152, 251, 152, 1)',
            'lightcoral': 'rgba(240, 128, 128, 1)',
            'khaki': 'rgba(240, 230, 140, 1)',
        }
        # Define picks and frontend element IDs.
        picks = [u'STEELERS', u'RAIDERS', u'RAMS']
        pick_ids = [self.creds.get('email').replace('@', '').replace('.', '') + get_team_abv(team)
                    for team in picks]
        # Login and verify you have no picks first.
        self.login()
        self.goto('week.week_picks', week=self.week)
        for pick_id in pick_ids:
            element = self.webdriver.find_element_by_id(pick_id)
            background_color = element.value_of_css_property('background-color')
            self.assertNotIn(background_color, list(color_map.values()))
        # Make the picks.
        user_obj = db.session.query(User).first()
        commit_picks(user=user_obj, week=self.week, teams=picks, email=False, verify=False)
        # Verify the correct picks now that they've been placed.
        self.goto('week.week_picks', week=self.week)
        for pick_id in pick_ids:
            element = self.webdriver.find_element_by_id(pick_id)
            background_color = element.value_of_css_property('background-color')
            self.assertIn(background_color, list(color_map.values()))
        # Go to leaderboard to confirm that scoring works.
        self.goto('main.leaderboard')
        element = self.webdriver.find_element_by_class_name('weekScore')  # there's only 1
        self.assertEqual(element.text, '2.0')

    def test_graphql_query(self):
        """While this test exercises the API endpoint, it also shows how to
        authenticate with the app using a simple HTTP request (rather than Selenium or
        another more complicated solution). This demonstrates the creds required to
        get past login_required, but does not show CSRF because it's disabled for the
        test app. See the README for how to provide the CSRF token.
        """
        query = """
        {
          users {
            email
          }
        }
        """
        with requests.session() as session:
            session.post(self.get_server_url() + '/user/sign-in',
                         data=self.creds,
                         headers=dict(referer=self.get_server_url()))
            response = session.get(self.get_server_url() + '/graphql',
                                   json={'query': query})
        user_email = response.json()['data']['users'][0]['email']
        self.assertEqual(user_email, 'test@nowhere.com')
