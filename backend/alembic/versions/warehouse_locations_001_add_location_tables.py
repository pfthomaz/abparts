"""add warehouse_locations and inventory_locations tables

Revision ID: warehouse_loc_001
Revises: add_machine_dates
Create Date: 2026-02-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'warehouse_loc_001'
down_revision = 'add_machine_dates'
branch_labels = None
depends_on = None


def upgrade():
    # Create warehouse_locations table
    op.create_table(
        'warehouse_locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('warehouses.id'), nullable=False),
        sa.Column('location_code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Unique constraint: location_code must be unique within a warehouse
    op.create_unique_constraint(
        'uq_warehouse_location_code',
        'warehouse_locations',
        ['warehouse_id', 'location_code']
    )

    # Create indexes for warehouse_locations
    op.create_index('ix_warehouse_locations_warehouse_id', 'warehouse_locations', ['warehouse_id'])
    op.create_index('ix_warehouse_locations_location_code', 'warehouse_locations', ['location_code'])

    # Create inventory_locations junction table
    op.create_table(
        'inventory_locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('inventory_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inventory.id'), nullable=False),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('warehouse_locations.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Create indexes for inventory_locations
    op.create_index('ix_inventory_locations_inventory_id', 'inventory_locations', ['inventory_id'])
    op.create_index('ix_inventory_locations_location_id', 'inventory_locations', ['location_id'])

    # Unique constraint: prevent duplicate assignments of the same inventory to the same location
    op.create_unique_constraint(
        'uq_inventory_location_assignment',
        'inventory_locations',
        ['inventory_id', 'location_id']
    )


def downgrade():
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('inventory_locations')
    op.drop_table('warehouse_locations')
