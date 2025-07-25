"""merge_migration_heads

Revision ID: b102b96926f9
Revises: inventory_workflow_001, add_security_session, predictive_maintenance, 31e87319dc9b
Create Date: 2025-07-25 14:03:43.752392

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b102b96926f9'
down_revision: Union[str, Sequence[str], None] = ('inventory_workflow_001', 'add_security_session', 'predictive_maintenance', '31e87319dc9b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
