"""add_machine_columns

Revision ID: add_machine_columns
Revises: add_security_session
Create Date: 2025-07-25 14:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_machine_columns'
down_revision: Union[str, Sequence[str], None] = 'add_security_session'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing columns to machines table."""
    
    # Create MachineStatus enum type if it doesn't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE machinestatus AS ENUM ('active', 'inactive', 'maintenance', 'decommissioned');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Add missing columns to machines table
    op.add_column('machines', sa.Column('purchase_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('machines', sa.Column('warranty_expiry_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('machines', sa.Column('status', postgresql.ENUM('active', 'inactive', 'maintenance', 'decommissioned', name='machinestatus'), nullable=False, server_default='active'))
    op.add_column('machines', sa.Column('last_maintenance_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('machines', sa.Column('next_maintenance_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('machines', sa.Column('location', sa.String(length=255), nullable=True))
    op.add_column('machines', sa.Column('notes', sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove added columns from machines table."""
    
    # Remove added columns
    op.drop_column('machines', 'notes')
    op.drop_column('machines', 'location')
    op.drop_column('machines', 'next_maintenance_date')
    op.drop_column('machines', 'last_maintenance_date')
    op.drop_column('machines', 'status')
    op.drop_column('machines', 'warranty_expiry_date')
    op.drop_column('machines', 'purchase_date')
    
    # Drop enum type if no other tables use it
    op.execute("DROP TYPE IF EXISTS machinestatus")