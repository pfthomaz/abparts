#!/usr/bin/env python3
"""
Simple Validation Test

Tests the validation functionality with the current database.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import get_db
from sqlalchemy import text


def test_validation():
    """Test validation with current database"""
    print("="*60)
    print("SIMPLE VALIDATION TEST")
    print("="*60)
    
    try:
        db = next(get_db())
        
        print("\n--- Organization Type Validation ---")
        
        # Check Oraseas EE constraint (exactly one)
        oraseas_count = db.execute(text(
            "SELECT COUNT(*) FROM organizations WHERE organization_type = 'oraseas_ee'"
        )).scalar()
        
        if oraseas_count == 1:
            print("✓ PASS: Exactly one Oraseas EE organization exists")
        elif oraseas_count == 0:
            print("✗ FAIL: No Oraseas EE organization found")
        else:
            print(f"✗ FAIL: Found {oraseas_count} Oraseas EE organizations, expected 1")
        
        # Check BossAqua constraint (at most one)
        bossaqua_count = db.execute(text(
            "SELECT COUNT(*) FROM organizations WHERE organization_type = 'bossaqua'"
        )).scalar()
        
        if bossaqua_count <= 1:
            print(f"✓ PASS: Found {bossaqua_count} BossAqua organizations (valid)")
        else:
            print(f"✗ FAIL: Found {bossaqua_count} BossAqua organizations, expected at most 1")
        
        # Check supplier parent relationships
        suppliers_without_parent = db.execute(text("""
            SELECT COUNT(*) FROM organizations 
            WHERE organization_type = 'supplier' AND parent_organization_id IS NULL
        """)).scalar()
        
        if suppliers_without_parent == 0:
            print("✓ PASS: All suppliers have parent organizations")
        else:
            print(f"✗ FAIL: {suppliers_without_parent} suppliers without parent organizations")
        
        print("\n--- User Role Validation ---")
        
        # Check super_admin constraint (must be in Oraseas EE)
        oraseas_org = db.execute(text(
            "SELECT id FROM organizations WHERE organization_type = 'oraseas_ee' LIMIT 1"
        )).fetchone()
        
        if oraseas_org:
            invalid_super_admins = db.execute(text("""
                SELECT COUNT(*) FROM users 
                WHERE role = 'super_admin' AND organization_id != :oraseas_id
            """), {"oraseas_id": oraseas_org.id}).scalar()
            
            if invalid_super_admins == 0:
                print("✓ PASS: All super_admins are in Oraseas EE")
            else:
                print(f"✗ FAIL: {invalid_super_admins} super_admins not in Oraseas EE")
        else:
            print("⚠ WARN: No Oraseas EE organization found")
        
        # Check that each organization has at least one admin
        orgs_without_admin = db.execute(text("""
            SELECT COUNT(*) FROM organizations o
            WHERE NOT EXISTS (
                SELECT 1 FROM users u 
                WHERE u.organization_id = o.id 
                AND u.role IN ('admin', 'super_admin')
            )
        """)).scalar()
        
        if orgs_without_admin == 0:
            print("✓ PASS: All organizations have at least one admin")
        else:
            print(f"✗ FAIL: {orgs_without_admin} organizations without admins")
        
        print("\n--- Inventory and Warehouse Validation ---")
        
        # Check that all inventory has valid warehouse references
        orphaned_inventory = db.execute(text("""
            SELECT COUNT(*) FROM inventory i 
            LEFT JOIN warehouses w ON i.warehouse_id = w.id 
            WHERE w.id IS NULL
        """)).scalar()
        
        if orphaned_inventory == 0:
            print("✓ PASS: All inventory linked to valid warehouses")
        else:
            print(f"✗ FAIL: {orphaned_inventory} orphaned inventory records")
        
        # Check that all warehouses belong to valid organizations
        orphaned_warehouses = db.execute(text("""
            SELECT COUNT(*) FROM warehouses w 
            LEFT JOIN organizations o ON w.organization_id = o.id 
            WHERE o.id IS NULL
        """)).scalar()
        
        if orphaned_warehouses == 0:
            print("✓ PASS: All warehouses linked to valid organizations")
        else:
            print(f"✗ FAIL: {orphaned_warehouses} orphaned warehouses")
        
        # Check inventory quantities are non-negative
        negative_inventory = db.execute(text(
            "SELECT COUNT(*) FROM inventory WHERE current_stock < 0"
        )).scalar()
        
        if negative_inventory == 0:
            print("✓ PASS: No negative inventory found")
        else:
            print(f"⚠ WARN: {negative_inventory} negative inventory records")
        
        print("\n--- Parts Classification Validation ---")
        
        # Check that all parts have valid types
        parts_without_type = db.execute(text(
            "SELECT COUNT(*) FROM parts WHERE part_type IS NULL"
        )).scalar()
        
        if parts_without_type == 0:
            print("✓ PASS: All parts have assigned types")
        else:
            print(f"✗ FAIL: {parts_without_type} parts without type")
        
        # Check proprietary parts classification
        proprietary_parts = db.execute(text(
            "SELECT COUNT(*) FROM parts WHERE is_proprietary = true"
        )).scalar()
        total_parts = db.execute(text("SELECT COUNT(*) FROM parts")).scalar()
        
        if proprietary_parts > 0:
            print(f"✓ PASS: {proprietary_parts}/{total_parts} parts marked as proprietary")
        else:
            print("⚠ WARN: No parts marked as proprietary")
        
        print("\n--- Data Summary ---")
        
        # Count records by type
        org_count = db.execute(text("SELECT COUNT(*) FROM organizations")).scalar()
        user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        part_count = db.execute(text("SELECT COUNT(*) FROM parts")).scalar()
        warehouse_count = db.execute(text("SELECT COUNT(*) FROM warehouses")).scalar()
        inventory_count = db.execute(text("SELECT COUNT(*) FROM inventory")).scalar()
        machine_count = db.execute(text("SELECT COUNT(*) FROM machines")).scalar()
        transaction_count = db.execute(text("SELECT COUNT(*) FROM transactions")).scalar()
        
        print(f"Organizations: {org_count}")
        print(f"Users: {user_count}")
        print(f"Parts: {part_count}")
        print(f"Warehouses: {warehouse_count}")
        print(f"Inventory records: {inventory_count}")
        print(f"Machines: {machine_count}")
        print(f"Transactions: {transaction_count}")
        
        print("\n🎉 Validation test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Validation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_validation()
    sys.exit(0 if success else 1)