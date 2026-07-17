"""add partial shipment/receipt tracking to customer orders

Adds quantity_shipped/quantity_received to customer_order_items and a
customer_order_item_id FK on transactions, so a customer order can be
shipped and received in multiple partial batches instead of all-at-once.

Backfills existing rows so already-shipped/received orders don't appear
as newly "partially" fulfilled.

Revision ID: partial_ship_001
Revises: net_cleaning_001, warehouse_loc_001
Create Date: 2026-07-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'partial_ship_001'
down_revision = ('net_cleaning_001', 'warehouse_loc_001')
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'customer_order_items',
        sa.Column('quantity_shipped', sa.DECIMAL(precision=10, scale=3), nullable=False, server_default='0')
    )
    op.add_column(
        'customer_order_items',
        sa.Column('quantity_received', sa.DECIMAL(precision=10, scale=3), nullable=False, server_default='0')
    )
    op.add_column(
        'transactions',
        sa.Column('customer_order_item_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('customer_order_items.id'), nullable=True)
    )
    op.create_index(
        'ix_transactions_customer_order_item_id',
        'transactions', ['customer_order_item_id']
    )

    # Backfill: orders that already progressed past a given stage should not
    # look "partially" fulfilled just because the new columns default to 0.
    op.execute("""
        UPDATE customer_order_items AS coi
        SET quantity_shipped = coi.quantity
        FROM customer_orders AS co
        WHERE co.id = coi.customer_order_id
          AND co.status IN ('Shipped', 'Received', 'Delivered')
    """)
    op.execute("""
        UPDATE customer_order_items AS coi
        SET quantity_received = coi.quantity
        FROM customer_orders AS co
        WHERE co.id = coi.customer_order_id
          AND co.status IN ('Received', 'Delivered')
    """)


def downgrade():
    op.drop_index('ix_transactions_customer_order_item_id', table_name='transactions')
    op.drop_column('transactions', 'customer_order_item_id')
    op.drop_column('customer_order_items', 'quantity_received')
    op.drop_column('customer_order_items', 'quantity_shipped')
