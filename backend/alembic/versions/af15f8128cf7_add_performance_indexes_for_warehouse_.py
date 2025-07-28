"""Add performance indexes for warehouse analytics

Revision ID: af15f8128cf7
Revises: fix_part_usage_schema
Create Date: 2025-07-28 14:42:41.081626

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af15f8128cf7'
down_revision: Union[str, Sequence[str], None] = 'fix_part_usage_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for warehouse analytics queries."""
    
    connection = op.get_bind()
    
    # Helper function to check if index exists
    def index_exists(index_name, table_name):
        result = connection.execute(sa.text("""
            SELECT 1 FROM pg_indexes 
            WHERE indexname = :index_name AND tablename = :table_name
        """), {"index_name": index_name, "table_name": table_name})
        return result.fetchone() is not None
    
    # Index for inventory queries by warehouse_id (most common filter)
    if not index_exists('idx_inventory_warehouse_id', 'inventory'):
        op.create_index('idx_inventory_warehouse_id', 'inventory', ['warehouse_id'])
    
    # Index for inventory queries by part_id
    if not index_exists('idx_inventory_part_id', 'inventory'):
        op.create_index('idx_inventory_part_id', 'inventory', ['part_id'])
    
    # Composite index for inventory queries by warehouse and part (for joins) - already exists
    # if not index_exists('idx_inventory_warehouse_part', 'inventory'):
    #     op.create_index('idx_inventory_warehouse_part', 'inventory', ['warehouse_id', 'part_id'])
    
    # Index for transactions by warehouse (from_warehouse_id)
    if not index_exists('idx_transactions_from_warehouse', 'transactions'):
        op.create_index('idx_transactions_from_warehouse', 'transactions', ['from_warehouse_id'])
    
    # Index for transactions by warehouse (to_warehouse_id)
    if not index_exists('idx_transactions_to_warehouse', 'transactions'):
        op.create_index('idx_transactions_to_warehouse', 'transactions', ['to_warehouse_id'])
    
    # Index for transactions by date (for time-based analytics) - already exists as idx_transactions_date
    # if not index_exists('idx_transactions_date', 'transactions'):
    #     op.create_index('idx_transactions_date', 'transactions', ['transaction_date'])
    
    # Composite index for transactions by warehouse and date (most common analytics query)
    if not index_exists('idx_transactions_from_warehouse_date', 'transactions'):
        op.create_index('idx_transactions_from_warehouse_date', 'transactions', ['from_warehouse_id', 'transaction_date'])
    
    if not index_exists('idx_transactions_to_warehouse_date', 'transactions'):
        op.create_index('idx_transactions_to_warehouse_date', 'transactions', ['to_warehouse_id', 'transaction_date'])
    
    # Index for transactions by part_id (for part-specific analytics) - already exists as idx_transactions_part
    # if not index_exists('idx_transactions_part_id', 'transactions'):
    #     op.create_index('idx_transactions_part_id', 'transactions', ['part_id'])
    
    # Index for supplier order items by part_id (for pricing lookups)
    if not index_exists('idx_supplier_order_items_part_id', 'supplier_order_items'):
        op.create_index('idx_supplier_order_items_part_id', 'supplier_order_items', ['part_id'])
    
    # Index for supplier orders by order_date (for recent pricing)
    if not index_exists('idx_supplier_orders_date', 'supplier_orders'):
        op.create_index('idx_supplier_orders_date', 'supplier_orders', ['order_date'])
    
    # Composite index for supplier order items with order date (for pricing analytics)
    if not index_exists('idx_supplier_order_items_part_date', 'supplier_order_items'):
        op.create_index('idx_supplier_order_items_part_date', 'supplier_order_items', ['part_id', 'supplier_order_id'])
    
    # Index for warehouses by organization_id (for organization-scoped queries)
    if not index_exists('idx_warehouses_organization_id', 'warehouses'):
        op.create_index('idx_warehouses_organization_id', 'warehouses', ['organization_id'])
    
    # Index for warehouses by is_active status
    if not index_exists('idx_warehouses_is_active', 'warehouses'):
        op.create_index('idx_warehouses_is_active', 'warehouses', ['is_active'])


def downgrade() -> None:
    """Remove performance indexes for warehouse analytics queries."""
    
    # Drop all the indexes we created
    op.drop_index('idx_inventory_warehouse_id', 'inventory')
    op.drop_index('idx_inventory_part_id', 'inventory')
    op.drop_index('idx_inventory_warehouse_part', 'inventory')
    op.drop_index('idx_transactions_from_warehouse', 'transactions')
    op.drop_index('idx_transactions_to_warehouse', 'transactions')
    op.drop_index('idx_transactions_date', 'transactions')
    op.drop_index('idx_transactions_from_warehouse_date', 'transactions')
    op.drop_index('idx_transactions_to_warehouse_date', 'transactions')
    op.drop_index('idx_transactions_part_id', 'transactions')
    op.drop_index('idx_supplier_order_items_part_id', 'supplier_order_items')
    op.drop_index('idx_supplier_orders_date', 'supplier_orders')
    op.drop_index('idx_supplier_order_items_part_date', 'supplier_order_items')
    op.drop_index('idx_warehouses_organization_id', 'warehouses')
    op.drop_index('idx_warehouses_is_active', 'warehouses')
