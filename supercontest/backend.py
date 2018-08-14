import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base


DB_NAME = 'supercontest.db'
DB_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(DB_DIR, DB_NAME)

# Start fresh, everytime (just for now)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

engine = create_engine('sqlite:///' + DB_PATH, echo=True)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
