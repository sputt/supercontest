Before anything:
```bash
virtualenv venv && . venv/bin/activate
pip install -e .
```

To create the database for the first time:
```python
from supercontest import create_db
create_db()
```

You must install nginx:
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
