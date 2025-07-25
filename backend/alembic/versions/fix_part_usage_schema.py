"""Fix part_usage schema consistency

Revision ID: fix_part_usage_schema
Revises: fd34c07414bf
Create Date: 2025-07-25 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fix_part_usage_schema'
down_revision = 'fd34c07414bf'
branch_labels = None
depends_on = None


def upgrade():
    # Rename quantity_used to quantity to match the model
    op.execute("ALTER TABLE part_usage RENAME COLUMN quantity_used TO quantity")
    
    # Add warehouse_id column that's missing from the database
    op.add_column('part_usage', sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Add foreign key constraint for warehouse_id
    op.create_foreign_key('part_usage_warehouse_id_fkey', 'part_usage', 'warehouses', ['warehouse_id'], ['id'])
    
    # Update existing records to set a default warehouse_id (using the first warehouse from each organization)
    op.execute("""
        UPDATE part_usage 
        SET warehouse_id = (
            SELECT w.id 
            FROM warehouses w 
            WHERE w.organization_id = part_usage.customer_organization_id 
            LIMIT 1
        )
        WHERE warehouse_id IS NULL
    """)
    
    # Make warehouse_id NOT NULL after setting default values
    op.alter_column('part_usage', 'warehouse_id', nullable=False)


def downgrade():
    # Make warehouse_id nullable first
    op.alter_column('part_usage', 'warehouse_id', nullable=True)
    
    # Drop foreign key constraint
    op.drop_constraint('part_usage_warehouse_id_fkey', 'part_usage', type_='foreignkey')
    
    # Drop warehouse_id column
    op.drop_column('part_usage', 'warehouse_id')
    
    # Rename quantity back to quantity_used
    op.execute("ALTER TABLE part_usage RENAME COLUMN quantity TO quantity_used")