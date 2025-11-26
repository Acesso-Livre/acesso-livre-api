"""add_timezone_to_reset_token_expires

Revision ID: cc4427f38b62
Revises: c7dc57ee62db
Create Date: 2025-11-26 20:50:35.838945

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "cc4427f38b62"
down_revision: Union[str, Sequence[str], None] = "c7dc57ee62db"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "admins",
        "reset_token_expires",
        existing_type=sa.TIMESTAMP(),
        type_=sa.TIMESTAMP(timezone=True),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "admins",
        "reset_token_expires",
        existing_type=sa.TIMESTAMP(timezone=True),
        type_=sa.TIMESTAMP(),
        existing_nullable=True,
    )
