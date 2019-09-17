"""First get all the joined tables for convenience. These are all the
FK chains from top to bottom:
    Score -> Line -> Week -> Season
    Pick -> Line -> Week -> Season
    Pick -> User
    User -> Season

From this, we can construct two primary tables. One for all matchups,
and one for all Picks (which is a superset of the latter).

All ids are forwarded through all joined tables, in case you want
to do inserts/updates on a subtable at any time.

These are functions so that you can call them at request time rather
than module load time.

This structure makes most of my queries in limbo somewhere between
lazy loading and eager loading.

I find this syntax a little more clear than the sqlalchemy .join()
syntax, even with the 'c' everywhere. Plus it coalesces the response
into one table, rather than multiple, even for unrelated tables (just FK)

Only the subquery tables require their cols to be accessed via the c
attribute. If you query on these subquery tables, the returns will
be rows that can have their cols accessed directly.
"""
# pylint: disable=no-member,bad-continuation,invalid-name
from supercontest import db
from supercontest.models import User, Pick, Score, Line, Week, Season


def join_week_season():
    """The basic inner join of Week and Season tables.
    """
    WeekSeason = db.session.query(
            Week.id.label('week_id'),
            Week.week,
            Season.season,
            Season.id.label('season_id'),
        ).filter(
            Week.season_id == Season.id,
        ).subquery()
    return WeekSeason


def join_line_week_season():
    """The join of the Line, Week, and Season tables.
    """
    WeekSeason = join_week_season()
    LineWeekSeason = db.session.query(
            Line.id.label('line_id'),
            Line.favored_team,
            Line.underdog_team,
            Line.datetime,
            Line.line,
            Line.home_team,
            WeekSeason.c.week_id,
            WeekSeason.c.week,
            WeekSeason.c.season,
            WeekSeason.c.season_id,
        ).filter(
            Line.week_id == WeekSeason.c.week_id,
        ).subquery()
    return LineWeekSeason


def join_to_matchups():
    """This one is basically the old Matchups table.

    It is a join on Score, Line, Week, and Season.
    """
    LineWeekSeason = join_line_week_season()
    FullMatchups = db.session.query(
            Score.id.label('score_id'),
            Score.favored_team_score,
            Score.underdog_team_score,
            Score.status,
            LineWeekSeason.c.line_id,
            LineWeekSeason.c.favored_team,
            LineWeekSeason.c.underdog_team,
            LineWeekSeason.c.datetime,
            LineWeekSeason.c.line,
            LineWeekSeason.c.home_team,
            LineWeekSeason.c.week_id,
            LineWeekSeason.c.week,
            LineWeekSeason.c.season,
            LineWeekSeason.c.season_id,
        ).filter(
            Score.line_id == LineWeekSeason.c.line_id,
        ).subquery()
    return FullMatchups


def join_to_picks():
    """And this is basically a join on the old Picks table with the old Matchups
    table. It contains everything you'd need. Only other useful identification columns
    are taken from the User table, not everything (like password, is_active...).

    It is a join on Pick, User, Score, Line, Week, and Season.
    """
    FullMatchups = join_to_matchups()
    FullPicks = db.session.query(
            Pick.id.label('pick_id'),
            Pick.team,
            User.id.label('user_id'),
            User.email,
            User.first_name,
            User.last_name,
            FullMatchups.c.score_id,
            FullMatchups.c.favored_team_score,
            FullMatchups.c.underdog_team_score,
            FullMatchups.c.status,
            FullMatchups.c.line_id,
            FullMatchups.c.favored_team,
            FullMatchups.c.underdog_team,
            FullMatchups.c.datetime,
            FullMatchups.c.line,
            FullMatchups.c.home_team,
            FullMatchups.c.week_id,
            FullMatchups.c.week,
            FullMatchups.c.season,
            FullMatchups.c.season_id,
        ).filter(
            Pick.line_id == FullMatchups.c.line_id,
            Pick.user_id == User.id,
        ).subquery()
    return FullPicks
