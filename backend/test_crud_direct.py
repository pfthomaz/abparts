#!/usr/bin/env python3
"""
Direct test of the CRUD function
"""

import sys
import os
sys.path.append('/app')

from app.database import SessionLocal
from app.crud.organizations import get_potential_parent_organizations
from app.models import OrganizationType

def test_crud_function():
    """Test the CRUD function directly"""
    
    db = SessionLocal()
    try:
        print("Testing get_potential_parent_organizations CRUD function...")
        
        # Test with supplier type
        print("\n1. Testing with SUPPLIER organization type:")
        supplier_parents = get_potential_parent_organizations(db, OrganizationType.supplier)
        print(f"   Found {len(supplier_parents)} potential parents")
        for org in supplier_parents:
            print(f"   - {org.name} ({org.organization_type.value})")
        
        # Test with customer type (should return empty list)
        print("\n2. Testing with CUSTOMER organization type:")
        customer_parents = get_potential_parent_organizations(db, OrganizationType.customer)
        print(f"   Found {len(customer_parents)} potential parents")
        
        print("\n✅ CRUD function test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ CRUD test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_crud_function()
    sys.exit(0 if success else 1)