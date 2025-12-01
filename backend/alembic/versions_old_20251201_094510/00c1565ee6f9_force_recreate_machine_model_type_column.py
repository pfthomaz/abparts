"""force_recreate_machine_model_type_column

Revision ID: 00c1565ee6f9
Revises: 5718aeeba9e9
Create Date: 2025-08-05 23:14:30.305264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00c1565ee6f9'
down_revision: Union[str, Sequence[str], None] = '5718aeeba9e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Force recreate machine model type column to fix enum issues."""
    # Drop the column completely
    op.drop_column('machines', 'model_type')
    
    # Drop the enum type
    op.execute("DROP TYPE IF EXISTS machinemodeltype CASCADE")
    
    # Create the enum type with correct values
    op.execute("CREATE TYPE machinemodeltype AS ENUM ('V3.1B', 'V4.0')")
    
    # Add the column back with the enum type
    op.execute("ALTER TABLE machines ADD COLUMN model_type machinemodeltype NOT NULL DEFAULT 'V3.1B'")
    
    # Update the existing records with correct values
    op.execute("UPDATE machines SET model_type = 'V3.1B' WHERE serial_number = 'ABV31B-SN001'")
    op.execute("UPDATE machines SET model_type = 'V4.0' WHERE serial_number = 'ABV40-SN002'")


def downgrade() -> None:
    """Revert the column recreation."""
    # Convert column to varchar temporarily
    op.execute("ALTER TABLE machines ALTER COLUMN model_type TYPE VARCHAR(50)")
    
    # Drop the new enum type
    op.execute("DROP TYPE machinemodeltype CASCADE")
    
    # Create the old enum type
    op.execute("CREATE TYPE machinemodeltype AS ENUM ('V3_1B', 'V4_0')")
    
    # Convert column back to enum type
    op.execute("ALTER TABLE machines ALTER COLUMN model_type TYPE machinemodeltype USING model_type::machinemodeltype")
