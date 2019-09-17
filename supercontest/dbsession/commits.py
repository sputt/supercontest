"""Wrappers around all commits with the db session. This is primarily
the logistics for committing, but also allows SLIGHT reformatting
of the data before commit (stripping asterisks from home teams, etc).

Any functional logic surrounding the data should exist in the module
for that type of data, not here. This is for simple commits to the db.
"""
# pylint: disable=no-member
from supercontest import db
from supercontest.models import Line, Pick, Score

from . import queries


def delete_rows(rows):
    """Wrapper around deleting rows. You may delete one or multiple.

    Args:
        rows (row or list of rows): objects to delete
    """
    if not isinstance(rows, list):
        rows = [rows]
    for row in rows:
        db.session.delete(row)
    db.session.commit()


def _commit_lines(week_id, lines):
    """Strips the asterisks (if any) from the team names
    so that they're pure before committing to the table. also adds that
    respective team to the home_team column.

    Args:
        week_id (int)
        lines (list): from the supercontest.core.lines.fetch_lines() return,
            of the format [FAV, UNDERDOG, DATETIME, LINE]
    """
    rows = []
    for line in lines:
        favored_team = line[0]
        underdog_team = line[1]
        if '*' in favored_team:
            favored_team = favored_team.replace('*', '')
            home_team = favored_team
        elif '*' in underdog_team:
            underdog_team = underdog_team.replace('*', '')
            home_team = underdog_team
        else:
            home_team = None
        row = Line(week_id=week_id,
                   favored_team=favored_team,
                   underdog_team=underdog_team,
                   datetime=line[2],
                   line=float(line[3]),
                   home_team=home_team)
        rows.append(row)
    db.session.add_all(rows)
    db.session.commit()


def _commit_scores(season, week, scores):
    """Commits the scores to the database.

    Args:
        season (int)
        week (int)
        scores (list of dicts): As returned from fetch_scores()
    """
    lines = queries.get_lines(season=season, week=week)
    score_rows_to_add = []
    for game in scores:
        # could use home or visiting team, this is an arbitrary binary
        visiting_team = game['visiting_team']
        for line in lines:
            if visiting_team == line.favored_team:
                favored_team_score = game['visiting_team_score']
                underdog_team_score = game['home_team_score']
                status = game['status']
                line_id = line.line_id
                break
            elif visiting_team == line.underdog_team:
                underdog_team_score = game['visiting_team_score']
                favored_team_score = game['home_team_score']
                status = game['status']
                line_id = line.line_id
                break
        if queries.score_exists(line_id=line_id):  # update
            score_row = queries.get_score(line_id=line_id)
            score_row.favored_team_score = favored_team_score
            score_row.underdog_team_score = underdog_team_score
            score_row.status = status
        else:  # insert
            score_rows_to_add.append(
                Score(line_id=line_id,
                      favored_team_score=favored_team_score,
                      underdog_team_score=underdog_team_score,
                      status=status)
            )
    # Create the rows for new scores.
    db.session.add_all(score_rows_to_add)
    # And the ones that already existed, but were updated, were done so above.
    db.session.commit()


def _commit_picks(season, week, user_id, teams):
    """The workhorse underneath commit_picks(). This function talks to the db.
    It will blindly add the picks. If you are going to do any cleaning, checking
    deleting of prior picks, they must be done before this function.

    Args:
        season (int)
        week (int)
        user_id (int)
        teams (list of strs): the team names
    """
    # In order to recommit the new picks, you need to know information about
    # the lines that correspond to the newly picked teams.
    all_matchups = queries.get_matchups(season=season, week=week)
    team_line_id_map = {}
    for matchup in all_matchups:
        team_line_id_map[matchup.favored_team] = matchup.line_id
        team_line_id_map[matchup.underdog_team] = matchup.line_id
    picks = [Pick(user_id=user_id, line_id=team_line_id_map[team], team=team)
             for team in teams]
    db.session.add_all(picks)
    db.session.commit()
