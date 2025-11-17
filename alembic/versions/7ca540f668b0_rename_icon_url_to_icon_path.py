"""rename_icon_url_to_icon_path

Revision ID: 7ca540f668b0
Revises: c7dc57ee62db
Create Date: 2025-11-17 17:16:31.109893

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7ca540f668b0"
down_revision: Union[str, Sequence[str], None] = "c7dc57ee62db"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "accessibility_items",
        "icon_url",
        new_column_name="icon_path",
        existing_type=sa.String(),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "accessibility_items",
        "icon_path",
        new_column_name="icon_url",
        existing_type=sa.String(),
    )
    pass
