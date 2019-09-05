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
        add_user(email='example@example.com', password='hello')  # nosec
        print('An example user has been added to the database')


class CommitLinesCommand(Command):
    """Commits the lines for a particular week
    """
    option_list = (
        Option('--season', '-s', dest='season', required=True, type=int,
               help=('The season to commit lines for')),
        Option('--week', '-w', dest='week', required=True, type=int,
               help=('Defines the week to commit lines for')),
    )
    def run(self, season, week):
        commit_lines(season=season, week=week)


class CommitScoresCommand(Command):
    """Commits the current scores
    """
    option_list = (
        Option('--season', '-s', dest='season', required=True, type=int,
               help=('The season to commit scores for')),
        Option('--week', '-w', dest='week', required=True, type=int,
               help=('Defines the week you expect, which is confirmed '
                     'against the week that the NFL returns scores for')),
    )
    def run(self, season, week):
        commit_scores(season=season, week=week)
