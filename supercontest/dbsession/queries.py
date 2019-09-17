"""Wrappers around all queries with the db session.
"""
# pylint: disable=bad-continuation,no-member,invalid-name
from supercontest import db
from supercontest.models import User, Season, Score
from supercontest.core.utilities import convert_date

from .joins import (
    join_week_season,
    join_line_week_season,
    join_to_matchups,
    join_to_picks,
)


def get_max_season():
    """Simple return of max season year.

    Returns:
        (int): max year or 0 if null
    """
    max_season = db.session.query(
            db.func.max(Season.season)
        ).scalar()
    return max_season or 0


def get_max_week(season):
    """Simple return of max week for a season.

    Args:
        season (int): season to restrict available weeks to

    Returns:
        (int): max week or 0 if null
    """
    WeekSeason = join_week_season()
    max_week = db.session.query(
            db.func.max(WeekSeason.c.week)
        ).filter(
            WeekSeason.c.season == season,
        ).scalar()
    return max_week or 0


def get_sorted_seasons():
    """Numerically sorted season years, ascending.

    Returns:
        (list of ints): all season years in ascending order
    """
    seasons = db.session.query(
            Season.season,
        ).order_by(
            Season.season,
        ).all()
    return [row.season for row in seasons]


def get_sorted_weeks(season):
    """Numerically sorted week numbers, ascending, for a given season.

    Args:
        season (int): season to restrict available weeks to

    Returns:
        (list of ints): all available weeks in ascending order for a season
    """
    WeekSeason = join_week_season()
    weeks = db.session.query(
            WeekSeason.c.week,
        ).filter(
            WeekSeason.c.season == season,
        ).order_by(
            WeekSeason.c.week,
        ).all()
    return [row.week for row in weeks]


def get_week_id(season, week):
    """Returns the id for a week, given its number and the season year.

    Args:
        season (int)
        week (int)

    Returns:
        (int)
    """
    WeekSeason = join_week_season()
    week_id = db.session.query(
            WeekSeason.c.week_id,
        ).filter(
            WeekSeason.c.season == season,
            WeekSeason.c.week == week,
        ).scalar()
    return week_id


def get_id_name_map():
    """Grabs the display name for every row in the user table,
    returning the first or last name if populated. If not, returns the email.

    Returns:
        (dict): keys are user IDs and values are names (or emails if no name)
    """
    users = db.session.query(
            User.id,
            User.first_name,
            User.last_name,
            User.email,
        ).all()
    return {row.id: (' '.join([row.first_name, row.last_name]) if
                     row.first_name or row.last_name else row.email)
            for row in users}


def get_lines(season, week):
    """Returns all cols from the LineWeekSeason table, without the score
    data of the matchups.

    Args:
        season (int)
        week (int)

    Returns:
        (list of rows): these objects contain the LineWeekSeason columns
    """
    LineWeekSeason = join_line_week_season()
    lines = db.session.query(
            LineWeekSeason,
        ).filter(
            LineWeekSeason.c.season == season,
            LineWeekSeason.c.week == week,
        ).all()
    return lines


def score_exists(line_id):
    """Checks if a row exists in the Score table for an id from the Line table.

    Args:
        line_id (int)

    Returns:
        (bool)
    """
    return db.session.query(Score).filter(Score.line_id == line_id).all() != []


def get_score(line_id):
    """Returns just the row from the Score table that matches a line.

    Args:
        line_id (int)

    Returns:
        (row): from Score table
    """
    return db.session.query(Score).filter(Score.line_id == line_id).one()


def get_matchups(season, week):
    """Filters the FullMatchup table on season and week.

    Args:
        season (int): season to restrict weeks to
        week (int): week to restrict matchups to

    Returns:
        (list of rows): these objects contain the FullMatchup columns
    """
    FullMatchups = join_to_matchups()
    matchups = db.session.query(
            FullMatchups,
        ).filter(
            FullMatchups.c.season == season,
            FullMatchups.c.week == week
        ).all()
    return matchups


def get_sorted_matchups(season, week):
    """Filters the FullMatchup table on season and week.
    Converts the datetime string into an actual datetime object so that
    sorting can be done deterministically.  The objects are sorted by
    datetime chronologically ascending, then favored_team alphabetically
    ascending.

    Args:
        season (int): season to restrict weeks to
        week (int): week to restrict matchups to

    Returns:
        (list of rows): these objects contain the FullMatchup columns, sorted
    """
    matchups = get_matchups(season=season, week=week)
    return sorted(matchups,
                  key=lambda matchup: (convert_date(matchup.datetime),
                                       matchup.favored_team))


def get_picks(season=None, week=None, user_id=None):
    """This one is moduler. If you pass a season, it will filter on that
    season. Same for week or user. Returns the full rows with all columns.

    Args:
        season (int): season to restrict weeks to
        week (int): week to restrict matchups to
        user_id (int): user_id to restrict picks to

    Returns:
        (list of rows): the rows in the FullPicks table for the requested data
    """
    FullPicks = join_to_picks()
    filters = []
    if season:
        filters.append(FullPicks.c.season == season)
    if week:
        filters.append(FullPicks.c.week == week)
    if user_id:
        filters.append(FullPicks.c.user_id == user_id)
    picks = db.session.query(
            FullPicks,
        ).filter(
            *filters
        ).all()
    return picks
