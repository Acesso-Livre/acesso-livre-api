"""remove top and left columns from accessibility_items table

Revision ID: c7dc57ee62db
Revises: 30e9d27e1540
Create Date: 2025-11-14 10:14:24.660246

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c7dc57ee62db"
down_revision: Union[str, Sequence[str], None] = "30e9d27e1540"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove top and left columns from accessibility_items table
    op.drop_column("accessibility_items", "left")
    op.drop_column("accessibility_items", "top")


def downgrade() -> None:
    """Downgrade schema."""
    # Add top and left columns back to accessibility_items table
    op.add_column(
        "accessibility_items",
        sa.Column("top", sa.Float(), nullable=False, server_default="0.0"),
    )
    op.add_column(
        "accessibility_items",
        sa.Column("left", sa.Float(), nullable=False, server_default="0.0"),
    )
