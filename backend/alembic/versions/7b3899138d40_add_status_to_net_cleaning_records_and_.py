"""add_status_to_net_cleaning_records_and_make_end_time_nullable

Revision ID: 7b3899138d40
Revises: net_cleaning_001
Create Date: 2026-01-25 11:06:37.845015

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b3899138d40'
down_revision: Union[str, Sequence[str], None] = 'net_cleaning_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add status column with default value 'completed'
    op.add_column('net_cleaning_records', 
        sa.Column('status', sa.String(20), nullable=False, server_default='completed'))
    
    # Make end_time nullable
    op.alter_column('net_cleaning_records', 'end_time',
                    existing_type=sa.DateTime(timezone=True),
                    nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove status column
    op.drop_column('net_cleaning_records', 'status')
    
    # Make end_time non-nullable again
    op.alter_column('net_cleaning_records', 'end_time',
                    existing_type=sa.DateTime(timezone=True),
                    nullable=False)
