"""add paid_date in order

Revision ID: 6350cb08945a
Revises: 9cfc4dd4854d
Create Date: 2023-06-23 13:46:26.179740

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6350cb08945a'
down_revision = '9cfc4dd4854d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('paid_date', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('paid_date')

    # ### end Alembic commands ###
