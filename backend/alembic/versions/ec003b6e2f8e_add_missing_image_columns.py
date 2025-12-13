"""add_missing_image_columns

Revision ID: ec003b6e2f8e
Revises: add_protocol_translations_06
Create Date: 2025-12-13 18:27:59.654787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ec003b6e2f8e'
down_revision: Union[str, Sequence[str], None] = 'add_protocol_translations_06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add profile photo columns to users
    op.add_column('users', sa.Column('profile_photo_url', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('profile_photo_data', sa.LargeBinary(), nullable=True))
    
    # Add logo columns to organizations
    op.add_column('organizations', sa.Column('logo_url', sa.String(length=500), nullable=True))
    op.add_column('organizations', sa.Column('logo_data', sa.LargeBinary(), nullable=True))
    
    # Add image data to parts
    op.add_column('parts', sa.Column('image_data', sa.ARRAY(sa.LargeBinary()), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove image data from parts
    op.drop_column('parts', 'image_data')
    
    # Remove logo columns from organizations
    op.drop_column('organizations', 'logo_data')
    op.drop_column('organizations', 'logo_url')
    
    # Remove profile photo columns from users
    op.drop_column('users', 'profile_photo_data')
    op.drop_column('users', 'profile_photo_url')
