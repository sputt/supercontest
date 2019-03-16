Before anything:
```bash
virtualenv venv && . venv/bin/activate
pip install -e .
```

If this is a relatively naked system, you may need the appropriate
Python headers to build uwsgi:
```bash
sudo apt install build-essential python-dev
```

To create the database for the first time:
```bash
python manage.py init_db
```

To fetch lines, we need a webdriver. You'll need chrome and
the chromedriver. This can probably be done with:
```bash
sudo apt install chromedriver
```

You must install nginx to serve the application:
```bash
sudo apt install nginx
```

Register the service with systemd (once):
```bash
sudo ln -s "$(pwd)/data/supercontest.service" /etc/systemd/system/supercontest.service
sudo systemctl start supercontest
```

Register the site with nginx (once):
```bash
sudo ln -s "$(pwd)/data/supercontest" /etc/nginx/sites-available/supercontest
sudo ln -s /etc/nginx/sites-available/supercontest /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

If you ever need to restart the service (necessary after you modify the app, change
routes, git pull in a new db update, etc):
```bash
sudo systemctl restart supercontest
```

Create a file called supercontest/config/private.py with following content.
```python
MAIL_PASSWORD = # name of the contest, without the location, all lowercase, then a funny number and a puncuation mark
SECRET_KEY = # run python -c "import random, string; print repr(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32)));"
```

To certify (do once):
```bash
sudo add-apt-repository ppa:certbot/certbot
sudo apt install python-certbot-nginx
sudo certbot --nginx -d southbaysupercontest.com -d www.southbaysupercontest.com
```

To renew certs:
```bash
certbot renew
```

To kill leftover chrome processes from line fetches:
```bash
killall chromedriver /opt/google/chrome/chrome
```

This app uses flask-script and flask-migrate, so it comes with the
usual commands:
```bash
python manage.py --help  # list all commands
python manage.py <command> --help  # usage help for command
python manage.py shell
python manage.py runserver
python mangage.py db upgrade
```

To manually commit lines, do the following. This is typically done
on Wednesday nights, after Westgate posts the lines. This should
be done before scores are committed, because it creates the matchup rows.
```bash
python manage.py commit_lines --week <num>
```

To manually commit scores, do the following. This should never need to
be done manually, but it's exposed as a development convenience.
```bash
python manage.py commit_scores --week <num>
```

To manually inspect the database, for example:
```bash
python manage.py shell  # this injects 'db' and 'models' into context
db.session.query(db.func.max(models.Matchup.week)).scalar()
```

To add users for testing, for example:
```bash
python manage.py shell
from supercontest.core.utilities import add_user
add_user(email='example@example.com', password='hello')
```

To initialize the migration scheme, run:
```bash
python manage.py db init
python manage.py db revision -m "initial revision"
python manage.py db upgrade
```

After you change any part of the models, run the following.
```bash
python manage.py db migrate -m "description of change"
```

Then manually check the migration script and commit that revision. To
update to this on another machine, simply run the following:
```bash
git pull
python manage.py db upgrade
```

If you have ever have an incomplete migration/upgrade prior or you want
to develop on the model:
```bash
python manage.py db stamp head
```

TO debug errors in the service:
```bash
sudo tail -f /var/log/nginx/error.log   # nginx error logs
sudo tail -f /var/log/nginx/access.log  # nginx access logs
sudo journalctl -u nginx                # nginx process logs
sudo journalctl -u supercontest         # uwsgi logs
```
