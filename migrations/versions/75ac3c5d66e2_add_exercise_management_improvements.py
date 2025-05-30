"""Add exercise management improvements

Revision ID: 75ac3c5d66e2
Revises: af180e90b0cd
Create Date: 2025-05-27 14:22:42.560422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75ac3c5d66e2'
down_revision = 'af180e90b0cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('exercise', schema=None) as batch_op:
        batch_op.add_column(sa.Column('subcategory', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('form_instructions', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('equipment_needed', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('difficulty_level', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('is_favorite', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('last_used', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('exercise', schema=None) as batch_op:
        batch_op.drop_column('last_used')
        batch_op.drop_column('is_favorite')
        batch_op.drop_column('difficulty_level')
        batch_op.drop_column('equipment_needed')
        batch_op.drop_column('form_instructions')
        batch_op.drop_column('subcategory')

    # ### end Alembic commands ###
