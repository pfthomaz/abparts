"""fix adjustment type enum

Revision ID: 20241130_fix_enum
Revises: 20241130_redesign_stock_adjustments
Create Date: 2024-11-30

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20241130_fix_enum'
down_revision = '20241130_stock_adj'
branch_labels = None
depends_on = None


def upgrade():
    # Drop and recreate the enum type with correct values
    op.execute("DROP TYPE IF EXISTS adjustmenttype CASCADE")
    op.execute("""
        CREATE TYPE adjustmenttype AS ENUM (
            'stock_take',
            'damage',
            'loss',
            'found',
            'correction',
            'return',
            'other'
        )
    """)
    
    # Recreate the column with the new enum
    op.execute("""
        ALTER TABLE stock_adjustments 
        ALTER COLUMN adjustment_type TYPE adjustmenttype 
        USING adjustment_type::text::adjustmenttype
    """)


def downgrade():
    # Recreate old enum
    op.execute("DROP TYPE IF EXISTS adjustmenttype CASCADE")
    op.execute("""
        CREATE TYPE adjustmenttype AS ENUM (
            'manual',
            'correction',
            'damage',
            'loss',
            'found',
            'other'
        )
    """)
    
    # Recreate the column with the old enum
    op.execute("""
        ALTER TABLE stock_adjustments 
        ALTER COLUMN adjustment_type TYPE adjustmenttype 
        USING adjustment_type::text::adjustmenttype
    """)
