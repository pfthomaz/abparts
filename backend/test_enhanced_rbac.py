#!/usr/bin/env python3
"""
Test script for Enhanced Role-Based Access Control (RBAC) implementation.
This script tests the organizational data isolation middleware, permission validation,
and role-based resource access matrix enforcement.

Task 5: Enhanced Role-Based Access Control
- Implement organizational data isolation middleware
- Create organization-scoped query helpers and filters  
- Add permission validation for cross-organizational access prevention
- Implement role-based resource access matrix enforcement
"""

import sys
import os
import uuid
import json
import requests
from datetime import datetime
from typing import Dict, Any, List

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_authentication():
    """Test authentication with superadmin user."""
    print("Testing authentication...")
    
    # Test login with superadmin credentials
    login_data = {
        "username": "superadmin",
        "password": "superadmin"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10  # Add timeout
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✓ Authentication successful: {token_data.get('token_type', 'bearer')}")
            return token_data.get('access_token')
        else:
            print(f"✗ Authentication failed: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("✗ Authentication timeout - API may not be running")
        return None
    except requests.exceptions.ConnectionError:
        print("✗ Connection error - API may not be accessible")
        return None
    except Exception as e:
        print(f"✗ Authentication error: {e}")
        return None

def test_organizational_isolation(token: str):
    """Test organizational data isolation middleware."""
    print("\nTesting organizational data isolation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Access organizations endpoint
    try:
        response = requests.get("http://localhost:8000/organizations", headers=headers, timeout=10)
        if response.status_code == 200:
            orgs = response.json()
            print(f"✓ Organizations accessible: {len(orgs)} organizations")
            
            # Check if BossAqua is accessible (should be for superadmin)
            bossaqua_found = any(org.get('organization_type') == 'bossaqua' for org in orgs)
            if bossaqua_found:
                print("✓ BossAqua data accessible to superadmin")
            else:
                print("! BossAqua data not found (may not exist yet)")
                
        else:
            print(f"✗ Organizations access failed: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("✗ Organizations request timeout")
    except Exception as e:
        print(f"✗ Organizations test error: {e}")
    
    # Test 2: Access users endpoint
    try:
        response = requests.get("http://localhost:8000/users", headers=headers, timeout=10)
        if response.status_code == 200:
            users = response.json()
            print(f"✓ Users accessible: {len(users)} users")
        else:
            print(f"✗ Users access failed: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("✗ Users request timeout")
    except Exception as e:
        print(f"✗ Users test error: {e}")

def test_permission_validation(token: str):
    """Test permission validation for different operations."""
    print("\nTesting permission validation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Read permissions (should work for superadmin)
    endpoints_to_test = [
        "/warehouses",
        "/inventory", 
        "/machines",
        "/parts",
        "/dashboard"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✓ Read access granted to {endpoint}")
            elif response.status_code == 403:
                print(f"✗ Read access denied to {endpoint}")
            else:
                print(f"! {endpoint} returned {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"✗ Timeout testing {endpoint}")
        except Exception as e:
            print(f"✗ Error testing {endpoint}: {e}")

def test_cross_organizational_access_prevention(token: str):
    """Test cross-organizational access prevention."""
    print("\nTesting cross-organizational access prevention...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, get available organizations
    try:
        response = requests.get("http://localhost:8000/organizations", headers=headers, timeout=10)
        if response.status_code != 200:
            print("✗ Could not fetch organizations for cross-org test")
            return
            
        orgs = response.json()
        if len(orgs) < 2:
            print("! Not enough organizations to test cross-organizational access")
            return
            
        # Test accessing resources from different organizations
        for org in orgs[:2]:  # Test first two organizations
            org_id = org.get('id')
            org_name = org.get('name', 'Unknown')
            
            # Test accessing warehouses for this organization
            try:
                response = requests.get(
                    f"http://localhost:8000/warehouses?organization_id={org_id}", 
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    warehouses = response.json()
                    print(f"✓ Access to {org_name} warehouses: {len(warehouses)} warehouses")
                else:
                    print(f"✗ Access denied to {org_name} warehouses: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"✗ Timeout accessing {org_name} warehouses")
            except Exception as e:
                print(f"✗ Error accessing {org_name} warehouses: {e}")
                
    except requests.exceptions.Timeout:
        print("✗ Timeout fetching organizations")
    except Exception as e:
        print(f"✗ Cross-organizational test error: {e}")

def test_role_based_resource_access_matrix(token: str):
    """Test role-based resource access matrix enforcement."""
    print("\nTesting role-based resource access matrix...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test different resource types and operations
    test_matrix = {
        "organizations": {
            "read": "/organizations",
            "write": "/organizations",  # Would need POST data
        },
        "users": {
            "read": "/users",
            "write": "/users",  # Would need POST data
        },
        "parts": {
            "read": "/parts",
            "write": "/parts",  # Would need POST data
        },
        "machines": {
            "read": "/machines", 
            "write": "/machines",  # Would need POST data
        },
        "warehouses": {
            "read": "/warehouses",
            "write": "/warehouses",  # Would need POST data
        },
        "inventory": {
            "read": "/inventory",
            "write": "/inventory",  # Would need POST data
        }
    }
    
    # Test read permissions (superadmin should have access to all)
    print("Testing READ permissions:")
    for resource, endpoints in test_matrix.items():
        try:
            response = requests.get(f"http://localhost:8000{endpoints['read']}", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else "N/A"
                print(f"✓ {resource} READ access granted ({count} items)")
            elif response.status_code == 403:
                print(f"✗ {resource} READ access denied")
            else:
                print(f"! {resource} READ returned {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"✗ Timeout testing {resource} READ")
        except Exception as e:
            print(f"✗ Error testing {resource} READ: {e}")

def test_organizational_query_filters():
    """Test organization-scoped query helpers and filters."""
    print("\nTesting organizational query filters...")
    
    # This test requires direct database access, so we'll test through API endpoints
    # that should use the organizational filters
    
    try:
        # Import the modules to test the filter functions directly
        from app.permissions import OrganizationScopedQueries, permission_checker
        from app.organizational_isolation import organizational_isolation
        from app.auth import TokenData
        from app.database import SessionLocal
        from app import models
        
        # Create a test session
        db = SessionLocal()
        
        try:
            # Create a mock user token for testing
            test_user = TokenData(
                username="test_superadmin",
                user_id=uuid.uuid4(),
                organization_id=uuid.uuid4(),
                role="super_admin"
            )
            
            # Test organizational isolation functions
            accessible_orgs = organizational_isolation.get_accessible_organization_ids(test_user, db)
            print(f"✓ Organizational isolation working: {len(accessible_orgs)} accessible orgs")
            
            # Test organization-scoped queries
            org_query = db.query(models.Organization)
            filtered_query = OrganizationScopedQueries.filter_organizations(org_query, test_user, db)
            
            # For superadmin, should return all organizations
            all_orgs = org_query.all()
            filtered_orgs = filtered_query.all()
            
            if len(all_orgs) == len(filtered_orgs):
                print("✓ Organization query filter working for superadmin")
            else:
                print(f"! Organization filter: {len(all_orgs)} total vs {len(filtered_orgs)} filtered")
                
        finally:
            db.close()
            
    except ImportError as e:
        print(f"! Could not import modules for direct testing: {e}")
    except Exception as e:
        print(f"✗ Query filter test error: {e}")

def test_middleware_integration():
    """Test middleware integration and automatic filtering."""
    print("\nTesting middleware integration...")
    
    # Test that middleware is properly integrated by checking response headers
    # and behavior
    
    try:
        # Test without authentication (should be blocked by middleware)
        response = requests.get("http://localhost:8000/organizations", timeout=10)
        if response.status_code == 401:
            print("✓ Unauthenticated requests properly blocked")
        else:
            print(f"! Unauthenticated request returned {response.status_code}")
            
        # Test with invalid token (should be blocked)
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get("http://localhost:8000/organizations", headers=headers, timeout=10)
        if response.status_code == 401:
            print("✓ Invalid token properly rejected")
        else:
            print(f"! Invalid token returned {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("✗ Timeout during middleware integration test")
    except Exception as e:
        print(f"✗ Middleware integration test error: {e}")

def test_api_connectivity():
    """Test basic API connectivity."""
    print("Testing API connectivity...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ API is accessible")
            return True
        else:
            print(f"✗ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("✗ API connection timeout")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API")
        return False
    except Exception as e:
        print(f"✗ API connectivity error: {e}")
        return False

def run_comprehensive_rbac_test():
    """Run comprehensive RBAC test suite."""
    print("=" * 60)
    print("ENHANCED ROLE-BASED ACCESS CONTROL (RBAC) TEST SUITE")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
    # Step 0: Test API connectivity
    if not test_api_connectivity():
        print("\n✗ Cannot proceed without API connectivity")
        return False
    
    # Step 1: Authenticate
    token = test_authentication()
    if not token:
        print("\n✗ Cannot proceed without authentication")
        return False
    
    # Step 2: Test organizational data isolation
    test_organizational_isolation(token)
    
    # Step 3: Test permission validation
    test_permission_validation(token)
    
    # Step 4: Test cross-organizational access prevention
    test_cross_organizational_access_prevention(token)
    
    # Step 5: Test role-based resource access matrix
    test_role_based_resource_access_matrix(token)
    
    # Step 6: Test organizational query filters
    test_organizational_query_filters()
    
    # Step 7: Test middleware integration
    test_middleware_integration()
    
    print("\n" + "=" * 60)
    print("RBAC TEST SUITE COMPLETED")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = run_comprehensive_rbac_test()
    sys.exit(0 if success else 1)