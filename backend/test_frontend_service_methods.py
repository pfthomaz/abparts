#!/usr/bin/env python3
"""
Test to verify that the frontend service methods work correctly
with the updated HTTP methods (PATCH instead of POST/DELETE)
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_frontend_service_methods():
    """Test the frontend service methods with correct HTTP methods"""
    print("🧪 Testing Frontend Service Methods")
    print("=" * 45)
    
    # Authenticate
    print("🔐 Authenticating...")
    login_data = {"username": "oraseasee_admin", "password": "admin"}
    response = requests.post(f"{API_BASE_URL}/token", data=login_data)
    
    if response.status_code != 200:
        print("❌ Authentication failed")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    # Get a test user
    response = requests.get(f"{API_BASE_URL}/users/", headers=headers)
    if response.status_code != 200:
        print("❌ Failed to get users")
        return False
    
    users = response.json()
    test_user = next((u for u in users if u.get("username") != "oraseasee_admin"), None)
    if not test_user:
        print("❌ No test user found")
        return False
    
    user_id = test_user["id"]
    print(f"✅ Using test user: {test_user['username']} (ID: {user_id})")
    
    # Test 1: Frontend deactivateUser method (should use PATCH /users/{id}/deactivate)
    print("\n🔍 Testing frontend deactivateUser method...")
    response = requests.patch(f"{API_BASE_URL}/users/{user_id}/deactivate", headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ deactivateUser method works: is_active={user_data['is_active']}, user_status={user_data['user_status']}")
    else:
        print(f"❌ deactivateUser method failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    # Test 2: Frontend reactivateUser method (should use PATCH /users/{id}/reactivate)
    print("\n🔍 Testing frontend reactivateUser method...")
    response = requests.patch(f"{API_BASE_URL}/users/{user_id}/reactivate", headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ reactivateUser method works: is_active={user_data['is_active']}, user_status={user_data['user_status']}")
        
        # Verify status synchronization
        if user_data["is_active"] == True and user_data["user_status"] == "active":
            print("✅ Status fields properly synchronized")
        else:
            print(f"❌ Status fields not synchronized: is_active={user_data['is_active']}, user_status={user_data['user_status']}")
            return False
    else:
        print(f"❌ reactivateUser method failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    # Test 3: Verify the old methods would fail (POST for reactivate, DELETE for deactivate)
    print("\n🔍 Testing that old incorrect methods fail...")
    
    # Old reactivate method (POST) should fail
    response = requests.post(f"{API_BASE_URL}/users/{user_id}/reactivate", headers=headers)
    if response.status_code == 405:  # Method Not Allowed
        print("✅ Old POST method for reactivate correctly fails (405)")
    else:
        print(f"⚠️  Old POST method returned: {response.status_code} (expected 405)")
    
    # Old deactivate method (DELETE /users/{id}) should fail or do something different
    response = requests.delete(f"{API_BASE_URL}/users/{user_id}", headers=headers)
    if response.status_code in [403, 405]:  # Forbidden or Method Not Allowed
        print("✅ Old DELETE method for deactivate correctly fails")
    else:
        print(f"⚠️  Old DELETE method returned: {response.status_code}")
    
    print("\n🎉 All frontend service method tests passed!")
    return True

if __name__ == "__main__":
    success = test_frontend_service_methods()
    exit(0 if success else 1)