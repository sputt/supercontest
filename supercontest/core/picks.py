import datetime

from supercontest.models import Pick, Matchup
from supercontest.core.utilities import send_mail
from supercontest import db

MAX_PICKS = 5
PICK_DAYS = [3, 4, 5, 6]  # 1 is Monday, 7 is Sunday. Picks are allowed Wed-Sat.
PICKABLE_STATUS = 'P'  # not yet started


class InvalidPicks(ValueError):
    pass


def commit_picks(user, week, teams, email=False):
    """Wrapper to write picks to the database.

    Args:
        user (obj): flask.current_user object
        teams (list): picks from the client, list of unicode string team names
    """
    # Initial condition checking.
    if len(teams) > MAX_PICKS:
        raise InvalidPicks('You cannot select more than 5 teams per week')
    if datetime.datetime.today().isoweekday() not in PICK_DAYS:
        raise InvalidPicks('Picks can only be placed Wednesday-Saturday')

    # The frontend adds an asterisk for home teams, simply remove here.
    teams = [team.replace('*', '') for team in teams]

    # Query to find out which games haven't started yet this week.
    pickable_matchups = db.session.query(
            Matchup.favored_team,
            Matchup.underdog_team
        ).filter_by(
            week=week,
            status=PICKABLE_STATUS
        ).all()
    # This are still structured in matchups, so flatten.
    pickable_teams = [team
                      for pickable_matchup in pickable_matchups
                      for team in pickable_matchup]
    for team in teams:
        if team not in pickable_teams:
            raise InvalidPicks('The {} game has already started'.format(team))

    # If you've made it this far, the picks are good. Wipe any previous
    # picks and commit the new ones.
    old_picks = db.session.query(Pick).filter_by(week=week, user_id=user.id).all()
    for old_pick in old_picks:
        db.session.delete(old_pick)
    picks = [Pick(week=week, team=team, user_id=user.id)
             for team in teams]
    db.session.add_all(picks)  # pylint: disable=no-member
    db.session.commit()  # pylint: disable=no-member

    if email is True:
        send_mail(subject='supercontest week {} picks'.format(week),
                  body='\n'.join(teams),
                  recipient=user.email)
