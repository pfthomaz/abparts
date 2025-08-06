"""add_missing_parts_columns

Revision ID: 3bef488d9675
Revises: ce25c4ebe17c
Create Date: 2025-08-06 13:06:56.364204

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3bef488d9675'
down_revision: Union[str, Sequence[str], None] = 'ce25c4ebe17c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing columns to parts table."""
    # Add part_code column
    op.execute("ALTER TABLE parts ADD COLUMN part_code VARCHAR(100)")
    
    # Add serial_number column  
    op.execute("ALTER TABLE parts ADD COLUMN serial_number VARCHAR(255)")


def downgrade() -> None:
    """Remove added columns from parts table."""
    # Drop serial_number column
    op.execute("ALTER TABLE parts DROP COLUMN serial_number")
    
    # Drop part_code column
    op.execute("ALTER TABLE parts DROP COLUMN part_code")
