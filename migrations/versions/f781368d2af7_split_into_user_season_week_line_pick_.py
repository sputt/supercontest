"""split into user/season/week/line/pick/score tables

Revision ID: f781368d2af7
Revises: ae2d17b1b686
Create Date: 2019-09-10 22:44:50.108756

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import Sequence, CreateSequence

# revision identifiers, used by Alembic.
revision = 'f781368d2af7'
down_revision = 'ae2d17b1b686'
branch_labels = None
depends_on = None


def upgrade():
    # This change was a huge redesign. Wrote the migration manually.

    # First, perform the changes to the existing tables.
    # Rename the Matchup table to Line table, and drop winner.
    op.rename_table('matchups', 'lines')
    op.execute('ALTER SEQUENCE matchups_id_seq '
               'RENAME TO lines_id_seq')
    op.execute('ALTER INDEX idx_16436_matchups_pkey '
               'RENAME TO idex_16436_lines_pkey')
    op.drop_column('lines', 'winner')

    # New Season table.
    op.execute(CreateSequence(Sequence('seasons_id_seq')))
    op.create_table('seasons',
        sa.Column('id', sa.Integer(), nullable=False,
                  server_default=sa.text("nextval('seasons_id_seq')")),
        sa.Column('season', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Populate the table with the available seasons.
    op.execute('INSERT INTO seasons (season) '
               'SELECT DISTINCT season FROM lines')

    # New Week table.
    op.execute(CreateSequence(Sequence('weeks_id_seq')))
    op.create_table('weeks',
        sa.Column('id', sa.Integer(), nullable=False,
                  server_default=sa.text("nextval('weeks_id_seq')")),
        sa.Column('season_id', sa.Integer(), nullable=False),
        sa.Column('week', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['season_id'], ['seasons.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Populate the table with the available weeks for each season.
    op.execute('INSERT INTO weeks (season_id, week) '
               'SELECT DISTINCT seasons.id, lines.week '
               'FROM seasons, lines '
               'WHERE seasons.season = lines.season')

    # Make the proper user-season assignments with the info we have.
    op.execute('DELETE FROM users '
               'WHERE email = \'jessepthompson@outlook.com.com\'')

    # New Score table.
    op.execute(CreateSequence(Sequence('scores_id_seq')))
    op.create_table('scores',
        sa.Column('id', sa.Integer(), nullable=False,
                  server_default=sa.text("nextval('scores_id_seq')")),
        sa.Column('line_id', sa.Integer(), nullable=False),
        sa.Column('favored_team_score', sa.Integer(), nullable=False),
        sa.Column('underdog_team_score', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['line_id'], ['lines.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Move the score/status cols from the Line table to the
    # new Score table.
    op.execute('INSERT INTO scores (line_id, favored_team_score, underdog_team_score, status) '
               'SELECT id, favored_team_score, underdog_team_score, status '
               'FROM lines')
    op.drop_column('lines', 'favored_team_score')
    op.drop_column('lines', 'underdog_team_score')
    op.drop_column('lines', 'status')

    # Change the explicit season and week cols in the Line table
    # to be proper a proper foreign key to the new week table.
    # Remember the week table has the season info.
    # You have to wait until after to make it not-nullable because
    # you're adding a new col to existing rows.
    op.add_column('lines', sa.Column('week_id', sa.Integer()))
    op.create_foreign_key('lines_week_id_fkey',
                          'lines', 'weeks',
                          ['week_id'], ['id'])
    op.execute('UPDATE lines '
               'SET week_id = weeks.id '
               'FROM weeks, seasons '
                # join conditions
               'WHERE weeks.season_id = seasons.id '
                # update conditions for matching
               'AND lines.week = weeks.week '
               'AND lines.season = seasons.season')
    op.alter_column('lines', 'week_id', nullable=False)
    op.drop_column('lines', 'week')
    op.drop_column('lines', 'season')

    # Similarly, drop the explicit season and weel cols in the Pick
    # table for a single FK to the Line table, inferred from
    # the team you picked (the Line table has season/week/team).
    op.add_column('picks', sa.Column('line_id', sa.Integer()))
    op.create_foreign_key('picks_line_id_fkey',
                          'picks', 'lines',
                          ['line_id'], ['id'])
    op.execute('UPDATE picks '
               'SET line_id = lines.id '
               'FROM lines, weeks, seasons '
                # join conditions
               'WHERE lines.week_id = weeks.id '
               'AND weeks.season_id = seasons.id '
                # update conditions for matching
               'AND picks.week = weeks.week '
               'AND picks.season = seasons.season '
               'AND (picks.team = lines.favored_team OR picks.team = lines.underdog_team)') 
    op.alter_column('picks', 'line_id', nullable=False)
    op.drop_column('picks', 'week')
    op.drop_column('picks', 'season')
    # Slight alterations for consistency as well.
    op.alter_column('picks', 'user_id', nullable=False)
    op.drop_column('picks', 'points')


def downgrade():
    raise Exception('Irreversible migration. Major version change. If '
                    'you need to go back, check the vcs hash date of this '
                    'version file and then revert to a backup that was '
                    'dumped with a timestamp before then.')
