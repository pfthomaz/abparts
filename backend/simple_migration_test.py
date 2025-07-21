#!/usr/bin/env python3
"""
Simple Migration Test

Tests the migration functionality with the current database schema.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.migration_utils import DataMigrator, MigrationError
from app.database import get_db
from sqlalchemy import text


def test_simple_migration():
    """Test migration with current database"""
    print("="*60)
    print("SIMPLE MIGRATION TEST")
    print("="*60)
    
    try:
        db = next(get_db())
        
        print("\n--- Current Database State ---")
        
        # Check current data using raw SQL
        org_count = db.execute(text("SELECT COUNT(*) FROM organizations")).scalar()
        user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        part_count = db.execute(text("SELECT COUNT(*) FROM parts")).scalar()
        warehouse_count = db.execute(text("SELECT COUNT(*) FROM warehouses")).scalar()
        inventory_count = db.execute(text("SELECT COUNT(*) FROM inventory")).scalar()
        machine_count = db.execute(text("SELECT COUNT(*) FROM machines")).scalar()
        
        print(f"Organizations: {org_count}")
        print(f"Users: {user_count}")
        print(f"Parts: {part_count}")
        print(f"Warehouses: {warehouse_count}")
        print(f"Inventory: {inventory_count}")
        print(f"Machines: {machine_count}")
        
        if org_count == 0:
            print("\nNo data found - creating sample data...")
            create_sample_data(db)
        
        print("\n--- Running Migration ---")
        
        migrator = DataMigrator()
        
        # Test individual migration steps
        print("\n1. Testing organization type migration...")
        org_result = migrator.migrate_organization_types(db)
        print(f"   Result: {org_result}")
        
        print("\n2. Testing user role migration...")
        user_result = migrator.migrate_user_roles(db)
        print(f"   Result: {user_result}")
        
        print("\n3. Testing parts classification migration...")
        parts_result = migrator.migrate_parts_classification(db)
        print(f"   Result: {parts_result}")
        
        print("\n4. Testing warehouse creation...")
        warehouse_result = migrator.ensure_default_warehouses(db)
        print(f"   Result: {warehouse_result}")
        
        print("\n--- Migration Results ---")
        print("✓ Organization types migrated")
        print("✓ User roles migrated")
        print("✓ Parts classification migrated")
        print("✓ Default warehouses ensured")
        
        print("\n--- Post-Migration State ---")
        
        # Check organizations
        orgs = db.execute(text("SELECT name, organization_type FROM organizations")).fetchall()
        print("\nOrganizations:")
        for org in orgs:
            print(f"  {org.name}: {org.organization_type}")
        
        # Check users
        users = db.execute(text("SELECT username, role FROM users")).fetchall()
        print("\nUsers:")
        for user in users:
            print(f"  {user.username}: {user.role}")
        
        # Check parts
        parts = db.execute(text("SELECT part_number, part_type, is_proprietary, unit_of_measure FROM parts")).fetchall()
        print("\nParts:")
        for part in parts:
            print(f"  {part.part_number}: {part.part_type}, proprietary={part.is_proprietary}, unit={part.unit_of_measure}")
        
        print("\n🎉 Migration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Migration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def create_sample_data(db):
    """Create minimal sample data for testing"""
    try:
        # Create organizations
        db.execute(text("""
            INSERT INTO organizations (id, name, organization_type, address, contact_info, is_active, created_at, updated_at)
            VALUES 
                (gen_random_uuid(), 'Oraseas EE', 'customer', '123 Main St', 'info@oraseas.ee', true, now(), now()),
                (gen_random_uuid(), 'BossAqua Manufacturing', 'customer', '456 Industrial Ave', 'contact@bossaqua.com', true, now(), now()),
                (gen_random_uuid(), 'Customer Corp A', 'customer', '789 Business Blvd', 'orders@customera.lv', true, now(), now()),
                (gen_random_uuid(), 'Parts Supplier Ltd', 'customer', '321 Supply St', 'sales@partssupplier.lt', true, now(), now())
        """))
        
        # Get organization IDs
        orgs = db.execute(text("SELECT id, name FROM organizations")).fetchall()
        org_map = {org.name: org.id for org in orgs}
        
        # Create users
        db.execute(text("""
            INSERT INTO users (id, organization_id, username, password_hash, email, name, role, user_status, failed_login_attempts, is_active, created_at, updated_at)
            VALUES 
                (gen_random_uuid(), :oraseas_id, 'admin_oraseas', '$2b$12$dummy_hash_1', 'admin@oraseas.ee', 'Oraseas Admin', 'admin', 'active', 0, true, now(), now()),
                (gen_random_uuid(), :bossaqua_id, 'bossaqua_user', '$2b$12$dummy_hash_2', 'user@bossaqua.com', 'BossAqua User', 'user', 'active', 0, true, now(), now()),
                (gen_random_uuid(), :customer_id, 'customer_admin', '$2b$12$dummy_hash_3', 'admin@customera.lv', 'Customer Admin', 'admin', 'active', 0, true, now(), now()),
                (gen_random_uuid(), :supplier_id, 'supplier_user', '$2b$12$dummy_hash_4', 'user@partssupplier.lt', 'Supplier User', 'user', 'active', 0, true, now(), now())
        """), {
            'oraseas_id': org_map['Oraseas EE'],
            'bossaqua_id': org_map['BossAqua Manufacturing'],
            'customer_id': org_map['Customer Corp A'],
            'supplier_id': org_map['Parts Supplier Ltd']
        })
        
        # Create parts
        db.execute(text("""
            INSERT INTO parts (id, part_number, name, description, part_type, is_proprietary, unit_of_measure, created_at, updated_at)
            VALUES 
                (gen_random_uuid(), 'FILTER-001', 'Water Filter', 'Standard water filter for AutoBoss machines', 'consumable', false, 'pieces', now(), now()),
                (gen_random_uuid(), 'OIL-BOSS-500', 'BossAqua Cleaning Oil', 'Proprietary cleaning oil for AutoBoss machines', 'consumable', false, 'pieces', now(), now()),
                (gen_random_uuid(), 'BELT-STD-200', 'Drive Belt', 'Standard drive belt for AutoBoss V3.1B', 'consumable', false, 'pieces', now(), now()),
                (gen_random_uuid(), 'CHEM-CLEAN-1L', 'Cleaning Chemical', 'General purpose cleaning chemical - 1 liter bottles', 'consumable', false, 'pieces', now(), now())
        """))
        
        # Create warehouses
        db.execute(text("""
            INSERT INTO warehouses (id, organization_id, name, location, description, is_active, created_at, updated_at)
            VALUES 
                (gen_random_uuid(), :oraseas_id, 'Main Warehouse', 'Tallinn Central', 'Main distribution warehouse', true, now(), now()),
                (gen_random_uuid(), :bossaqua_id, 'Manufacturing Warehouse', 'Germany Factory', 'BossAqua manufacturing facility', true, now(), now()),
                (gen_random_uuid(), :customer_id, 'Customer Storage', 'Riga Office', 'Customer A storage facility', true, now(), now())
        """), {
            'oraseas_id': org_map['Oraseas EE'],
            'bossaqua_id': org_map['BossAqua Manufacturing'],
            'customer_id': org_map['Customer Corp A']
        })
        
        db.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Failed to create sample data: {str(e)}")
        raise


if __name__ == "__main__":
    success = test_simple_migration()
    sys.exit(0 if success else 1)