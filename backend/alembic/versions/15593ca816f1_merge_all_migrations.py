"""merge_all_migrations

Revision ID: 15593ca816f1
Revises: 20251117_shipped_date, add_parts_perf_idx
Create Date: 2025-11-19 12:50:29.769981

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15593ca816f1'
down_revision: Union[str, Sequence[str], None] = ('20251117_shipped_date', 'add_parts_perf_idx')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
