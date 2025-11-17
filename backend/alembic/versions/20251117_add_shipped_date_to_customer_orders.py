"""add_shipped_date_to_customer_orders

Revision ID: 20251117_shipped_date
Revises: fd34c07414bf
Create Date: 2025-11-17 18:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251117_shipped_date'
down_revision = 'fd34c07414bf'
branch_labels = None
depends_on = None


def upgrade():
    """Add shipped_date column to customer_orders table."""
    op.add_column('customer_orders', 
        sa.Column('shipped_date', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    """Remove shipped_date column from customer_orders table."""
    op.drop_column('customer_orders', 'shipped_date')
