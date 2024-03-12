"""add weekdays

Revision ID: 14cb8c90a9ea
Revises: ff6f83aae3b8
Create Date: 2024-03-12 15:37:38.070134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14cb8c90a9ea'
down_revision: Union[str, None] = 'ff6f83aae3b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("workout_plan", sa.Column("weekdays", sa.String))
    op.drop_column("workout_plan", "frequency")

def downgrade() -> None:
    op.drop_column("workout_plan", "weekdays")
