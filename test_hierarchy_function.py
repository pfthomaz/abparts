#!/usr/bin/env python3
"""
Simple test script to verify the get_organization_hierarchy_tree function works.
"""

import sys
import os
sys.path.append('/app')

from app.database import SessionLocal
from app.crud.organizations import get_organization_hierarchy_tree
from app.models import Organization, OrganizationType
import uuid

def test_hierarchy_function():
    """Test the hierarchy function with existing data."""
    db = SessionLocal()
    try:
        # Test with no filtering (should work even with empty database)
        result = get_organization_hierarchy_tree(db, include_inactive=True)
        print(f"Hierarchy tree result: {len(result)} root organizations")
        
        for org in result:
            print(f"- {org.name} ({org.organization_type}) - Children: {len(org.children)}")
            for child in org.children:
                print(f"  - {child.name} ({child.organization_type})")
        
        print("✅ Hierarchy function test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Hierarchy function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    test_hierarchy_function()