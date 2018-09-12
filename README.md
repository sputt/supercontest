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

To run the application:
```bash
python run.py development
python run.py production
```
