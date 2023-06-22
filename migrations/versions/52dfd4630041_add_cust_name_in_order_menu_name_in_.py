"""add cust_name in Order, menu_name in Order_Items

Revision ID: 52dfd4630041
Revises: a3833d51df22
Create Date: 2023-06-22 15:03:46.950939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52dfd4630041'
down_revision = 'a3833d51df22'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('customer_name', sa.Integer(), nullable=False))
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('order_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('menu_name', sa.String(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order_items', schema=None) as batch_op:
        batch_op.drop_column('menu_name')

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_column('customer_name')

    # ### end Alembic commands ###