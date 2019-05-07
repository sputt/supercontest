"""Just the run wrapper, the entry point for uwsgi in data/supercontest.ini
"""
from supercontest import get_app

app = get_app()  # pylint: disable=invalid-name

if __name__ == '__main__':
    app.run()
