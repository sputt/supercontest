"""Wrappers around all interactions with the db.session: mostly
queries and commits.

The modules in this package are the only ones in the entire
distribution that should invoke the db object.

This makes the application side of migrations much easier to update.
"""
