"""baseline schema

Revision ID: 00_baseline
Revises: 
Create Date: 2024-12-01

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '00_baseline'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Schema is already in place from production
    # This migration just marks the baseline
    pass


def downgrade():
    # Cannot downgrade from baseline
    raise Exception("Cannot downgrade from baseline migration")
