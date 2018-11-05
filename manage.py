from flask_migrate import MigrateCommand
from flask_script import Manager
from supercontest import get_app, db, models
from supercontest.commands import (
    InitDbCommand,
    CommitLinesCommand,
    CommitScoresCommand,
)

manager = Manager(get_app)

manager.add_command('db', MigrateCommand)
manager.add_command('init_db', InitDbCommand)
manager.add_command('commit_lines', CommitLinesCommand)
manager.add_command('commit_scores', CommitScoresCommand)


@manager.shell
def make_shell_context():
    return dict(db=db, models=models)


if __name__ == '__main__':
    manager.run()
