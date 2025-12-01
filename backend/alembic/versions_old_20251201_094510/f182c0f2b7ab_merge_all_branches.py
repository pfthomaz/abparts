"""merge_all_branches

Revision ID: f182c0f2b7ab
Revises: 15593ca816f1, 20251124_order_txn
Create Date: 2025-11-29 14:53:31.432520

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f182c0f2b7ab'
down_revision: Union[str, Sequence[str], None] = ('15593ca816f1', '20251124_order_txn')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
