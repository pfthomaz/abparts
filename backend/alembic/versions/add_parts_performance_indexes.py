"""add_parts_performance_indexes

Revision ID: add_parts_perf_idx
Revises: fd34c07414bf
Create Date: 2025-01-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_parts_perf_idx'
down_revision: Union[str, Sequence[str], None] = '3bef488d9675'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for parts table."""
    
    # Create composite index on (part_type, is_proprietary) for efficient filtering
    op.create_index(
        'idx_parts_type_proprietary',
        'parts',
        ['part_type', 'is_proprietary'],
        unique=False
    )
    
    # Add index on manufacturer field for manufacturer-based queries
    op.create_index(
        'idx_parts_manufacturer',
        'parts',
        ['manufacturer'],
        unique=False,
        postgresql_where=sa.text('manufacturer IS NOT NULL')
    )
    
    # Implement full-text search index on name field for multilingual search
    op.execute(
        "CREATE INDEX idx_parts_name_fulltext ON parts USING gin(to_tsvector('english', name))"
    )


def downgrade() -> None:
    """Remove performance indexes for parts table."""
    
    # Drop the indexes in reverse order
    op.execute("DROP INDEX IF EXISTS idx_parts_name_fulltext")
    op.drop_index('idx_parts_manufacturer', table_name='parts')
    op.drop_index('idx_parts_type_proprietary', table_name='parts')