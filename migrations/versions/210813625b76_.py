"""empty message

Revision ID: 210813625b76
Revises: f42dc765f5e9
Create Date: 2024-07-17 23:10:34.421655

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '210813625b76'
down_revision = 'f42dc765f5e9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_exercise', schema=None) as batch_op:
        batch_op.alter_column('exercise_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('count',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_exercise', schema=None) as batch_op:
        batch_op.alter_column('count',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('exercise_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
