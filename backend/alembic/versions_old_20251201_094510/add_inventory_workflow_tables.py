"""add_inventory_workflow_tables

Revision ID: inventory_workflow_001
Revises: 31e87319dc9a
Create Date: 2025-01-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'inventory_workflow_001'
down_revision = '31e87319dc9a'
branch_labels = None
depends_on = None


def upgrade():
    # Create stocktake_status enum
    stocktake_status_enum = postgresql.ENUM(
        'planned', 'in_progress', 'completed', 'cancelled',
        name='stocktakestatus'
    )
    stocktake_status_enum.create(op.get_bind())
    
    # Create inventory_alert_type enum
    inventory_alert_type_enum = postgresql.ENUM(
        'low_stock', 'stockout', 'expiring', 'expired', 'excess', 'discrepancy',
        name='inventoryalerttype'
    )
    inventory_alert_type_enum.create(op.get_bind())
    
    # Create inventory_alert_severity enum
    inventory_alert_severity_enum = postgresql.ENUM(
        'low', 'medium', 'high', 'critical',
        name='inventoryalertseverity'
    )
    inventory_alert_severity_enum.create(op.get_bind())
    
    # Create stocktakes table
    op.create_table('stocktakes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', stocktake_status_enum, nullable=False, server_default='planned'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('scheduled_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('completed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['completed_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['scheduled_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stocktakes_warehouse_id'), 'stocktakes', ['warehouse_id'], unique=False)
    op.create_index(op.f('ix_stocktakes_status'), 'stocktakes', ['status'], unique=False)
    op.create_index(op.f('ix_stocktakes_scheduled_date'), 'stocktakes', ['scheduled_date'], unique=False)
    
    # Create stocktake_items table
    op.create_table('stocktake_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stocktake_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('part_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('expected_quantity', sa.DECIMAL(precision=10, scale=3), nullable=False),
        sa.Column('actual_quantity', sa.DECIMAL(precision=10, scale=3), nullable=True),
        sa.Column('counted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('counted_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['counted_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
        sa.ForeignKeyConstraint(['stocktake_id'], ['stocktakes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stocktake_items_stocktake_id'), 'stocktake_items', ['stocktake_id'], unique=False)
    op.create_index(op.f('ix_stocktake_items_part_id'), 'stocktake_items', ['part_id'], unique=False)
    
    # Create inventory_alerts table
    op.create_table('inventory_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('part_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('alert_type', inventory_alert_type_enum, nullable=False),
        sa.Column('severity', inventory_alert_severity_enum, nullable=False),
        sa.Column('threshold_value', sa.DECIMAL(precision=10, scale=3), nullable=True),
        sa.Column('current_value', sa.DECIMAL(precision=10, scale=3), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
        sa.ForeignKeyConstraint(['resolved_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_alerts_warehouse_id'), 'inventory_alerts', ['warehouse_id'], unique=False)
    op.create_index(op.f('ix_inventory_alerts_part_id'), 'inventory_alerts', ['part_id'], unique=False)
    op.create_index(op.f('ix_inventory_alerts_alert_type'), 'inventory_alerts', ['alert_type'], unique=False)
    op.create_index(op.f('ix_inventory_alerts_severity'), 'inventory_alerts', ['severity'], unique=False)
    op.create_index(op.f('ix_inventory_alerts_is_active'), 'inventory_alerts', ['is_active'], unique=False)
    
    # Create inventory_adjustments table
    op.create_table('inventory_adjustments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('part_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity_change', sa.DECIMAL(precision=10, scale=3), nullable=False),
        sa.Column('previous_quantity', sa.DECIMAL(precision=10, scale=3), nullable=False),
        sa.Column('new_quantity', sa.DECIMAL(precision=10, scale=3), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('adjusted_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('adjustment_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('stocktake_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['adjusted_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
        sa.ForeignKeyConstraint(['stocktake_id'], ['stocktakes.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_adjustments_warehouse_id'), 'inventory_adjustments', ['warehouse_id'], unique=False)
    op.create_index(op.f('ix_inventory_adjustments_part_id'), 'inventory_adjustments', ['part_id'], unique=False)
    op.create_index(op.f('ix_inventory_adjustments_adjustment_date'), 'inventory_adjustments', ['adjustment_date'], unique=False)
    op.create_index(op.f('ix_inventory_adjustments_stocktake_id'), 'inventory_adjustments', ['stocktake_id'], unique=False)


def downgrade():
    # Drop tables
    op.drop_table('inventory_adjustments')
    op.drop_table('inventory_alerts')
    op.drop_table('stocktake_items')
    op.drop_table('stocktakes')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS inventoryalertseverity')
    op.execute('DROP TYPE IF EXISTS inventoryalerttype')
    op.execute('DROP TYPE IF EXISTS stocktakestatus')