# Startup

Install the necessary docker capability:
```bash
sudo apt install docker.io
# follow instructions online to install docker-compose, don't use apt
```

Make sure postgres/nginx/flask aren't running on the host,
occupying the default ports that the containers will use.

Create a file called `supercontest/config/private.py` with the following content:
```python
MAIL_PASSWORD = <>  # find in my saved passwords, same as POSTGRES_PASSWORD but with single quotes
SECRET_KEY = # run python -c "import random, string; print repr(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32)));"
```

Create a file called `docker/database/private.conf` with the following content:
```yml
POSTGRES_PASSWORD=<>  # find in my saved passwords, same as MAIL_PASSWORD but without quotes
```

Create a file called `supercontest/config/dashboard.cfg` with the following content:
```ini
[authentication]
USERNAME=bmahlstedt
PASSWORD=<your supercontest password>
SECURITY_TOKEN=<make this up>
```

Restore an existing database (from /backups/postgres/supercontest.dump):
```bash
make restore-local-db-from-local
```

If you're bringing up the production application, it expects an nginx webserver
to reverse-proxy traffic to its container. Follow the instruction in
https://github.com/brianmahlstedt/infra/blob/master/README.md to create the docker network
and nginx/letsencrypt containers to serve the traffic.

Now, bring up the services. Dev/prod simply have different configurations
(ports, autoreload, etc). `docker-compose down` whenever you want to end them.
```bash
make [build-]start-[dev|prod]
```

After that first manual bringup, it is recommened to use ansible from a more
convenient control node (eg your laptop) to deploy at will. See below.

# Helpful

flask-script (python manage.py <>) is used as a makefile of sorts for the
Python functionality of this application (fetching the lines in Python, etc).
There is a standard makefile for the bash API of this application (making
a backup of the db, starting a dev service container, etc).

Deployments are done with ansible, wrapped by our makefile:
```bash
make deploy
```

Deployments will rebuild and restart the production containers, but do not
automatically run database migrations. If your change involved the models,
ssh into the droplet and run `python manage.py db upgrade` from the app
container.

Reindex the ctags for vim:
```bash
make reindex-ctags
```

To explore the db (locally):
```bash
make explore-local-db
```

You may backup and restore the database locally with the following. They are
idempotent, and the backup is stored at ./backups/postgres/supercontest.dump.
```bash
make backup-local-db-to-local
make restore-local-db-from-local
```

This can also be done remotely, which basically just SSHs into the production server,
runs the equivalent local command, then SCPs the file back. These enter through the
makefile, farm out to ansible for SSH/SCP, then back to the makefile to run the local
command. "restore" will pull ./backups/postgres/supercontest.dump from local. "backup"
will leave a uniquely timestamped dump file in ./backups/postgres/supercontest.dump.
```bash
make backup-remote-db-to-local
make restore-remote-db-from-local
```

The following manage.py commands need to be run in the app container, because
they require access to various app pieces. For example, the database migrations
need python, flask-scripts, a psycopg2 connection to the db, etc. Simply shell
into the app container and then run them as you normally would on the host.
It will add the migration file to the volume in the container, which gets synced
back to vcs on your host.
```bash
make enter-[dev|prod]-app
```

To manually commit lines, do the following. This is typically done
on Wednesday nights, after Westgate posts the lines. This should
be done before scores are committed, because it creates the matchup rows.
```bash
python manage.py commit_lines --season <XXXX> --week <X>
```

To manually commit scores, do the following. This should never need to
be done manually, but it's exposed as a development convenience.
```bash
python manage.py commit_scores --season <XXXX> --week <X>
```

To manually inspect the database, for example:
```bash
python manage.py shell  # this injects 'db' and all the models into context
db.session.query(db.func.max(Season.season)).scalar()
```

After you change any part of the models, run the following.
```bash
python manage.py db migrate -m "description of change"
```

Then manually check the migration script and commit that revision 
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

The matchup dates and times are kept in the db in the same string format that
Westgate returns. To convert this to a python datetime object, or reformat it
back to whatever new string display you want:
```python
from dateutil import parser as dateutil_parser
datetime_obj = dateutil_parser.parse(datetime_str)
new_datetime_str = datetime_obj.strftime('%a %I:%m %p')  # eg, "Sun 10:05 AM"
```

An example query with an implicit inner join:
```sql
select seasons.season, weeks.week from seasons, weeks where seasons.id = weeks.season_id order by season, week;
```
```python
db.session.query(Season.season, Week.week).filter(Season.id == Week.season_id).order_by(Season.season, Week.week).all()
```

There is a monitoring dashboard available at the `/dashboard` endpoint. You
can check traffic, requests, total times, and much more.

# Debugging

To debug errors in the service:
```bash
docker logs -f <>
```

If directly on the machines:
```bash
sudo tail -f /var/log/nginx/error.log   # nginx error logs
sudo tail -f /var/log/nginx/access.log  # nginx access logs
sudo journalctl -r -u nginx             # nginx process logs
sudo journalctl -r -u supercontest      # uwsgi logs
```

# Weekly Tasks

You must do two things weekly, manually. Cron jobs could be written for
these, but (a) one is dependent on westgate, and I don't want to tie
automation to that and (b) they require the backup destination to be live,
which my laptop is not guaranteed to be.

#### Wednesday evening after 5 pm

Check Westgate to ensure the new lines for this week have been posted.
Ensure they have before continuing.

Backup the prod database as a precaution, before changing anything.
Run this on your laptop. It will automatically create a unique filename with timestamp.
```bash
make backup-remote-db-to-local
```

Sometimes the selenium webdriver needs a kick. Just restart the app to be
sure:
```bash
docker-compose restart supercontest-app-prod
```

Get into the production app container. Here is the usual way:
```bash
ssh sc
tmux attach
make enter-prod-app
```

Once in, actually fetch and commit the new lines. Be careful to put
the correct season and week:
```bash
python manage.py commit_lines --season <XXXX> --week <X>
```

Open the app in a browser to verify if it worked.

Then backup the database, to lock in everything since last week.
Run this on your laptop. It will automatically create a unique filename with timestamp.
```bash
make backup-remote-db-to-local
```

#### Sunday morning as early as possible

Run this whenever is most convenient after Saturday pick lockdown, before games
start. This simply captures the fresh picks from this week. It can be referenced 
later to check if anyone cheated for any week. It, again, should be run from
your laptop, and automatically creates a unique name from the timestamp.
```bash
make backup-remote-db-to-local
```
