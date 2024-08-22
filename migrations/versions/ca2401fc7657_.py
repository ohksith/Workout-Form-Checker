"""empty message

Revision ID: ca2401fc7657
Revises: 4b0ac2e205e8
Create Date: 2024-08-22 01:47:04.978988

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca2401fc7657'
down_revision = '4b0ac2e205e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('rep_goal',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('rep_goal',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###