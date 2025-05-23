"""Initial database schema; created Exercise and WorkoutLog tables.

Revision ID: 60927801bf02
Revises: 
Create Date: 2025-05-23 10:56:14.324764

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60927801bf02'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('exercise',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('workout_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('exercise_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('sets', sa.Integer(), nullable=True),
    sa.Column('reps', sa.Integer(), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.Column('duration_minutes', sa.Integer(), nullable=True),
    sa.Column('distance_km', sa.Float(), nullable=True),
    sa.Column('notes', sa.String(length=300), nullable=True),
    sa.Column('is_pb', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['exercise_id'], ['exercise.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('workout_log')
    op.drop_table('exercise')
    # ### end Alembic commands ###
