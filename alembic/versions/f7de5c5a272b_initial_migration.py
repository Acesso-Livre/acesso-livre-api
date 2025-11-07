"""initial migration

Revision ID: f7de5c5a272b
Revises: 
Create Date: 2025-11-07 14:10:37.219846

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f7de5c5a272b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Criar tabela accessibility_items
    op.create_table(
        'accessibility_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('icon_url', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar tabela locations
    op.create_table(
        'locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('avg_rating', sa.Float(), nullable=True, default=0.0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar tabela admins
    op.create_table(
        'admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.Text(), nullable=False),
        sa.Column('reset_token_hash', sa.String(), nullable=True),
        sa.Column('reset_token_expires', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Criar tabela associativa location_accessibility (many-to-many)
    op.create_table(
        'location_accessibility',
        sa.Column('location_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.ForeignKeyConstraint(['item_id'], ['accessibility_items.id'], ),
        sa.PrimaryKeyConstraint('location_id', 'item_id')
    )
    
    # Criar tabela comments
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_name', sa.String(length=255), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('location_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índices
    op.create_index('ix_admins_email', 'admins', ['email'], unique=True)
    op.create_index('ix_comments_location_id', 'comments', ['location_id'])
    op.create_index('ix_comments_user_name', 'comments', ['user_name'])
    
    # Criar constraints de verificação
    op.create_check_constraint('rating_range', 'comments', 'rating >= 1 AND rating <= 5')
    op.create_check_constraint('status_values', 'comments', "status IN ('pending', 'approved', 'rejected')")


def downgrade() -> None:
    """Downgrade schema."""
    # Remover constraints de verificação
    op.drop_constraint('status_values', 'comments', type_='check')
    op.drop_constraint('rating_range', 'comments', type_='check')
    
    # Remover índices
    op.drop_index('ix_comments_user_name')
    op.drop_index('ix_comments_location_id')
    op.drop_index('ix_admins_email')
    
    # Remover tabelas em ordem reversa (devido às foreign keys)
    op.drop_table('comments')
    op.drop_table('location_accessibility')
    op.drop_table('admins')
    op.drop_table('locations')
    op.drop_table('accessibility_items')
