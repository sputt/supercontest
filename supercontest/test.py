# these import backend, which creates a new db
import users, picks, lines, scores, matchups

# this should happen once
users.commit_users()

# you'll probably have to enter this if westgate doesn't expose it
week=17

# this will an endpoint (pick), many times per week
picks.commit_pick('Brad Atwood', 1, 'Steelers')

# this will happen once a week
lines.commit_lines(week=week, lines=lines.spoof_lines())

# this will an endpoint (refresh), many times per week
scores.commit_scores(week=week, scores=scores.spoof_scores())
# matchups.compare_scores_to_lines
# matchups.compares_deltas_to_picks
