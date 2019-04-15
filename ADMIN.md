# Startup

Install the necessary docker capability:
```bash
sudo apt install docker.io
# follow instructions online to install docker-compose, don't use apt
```

Make sure postgres/nginx/flask aren't running on the host,
occupying the default ports that the containers will use.

Create a file called supercontest/config/private.py with the following content:
```python
MAIL_PASSWORD = <>  # find in my saved passwords, same as POSTGRES_PASSWORD but with single quotes
SECRET_KEY = # run python -c "import random, string; print repr(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32)));"
```

Create a file called docker/database/private.conf with the following content:
```yml
POSTGRES_PASSWORD=<>  # find in my saved passwords, same as MAIL_PASSWORD but without quotes
```

Initialize SSL certification so that Nginx starts with a dummy cert before getting
the real ones (this ups and downs your webserver container):
```bash
sudo ./init-letsencrypt.sh
```

Restore an existing database (from /backups/postgres/supercontest.dump):
```bash
make restore-local-db-from-local
```

To bring up the services, run the following. Dev just starts flask and postgres
containers. Prod starts nginx and certbot containers as well. Run the usual
`docker-compose down` whenever you want to end them.
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

# Debugging

To debug errors in the service:
```bash
docker logs -f <flask/nginx/postgres>
```

If directly on the machines:
```bash
sudo tail -f /var/log/nginx/error.log   # nginx error logs
sudo tail -f /var/log/nginx/access.log  # nginx access logs
sudo journalctl -r -u nginx             # nginx process logs
sudo journalctl -r -u supercontest      # uwsgi logs
```
