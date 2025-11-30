"""redesign stock adjustments system

Revision ID: 20241130_redesign_stock_adjustments
Revises: 20251124_add_customer_order_id_to_transactions
Create Date: 2024-11-30 18:00:00.000000

This migration redesigns the stock adjustments system:
1. Drops the unused inventory_adjustments table
2. Redesigns stock_adjustments table to be warehouse-based
3. Creates stock_adjustment_items table for line-item tracking
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '20241130_stock_adj'  # 19 chars - within 32 char limit
down_revision = '20251124_order_txn'  # Verify this matches production!
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Drop inventory_adjustments table if it exists
    op.execute("""
        DROP TABLE IF EXISTS inventory_adjustments CASCADE;
    """)
    
    # Step 2: Create adjustment_type enum
    adjustment_type_enum = postgresql.ENUM(
        'manual', 'correction', 'damage', 'loss', 'found', 'other',
        name='adjustmenttype',
        create_type=False
    )
    adjustment_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Step 3: Backup existing stock_adjustments data (if any)
    op.execute("""
        CREATE TABLE IF NOT EXISTS stock_adjustments_backup AS 
        SELECT * FROM stock_adjustments;
    """)
    
    # Step 4: Modify stock_adjustments table structure
    # Drop the old foreign key constraint
    op.execute("""
        ALTER TABLE stock_adjustments 
        DROP CONSTRAINT IF EXISTS stock_adjustments_inventory_id_fkey;
    """)
    
    # Remove inventory_id column
    op.drop_column('stock_adjustments', 'inventory_id')
    
    # Add new columns
    op.add_column('stock_adjustments', 
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column('stock_adjustments', 
        sa.Column('adjustment_type', adjustment_type_enum, nullable=True, server_default='manual')
    )
    op.add_column('stock_adjustments', 
        sa.Column('reason', sa.Text(), nullable=True)
    )
    
    # Rename quantity_adjusted to total_items_adjusted
    op.alter_column('stock_adjustments', 'quantity_adjusted',
        new_column_name='total_items_adjusted',
        type_=sa.Integer(),
        nullable=True
    )
    
    # Add foreign key for warehouse_id
    op.create_foreign_key(
        'stock_adjustments_warehouse_id_fkey',
        'stock_adjustments', 'warehouses',
        ['warehouse_id'], ['id']
    )
    
    # Step 5: Create stock_adjustment_items table
    op.create_table(
        'stock_adjustment_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('stock_adjustment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('part_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity_before', sa.DECIMAL(precision=10, scale=3), nullable=False),
        sa.Column('quantity_after', sa.DECIMAL(precision=10, scale=3), nullable=False),
        sa.Column('quantity_change', sa.DECIMAL(precision=10, scale=3), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['stock_adjustment_id'], ['stock_adjustments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['part_id'], ['parts.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index(
        'ix_stock_adjustment_items_stock_adjustment_id',
        'stock_adjustment_items',
        ['stock_adjustment_id']
    )
    op.create_index(
        'ix_stock_adjustment_items_part_id',
        'stock_adjustment_items',
        ['part_id']
    )
    op.create_index(
        'ix_stock_adjustments_warehouse_id',
        'stock_adjustments',
        ['warehouse_id']
    )
    op.create_index(
        'ix_stock_adjustments_adjustment_date',
        'stock_adjustments',
        ['adjustment_date']
    )
    
    # Step 6: Make warehouse_id and adjustment_type NOT NULL after adding them
    # (They were nullable initially to allow adding the column)
    op.execute("""
        DELETE FROM stock_adjustments WHERE warehouse_id IS NULL;
    """)
    op.alter_column('stock_adjustments', 'warehouse_id', nullable=False)
    op.alter_column('stock_adjustments', 'adjustment_type', nullable=False)
    op.alter_column('stock_adjustments', 'total_items_adjusted', nullable=False, server_default='0')


def downgrade():
    # Drop new tables and columns
    op.drop_table('stock_adjustment_items')
    
    # Drop indexes
    op.drop_index('ix_stock_adjustments_adjustment_date', 'stock_adjustments')
    op.drop_index('ix_stock_adjustments_warehouse_id', 'stock_adjustments')
    
    # Restore old structure
    op.drop_column('stock_adjustments', 'reason')
    op.drop_column('stock_adjustments', 'adjustment_type')
    op.drop_column('stock_adjustments', 'warehouse_id')
    
    # Rename back
    op.alter_column('stock_adjustments', 'total_items_adjusted',
        new_column_name='quantity_adjusted',
        type_=sa.DECIMAL(precision=10, scale=3)
    )
    
    # Add back inventory_id
    op.add_column('stock_adjustments',
        sa.Column('inventory_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    
    # Restore foreign key
    op.create_foreign_key(
        'stock_adjustments_inventory_id_fkey',
        'stock_adjustments', 'inventory',
        ['inventory_id'], ['id']
    )
    
    # Drop enum
    op.execute("DROP TYPE IF EXISTS adjustmenttype;")
    
    # Restore backup if it exists
    op.execute("""
        INSERT INTO stock_adjustments 
        SELECT * FROM stock_adjustments_backup
        ON CONFLICT (id) DO NOTHING;
    """)
    
    # Drop backup table
    op.execute("DROP TABLE IF EXISTS stock_adjustments_backup;")
