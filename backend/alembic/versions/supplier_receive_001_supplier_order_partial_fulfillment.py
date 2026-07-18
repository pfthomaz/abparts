"""add partial receipt/write-off tracking to supplier orders

Adds quantity_received/quantity_written_off to supplier_order_items, and
supplier_order_id/supplier_order_item_id FKs on transactions, mirroring the
customer-order partial-shipment work so Oraseas EE can receive (and write
off) a supplier order in multiple partial batches instead of all-at-once.

Backfills existing rows so already-delivered orders don't appear as newly
"partially" received.

Branches off writeoff_001 (not drop_part_order_001, which production has
deliberately deferred) since this is unrelated - deploy by targeting it
explicitly (`alembic upgrade supplier_receive_001`) rather than `head`.

Revision ID: supplier_receive_001
Revises: writeoff_001
Create Date: 2026-07-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'supplier_receive_001'
down_revision = 'writeoff_001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'supplier_order_items',
        sa.Column('quantity_received', sa.DECIMAL(precision=10, scale=3), nullable=False, server_default='0')
    )
    op.add_column(
        'supplier_order_items',
        sa.Column('quantity_written_off', sa.DECIMAL(precision=10, scale=3), nullable=False, server_default='0')
    )
    op.add_column(
        'transactions',
        sa.Column('supplier_order_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('supplier_orders.id'), nullable=True)
    )
    op.add_column(
        'transactions',
        sa.Column('supplier_order_item_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('supplier_order_items.id'), nullable=True)
    )
    op.create_index(
        'ix_transactions_supplier_order_item_id',
        'transactions', ['supplier_order_item_id']
    )

    # Backfill: orders already delivered under the old one-shot fulfillment
    # flow should not look "partially received" just because the new
    # columns default to 0.
    op.execute("""
        UPDATE supplier_order_items AS soi
        SET quantity_received = soi.quantity
        FROM supplier_orders AS so
        WHERE so.id = soi.supplier_order_id
          AND so.status IN ('Delivered', 'Received')
    """)


def downgrade():
    op.drop_index('ix_transactions_supplier_order_item_id', table_name='transactions')
    op.drop_column('transactions', 'supplier_order_item_id')
    op.drop_column('transactions', 'supplier_order_id')
    op.drop_column('supplier_order_items', 'quantity_written_off')
    op.drop_column('supplier_order_items', 'quantity_received')
