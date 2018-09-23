from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from IPython import embed
from supercontest.models import Matchup


engine = create_engine('sqlite:///supercontest.db', echo=True)
session = sessionmaker(bind=engine)()
embed()

# then you can do stuff like:
# matchups = session.query(Matchup).filter_by(week=X).all()
# matchups[0].favored_team_score
