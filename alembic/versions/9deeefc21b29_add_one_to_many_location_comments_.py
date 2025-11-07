"""add one-to-many location comments relationship

Revision ID: 9deeefc21b29
Revises: f7de5c5a272b
Create Date: 2025-11-07 14:57:41.362287

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9deeefc21b29'
down_revision: Union[str, Sequence[str], None] = 'f7de5c5a272b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
