"""add one-to-many location comments relationship

Revision ID: 9deeefc21b29
Revises: f7de5c5a272b
Create Date: 2025-11-07 14:57:41.362287

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9deeefc21b29'
down_revision: Union[str, Sequence[str], None] = 'f7de5c5a272b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_foreign_key(
        'fk_comments_location_id',
        'comments', 'locations',
        ['location_id'], ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_comments_location_id', 'comments', type_='foreignkey')
