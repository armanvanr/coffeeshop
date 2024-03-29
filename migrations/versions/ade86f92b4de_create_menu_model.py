"""create menu model

Revision ID: ade86f92b4de
Revises: 
Create Date: 2023-06-21 13:41:21.637164

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ade86f92b4de'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('menu',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('desc', sa.String(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('stock', sa.SmallInteger(), nullable=False),
    sa.Column('img_url', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('menu', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_menu_id'), ['id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('menu', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_menu_id'))

    op.drop_table('menu')
    # ### end Alembic commands ###
