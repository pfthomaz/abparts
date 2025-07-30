"""fix_machine_model_type_enum_values

Revision ID: 620ec30a7e37
Revises: d3abe3b28834
Create Date: 2025-07-30 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '620ec30a7e37'
down_revision: Union[str, Sequence[str], None] = 'd3abe3b28834'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix the machine model type enum values to match SQLAlchemy expectations."""
    
    # Drop any existing check constraints on model_type
    op.execute("ALTER TABLE machines DROP CONSTRAINT IF EXISTS machines_model_type_check")
    
    # Drop the existing enum and recreate with correct values
    op.execute("ALTER TABLE machines ALTER COLUMN model_type TYPE VARCHAR(100)")
    op.execute("DROP TYPE IF EXISTS machinemodeltype")
    
    # Create new enum with correct values that match SQLAlchemy enum names
    machine_model_type_enum = postgresql.ENUM('V3_1B', 'V4_0', name='machinemodeltype')
    machine_model_type_enum.create(op.get_bind())
    
    # Update existing data to match new enum values
    op.execute("UPDATE machines SET model_type = 'V3_1B' WHERE model_type = 'V3.1B'")
    op.execute("UPDATE machines SET model_type = 'V4_0' WHERE model_type = 'V4.0'")
    
    # Convert column back to enum
    op.execute("ALTER TABLE machines ALTER COLUMN model_type TYPE machinemodeltype USING model_type::machinemodeltype")


def downgrade() -> None:
    """Revert the machine model type enum values."""
    
    # Convert back to VARCHAR
    op.execute("ALTER TABLE machines ALTER COLUMN model_type TYPE VARCHAR(100)")
    
    # Update data back to original format
    op.execute("UPDATE machines SET model_type = 'V3.1B' WHERE model_type = 'V3_1B'")
    op.execute("UPDATE machines SET model_type = 'V4.0' WHERE model_type = 'V4_0'")
    
    # Drop and recreate enum with original values
    op.execute("DROP TYPE IF EXISTS machinemodeltype")
    machine_model_type_enum = postgresql.ENUM('V3.1B', 'V4.0', name='machinemodeltype')
    machine_model_type_enum.create(op.get_bind())
    
    # Convert column back to enum
    op.execute("ALTER TABLE machines ALTER COLUMN model_type TYPE machinemodeltype USING model_type::machinemodeltype")