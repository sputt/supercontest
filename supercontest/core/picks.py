from supercontest.dbsession import queries, commits
from supercontest.core.utilities import send_mail, is_today

MAX_PICKS = 5
PICK_DAYS = ['Wednesday', 'Thursday', 'Friday', 'Saturday']
PICKABLE_STATUS = 'P'  # not yet started (pregame)


class InvalidPicks(ValueError):
    pass


def commit_picks(user_id, season, week, teams, email='', verify=True):  # pylint: disable=too-many-arguments
    """Wrapper to write picks to the database.

    Args:
        user_id (obj): user id
        season (int): the season to pick for
        week (int): the week to pick for
        teams (list): picks from the client, list of unicode string team names
        email (str): email address to send to - if empty string, won't send
        verify (bool): check conditions like max5 or weekday, or skip checks
    """
    # Check their existing picks (if any) before comparing to this new attempt.
    old_picks = queries.get_picks(season=season, week=week, user_id=user_id)
    old_teams = [pick.team for pick in old_picks]

    # The frontend adds an asterisk for home teams, simply remove here.
    new_teams = [team.replace('*', '') for team in teams]

    # Initial condition checking.
    if verify is True:
        if len(new_teams) > MAX_PICKS:
            raise InvalidPicks('You cannot select more than 5 teams per week')
        if not is_today(PICK_DAYS):
            raise InvalidPicks('Picks can only be placed Wednesday-Saturday')

        matchups = queries.get_matchups(season=season, week=week)
        pickable_teams = [matchup.team for matchup in matchups
                          if matchup.status == PICKABLE_STATUS]
        # This is the serverside check for "this game hasn't started yet" -
        # it doesn't raise/return an exception/error, it simply strips the
        # unpickable teams from what you're trying to commit to the pick table.
        valid_teams = [team for team in new_teams if team in pickable_teams]
        invalid_teams = list(set(new_teams) - set(valid_teams))
        # If this clause is entered, some of the picks are unpickable. This is
        # ok if they picked the thursday game, and are modifying the other
        # four. In all other cases, this would be a malicious attempt.
        if invalid_teams:
            # First, take all the teams that the user is trying to pick but
            # the game has already started. Then check to see if they
            # already picked that team. If ANY of attempted picks were not
            # picked already, and the game has started, something is wrong.
            # We should theoretically never get here, because the frontend
            # checks for this.
            if not all([team in old_teams for team in invalid_teams]):
                raise InvalidPicks(
                    'A pick is being attempted on a game that has '
                    'already started, and for a pick that the user '
                    'did NOT already place. This is likely a '
                    'malicious attempt, since the frontend should '
                    'screen for this.'
                )
            # If the user has already picked this team, and the game has
            # already started, then they're just resubmitting (likely with
            # other non-thursday picks). Pass it on to be deleted and
            # recommitted as the same, just like the new picks.

    # If you've made it this far, the picks are good. Wipe any previous
    # picks and commit the new ones.
    commits.delete_rows(old_picks)
    commits._commit_picks(season=season, week=week, user_id=user_id, teams=new_teams)  # pylint: disable=protected-access

    if email:
        send_mail(subject='supercontest week {} picks'.format(week),
                  body='\n'.join(new_teams),
                  recipient=email)
