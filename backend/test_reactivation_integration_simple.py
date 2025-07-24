#!/usr/bin/env python3
"""
Simple integration test to verify the reactivation endpoint works correctly
with the updated CRUD function.
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_reactivation_integration():
    """Test the complete reactivation flow"""
    print("🧪 Testing User Reactivation Integration")
    print("=" * 50)
    
    # Step 1: Authenticate
    login_data = {"username": "oraseasee_admin", "password": "admin"}
    response = requests.post(f"{API_BASE_URL}/token", data=login_data)
    
    if response.status_code != 200:
        print("❌ Authentication failed")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    # Step 2: Get an existing user to test with
    response = requests.get(f"{API_BASE_URL}/users/", headers=headers)
    if response.status_code != 200:
        print("❌ Failed to get users")
        return False
    
    users = response.json()
    test_user = None
    for user in users:
        if user.get("username") != "oraseasee_admin":  # Don't test with admin user
            test_user = user
            break
    
    if not test_user:
        print("❌ No suitable test user found")
        return False
    
    user_id = test_user["id"]
    print(f"✅ Using test user: {test_user['username']} (ID: {user_id})")
    
    # Step 3: Deactivate the user
    response = requests.patch(f"{API_BASE_URL}/users/{user_id}/deactivate", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to deactivate user: {response.status_code}")
        return False
    
    deactivated_user = response.json()
    print(f"✅ User deactivated: is_active={deactivated_user['is_active']}, user_status={deactivated_user['user_status']}")
    
    # Step 4: Reactivate the user
    response = requests.patch(f"{API_BASE_URL}/users/{user_id}/reactivate", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to reactivate user: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    reactivated_user = response.json()
    print(f"✅ User reactivated: is_active={reactivated_user['is_active']}, user_status={reactivated_user['user_status']}")
    
    # Step 5: Verify status synchronization
    if reactivated_user["is_active"] == True and reactivated_user["user_status"] == "active":
        print("✅ Status fields are properly synchronized")
        print("🎉 Integration test PASSED!")
        return True
    else:
        print("❌ Status fields are not synchronized")
        print(f"   Expected: is_active=True, user_status=active")
        print(f"   Actual: is_active={reactivated_user['is_active']}, user_status={reactivated_user['user_status']}")
        return False

if __name__ == "__main__":
    success = test_reactivation_integration()
    exit(0 if success else 1)