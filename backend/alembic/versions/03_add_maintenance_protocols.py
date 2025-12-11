"""add maintenance protocols and service management

Revision ID: 03_add_maintenance_protocols
Revises: 01_add_updated_at
Create Date: 2025-12-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '03_add_maintenance_protocols'
down_revision = '01_add_updated_at'
branch_labels = None
depends_on = None


def upgrade():
    # Create maintenance_protocols table
    op.create_table(
        'maintenance_protocols',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('protocol_type', sa.String(50), nullable=False),  # 'daily', 'weekly', 'scheduled'
        sa.Column('service_interval_hours', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_recurring', sa.Boolean, default=False),  # True for recurring services, False for one-time
        sa.Column('machine_model', sa.String(50), nullable=True),  # 'V3.1B', 'V4.0', NULL for all models
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('display_order', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create protocol_checklist_items table
    op.create_table(
        'protocol_checklist_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('protocol_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_order', sa.Integer, nullable=False),
        sa.Column('item_description', sa.Text, nullable=False),
        sa.Column('item_type', sa.String(50), nullable=False),  # 'check', 'service', 'replacement'
        sa.Column('item_category', sa.String(100), nullable=True),
        sa.Column('part_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('estimated_quantity', sa.Numeric(10, 3), nullable=True),
        sa.Column('is_critical', sa.Boolean, default=False),
        sa.Column('estimated_duration_minutes', sa.Integer, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['protocol_id'], ['maintenance_protocols.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ondelete='SET NULL')
    )
    
    # Create maintenance_executions table
    op.create_table(
        'maintenance_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('protocol_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('performed_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('performed_date', sa.DateTime, nullable=True),  # Nullable to allow in-progress executions
        sa.Column('machine_hours_at_service', sa.Numeric(10, 2), nullable=True),  # Nullable to allow in-progress executions
        sa.Column('next_service_due_hours', sa.Numeric(10, 2), nullable=True),
        sa.Column('status', sa.String(50), default='in_progress'),  # 'scheduled', 'in_progress', 'completed', 'partial', 'skipped'
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['protocol_id'], ['maintenance_protocols.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['performed_by_user_id'], ['users.id'], ondelete='RESTRICT')
    )
    
    # Create maintenance_checklist_completions table
    op.create_table(
        'maintenance_checklist_completions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('execution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('checklist_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_completed', sa.Boolean, default=False),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('part_usage_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['execution_id'], ['maintenance_executions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['checklist_item_id'], ['protocol_checklist_items.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['part_usage_id'], ['part_usage.id'], ondelete='SET NULL')
    )
    
    # Create maintenance_reminders table
    op.create_table(
        'maintenance_reminders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('protocol_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reminder_type', sa.String(50), nullable=False),
        sa.Column('due_date', sa.Date, nullable=True),
        sa.Column('due_hours', sa.Numeric(10, 2), nullable=True),
        sa.Column('status', sa.String(50), default='pending'),  # 'pending', 'acknowledged', 'completed', 'dismissed'
        sa.Column('acknowledged_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['protocol_id'], ['maintenance_protocols.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['acknowledged_by_user_id'], ['users.id'], ondelete='SET NULL')
    )
    
    # Create indexes for performance
    op.create_index('idx_protocol_type_model', 'maintenance_protocols', ['protocol_type', 'machine_model'])
    op.create_index('idx_checklist_protocol', 'protocol_checklist_items', ['protocol_id', 'item_order'])
    op.create_index('idx_execution_machine', 'maintenance_executions', ['machine_id', 'performed_date'])
    op.create_index('idx_reminder_machine_status', 'maintenance_reminders', ['machine_id', 'status'])
    op.create_index('idx_reminder_due_hours', 'maintenance_reminders', ['due_hours', 'status'])
    
    # Update existing machine_maintenance table to link with new system
    op.add_column('machine_maintenance', sa.Column('execution_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_machine_maintenance_execution', 'machine_maintenance', 'maintenance_executions', ['execution_id'], ['id'], ondelete='SET NULL')
    
    # Add machine_model to machines table if not exists
    # Check if column exists first
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('machines')]
    
    if 'machine_model' not in columns:
        op.add_column('machines', sa.Column('machine_model', sa.String(50), nullable=True))


def downgrade():
    # Remove foreign key from machine_maintenance table
    op.drop_constraint('fk_machine_maintenance_execution', 'machine_maintenance', type_='foreignkey')
    op.drop_column('machine_maintenance', 'execution_id')
    
    # Drop indexes
    op.drop_index('idx_reminder_due_hours', 'maintenance_reminders')
    op.drop_index('idx_reminder_machine_status', 'maintenance_reminders')
    op.drop_index('idx_execution_machine', 'maintenance_executions')
    op.drop_index('idx_checklist_protocol', 'protocol_checklist_items')
    op.drop_index('idx_protocol_type_model', 'maintenance_protocols')
    
    # Drop tables in reverse order
    op.drop_table('maintenance_reminders')
    op.drop_table('maintenance_checklist_completions')
    op.drop_table('maintenance_executions')
    op.drop_table('protocol_checklist_items')
    op.drop_table('maintenance_protocols')
    
    # Optionally remove machine_model from machines (commented out to preserve data)
    # op.drop_column('machines', 'machine_model')
