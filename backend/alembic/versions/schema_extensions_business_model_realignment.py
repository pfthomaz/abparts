"""schema_extensions_business_model_realignment

Revision ID: schema_extensions_001
Revises: c1b2ad88622a
Create Date: 2025-07-30 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'schema_extensions_001'
down_revision: Union[str, Sequence[str], None] = 'c1b2ad88622a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply schema extensions for business model realignment."""
    
    # 1. Add country field to organizations table with enum constraint
    op.add_column('organizations', sa.Column('country', sa.String(length=3), nullable=True))
    op.execute("""
        ALTER TABLE organizations 
        ADD CONSTRAINT organizations_country_check 
        CHECK (country IN ('GR', 'KSA', 'ES', 'CY', 'OM'))
    """)
    
    # 2. Add supplier parent organization validation constraint (already exists in base migration)
    # This constraint already exists: supplier_must_have_parent
    
    # 3. Create machine_hours table with proper relationships and indexes
    op.create_table('machine_hours',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recorded_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('hours_value', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('recorded_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recorded_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for machine_hours table
    op.create_index('ix_machine_hours_machine_id', 'machine_hours', ['machine_id'])
    op.create_index('ix_machine_hours_recorded_date', 'machine_hours', ['recorded_date'])
    op.create_index('ix_machine_hours_machine_date', 'machine_hours', ['machine_id', 'recorded_date'])
    
    # 4. Extend parts table with manufacturer, part_code, and serial_number fields
    op.add_column('parts', sa.Column('manufacturer', sa.String(length=255), nullable=True))
    op.add_column('parts', sa.Column('part_code', sa.String(length=100), nullable=True))
    op.add_column('parts', sa.Column('serial_number', sa.String(length=255), nullable=True))
    
    # 5. Update parts name field to support longer multilingual strings
    op.alter_column('parts', 'name',
                   existing_type=sa.String(length=255),
                   type_=sa.Text(),
                   existing_nullable=False)
    
    # 6. Add machine model type enum validation for V3.1B and V4.0
    op.execute("""
        ALTER TABLE machines 
        ADD CONSTRAINT machines_model_type_check 
        CHECK (model_type IN ('V3.1B', 'V4.0'))
    """)
    
    # 7. Add indexes for new parts fields
    op.create_index('ix_parts_manufacturer', 'parts', ['manufacturer'])
    op.create_index('ix_parts_part_code', 'parts', ['part_code'])
    op.create_index('ix_parts_serial_number', 'parts', ['serial_number'])


def downgrade() -> None:
    """Remove schema extensions for business model realignment."""
    
    # Remove indexes for parts fields
    op.drop_index('ix_parts_serial_number', table_name='parts')
    op.drop_index('ix_parts_part_code', table_name='parts')
    op.drop_index('ix_parts_manufacturer', table_name='parts')
    
    # Remove machine model type constraint
    op.execute("ALTER TABLE machines DROP CONSTRAINT IF EXISTS machines_model_type_check")
    
    # Revert parts name field to original length
    op.alter_column('parts', 'name',
                   existing_type=sa.Text(),
                   type_=sa.String(length=255),
                   existing_nullable=False)
    
    # Remove new parts columns
    op.drop_column('parts', 'serial_number')
    op.drop_column('parts', 'part_code')
    op.drop_column('parts', 'manufacturer')
    
    # Drop machine_hours table and its indexes
    op.drop_index('ix_machine_hours_machine_date', table_name='machine_hours')
    op.drop_index('ix_machine_hours_recorded_date', table_name='machine_hours')
    op.drop_index('ix_machine_hours_machine_id', table_name='machine_hours')
    op.drop_table('machine_hours')
    
    # Remove country constraint and column
    op.execute("ALTER TABLE organizations DROP CONSTRAINT IF EXISTS organizations_country_check")
    op.drop_column('organizations', 'country')