from supercontest.models import Pick, Matchup
from supercontest.core.utilities import send_mail, is_today
from supercontest import db

MAX_PICKS = 5
PICK_DAYS = ['Wednesday', 'Thursday', 'Friday', 'Saturday']
PICKABLE_STATUS = 'P'  # not yet started


class InvalidPicks(ValueError):
    pass


def commit_picks(user, season, week, teams, email=False, verify=True):  # pylint: disable=too-many-arguments
    """Wrapper to write picks to the database.

    Args:
        user (obj): flask.current_user object
        season (int): the season to pick for
        week (int): the week to pick for
        teams (list): picks from the client, list of unicode string team names
        email (bool): send mail or don't send mail
        verify (bool): check conditions like max5 or weekday, or skip checks
    """
    # The frontend adds an asterisk for home teams, simply remove here.
    teams = [team.replace('*', '') for team in teams]

    # Initial condition checking.
    if verify is True:
        if len(teams) > MAX_PICKS:
            raise InvalidPicks('You cannot select more than 5 teams per week')
        if not is_today(PICK_DAYS):
            raise InvalidPicks('Picks can only be placed Wednesday-Saturday')

        # Query to find out which games haven't started yet this week.
        pickable_matchups = db.session.query(  # pylint: disable=no-member
            Matchup.favored_team,
            Matchup.underdog_team
        ).filter_by(
            season=season,
            week=week,
            status=PICKABLE_STATUS
        ).all()
        # These are still structured in matchups, so flatten.
        pickable_teams = [team
                          for pickable_matchup in pickable_matchups
                          for team in pickable_matchup]
        for team in teams:
            if team not in pickable_teams:
                raise InvalidPicks('The {} game has already started'.format(team))

    # If you've made it this far, the picks are good. Wipe any previous
    # picks and commit the new ones.
    old_picks = db.session.query(Pick).filter_by(  # pylint: disable=no-member
        season=season, week=week, user_id=user.id).all()
    for old_pick in old_picks:
        db.session.delete(old_pick)  # pylint: disable=no-member
    picks = [Pick(season=season, week=week, team=team, user_id=user.id)
             for team in teams]
    db.session.add_all(picks)  # pylint: disable=no-member
    db.session.commit()  # pylint: disable=no-member

    if email is True:
        send_mail(subject='supercontest week {} picks'.format(week),
                  body='\n'.join(teams),
                  recipient=user.email)
