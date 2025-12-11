#!/usr/bin/env python3
"""
Simple test script for the get_potential_parent_organizations function
"""

import sys
import os
sys.path.append('/app')

from app.database import SessionLocal
from app.crud.organizations import get_potential_parent_organizations
from app.models import OrganizationType

def test_potential_parents():
    """Test the get_potential_parent_organizations function"""
    db = SessionLocal()
    
    try:
        print("Testing get_potential_parent_organizations function...")
        
        # Test with supplier type (should return Customer and Oraseas EE orgs)
        print("\n1. Testing with SUPPLIER organization type:")
        supplier_parents = get_potential_parent_organizations(db, OrganizationType.supplier)
        print(f"   Found {len(supplier_parents)} potential parents")
        for org in supplier_parents:
            print(f"   - {org.name} ({org.organization_type.value})")
        
        # Test with customer type (should return empty list)
        print("\n2. Testing with CUSTOMER organization type:")
        customer_parents = get_potential_parent_organizations(db, OrganizationType.customer)
        print(f"   Found {len(customer_parents)} potential parents")
        
        # Test with oraseas_ee type (should return empty list)
        print("\n3. Testing with ORASEAS_EE organization type:")
        oraseas_parents = get_potential_parent_organizations(db, OrganizationType.oraseas_ee)
        print(f"   Found {len(oraseas_parents)} potential parents")
        
        # Test with bossaqua type (should return empty list)
        print("\n4. Testing with BOSSAQUA organization type:")
        bossaqua_parents = get_potential_parent_organizations(db, OrganizationType.bossaqua)
        print(f"   Found {len(bossaqua_parents)} potential parents")
        
        print("\n✅ All tests completed successfully!")
        
        # Verify business logic
        assert len(supplier_parents) > 0, "Suppliers should have potential parents"
        assert len(customer_parents) == 0, "Customers should not have potential parents"
        assert len(oraseas_parents) == 0, "Oraseas EE should not have potential parents"
        assert len(bossaqua_parents) == 0, "BossAqua should not have potential parents"
        
        # Verify supplier parents are only Customer or Oraseas EE types
        for org in supplier_parents:
            assert org.organization_type in [OrganizationType.customer, OrganizationType.oraseas_ee], \
                f"Invalid parent type: {org.organization_type}"
            assert org.is_active, "All returned organizations should be active"
        
        print("✅ All business logic assertions passed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = test_potential_parents()
    sys.exit(0 if success else 1)