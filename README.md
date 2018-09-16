Before performing any administrative commands:
```bash
virtualenv venv && . venv/bin/activate
pip install -r requirements.txt
```

To create the database for the first time:
```bash
python create.py development
python create.py production
```

Before running the application:
```
mkdir instance
vim instance/config.py
# add the following:
# SECRET_KEY = 'mysecret'
# WTF_CSRF_SECRET_KEY = 'mycsrfsecret'
```

To run the application:
```bash
python run.py development
python run.py production
```

Scores are usually updated within ~30 seconds.
