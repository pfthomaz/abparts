#!/usr/bin/env python3
"""
Comprehensive Security Test for Backend Organization Filtering
Tests that the backend correctly filters machines by organization
"""

import requests
import sys

API_BASE = "http://localhost:8000"

# Test users
SUPER_ADMIN = {"username": "dthomaz", "password": "amFT1999!"}
KEFALONIA_ADMIN = {"username": "Zisis", "password": "letmein"}

def login(username, password):
    """Login and return token"""
    response = requests.post(
        f"{API_BASE}/token",
        data={"username": username, "password": password}
    )
    if response.status_code != 200:
        print(f"❌ Login failed for {username}: {response.text}")
        return None
    
    token = response.json()["access_token"]
    print(f"✅ Logged in as {username}")
    return token

def get_machines(token):
    """Get machines for current user"""
    response = requests.get(
        f"{API_BASE}/machines/",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code != 200:
        print(f"❌ Failed to get machines: {response.text}")
        return []
    
    machines = response.json()
    return machines

def test_super_admin_sees_all():
    """Test that super admin sees all machines"""
    print("\n" + "="*60)
    print("TEST 1: Super Admin Should See All Machines")
    print("="*60)
    
    token = login(SUPER_ADMIN["username"], SUPER_ADMIN["password"])
    if not token:
        return False
    
    machines = get_machines(token)
    print(f"   Machines returned: {len(machines)}")
    
    # Should see all 11 machines
    if len(machines) != 11:
        print(f"❌ FAIL: Expected 11 machines, got {len(machines)}")
        return False
    
    # Show organizations
    orgs = set(m['customer_organization_id'] for m in machines)
    print(f"   Organizations: {len(orgs)} different orgs")
    
    print("✅ PASS: Super admin sees all machines")
    return True

def test_kefalonia_admin_sees_only_their_org():
    """Test that Kefalonia admin sees only their org's machines"""
    print("\n" + "="*60)
    print("TEST 2: Kefalonia Admin Should See Only Their Org's Machines")
    print("="*60)
    
    token = login(KEFALONIA_ADMIN["username"], KEFALONIA_ADMIN["password"])
    if not token:
        return False
    
    machines = get_machines(token)
    print(f"   Machines returned: {len(machines)}")
    
    # Should see only 5 machines (Kefalonia's machines)
    if len(machines) != 5:
        print(f"❌ FAIL: Expected 5 machines, got {len(machines)}")
        print("   Machines:")
        for m in machines:
            print(f"     - {m['name']} (org: {m['customer_organization_id']})")
        return False
    
    # All machines should belong to same org
    orgs = set(m['customer_organization_id'] for m in machines)
    if len(orgs) != 1:
        print(f"❌ FAIL: Machines belong to {len(orgs)} different orgs (should be 1)")
        return False
    
    kefalonia_org_id = list(orgs)[0]
    print(f"   Kefalonia Org ID: {kefalonia_org_id}")
    print("✅ PASS: Kefalonia admin sees only their org's machines")
    return True

def test_cross_user_isolation():
    """Test that switching users doesn't leak data"""
    print("\n" + "="*60)
    print("TEST 3: Cross-User Data Isolation (Backend)")
    print("="*60)
    
    # Login as super admin
    print("\n1. Login as super admin...")
    super_token = login(SUPER_ADMIN["username"], SUPER_ADMIN["password"])
    if not super_token:
        return False
    
    super_machines = get_machines(super_token)
    print(f"   Super admin sees: {len(super_machines)} machines")
    
    if len(super_machines) != 11:
        print(f"❌ FAIL: Super admin should see 11 machines, got {len(super_machines)}")
        return False
    
    # Login as Kefalonia admin
    print("\n2. Login as Kefalonia admin...")
    kef_token = login(KEFALONIA_ADMIN["username"], KEFALONIA_ADMIN["password"])
    if not kef_token:
        return False
    
    kef_machines = get_machines(kef_token)
    print(f"   Kefalonia admin sees: {len(kef_machines)} machines")
    
    # Verify Kefalonia admin doesn't see super admin's data
    if len(kef_machines) != 5:
        print(f"❌ FAIL: Kefalonia admin sees {len(kef_machines)} machines instead of 5")
        print("   This indicates backend filtering is NOT working!")
        return False
    
    # Verify all machines belong to same org
    orgs = set(m['customer_organization_id'] for m in kef_machines)
    if len(orgs) != 1:
        print(f"❌ FAIL: Kefalonia admin sees machines from {len(orgs)} orgs (should be 1)")
        return False
    
    print("✅ PASS: Backend correctly filters by organization")
    return True

def main():
    """Run all security tests"""
    print("\n" + "="*60)
    print("BACKEND SECURITY TEST SUITE")
    print("Testing Organization-Based Filtering")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Super Admin Access", test_super_admin_sees_all()))
    results.append(("Org-Scoped Access", test_kefalonia_admin_sees_only_their_org()))
    results.append(("Cross-User Isolation", test_cross_user_isolation()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL BACKEND SECURITY TESTS PASSED!")
        print("\nThe backend is correctly filtering data by organization.")
        print("The frontend caching security fix is now in place.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} SECURITY TEST(S) FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
