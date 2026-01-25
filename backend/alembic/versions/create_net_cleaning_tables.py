"""add_net_cleaning_tables

Revision ID: net_cleaning_001
Revises: ab2c1f16b0b3
Create Date: 2026-01-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'net_cleaning_001'
down_revision = 'ab2c1f16b0b3'
branch_labels = None
depends_on = None


def upgrade():
    # Create farm_sites table
    op.create_table(
        'farm_sites',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('location', sa.String(500), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create indexes for farm_sites
    op.create_index('ix_farm_sites_organization_id', 'farm_sites', ['organization_id'])
    op.create_index('ix_farm_sites_active', 'farm_sites', ['active'])

    # Create nets table
    op.create_table(
        'nets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('farm_site_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('farm_sites.id'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('diameter', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('vertical_depth', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('cone_depth', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('mesh_size', sa.String(50), nullable=True),
        sa.Column('material', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create indexes for nets
    op.create_index('ix_nets_farm_site_id', 'nets', ['farm_site_id'])
    op.create_index('ix_nets_active', 'nets', ['active'])

    # Create net_cleaning_records table
    op.create_table(
        'net_cleaning_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('net_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('nets.id'), nullable=False),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('machines.id'), nullable=True),
        sa.Column('operator_name', sa.String(200), nullable=False),
        sa.Column('cleaning_mode', sa.Integer, nullable=False),
        sa.Column('depth_1', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('depth_2', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('depth_3', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Integer, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create indexes for net_cleaning_records
    op.create_index('ix_net_cleaning_records_net_id', 'net_cleaning_records', ['net_id'])
    op.create_index('ix_net_cleaning_records_machine_id', 'net_cleaning_records', ['machine_id'])
    op.create_index('ix_net_cleaning_records_start_time', 'net_cleaning_records', ['start_time'])
    op.create_index('ix_net_cleaning_records_created_by', 'net_cleaning_records', ['created_by'])
    
    # Add check constraint for cleaning_mode
    op.create_check_constraint(
        'ck_cleaning_mode_valid',
        'net_cleaning_records',
        'cleaning_mode IN (1, 2, 3)'
    )
    
    # Add check constraint for end_time > start_time
    op.create_check_constraint(
        'ck_end_time_after_start_time',
        'net_cleaning_records',
        'end_time > start_time'
    )


def downgrade():
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('net_cleaning_records')
    op.drop_table('nets')
    op.drop_table('farm_sites')
