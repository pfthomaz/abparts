#!/usr/bin/env python3
"""
Verify that the API correctly filters machines by organization for admin users.
This script simulates API calls to verify the backend permission checking works.
"""

import requests
import json

API_BASE = "http://localhost:8000"

def login(username, password):
    """Login and get access token."""
    response = requests.post(
        f"{API_BASE}/token",
        data={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def get_machines(token):
    """Get machines list with authentication."""
    response = requests.get(
        f"{API_BASE}/machines/",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Get machines failed: {response.status_code} - {response.text}")
        return None

def get_current_user(token):
    """Get current user info."""
    response = requests.get(
        f"{API_BASE}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Get user failed: {response.status_code} - {response.text}")
        return None

def test_user(username, password, expected_machine_count, description):
    """Test a specific user's machine access."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"{'='*60}")
    
    # Login
    print(f"1. Logging in as '{username}'...")
    token = login(username, password)
    if not token:
        print("   ❌ Login failed!")
        return False
    print("   ✅ Login successful")
    
    # Get user info
    print(f"2. Getting user info...")
    user = get_current_user(token)
    if not user:
        print("   ❌ Failed to get user info!")
        return False
    print(f"   ✅ User: {user['username']}")
    print(f"      Role: {user['role']}")
    print(f"      Organization: {user.get('organization', {}).get('name', 'Unknown')}")
    
    # Get machines
    print(f"3. Getting machines list...")
    machines = get_machines(token)
    if machines is None:
        print("   ❌ Failed to get machines!")
        return False
    
    actual_count = len(machines)
    print(f"   Machines returned: {actual_count}")
    
    # Verify count
    if actual_count == expected_machine_count:
        print(f"   ✅ PASS: Got expected {expected_machine_count} machines")
        
        # Show machine details
        if machines:
            print(f"\n   Machines:")
            for m in machines:
                print(f"      - {m['name']} (S/N: {m['serial_number']})")
        
        return True
    else:
        print(f"   ❌ FAIL: Expected {expected_machine_count} machines, got {actual_count}")
        
        # Show what we got
        if machines:
            print(f"\n   Machines returned:")
            for m in machines:
                print(f"      - {m['name']} (S/N: {m['serial_number']})")
        
        return False

def main():
    print("\n" + "="*60)
    print("Machine Security Fix - API Verification")
    print("="*60)
    print("\nThis script verifies that the backend API correctly filters")
    print("machines by organization for admin users.")
    
    results = []
    
    # Test 1: Super admin should see all machines
    results.append(test_user(
        username="dthomaz",
        password="password123",  # Update with actual password
        expected_machine_count=11,
        description="Super Admin (should see ALL 11 machines)"
    ))
    
    # Test 2: Kefalonia admin should see only their machines
    results.append(test_user(
        username="lefteris",
        password="password123",  # Update with actual password
        expected_machine_count=5,
        description="Kefalonia Admin (should see ONLY 5 machines)"
    ))
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Backend filtering is working correctly.")
    else:
        print("❌ Some tests failed! Backend filtering may have issues.")
    
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
