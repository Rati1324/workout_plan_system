"""remove user_id from exercise

Revision ID: ff6f83aae3b8
Revises: 38743abd0166
Create Date: 2024-03-11 10:20:05.974866

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff6f83aae3b8'
down_revision: Union[str, None] = '38743abd0166'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # remove user_Id column an drelation from exercise
    op.drop_column('exercise', 'user_id')
    # op.drop_constraint('fk_exercise_user_id', 'exercise', type_='foreignkey')    


def downgrade() -> None:
    pass
