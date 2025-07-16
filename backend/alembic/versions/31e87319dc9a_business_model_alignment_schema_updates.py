"""business_model_alignment_schema_updates

Revision ID: 31e87319dc9a
Revises: 
Create Date: 2025-07-16 00:41:55.392706

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '31e87319dc9a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to align with business model requirements."""
    
    # Create enum types - SQLAlchemy will handle creation automatically when tables are created    

    # Create all tables first
    
    # Create organizations table
    op.create_table('organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('organization_type', sa.Enum('oraseas_ee', 'bossaqua', 'customer', 'supplier', name='organizationtype'), nullable=False),
        sa.Column('parent_organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('contact_info', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint(
            "organization_type != 'supplier' OR parent_organization_id IS NOT NULL",
            name='supplier_must_have_parent'
        ),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)
    
    # Create warehouses table
    op.create_table('warehouses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('location', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'name', name='_org_warehouse_name_uc')
    )
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.Enum('user', 'admin', 'super_admin', name='userrole'), nullable=False),
        sa.Column('user_status', sa.Enum('active', 'inactive', 'pending_invitation', 'locked', name='userstatus'), nullable=False, server_default='active'),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('invitation_token', sa.String(length=255), nullable=True),
        sa.Column('invitation_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('password_reset_token', sa.String(length=255), nullable=True),
        sa.Column('password_reset_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index('ix_users_org_role', 'users', ['organization_id', 'role'], unique=False)    

    # Create parts table
    op.create_table('parts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('part_number', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('part_type', sa.Enum('consumable', 'bulk_material', name='parttype'), nullable=False, server_default='consumable'),
        sa.Column('is_proprietary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('unit_of_measure', sa.String(length=50), nullable=False, server_default='pieces'),
        sa.Column('manufacturer_part_number', sa.String(length=255), nullable=True),
        sa.Column('manufacturer_delivery_time_days', sa.Integer(), nullable=True),
        sa.Column('local_supplier_delivery_time_days', sa.Integer(), nullable=True),
        sa.Column('image_urls', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('part_number')
    )
    op.create_index(op.f('ix_parts_part_number'), 'parts', ['part_number'], unique=False)
    
    # Create machines table
    op.create_table('machines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_type', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('serial_number', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['customer_organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('serial_number')
    )
    op.create_index('ix_machines_customer', 'machines', ['customer_organization_id'], unique=False)
    
    # Create inventory table (warehouse-based)
    op.create_table('inventory',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('part_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('current_stock', sa.DECIMAL(precision=10, scale=3), nullable=False, server_default='0'),
        sa.Column('minimum_stock_recommendation', sa.DECIMAL(precision=10, scale=3), nullable=False, server_default='0'),
        sa.Column('unit_of_measure', sa.String(length=50), nullable=False),
        sa.Column('reorder_threshold_set_by', sa.String(length=50), nullable=True),
        sa.Column('last_recommendation_update', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('warehouse_id', 'part_id', name='_warehouse_part_uc')
    )
    op.create_index('ix_inventory_warehouse_part', 'inventory', ['warehouse_id', 'part_id'], unique=False)  
  
    # Create transactions table
    op.create_table('transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_type', sa.Enum('creation', 'transfer', 'consumption', 'adjustment', name='transactiontype'), nullable=False),
        sa.Column('part_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_warehouse_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('to_warehouse_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('quantity', sa.DECIMAL(precision=10, scale=3), nullable=False),
        sa.Column('unit_of_measure', sa.String(length=50), nullable=False),
        sa.Column('performed_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
        sa.ForeignKeyConstraint(['from_warehouse_id'], ['warehouses.id'], ),
        sa.ForeignKeyConstraint(['to_warehouse_id'], ['warehouses.id'], ),
        sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ),
        sa.ForeignKeyConstraint(['performed_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_transactions_date', 'transactions', ['transaction_date'], unique=False)
    op.create_index('ix_transactions_part', 'transactions', ['part_id'], unique=False)
    op.create_index('ix_transactions_warehouse', 'transactions', ['from_warehouse_id', 'to_warehouse_id'], unique=False)
    
    # Create supplier_orders table
    op.create_table('supplier_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ordering_organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('supplier_name', sa.String(length=255), nullable=False),
        sa.Column('order_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expected_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ordering_organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create supplier_order_items table
    op.create_table('supplier_order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('supplier_order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('part_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.DECIMAL(precision=10, scale=3), nullable=False, server_default='1'),
        sa.Column('unit_price', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['supplier_order_id'], ['supplier_orders.id'], ),
        sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )    
    
# Create customer_orders table
    op.create_table('customer_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('oraseas_organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expected_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('ordered_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['customer_organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['oraseas_organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['ordered_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create customer_order_items table
    op.create_table('customer_order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('part_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.DECIMAL(precision=10, scale=3), nullable=False, server_default='1'),
        sa.Column('unit_price', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['customer_order_id'], ['customer_orders.id'], ),
        sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create part_usage table
    op.create_table('part_usage',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('part_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('usage_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('quantity_used', sa.DECIMAL(precision=10, scale=3), nullable=False, server_default='1'),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('recorded_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['customer_organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['part_id'], ['parts.id'], ),
        sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ),
        sa.ForeignKeyConstraint(['recorded_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )    
   
 # Create stock_adjustments table
    op.create_table('stock_adjustments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('inventory_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('adjustment_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('quantity_adjusted', sa.DECIMAL(precision=10, scale=3), nullable=False),
        sa.Column('reason_code', sa.String(length=100), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['inventory_id'], ['inventory.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add business rule constraints
    
    # Constraint to ensure only one Oraseas EE organization
    op.execute("""
        CREATE UNIQUE INDEX unique_oraseas_ee 
        ON organizations (organization_type) 
        WHERE organization_type = 'oraseas_ee'
    """)
    
    # Constraint to ensure only one BossAqua organization
    op.execute("""
        CREATE UNIQUE INDEX unique_bossaqua 
        ON organizations (organization_type) 
        WHERE organization_type = 'bossaqua'
    """)
    
    # Constraint to ensure super_admin users belong to Oraseas EE only
    op.execute("""
        ALTER TABLE users ADD CONSTRAINT super_admin_oraseas_only 
        CHECK (
            role != 'super_admin' OR 
            organization_id IN (
                SELECT id FROM organizations WHERE organization_type = 'oraseas_ee'
            )
        )
    """)    

    # Create function to automatically update inventory based on transactions
    op.execute("""
        CREATE OR REPLACE FUNCTION update_inventory_on_transaction()
        RETURNS TRIGGER AS $func$
        BEGIN
            -- Handle different transaction types
            CASE NEW.transaction_type
                WHEN 'creation' THEN
                    -- Increase inventory in to_warehouse
                    IF NEW.to_warehouse_id IS NOT NULL THEN
                        INSERT INTO inventory (warehouse_id, part_id, current_stock, unit_of_measure)
                        VALUES (NEW.to_warehouse_id, NEW.part_id, NEW.quantity, NEW.unit_of_measure)
                        ON CONFLICT (warehouse_id, part_id)
                        DO UPDATE SET 
                            current_stock = inventory.current_stock + NEW.quantity,
                            last_updated = NOW();
                    END IF;
                    
                WHEN 'transfer' THEN
                    -- Decrease from source warehouse
                    IF NEW.from_warehouse_id IS NOT NULL THEN
                        UPDATE inventory 
                        SET current_stock = current_stock - NEW.quantity,
                            last_updated = NOW()
                        WHERE warehouse_id = NEW.from_warehouse_id AND part_id = NEW.part_id;
                    END IF;
                    
                    -- Increase in destination warehouse
                    IF NEW.to_warehouse_id IS NOT NULL THEN
                        INSERT INTO inventory (warehouse_id, part_id, current_stock, unit_of_measure)
                        VALUES (NEW.to_warehouse_id, NEW.part_id, NEW.quantity, NEW.unit_of_measure)
                        ON CONFLICT (warehouse_id, part_id)
                        DO UPDATE SET 
                            current_stock = inventory.current_stock + NEW.quantity,
                            last_updated = NOW();
                    END IF;
                    
                WHEN 'consumption' THEN
                    -- Decrease inventory in from_warehouse
                    IF NEW.from_warehouse_id IS NOT NULL THEN
                        UPDATE inventory 
                        SET current_stock = current_stock - NEW.quantity,
                            last_updated = NOW()
                        WHERE warehouse_id = NEW.from_warehouse_id AND part_id = NEW.part_id;
                    END IF;
                    
                WHEN 'adjustment' THEN
                    -- Adjust inventory in specified warehouse
                    IF NEW.to_warehouse_id IS NOT NULL THEN
                        INSERT INTO inventory (warehouse_id, part_id, current_stock, unit_of_measure)
                        VALUES (NEW.to_warehouse_id, NEW.part_id, NEW.quantity, NEW.unit_of_measure)
                        ON CONFLICT (warehouse_id, part_id)
                        DO UPDATE SET 
                            current_stock = inventory.current_stock + NEW.quantity,
                            last_updated = NOW();
                    END IF;
            END CASE;
            
            RETURN NEW;
        END;
        $func$ LANGUAGE plpgsql;
    """)
    
    # Create trigger to automatically update inventory
    op.execute("""
        CREATE TRIGGER trigger_update_inventory_on_transaction
        AFTER INSERT ON transactions
        FOR EACH ROW
        EXECUTE FUNCTION update_inventory_on_transaction();
    """)
    
    # Create function to prevent negative inventory (optional - can be disabled for certain scenarios)
    op.execute("""
        CREATE OR REPLACE FUNCTION check_inventory_balance()
        RETURNS TRIGGER AS $func$
        BEGIN
            IF NEW.current_stock < 0 THEN
                RAISE EXCEPTION 'Inventory cannot be negative. Current stock would be: %', NEW.current_stock;
            END IF;
            RETURN NEW;
        END;
        $func$ LANGUAGE plpgsql;
    """)
    
    # Create trigger to check inventory balance (can be disabled if needed)
    op.execute("""
        CREATE TRIGGER trigger_check_inventory_balance
        BEFORE UPDATE ON inventory
        FOR EACH ROW
        EXECUTE FUNCTION check_inventory_balance();
    """)


def downgrade() -> None:
    """Downgrade schema - remove all business model alignment changes."""
    
    # Drop triggers first
    op.execute("DROP TRIGGER IF EXISTS trigger_check_inventory_balance ON inventory")
    op.execute("DROP TRIGGER IF EXISTS trigger_update_inventory_on_transaction ON transactions")
    
    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS check_inventory_balance()")
    op.execute("DROP FUNCTION IF EXISTS update_inventory_on_transaction()")
    
    # Drop constraints
    op.execute("DROP INDEX IF EXISTS unique_oraseas_ee")
    op.execute("DROP INDEX IF EXISTS unique_bossaqua")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS super_admin_oraseas_only")
    
    # Drop tables in reverse order of creation
    op.drop_table('stock_adjustments')
    op.drop_table('part_usage')
    op.drop_table('customer_order_items')
    op.drop_table('customer_orders')
    op.drop_table('supplier_order_items')
    op.drop_table('supplier_orders')
    op.drop_table('transactions')
    op.drop_table('inventory')
    op.drop_table('machines')
    op.drop_table('parts')
    op.drop_table('users')
    op.drop_table('warehouses')
    op.drop_table('organizations')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS transactiontype")
    op.execute("DROP TYPE IF EXISTS userstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS parttype")
    op.execute("DROP TYPE IF EXISTS organizationtype")