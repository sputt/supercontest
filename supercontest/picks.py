from models import User, Pick, Matchup
from backend import session_scope


def commit_pick(name, week, team):
    """Contains logic to:
        * Reject a pick if a user already picked that team that week.
        * FIFO if the user has already picked 5 teams that week.
    """
    with session_scope() as session:
        user = session.query(User).filter_by(name=name).first()
        picks = session.query(Pick).filter_by(user=user, week=week).all()
        matchups = session.query(Matchup).filter_by(week=week).all()
        for _matchup in matchups:
            if team in [_matchup.favored_team, _matchup.unfavored_team]:
                # TODO: this should change to whatever letter denotes an unstarted game
                if _matchup.status != 'NOTSTARTEDYET':
                    msg = ('The {} game has already started for Week {}, '
                           '{} cannot pick it'.format(team, week, name))
                    return msg
        teams_already_picked = [_pick.team for _pick in picks]
        if team in teams_already_picked:
            msg = '{} already picked the {} for Week {}'.format(name, team, week)
        else:
            if len(teams_already_picked) == 5:
                session.delete(picks.pop(0))
                msg = 'Dropping oldest pick ({}). '.format(teams_already_picked.pop(0))
            else:
                msg = ''
            team_picks = teams_already_picked + [team]
            msg += "{}'s week {} picks: {}".format(name, week, ', '.join(team_picks))
            session.add(Pick(user=user, week=week, team=team))
    return msg
