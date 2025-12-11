"""add_user_management_audit_log

Revision ID: add_user_mgmt_audit
Revises: add_user_profile_fields
Create Date: 2025-07-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_user_mgmt_audit'
down_revision: Union[str, Sequence[str], None] = 'add_user_profile_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user management audit log table."""
    
    # Create user_management_audit_logs table
    op.create_table('user_management_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('performed_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['performed_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_user_mgmt_audit_user_id', 'user_management_audit_logs', ['user_id'], unique=False)
    op.create_index('ix_user_mgmt_audit_timestamp', 'user_management_audit_logs', ['timestamp'], unique=False)
    op.create_index('ix_user_mgmt_audit_action', 'user_management_audit_logs', ['action'], unique=False)


def downgrade() -> None:
    """Remove user management audit log table."""
    
    # Drop indexes
    op.drop_index('ix_user_mgmt_audit_action', table_name='user_management_audit_logs')
    op.drop_index('ix_user_mgmt_audit_timestamp', table_name='user_management_audit_logs')
    op.drop_index('ix_user_mgmt_audit_user_id', table_name='user_management_audit_logs')
    
    # Drop table
    op.drop_table('user_management_audit_logs')