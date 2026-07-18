"""add quantity_written_off tracking to customer order items

Lets Oraseas EE declare a shipped-but-never-received quantity as lost/damaged
in transit, closing the tracking gap without requiring an eventual receipt
confirmation for it.

Branches directly off partial_ship_001 (not drop_part_order_001) since
production has deliberately deferred that table-drop migration indefinitely
and this feature is unrelated to it. The two are independent and can be
applied in either order; on a host that hasn't run drop_part_order_001 yet,
deploy this by targeting it explicitly (`alembic upgrade writeoff_001`)
rather than `alembic upgrade head`.

Revision ID: writeoff_001
Revises: partial_ship_001
Create Date: 2026-07-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'writeoff_001'
down_revision = 'partial_ship_001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'customer_order_items',
        sa.Column('quantity_written_off', sa.DECIMAL(precision=10, scale=3), nullable=False, server_default='0')
    )


def downgrade():
    op.drop_column('customer_order_items', 'quantity_written_off')
