"""on production server

Revision ID: cfb071e4c6b9
Revises: 894dba7ef5ad
Create Date: 2018-11-05 16:46:31.273945

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfb071e4c6b9'
down_revision = '894dba7ef5ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=225, collation='NOCASE'), server_default='', nullable=False))
        batch_op.add_column(sa.Column('email_confirmed_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False))
        batch_op.add_column(sa.Column('password', sa.String(length=255), server_default='', nullable=False))
        batch_op.add_column(sa.Column('username', sa.String(length=100, collation='NOCASE'), server_default='', nullable=False))
        batch_op.create_unique_constraint('email_constraint', ['email'])
        batch_op.create_unique_constraint('password_constraint', ['password'])
        batch_op.create_unique_constraint('username_constraint', ['username'])
        batch_op.drop_column('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(), nullable=False))
        batch_op.drop_constraint('username_constraint', type_='unique')
        batch_op.drop_constraint('password_constraint', type_='unique')
        batch_op.drop_constraint('email_constraint', type_='unique')
        batch_op.drop_column('username')
        batch_op.drop_column('password')
        batch_op.drop_column('is_active')
        batch_op.drop_column('email_confirmed_at')
        batch_op.drop_column('email')

    # ### end Alembic commands ###