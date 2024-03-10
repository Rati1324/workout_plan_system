"""add break time column

Revision ID: 9582430d7531
Revises: 6c9c362d8073
Create Date: 2024-03-10 13:36:19.547473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9582430d7531'
down_revision: Union[str, None] = '6c9c362d8073'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('excercise_workout', sa.Column('break_time', sa.Float))


def downgrade() -> None:
    op.drop_column('excercise_workout', 'break_time')
