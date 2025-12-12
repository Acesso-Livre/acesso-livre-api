"""create comment_icons table and association

Revision ID: ff9b0ca356e9
Revises: add_comment_icon_url
Create Date: 2025-12-11 21:40:28.446907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ff9b0ca356e9'
down_revision: Union[str, Sequence[str], None] = 'add_comment_icon_url'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create comment_icons table
    op.create_table(
        'comment_icons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('icon_url', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create association table for many-to-many relationship between comments and comment_icons
    op.create_table(
        'comment_comment_icons',
        sa.Column('comment_id', sa.Integer(), nullable=False),
        sa.Column('icon_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ),
        sa.ForeignKeyConstraint(['icon_id'], ['comment_icons.id'], ),
        sa.PrimaryKeyConstraint('comment_id', 'icon_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop association table
    op.drop_table('comment_comment_icons')
    
    # Drop comment_icons table
    op.drop_table('comment_icons')
