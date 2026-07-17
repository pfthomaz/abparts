"""drop unused part_order_requests / part_order_items tables

The PartOrderRequest/PartOrderItem model, its dedicated /part-orders router,
and the /transactions/part-order(s) endpoints were never called by the
frontend (confirmed via a full grep of frontend/src) and are being removed
as dead code. This drops their backing tables.

Revision ID: drop_part_order_001
Revises: partial_ship_001
Create Date: 2026-07-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'drop_part_order_001'
down_revision = 'partial_ship_001'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('part_order_items')
    op.drop_table('part_order_requests')


def downgrade():
    op.create_table(
        'part_order_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_number', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('customer_organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('supplier_type', sa.Enum('ORASEAS_EE', 'EXTERNAL_SUPPLIER', name='supplier_type'), nullable=False),
        sa.Column('supplier_organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=True),
        sa.Column('supplier_name', sa.String(255), nullable=True),
        sa.Column('status', sa.Enum('REQUESTED', 'APPROVED', 'ORDERED', 'SHIPPED', 'RECEIVED', 'CANCELLED', name='order_status'), nullable=False),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='order_priority'), nullable=False),
        sa.Column('requested_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expected_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('fulfillment_notes', sa.Text, nullable=True),
        sa.Column('requested_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('approved_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('received_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_table(
        'part_order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_request_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('part_order_requests.id'), nullable=False),
        sa.Column('part_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('parts.id'), nullable=False),
        sa.Column('quantity', sa.DECIMAL(precision=10, scale=3), nullable=False),
        sa.Column('unit_price', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('destination_warehouse_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('warehouses.id'), nullable=False),
        sa.Column('received_quantity', sa.DECIMAL(precision=10, scale=3), nullable=True, server_default='0'),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
