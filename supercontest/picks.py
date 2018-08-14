from models import Pick, User
from backend import session_scope


def add_pick(name, week, team):
    """Contains logic to:
        * Reject a pick if a user already picked that team that week.
        * FIFO if the user has already picked 5 teams that week.
    """
    with session_scope() as session:
        user = session.query(User).filter_by(name=name).first()
        picks = session.query(Pick).filter_by(user=user, week=week).all()
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
