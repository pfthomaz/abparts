"""add_user_profile_fields

Revision ID: add_user_profile_fields
Revises: 31e87319dc9a
Create Date: 2025-07-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_user_profile_fields'
down_revision: Union[str, Sequence[str], None] = '31e87319dc9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user profile management fields."""
    
    # Add email verification fields
    op.add_column('users', sa.Column('email_verification_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('email_verification_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('pending_email', sa.String(length=255), nullable=True))
    
    # Add invited_by_user_id foreign key constraint that was missing
    op.add_column('users', sa.Column('invited_by_user_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_users_invited_by_user_id', 'users', 'users', ['invited_by_user_id'], ['id'])
    
    # Create invitation_audit_logs table
    op.create_table('invitation_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('performed_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['performed_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Remove user profile management fields."""
    
    # Drop invitation_audit_logs table
    op.drop_table('invitation_audit_logs')
    
    # Remove foreign key constraint
    op.drop_constraint('fk_users_invited_by_user_id', 'users', type_='foreignkey')
    
    # Remove columns
    op.drop_column('users', 'invited_by_user_id')
    op.drop_column('users', 'pending_email')
    op.drop_column('users', 'email_verification_expires_at')
    op.drop_column('users', 'email_verification_token')