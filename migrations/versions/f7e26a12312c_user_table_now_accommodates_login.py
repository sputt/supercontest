"""user table now accommodates login

Revision ID: f7e26a12312c
Revises: 894dba7ef5ad
Create Date: 2019-02-28 19:32:40.422127

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7e26a12312c'
down_revision = '894dba7ef5ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('first_name', sa.String(length=50, collation='NOCASE'), server_default='', nullable=False))
        batch_op.add_column(sa.Column('last_name', sa.String(length=50, collation='NOCASE'), server_default='', nullable=False))
        batch_op.drop_constraint(u'password_constraint', type_='unique')
        batch_op.drop_constraint(u'username_constraint', type_='unique')
        batch_op.drop_column('username')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.VARCHAR(length=100), server_default=sa.text(u"''"), nullable=False))
        batch_op.create_unique_constraint(u'username_constraint', ['username'])
        batch_op.create_unique_constraint(u'password_constraint', ['password'])
        batch_op.drop_column('last_name')
        batch_op.drop_column('first_name')

    # ### end Alembic commands ###