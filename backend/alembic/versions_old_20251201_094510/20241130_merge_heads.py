"""merge migration heads

Revision ID: 20241130_merge_heads
Revises: 20241130_redesign_stock_adjustments, 5a156a1f6ce7
Create Date: 2024-11-30 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20241130_merge'  # Max 32 chars
down_revision = ('20241130_stock_adj', '5a156a1f6ce7')
branch_labels = None
depends_on = None


def upgrade():
    # This is a merge migration, no changes needed
    pass


def downgrade():
    # This is a merge migration, no changes needed
    pass
