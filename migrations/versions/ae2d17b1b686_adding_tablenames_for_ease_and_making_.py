"""reset seqs, pluralize table names, drop some defaults, make some nullable

Revision ID: ae2d17b1b686
Revises: 5611e69e53d2
Create Date: 2019-09-10 13:04:43.923007

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ae2d17b1b686'
down_revision = '5611e69e53d2'
branch_labels = None
depends_on = None

cols_to_change_default = ['email', 'is_active', 'password']
cols_to_change_nullable = ['first_name', 'last_name']
seqs_to_reset = ['user', 'pick', 'matchup']
tables_to_rename = ['user', 'pick', 'matchup']
pkey_map = {'user': '16448',
            'pick': '16459',
            'matchup': '16436'}


def upgrade():
    # I manually wrote this upgrade and downgrade.    

    # Set the nextval correctly for all sequences.
    for seq in seqs_to_reset:
        op.execute('SELECT setval(\'{}_id_seq\', (SELECT MAX(id) from public.{}))'.format(seq, seq))
    # Drop a few defaults.
    for col in cols_to_change_default:
        op.execute('ALTER TABLE public.user ALTER COLUMN {} DROP DEFAULT'.format(col))
    # Then make a few user cols optional.
    for col in cols_to_change_nullable:
        op.alter_column('user', col, nullable=True)
    # Then rename all tables.
    for table in tables_to_rename:
        op.rename_table(table, table+'s')
        op.execute('ALTER SEQUENCE {}_id_seq RENAME TO {}_id_seq'.format(table, table+'s'))
        op.execute('ALTER INDEX idx_{}_{}_pkey RENAME TO idx_{}_{}_pkey'.format(pkey_map[table], table, pkey_map[table], table+'s'))


def downgrade():
    # I manually wrote this upgrade and downgrade.    

    # Set the nextval correctly for all sequences. This is the same as the upgrade,
    # just makes it the max of all current ids.
    for seq in seqs_to_reset:
        op.execute('SELECT setval(\'{}_id_seq\', (SELECT MAX(id) from public.{}))'.format(seq, seq))
    # Add a few defaults back.
    for col in cols_to_change_default:
        op.execute('ALTER TABLE public.user ALTER COLUMN {} SET DEFAULT \'\''.format(col))
    # Then make the few user cols not nullable again.
    for col in cols_to_change_nullable:
        op.alter_column('user', col, nullable=False)
    # Then rename all tables.
    for table in tables_to_rename:
        op.rename_table(table+'s', table)
        op.execute('ALTER SEQUENCE {}_id_seq RENAME TO {}_id_seq'.format(table+'s', table))
        op.execute('ALTER INDEX idx_{}_{}_pkey RENAME TO idx_{}_{}_pkey'.format(pkey_map[table], table+'s', pkey_map[table], table))
