"""merge_all_heads_before_hybrid_storage

Revision ID: 5a156a1f6ce7
Revises: a1ca172ca9cc, 20251129_hybrid_storage
Create Date: 2025-11-29 17:47:11.230341

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a156a1f6ce7'
down_revision: Union[str, Sequence[str], None] = ('a1ca172ca9cc', '20251129_hybrid_storage')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
