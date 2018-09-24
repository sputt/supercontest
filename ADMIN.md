Before anything:
```bash
virtualenv venv && . venv/bin/activate
pip install -e .
```

To create the database for the first time:
```python
from supercontest.app import create_db
create_db()
```

To fetch lines, we need a webdriver. You'll need chrome and
the chromedriver. I think this can be done with:
```bash
sudo apt install chromedriver
```

You must install nginx to serve the application:
```
sudo apt install nginx
```

Copy `data/supercontest.service` to  `/etc/systemd/system/`. Then you can run:
```bash
sudo systemctl start supercontest
```

Copy `data/supercontest` to `/etc/nginx/sites-available/`. Then initialize (once) with:
```bash
sudo ln -s /etc/nginx/sites-available/supercontest /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

If you ever need to restart the service (necessary after you modify the app, change
routes, git pull in a new db update, etc):
```bash
sudo systemctl restart supercontest
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

To manually commit lines, do the following. This is typically done
on Wednesday nights, after Westgate posts the lines. This must
be done before scores are committed, because it creates the matchup rows.
```bash
commit-lines <weeknum>
```

To manually commit scores, do the following. This should never need to
be done manually, but it's exposed as a development convenience.
```bash
commit-scores <weeknum>
```
