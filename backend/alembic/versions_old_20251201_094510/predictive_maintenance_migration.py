"""Add predictive maintenance models

Revision ID: predictive_maintenance
Revises: 
Create Date: 2023-07-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'predictive_maintenance'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types
    op.execute("CREATE TYPE maintenance_risk_level AS ENUM ('low', 'medium', 'high', 'critical')")
    op.execute("CREATE TYPE maintenance_priority AS ENUM ('low', 'medium', 'high', 'urgent')")
    op.execute("CREATE TYPE maintenance_status AS ENUM ('pending', 'scheduled', 'in_progress', 'completed', 'cancelled')")
    
    # Create predictive_maintenance_models table
    op.create_table(
        'predictive_maintenance_models',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('model_type', sa.String(100), nullable=False),
        sa.Column('target_metric', sa.String(100), nullable=False),
        sa.Column('features', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('hyperparameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('performance_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('version', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False)
    )
    
    # Create machine_model_associations table
    op.create_table(
        'machine_model_associations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('predictive_model_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('predictive_maintenance_models.id'), nullable=False),
        sa.Column('machine_model_type', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('predictive_model_id', 'machine_model_type', name='_predictive_model_machine_model_uc')
    )
    
    # Create machine_predictions table
    op.create_table(
        'machine_predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('machines.id'), nullable=False),
        sa.Column('predictive_model_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('predictive_maintenance_models.id'), nullable=False),
        sa.Column('prediction_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('failure_probability', sa.Float(), nullable=True),
        sa.Column('remaining_useful_life', sa.Integer(), nullable=True),
        sa.Column('predicted_failure_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('risk_level', sa.Enum('low', 'medium', 'high', 'critical', name='maintenance_risk_level'), nullable=False),
        sa.Column('prediction_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    
    # Create maintenance_recommendations table
    op.create_table(
        'maintenance_recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('machines.id'), nullable=False),
        sa.Column('prediction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('machine_predictions.id'), nullable=False),
        sa.Column('recommendation_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('recommended_maintenance_type', sa.Enum('scheduled', 'unscheduled', 'repair', 'inspection', 'cleaning', 'calibration', 'other', name='maintenance_type'), nullable=False),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'urgent', name='maintenance_priority'), nullable=False),
        sa.Column('recommended_completion_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'scheduled', 'in_progress', 'completed', 'cancelled', name='maintenance_status'), nullable=False, server_default='pending'),
        sa.Column('resolved_by_maintenance_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('machine_maintenance.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    
    # Create recommended_parts table
    op.create_table(
        'recommended_parts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('recommendation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('maintenance_recommendations.id'), nullable=False),
        sa.Column('part_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('parts.id'), nullable=False),
        sa.Column('quantity', sa.DECIMAL(precision=10, scale=3), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    
    # Create maintenance_indicators table
    op.create_table(
        'maintenance_indicators',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('indicator_type', sa.String(100), nullable=False),
        sa.Column('unit_of_measure', sa.String(50), nullable=True),
        sa.Column('threshold_warning', sa.Float(), nullable=True),
        sa.Column('threshold_critical', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    
    # Create machine_indicator_values table
    op.create_table(
        'machine_indicator_values',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('machines.id'), nullable=False),
        sa.Column('indicator_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('maintenance_indicators.id'), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('recorded_by_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    
    # Create indexes
    op.create_index('ix_machine_predictions_machine_id', 'machine_predictions', ['machine_id'])
    op.create_index('ix_machine_predictions_risk_level', 'machine_predictions', ['risk_level'])
    op.create_index('ix_maintenance_recommendations_machine_id', 'maintenance_recommendations', ['machine_id'])
    op.create_index('ix_maintenance_recommendations_status', 'maintenance_recommendations', ['status'])
    op.create_index('ix_maintenance_recommendations_priority', 'maintenance_recommendations', ['priority'])
    op.create_index('ix_machine_indicator_values_machine_id', 'machine_indicator_values', ['machine_id'])
    op.create_index('ix_machine_indicator_values_indicator_id', 'machine_indicator_values', ['indicator_id'])


def downgrade():
    # Drop tables
    op.drop_table('machine_indicator_values')
    op.drop_table('maintenance_indicators')
    op.drop_table('recommended_parts')
    op.drop_table('maintenance_recommendations')
    op.drop_table('machine_predictions')
    op.drop_table('machine_model_associations')
    op.drop_table('predictive_maintenance_models')
    
    # Drop enum types
    op.execute("DROP TYPE maintenance_status")
    op.execute("DROP TYPE maintenance_priority")
    op.execute("DROP TYPE maintenance_risk_level")