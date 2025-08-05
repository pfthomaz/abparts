"""fix_machine_model_type_enum_values

Revision ID: 5718aeeba9e9
Revises: 87c7b6846dd4
Create Date: 2025-08-05 22:42:46.548327

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5718aeeba9e9'
down_revision: Union[str, Sequence[str], None] = '87c7b6846dd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix machine model type enum values."""
    # Convert column to varchar temporarily
    op.execute("ALTER TABLE machines ALTER COLUMN model_type TYPE VARCHAR(50)")
    
    # Drop the old enum type
    op.execute("DROP TYPE machinemodeltype CASCADE")
    
    # Create the new enum type with correct values
    op.execute("CREATE TYPE machinemodeltype AS ENUM ('V3.1B', 'V4.0')")
    
    # Convert column back to enum type
    op.execute("ALTER TABLE machines ALTER COLUMN model_type TYPE machinemodeltype USING model_type::machinemodeltype")


def downgrade() -> None:
    """Revert machine model type enum values."""
    # Convert column to varchar temporarily
    op.execute("ALTER TABLE machines ALTER COLUMN model_type TYPE VARCHAR(50)")
    
    # Drop the new enum type
    op.execute("DROP TYPE machinemodeltype CASCADE")
    
    # Create the old enum type with old values
    op.execute("CREATE TYPE machinemodeltype AS ENUM ('V3_1B', 'V4_0')")
    
    # Convert column back to enum type
    op.execute("ALTER TABLE machines ALTER COLUMN model_type TYPE machinemodeltype USING model_type::machinemodeltype")
