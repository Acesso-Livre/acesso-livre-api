"""move top and left fields from accessibility_items to locations

Revision ID: 30e9d27e1540
Revises: 57a7a4bd2744
Create Date: 2025-11-14 10:08:00.961308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30e9d27e1540'
down_revision: Union[str, Sequence[str], None] = '57a7a4bd2744'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add top and left columns to locations table
    op.add_column('locations', sa.Column('top', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('locations', sa.Column('left', sa.Float(), nullable=False, server_default='0.0'))

    # Drop top and left columns from accessibility_items table
    op.drop_column('accessibility_items', 'left')
    op.drop_column('accessibility_items', 'top')


def downgrade() -> None:
    """Downgrade schema."""
    # Add top and left columns back to accessibility_items table
    op.add_column('accessibility_items', sa.Column('top', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('accessibility_items', sa.Column('left', sa.Float(), nullable=False, server_default='0.0'))

    # Drop top and left columns from locations table
    op.drop_column('locations', 'left')
    op.drop_column('locations', 'top')