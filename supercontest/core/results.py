from supercontest.dbsession import queries

# The scores update Th, Sun, Mon, and then add Wednesday
# because we want to fetch scores on Wednesdays after the lines
# are update (they'll all be zero, but will fill the tables).
RESULTS_DAYS = ['Wednesday', 'Thursday', 'Sunday', 'Monday']


def get_week_teams(season, week, user_id=None):
    """Helper function for the picks view. Returns the picked teams and
    for all users for this week. For active pick days, where only the
    current user is shown, his/her ID may be passed here.

    Args:
        season (int)
        week (int)
        user_id (int): If passed, this will only return data for that user

    Returns:
        (dict): {user_id: [team1, team2,...], user_id...}
    """
    # get_picks() respects if user_id is None.
    picks = queries.get_picks(season=season, week=week, user_id=user_id)
    week_totals = {}
    for pick in picks:
        if not week_totals.get(pick.user_id):
            week_totals[pick.user_id] = []
        week_totals[pick.user_id].append(pick.team)
    return week_totals


def get_all_week_totals(season):
    """Helper function for the leaderboard. Returns the point scores
    for all users for all weeks.

    Args:
        season (int): the season to return all weekly totals for

    Returns:
        (dict): {user_id: {week: points, week: points...}...}
    """
    picks = queries.get_picks(season=season)
    all_week_totals = {}
    for pick in picks:
        if not all_week_totals.get(pick.user_id):
            all_week_totals[pick.user_id] = {}
        if not all_week_totals[pick.user_id].get(pick.week):
            all_week_totals[pick.user_id][pick.week] = 0
        all_week_totals[pick.user_id][pick.week] += determine_current_pick_points(pick)
    return all_week_totals


def get_sorted_week_teams(week_teams, points_map):
    """Helper function for the picks view. Returns the week's picks
    for all users, sorted by the resultant total point scores. It does
    not calculate these; you must provide a lookup.

    Args:
        week_teams (dict): the return dict from get_week_teams()
        points_map (dict): {team: points, team: points...}

    Returns:
        (list): [(user_id, [teams]), (user_id, [teams])...] (sorted)
    """
    week_totals = {user_id: sum([points_map[team] for team in teams])
                   for user_id, teams in week_teams.items()}
    sorted_picks = [
        (user_id, week_teams[user_id])
        for user_id in sorted(week_totals, key=week_totals.get, reverse=True)
    ]
    return sorted_picks


def get_season_totals(all_week_totals):
    """Helper function for the leaderboard. Returns the total season scores
    for all users, sorted.

    Args:
        all_week_totals (dict): the return dict from get_all_week_totals()

    Returns:
        (list): [(user_id, points), (user_id, points)...] (sorted)
    """
    season_totals = {user_id: sum(week_points_dict.values())
                     for user_id, week_points_dict in all_week_totals.items()}
    sorted_season_totals = [
        (user_id, season_totals[user_id])
        for user_id in sorted(season_totals, key=season_totals.get, reverse=True)
    ]
    return sorted_season_totals


def determine_current_coverer(row):
    """Takes a matchup and determines which team is currently covering.
    If the matchup is currently a push, a string with both team names
    concatenated is returned. Any row can be passed that has scores,
    team names, and a line.

    Args:
        row (sqla): a row from the FullMatchups or FullPicks table

    Returns:
        (str) the name matching the team that's covering
    """
    delta = row.favored_team_score - row.underdog_team_score
    if delta > row.line:
        coverer = row.favored_team
    elif delta == row.line:
        # if the line is a push, include both team names in string
        coverer = row.favored_team + row.underdog_team
    else:
        coverer = row.underdog_team
    return coverer


def determine_current_pick_points(row, team=None):
    """Takes a pick and determines how many points it is currently earning.
    Any row can be passed that has scores, team names, a line, and a picked
    team. Usually, you'd just call this function with (row=pick_row), but you
    may also call it with (row=matchup_row, team=team) and it will compare
    the provided team against the line/scores from the matchup row, as a
    simulated pick.

    Args:
        row (sqla): a row from the FullPicks table or FullMatchups table
        team (str): pass a team to simulate a pick, if row is just lines
            and scores from the matchups table

    Returns:
        (float) the points that this row is currently earning
    """
    coverer = determine_current_coverer(row)
    picked_team = team or row.team
    if picked_team == coverer:
        points = 1.0
    # Remember for a push, coverer is a string with both team names.
    elif picked_team in coverer:
        points = 0.5
    else:
        points = 0.0
    return points
