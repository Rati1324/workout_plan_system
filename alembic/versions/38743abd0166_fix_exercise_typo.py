"""fix exercise typo

Revision ID: 38743abd0166
Revises: 9582430d7531
Create Date: 2024-03-10 15:14:05.606243

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38743abd0166'
down_revision: Union[str, None] = '9582430d7531'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # write migration for renaming tables, excercises to exercises
    op.rename_table('excercise', 'exercise')
    # write migration for renaming tables,  excercise_muscle to exercise_muscle
    op.rename_table('excercise_muscle', 'exercise_muscle')
    # write migration for renaming tables,  excercise_workout to exercise_workout
    op.rename_table('excercise_workout', 'exercise_workout')
    # rename excercise_id to exercise_id
    op.alter_column('exercise_muscle', 'excercise_id', new_column_name='exercise_id')
    op.alter_column('exercise_workout', 'excercise_id', new_column_name='exercise_id')
    op.alter_column('goal', 'excercise_id', new_column_name='exercise_id')
        

    # ### end Alembic commands ###


def downgrade() -> None:
    pass