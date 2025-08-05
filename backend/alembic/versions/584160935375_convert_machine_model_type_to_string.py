"""convert_machine_model_type_to_string

Revision ID: 584160935375
Revises: 00c1565ee6f9
Create Date: 2025-08-05 23:16:15.499049

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '584160935375'
down_revision: Union[str, Sequence[str], None] = '00c1565ee6f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert machine model type from enum to string."""
    # Convert the column to string type
    op.execute("ALTER TABLE machines ALTER COLUMN model_type TYPE VARCHAR(10)")
    
    # Drop the enum type since we're not using it anymore
    op.execute("DROP TYPE IF EXISTS machinemodeltype CASCADE")


def downgrade() -> None:
    """Revert machine model type from string to enum."""
    # Create the enum type
    op.execute("CREATE TYPE machinemodeltype AS ENUM ('V3.1B', 'V4.0')")
    
    # Convert column back to enum type
    op.execute("ALTER TABLE machines ALTER COLUMN model_type TYPE machinemodeltype USING model_type::machinemodeltype")
