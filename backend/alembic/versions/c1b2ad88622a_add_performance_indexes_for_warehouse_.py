"""Add performance indexes for warehouse analytics

Revision ID: c1b2ad88622a
Revises: af15f8128cf7
Create Date: 2025-07-28 14:45:42.722124

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1b2ad88622a'
down_revision: Union[str, Sequence[str], None] = 'af15f8128cf7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for warehouse analytics queries."""
    
    # Helper function to create index if it doesn't exist
    def create_index_if_not_exists(index_name, table_name, columns):
        connection = op.get_bind()
        result = connection.execute(sa.text(f"""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = '{table_name}' AND indexname = '{index_name}'
        """))
        if not result.fetchone():
            op.create_index(index_name, table_name, columns)
    
    # Inventory table indexes for analytics queries
    create_index_if_not_exists('idx_inventory_warehouse_id', 'inventory', ['warehouse_id'])
    create_index_if_not_exists('idx_inventory_part_id', 'inventory', ['part_id'])
    create_index_if_not_exists('idx_inventory_warehouse_part', 'inventory', ['warehouse_id', 'part_id'])
    create_index_if_not_exists('idx_inventory_current_stock', 'inventory', ['current_stock'])
    create_index_if_not_exists('idx_inventory_last_updated', 'inventory', ['last_updated'])
    
    # Transaction table indexes for analytics queries
    create_index_if_not_exists('idx_transactions_warehouse_from', 'transactions', ['from_warehouse_id'])
    create_index_if_not_exists('idx_transactions_warehouse_to', 'transactions', ['to_warehouse_id'])
    create_index_if_not_exists('idx_transactions_part_id', 'transactions', ['part_id'])
    create_index_if_not_exists('idx_transactions_date', 'transactions', ['transaction_date'])
    create_index_if_not_exists('idx_transactions_type', 'transactions', ['transaction_type'])
    create_index_if_not_exists('idx_transactions_warehouse_date', 'transactions', ['from_warehouse_id', 'transaction_date'])
    create_index_if_not_exists('idx_transactions_warehouse_to_date', 'transactions', ['to_warehouse_id', 'transaction_date'])
    
    # Warehouse table indexes
    create_index_if_not_exists('idx_warehouses_organization_id', 'warehouses', ['organization_id'])
    create_index_if_not_exists('idx_warehouses_is_active', 'warehouses', ['is_active'])
    
    # Parts table indexes for joins
    create_index_if_not_exists('idx_parts_part_number', 'parts', ['part_number'])
    
    # Supplier order items for pricing data
    create_index_if_not_exists('idx_supplier_order_items_part_id', 'supplier_order_items', ['part_id'])
    create_index_if_not_exists('idx_supplier_order_items_unit_price', 'supplier_order_items', ['unit_price'])
    
    # Supplier orders for date filtering
    create_index_if_not_exists('idx_supplier_orders_order_date', 'supplier_orders', ['order_date'])


def downgrade() -> None:
    """Remove performance indexes for warehouse analytics queries."""
    
    # Drop inventory indexes
    op.drop_index('idx_inventory_warehouse_id', 'inventory')
    op.drop_index('idx_inventory_part_id', 'inventory')
    op.drop_index('idx_inventory_warehouse_part', 'inventory')
    op.drop_index('idx_inventory_current_stock', 'inventory')
    op.drop_index('idx_inventory_last_updated', 'inventory')
    
    # Drop transaction indexes
    op.drop_index('idx_transactions_warehouse_from', 'transactions')
    op.drop_index('idx_transactions_warehouse_to', 'transactions')
    op.drop_index('idx_transactions_part_id', 'transactions')
    op.drop_index('idx_transactions_date', 'transactions')
    op.drop_index('idx_transactions_type', 'transactions')
    op.drop_index('idx_transactions_warehouse_date', 'transactions')
    op.drop_index('idx_transactions_warehouse_to_date', 'transactions')
    
    # Drop warehouse indexes
    op.drop_index('idx_warehouses_organization_id', 'warehouses')
    op.drop_index('idx_warehouses_is_active', 'warehouses')
    
    # Drop parts indexes
    op.drop_index('idx_parts_part_number', 'parts')
    
    # Drop supplier order items indexes
    op.drop_index('idx_supplier_order_items_part_id', 'supplier_order_items')
    op.drop_index('idx_supplier_order_items_unit_price', 'supplier_order_items')
    
    # Drop supplier orders indexes
    op.drop_index('idx_supplier_orders_order_date', 'supplier_orders')
