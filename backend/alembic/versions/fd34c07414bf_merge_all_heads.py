"""merge_all_heads

Revision ID: fd34c07414bf
Revises: add_machine_columns, b102b96926f9
Create Date: 2025-07-25 14:29:11.200993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd34c07414bf'
down_revision: Union[str, Sequence[str], None] = ('add_machine_columns', 'b102b96926f9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
