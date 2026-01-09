"""add preferred_language to users

Revision ID: 04_add_preferred_language
Revises: 03_add_maintenance_protocols
Create Date: 2025-12-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04_add_preferred_language'
down_revision = '03_add_maintenance_protocols'
branch_labels = None
depends_on = None


def upgrade():
    # Add preferred_language column to users table if it doesn't exist
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'preferred_language' not in columns:
        op.add_column('users', sa.Column('preferred_language', sa.String(length=5), nullable=True, server_default='en'))
        print("✅ Added preferred_language column to users table")
    else:
        print("ℹ️  preferred_language column already exists, skipping")


def downgrade():
    # Remove preferred_language column from users table
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'preferred_language' in columns:
        op.drop_column('users', 'preferred_language')
        print("✅ Removed preferred_language column from users table")
    else:
        print("ℹ️  preferred_language column doesn't exist, skipping")
