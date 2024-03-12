"""added order to workout plan

Revision ID: 6c9c362d8073
Revises: 7445b3784735
Create Date: 2024-03-10 13:01:34.376267

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c9c362d8073'
down_revision: Union[str, None] = '7445b3784735'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('excercise_workout', sa.Column('order', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('excercise_workout', 'order')