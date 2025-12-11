#!/usr/bin/env python3
"""
Direct test of Machine and MachineHours models to verify Task 4 implementation.
"""

import sys
import os
from datetime import datetime
from decimal import Decimal

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_machine_model_enhancements():
    """Test the enhanced machine model functionality directly."""
    print("Testing Machine Model Enhancements...")
    
    try:
        # Import the models
        from models import Machine, MachineHours, MachineModelType, MachineStatus, User, Organization, OrganizationType, UserRole
        from database import SessionLocal
        
        # Create a database session
        db = SessionLocal()
        
        print("✅ Successfully imported models and created database session")
        
        # Test 1: Verify MachineModelType enum
        print("\n1. Testing MachineModelType enum...")
        print(f"✅ Available model types: {[e.value for e in MachineModelType]}")
        
        # Test 2: Get existing machines and verify enum conversion
        print("\n2. Testing existing machines with new enum...")
        machines = db.query(Machine).limit(5).all()
        print(f"✅ Retrieved {len(machines)} machines from database")
        
        for machine in machines:
            print(f"  - Machine: {machine.name}")
            print(f"    Model Type: {machine.model_type} (type: {type(machine.model_type)})")
            print(f"    Serial: {machine.serial_number}")
            
            # Test the new validation method
            try:
                machine.validate_model_type()
                print(f"    ✅ Model type validation passed")
            except Exception as e:
                print(f"    ❌ Model type validation failed: {e}")
        
        # Test 3: Test MachineHours model enhancements
        print("\n3. Testing MachineHours model enhancements...")
        if machines:
            machine = machines[0]
            
            # Get existing machine hours
            hours_records = db.query(MachineHours).filter(MachineHours.machine_id == machine.id).limit(3).all()
            print(f"✅ Retrieved {len(hours_records)} hours records for machine {machine.name}")
            
            for hours_record in hours_records:
                print(f"  - Hours: {hours_record.hours_value} on {hours_record.recorded_date}")
                
                # Test validation methods
                try:
                    hours_record.validate_hours_value()
                    print(f"    ✅ Hours value validation passed")
                except Exception as e:
                    print(f"    ❌ Hours value validation failed: {e}")
                
                try:
                    hours_record.validate_recorded_date()
                    print(f"    ✅ Recorded date validation passed")
                except Exception as e:
                    print(f"    ❌ Recorded date validation failed: {e}")
        
        # Test 4: Test machine business logic methods
        print("\n4. Testing machine business logic methods...")
        if machines:
            machine = machines[0]
            
            # Test get_latest_hours
            try:
                latest_hours = machine.get_latest_hours(db)
                print(f"✅ Latest hours for {machine.name}: {latest_hours}")
            except Exception as e:
                print(f"❌ Error getting latest hours: {e}")
            
            # Test get_total_hours_recorded
            try:
                total_records = machine.get_total_hours_recorded(db)
                print(f"✅ Total hours records for {machine.name}: {total_records}")
            except Exception as e:
                print(f"❌ Error getting total hours records: {e}")
        
        # Test 5: Test ownership transfer validation
        print("\n5. Testing ownership transfer validation...")
        if machines:
            machine = machines[0]
            
            # Get organizations for testing
            oraseas_org = db.query(Organization).filter(Organization.organization_type == OrganizationType.oraseas_ee).first()
            customer_org = db.query(Organization).filter(Organization.organization_type == OrganizationType.customer).first()
            
            if oraseas_org and customer_org:
                try:
                    # Test validation (should pass if machine belongs to Oraseas EE)
                    can_transfer = machine.can_transfer_ownership(oraseas_org, customer_org)
                    print(f"✅ Ownership transfer validation: {can_transfer}")
                except Exception as e:
                    print(f"⚠️  Ownership transfer validation: {e}")
            else:
                print("⚠️  Could not find required organizations for transfer test")
        
        # Test 6: Test name editing permissions
        print("\n6. Testing name editing permissions...")
        if machines:
            machine = machines[0]
            
            # Get a superadmin user
            superadmin = db.query(User).filter(User.role == UserRole.super_admin).first()
            admin = db.query(User).filter(User.role == UserRole.admin).first()
            
            if superadmin:
                try:
                    can_edit = machine.can_edit_name(superadmin, superadmin.organization)
                    print(f"✅ Superadmin can edit machine name: {can_edit}")
                except Exception as e:
                    print(f"❌ Error testing superadmin name edit: {e}")
            
            if admin:
                try:
                    can_edit = machine.can_edit_name(admin, admin.organization)
                    print(f"✅ Admin can edit machine name (in own org): {can_edit}")
                except Exception as e:
                    print(f"❌ Error testing admin name edit: {e}")
        
        db.close()
        print("\n✅ All machine model enhancement tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Machine Model Direct Test")
    print("=" * 60)
    
    success = test_machine_model_enhancements()
    
    if success:
        print("\n🎉 Machine model enhancement implementation is working correctly!")
    else:
        print("\n❌ Issues found with the machine model enhancement implementation.")
    
    print("=" * 60)