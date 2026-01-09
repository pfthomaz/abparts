"""add updated_at columns to all tables

Revision ID: 01_add_updated_at
Revises: 00_baseline
Create Date: 2024-12-01 19:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '01_add_updated_at'
down_revision = '00_baseline'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add updated_at column to tables that don't have it.
    Also add a trigger to automatically update the timestamp.
    """
    
    # Create the trigger function if it doesn't exist
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # List of tables that need updated_at column
    tables_needing_updated_at = [
        'transactions',
        'customer_orders',
        'customer_order_items',
        'supplier_orders',
        'supplier_order_items',
        'part_usage',  # Legacy table
        'part_usage_records',
        'part_usage_items',
        'machine_sales',
        'part_order_requests',
        'part_order_items',
    ]
    
    for table_name in tables_needing_updated_at:
        # Check if table exists
        connection = op.get_bind()
        result = connection.execute(sa.text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            )
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            print(f"Skipping {table_name} - table does not exist")
            continue
        
        # Check if updated_at column already exists
        result = connection.execute(sa.text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND column_name = 'updated_at'
            )
        """))
        column_exists = result.scalar()
        
        if column_exists:
            print(f"Skipping {table_name} - updated_at already exists")
            continue
        
        print(f"Adding updated_at to {table_name}")
        
        # Add the column with default value
        op.execute(f"""
            ALTER TABLE {table_name}
            ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE 
            DEFAULT CURRENT_TIMESTAMP NOT NULL
        """)
        
        # Create trigger to auto-update the column
        op.execute(f"""
            DROP TRIGGER IF EXISTS update_{table_name}_updated_at ON {table_name};
            
            CREATE TRIGGER update_{table_name}_updated_at
            BEFORE UPDATE ON {table_name}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)
        
        print(f"✓ Added updated_at and trigger to {table_name}")


def downgrade():
    """
    Remove updated_at columns and triggers.
    """
    
    tables = [
        'transactions',
        'customer_orders',
        'customer_order_items',
        'supplier_orders',
        'supplier_order_items',
        'part_usage',
        'part_usage_records',
        'part_usage_items',
        'machine_sales',
        'part_order_requests',
        'part_order_items',
    ]
    
    for table_name in tables:
        # Check if table exists
        connection = op.get_bind()
        result = connection.execute(sa.text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{table_name}'
            )
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            continue
        
        # Drop trigger
        op.execute(f"""
            DROP TRIGGER IF EXISTS update_{table_name}_updated_at ON {table_name};
        """)
        
        # Check if column exists before dropping
        result = connection.execute(sa.text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND column_name = 'updated_at'
            )
        """))
        column_exists = result.scalar()
        
        if column_exists:
            op.execute(f"""
                ALTER TABLE {table_name}
                DROP COLUMN IF EXISTS updated_at;
            """)
    
    # Drop the trigger function
    op.execute("""
        DROP FUNCTION IF EXISTS update_updated_at_column();
    """)
