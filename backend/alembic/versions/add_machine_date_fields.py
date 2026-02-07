"""add machine date and status fields

Revision ID: add_machine_dates
Revises: 7b3899138d40
Create Date: 2026-02-07 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_machine_dates'
down_revision = '7b3899138d40'
branch_labels = None
depends_on = None


def upgrade():
    """Add date and status fields to machines table."""
    
    # Create the MachineStatus enum type if it doesn't exist
    machine_status_enum = postgresql.ENUM('active', 'inactive', 'maintenance', 'decommissioned', name='machinestatus', create_type=False)
    machine_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Add columns to machines table
    # Check if columns exist before adding them
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('machines')]
    
    if 'purchase_date' not in existing_columns:
        op.add_column('machines', sa.Column('purchase_date', sa.DateTime(timezone=True), nullable=True))
    
    if 'warranty_expiry_date' not in existing_columns:
        op.add_column('machines', sa.Column('warranty_expiry_date', sa.DateTime(timezone=True), nullable=True))
    
    if 'status' not in existing_columns:
        op.add_column('machines', sa.Column('status', machine_status_enum, nullable=False, server_default='active'))
    
    if 'last_maintenance_date' not in existing_columns:
        op.add_column('machines', sa.Column('last_maintenance_date', sa.DateTime(timezone=True), nullable=True))
    
    if 'next_maintenance_date' not in existing_columns:
        op.add_column('machines', sa.Column('next_maintenance_date', sa.DateTime(timezone=True), nullable=True))
    
    if 'location' not in existing_columns:
        op.add_column('machines', sa.Column('location', sa.String(255), nullable=True))
    
    if 'notes' not in existing_columns:
        op.add_column('machines', sa.Column('notes', sa.Text(), nullable=True))


def downgrade():
    """Remove date and status fields from machines table."""
    
    # Drop columns
    op.drop_column('machines', 'notes')
    op.drop_column('machines', 'location')
    op.drop_column('machines', 'next_maintenance_date')
    op.drop_column('machines', 'last_maintenance_date')
    op.drop_column('machines', 'status')
    op.drop_column('machines', 'warranty_expiry_date')
    op.drop_column('machines', 'purchase_date')
    
    # Drop the enum type
    machine_status_enum = postgresql.ENUM('active', 'inactive', 'maintenance', 'decommissioned', name='machinestatus')
    machine_status_enum.drop(op.get_bind(), checkfirst=True)
