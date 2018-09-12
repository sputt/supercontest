#!/usr/bin/env python
"""
This script runs the application.
You must pass "development" or "production" as a clarg to this script.
This script assumes create.py has already been run to create the db.
"""
import os
import sys

this_dir = os.path.dirname(os.path.realpath(__file__))
mode = sys.argv[1]
full_cfg_path = os.path.join(this_dir, 'config', mode + '.py')
os.environ['APP_CONFIG_FILE'] = full_cfg_path 

from supercontest import (run_app,
                          users, picks, lines, scores, matchups)

# start the flask application
run_app()

# this should happen once
users.commit_users()

# you'll probably have to enter this if westgate doesn't expose it
week=17

# this will an endpoint (pick), many times per week
picks.commit_pick(name='Brad Atwood', week=week, team='STEELERS')
picks.commit_pick(name='Brad Atwood', week=week, team='PATRIOTS')
picks.commit_pick(name='Brad Atwood', week=week, team='TITANS')

# this will happen once a week
lines.commit_lines(week=week, lines=lines.spoof_lines())

# this will an endpoint (refresh), many times per week
scores.commit_scores(week=week, scores=scores.spoof_scores())
matchups.commit_results(week=week, results=matchups.compare_scores_to_lines(week=week))
