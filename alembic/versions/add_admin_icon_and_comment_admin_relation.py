"""Add icon_url to comments table

Revision ID: add_comment_icon_url
Revises: cc4427f38b62
Create Date: 2025-12-08 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'add_comment_icon_url'
down_revision: Union[str, Sequence[str], None] = 'cc4427f38b62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add icon_url column to comments table to store the accessibility item icon
    op.add_column('comments', sa.Column('icon_url', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove icon_url column from comments table
    op.drop_column('comments', 'icon_url')
