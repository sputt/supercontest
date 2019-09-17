from flask_migrate import MigrateCommand
from flask_script import Manager

from supercontest import get_app, db
from supercontest.models import User, Line, Score, Pick, Week, Season
from supercontest.commands import CommitLinesCommand, CommitScoresCommand

manager = Manager(get_app)

manager.add_command('db', MigrateCommand)

manager.add_command('commit_lines', CommitLinesCommand)
manager.add_command('commit_scores', CommitScoresCommand)


@manager.shell
def make_shell_context():
    return dict(db=db,
                User=User,
                Line=Line,
                Score=Score,
                Pick=Pick,
                Week=Week,
                Season=Season)


if __name__ == '__main__':
    manager.run()
