"""add_security_session_tables

Revision ID: add_security_session
Revises: add_user_mgmt_audit
Create Date: 2025-07-16 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_security_session'
down_revision: Union[str, Sequence[str], None] = 'add_user_mgmt_audit'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add security events and user sessions tables."""
    
    # Create security_events table
    op.create_table('security_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('risk_level', sa.String(length=20), nullable=False, server_default='low'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_sessions table
    op.create_table('user_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('terminated_reason', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_token')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_security_events_user_id', 'security_events', ['user_id'], unique=False)
    op.create_index('ix_security_events_timestamp', 'security_events', ['timestamp'], unique=False)
    op.create_index('ix_security_events_event_type', 'security_events', ['event_type'], unique=False)
    op.create_index('ix_security_events_risk_level', 'security_events', ['risk_level'], unique=False)
    
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'], unique=False)
    op.create_index('ix_user_sessions_session_token', 'user_sessions', ['session_token'], unique=False)
    op.create_index('ix_user_sessions_expires_at', 'user_sessions', ['expires_at'], unique=False)
    op.create_index('ix_user_sessions_is_active', 'user_sessions', ['is_active'], unique=False)


def downgrade() -> None:
    """Remove security events and user sessions tables."""
    
    # Drop indexes
    op.drop_index('ix_user_sessions_is_active', table_name='user_sessions')
    op.drop_index('ix_user_sessions_expires_at', table_name='user_sessions')
    op.drop_index('ix_user_sessions_session_token', table_name='user_sessions')
    op.drop_index('ix_user_sessions_user_id', table_name='user_sessions')
    
    op.drop_index('ix_security_events_risk_level', table_name='security_events')
    op.drop_index('ix_security_events_event_type', table_name='security_events')
    op.drop_index('ix_security_events_timestamp', table_name='security_events')
    op.drop_index('ix_security_events_user_id', table_name='security_events')
    
    # Drop tables
    op.drop_table('user_sessions')
    op.drop_table('security_events')