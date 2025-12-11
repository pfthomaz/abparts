"""fix_part_usage_table_schema

Revision ID: ce25c4ebe17c
Revises: 584160935375
Create Date: 2025-08-05 23:31:03.476328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce25c4ebe17c'
down_revision: Union[str, Sequence[str], None] = '584160935375'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix part_usage table schema to match model definition."""
    # Rename quantity_used column to quantity to match model
    op.execute("ALTER TABLE part_usage RENAME COLUMN quantity_used TO quantity")
    
    # Add missing warehouse_id column
    op.execute("ALTER TABLE part_usage ADD COLUMN warehouse_id UUID")
    
    # Add foreign key constraint for warehouse_id
    op.execute("ALTER TABLE part_usage ADD CONSTRAINT part_usage_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)")
    
    # Update existing records to have a default warehouse_id (use the first warehouse)
    op.execute("""
        UPDATE part_usage 
        SET warehouse_id = (SELECT id FROM warehouses LIMIT 1) 
        WHERE warehouse_id IS NULL
    """)
    
    # Make warehouse_id NOT NULL after setting default values
    op.execute("ALTER TABLE part_usage ALTER COLUMN warehouse_id SET NOT NULL")


def downgrade() -> None:
    """Revert part_usage table schema changes."""
    # Remove NOT NULL constraint from warehouse_id
    op.execute("ALTER TABLE part_usage ALTER COLUMN warehouse_id DROP NOT NULL")
    
    # Drop foreign key constraint
    op.execute("ALTER TABLE part_usage DROP CONSTRAINT part_usage_warehouse_id_fkey")
    
    # Drop warehouse_id column
    op.execute("ALTER TABLE part_usage DROP COLUMN warehouse_id")
    
    # Rename quantity column back to quantity_used
    op.execute("ALTER TABLE part_usage RENAME COLUMN quantity TO quantity_used")
