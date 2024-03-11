"""add break between exercise column

Revision ID: 88cac1d8b16e
Revises: 38743abd0166
Create Date: 2024-03-11 08:00:00.096655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88cac1d8b16e'
down_revision: Union[str, None] = '38743abd0166'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
