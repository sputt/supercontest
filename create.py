#!/usr/bin/env python
"""
This script creates the database for the first time.
You must pass "development" or "production" as a clarg to this script.
"""
import os
import sys

this_dir = os.path.dirname(os.path.realpath(__file__))
mode = sys.argv[1]
full_cfg_path = os.path.join(this_dir, 'config', mode + '.py')
os.environ['APP_CONFIG_FILE'] = full_cfg_path 

from supercontest import create_db

create_db()
