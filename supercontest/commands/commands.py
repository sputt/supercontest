# pylint: disable=no-self-use, method-hidden, arguments-differ
from flask_script import Command, Option

from supercontest import db
from supercontest.core.lines import commit_lines
from supercontest.core.scores import commit_scores
from supercontest.core.utilities import add_user


class InitDbCommand(Command):
    """Creates the database tables
    """
    def run(self):
        db.drop_all()
        db.create_all()
        db.session.commit()  # pylint: disable=no-member
        print('Database has been initialized')
        add_user(email='example@example.com', password='hello')
        print('An example user has been added to the database')


class CommitLinesCommand(Command):
    """Commits the lines for a particular week
    """
    option_list = (Option('--week', '-w',
                          dest='week', required=True, type=int,
                          help=('Defines the week you expect, which is '
                                'confirmed against the week that Westgate '
                                'returns lines for')),)
    def run(self, week):
        commit_lines(week=week)


class CommitScoresCommand(Command):
    """Commits the current scores
    """
    option_list = (Option('--week', '-w',
                          dest='week', required=True, type=int,
                          help=('Defines the week you expect, which is '
                                'confirmed against the week that the NFL '
                                'returns scores for')),)
    def run(self, week):
        commit_scores(week=week)
