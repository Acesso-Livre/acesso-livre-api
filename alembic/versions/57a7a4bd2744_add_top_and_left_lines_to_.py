"""add top and left lines to AccessibilityItem

Revision ID: 57a7a4bd2744
Revises: 9deeefc21b29
Create Date: 2025-11-07 15:58:35.553956

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '57a7a4bd2744'
down_revision: Union[str, Sequence[str], None] = '9deeefc21b29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('accessibility_items', sa.Column('top', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('accessibility_items', sa.Column('left', sa.Float(), nullable=False, server_default='0.0'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('accessibility_items', 'left')
    op.drop_column('accessibility_items', 'top')
