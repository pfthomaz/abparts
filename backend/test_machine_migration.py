#!/usr/bin/env python3
"""
Test script to validate machine schema migration functionality.
This script tests the machine table schema and enum handling.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import DATABASE_URL
from app.models import Machine, MachineStatus
import uuid
from datetime import datetime

def test_machine_schema():
    """Test that machine schema is properly configured."""
    print("Testing machine schema...")
    
    # Create database connection
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        # Test 1: Verify all columns exist
        print("1. Checking machine table structure...")
        result = session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'machines' 
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        expected_columns = {
            'id', 'customer_organization_id', 'model_type', 'name', 'serial_number',
            'created_at', 'updated_at', 'purchase_date', 'warranty_expiry_date',
            'status', 'last_maintenance_date', 'next_maintenance_date', 'location', 'notes'
        }
        
        actual_columns = {col[0] for col in columns}
        
        if expected_columns.issubset(actual_columns):
            print("   ✓ All expected columns exist")
        else:
            missing = expected_columns - actual_columns
            print(f"   ✗ Missing columns: {missing}")
            return False
        
        # Test 2: Verify enum type exists and has correct values
        print("2. Checking machinestatus enum...")
        result = session.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'machinestatus')
            ORDER BY enumlabel
        """))
        
        enum_values = {row[0] for row in result.fetchall()}
        expected_enum_values = {'active', 'inactive', 'maintenance', 'decommissioned'}
        
        if enum_values == expected_enum_values:
            print("   ✓ Enum type has correct values")
        else:
            print(f"   ✗ Enum values mismatch. Expected: {expected_enum_values}, Got: {enum_values}")
            return False
        
        # Test 3: Test enum handling in SQLAlchemy model
        print("3. Testing enum handling in model...")
        try:
            # Test that we can reference enum values
            active_status = MachineStatus.active
            inactive_status = MachineStatus.inactive
            maintenance_status = MachineStatus.maintenance
            decommissioned_status = MachineStatus.decommissioned
            
            print("   ✓ All enum values accessible from Python")
        except Exception as e:
            print(f"   ✗ Error accessing enum values: {e}")
            return False
        
        # Test 4: Test default value handling
        print("4. Checking default values...")
        result = session.execute(text("""
            SELECT column_default 
            FROM information_schema.columns 
            WHERE table_name = 'machines' AND column_name = 'status'
        """))
        
        default_value = result.fetchone()[0]
        if "'active'::machinestatus" in default_value:
            print("   ✓ Status column has correct default value")
        else:
            print(f"   ✗ Unexpected default value: {default_value}")
            return False
        
        print("\n✓ All migration tests passed!")
        return True

def test_machine_crud():
    """Test basic CRUD operations with the migrated schema."""
    print("\nTesting machine CRUD operations...")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        try:
            # First, get a valid organization ID
            result = session.execute(text("SELECT id FROM organizations LIMIT 1"))
            org_row = result.fetchone()
            if not org_row:
                print("   ⚠ No organizations found, skipping CRUD test")
                return True
            
            org_id = org_row[0]
            
            # Test creating a machine with enum status
            test_machine = Machine(
                customer_organization_id=org_id,
                model_type="V4.0",
                name="Test Machine",
                serial_number=f"TEST-{uuid.uuid4().hex[:8]}",
                status=MachineStatus.active,
                purchase_date=datetime.now(),
                location="Test Location",
                notes="Test migration machine"
            )
            
            session.add(test_machine)
            session.commit()
            print("   ✓ Machine created successfully")
            
            # Test reading the machine
            retrieved_machine = session.query(Machine).filter_by(id=test_machine.id).first()
            if retrieved_machine and retrieved_machine.status == MachineStatus.active:
                print("   ✓ Machine retrieved with correct enum value")
            else:
                print("   ✗ Error retrieving machine or enum value")
                return False
            
            # Test updating enum status
            retrieved_machine.status = MachineStatus.maintenance
            session.commit()
            
            # Verify update
            updated_machine = session.query(Machine).filter_by(id=test_machine.id).first()
            if updated_machine.status == MachineStatus.maintenance:
                print("   ✓ Machine status updated successfully")
            else:
                print("   ✗ Error updating machine status")
                return False
            
            # Clean up
            session.delete(updated_machine)
            session.commit()
            print("   ✓ Machine deleted successfully")
            
            print("✓ All CRUD tests passed!")
            return True
            
        except Exception as e:
            print(f"   ✗ CRUD test failed: {e}")
            session.rollback()
            return False

if __name__ == "__main__":
    print("Machine Migration Validation Test")
    print("=" * 40)
    
    schema_ok = test_machine_schema()
    crud_ok = test_machine_crud()
    
    if schema_ok and crud_ok:
        print("\n🎉 All migration tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)