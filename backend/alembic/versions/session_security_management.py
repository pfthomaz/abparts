"""Session and Security Management

Revision ID: 31e87319dc9b
Revises: 31e87319dc9a
Create Date: 2025-07-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '31e87319dc9b'
down_revision = '31e87319dc9a'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_sessions table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'user_sessions'):
        op.create_table('user_sessions',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('session_token', sa.String(255), unique=True, nullable=False, index=True),
            sa.Column('ip_address', sa.String(45), nullable=True),
            sa.Column('user_agent', sa.Text, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
            sa.Column('terminated_reason', sa.String(100), nullable=True)
        )
    
    # Create security_events table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'security_events'):
        op.create_table('security_events',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('event_type', sa.String(50), nullable=False),
            sa.Column('ip_address', sa.String(45), nullable=True),
            sa.Column('user_agent', sa.Text, nullable=True),
            sa.Column('session_id', sa.String(255), nullable=True),
            sa.Column('details', sa.Text, nullable=True),
            sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('risk_level', sa.String(20), nullable=False, server_default='low')
        )
        
        # Create index on event_type and timestamp for faster queries
        op.create_index('ix_security_events_event_type', 'security_events', ['event_type'])
        op.create_index('ix_security_events_timestamp', 'security_events', ['timestamp'])
        op.create_index('ix_security_events_risk_level', 'security_events', ['risk_level'])
    
    # Add session-related columns to users table if they don't exist
    with op.batch_alter_table('users') as batch_op:
        # Check if columns exist before adding them
        columns = [c['name'] for c in sa.inspect(op.get_bind()).get_columns('users')]
        
        if 'failed_login_attempts' not in columns:
            batch_op.add_column(sa.Column('failed_login_attempts', sa.Integer, nullable=False, server_default='0'))
        
        if 'locked_until' not in columns:
            batch_op.add_column(sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))
        
        if 'last_login' not in columns:
            batch_op.add_column(sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    # Drop tables in reverse order
    op.drop_table('security_events')
    op.drop_table('user_sessions')
    
    # Remove columns from users table
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('failed_login_attempts')
        batch_op.drop_column('locked_until')
        batch_op.drop_column('last_login')