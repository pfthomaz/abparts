"""add customer_order_id to transactions

Revision ID: 20251124_order_txn
Revises: fd34c07414bf
Create Date: 2025-11-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251124_order_txn'
down_revision = 'fd34c07414bf'
branch_labels = None
depends_on = None


def upgrade():
    # Add customer_order_id column to transactions table
    op.add_column('transactions', 
        sa.Column('customer_order_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_transactions_customer_order_id',
        'transactions', 'customer_orders',
        ['customer_order_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Add index for better query performance
    op.create_index(
        'ix_transactions_customer_order_id',
        'transactions',
        ['customer_order_id']
    )


def downgrade():
    # Remove index
    op.drop_index('ix_transactions_customer_order_id', table_name='transactions')
    
    # Remove foreign key
    op.drop_constraint('fk_transactions_customer_order_id', 'transactions', type_='foreignkey')
    
    # Remove column
    op.drop_column('transactions', 'customer_order_id')
