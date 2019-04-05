"""adding postgres sequences to all primary key ids for all tables

Revision ID: 493b07f8aea0
Revises: 46a3c7d90935
Create Date: 2019-04-05 14:08:31.363131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '493b07f8aea0'
down_revision = '46a3c7d90935'
branch_labels = None
depends_on = None

"""Everything below was manually done, not autogenerated by Alembic, because
it can't recognize the addition of Sequences for Postgres primary key IDs.
"""

tables = {'user': 43, 'pick': 3106, 'matchup': 263}


def modify_sequence(create, table_name, start):
    """create is a boolean. If false, it will drop.
    """
    # just bypass for implementations that don't have sequences, like sqlite
    if op._proxy.migration_context.dialect.supports_sequences:
        sequence_name = '{}_id_seq'.format(table_name)
        sequence = sa.schema.Sequence(sequence_name, start=start)
        action = sa.schema.CreateSequence(sequence) if create else sa.schema.DropSequence(sequence)
        op.execute(action)


def upgrade():
    for table_name, start in tables.iteritems():
        modify_sequence(create=True, table_name=table_name, start=start)


def downgrade():
    for table_name, start in tables.iteritems():
        modify_sequence(create=False, table_name=table_name, start=start)
