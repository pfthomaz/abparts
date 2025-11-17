#!/usr/bin/env python3
"""
Test user creation after fixing enum issues
"""
import requests
import json

def test_user_creation():
    print("👤 Testing User Creation After Enum Fix")
    print("=" * 50)
    
    try:
        # Login first
        print("1. Authenticating...")
        login_response = requests.post(
            "http://localhost:8000/token",
            data={"username": "superadmin", "password": "superadmin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("✅ Authentication successful")
        
        # Test /users/me endpoint first
        print("\n2. Testing user details endpoint...")
        me_response = requests.get(
            "http://localhost:8000/users/me/",
            headers=headers,
            timeout=10
        )
        
        print(f"User details status: {me_response.status_code}")
        if me_response.status_code == 200:
            user_data = me_response.json()
            print(f"✅ User details retrieved successfully")
            print(f"   - Username: {user_data.get('username')}")
            print(f"   - Role: {user_data.get('role')}")
            print(f"   - Organization ID: {user_data.get('organization_id')}")
        else:
            print(f"❌ User details failed: {me_response.text}")
            
        # Test user creation
        print("\n3. Testing user creation...")
        
        # First get the current user's organization ID
        if me_response.status_code == 200:
            current_user = me_response.json()
            org_id = current_user.get('organization_id')
            
            user_data = {
                "username": "testuser001",
                "email": "testuser001@example.com",
                "name": "Test User 001",
                "password": "testpassword123",
                "role": "user",
                "organization_id": org_id
            }
            
            print(f"Creating user: {user_data['username']} in org: {org_id}")
            
            create_response = requests.post(
                "http://localhost:8000/users/",
                json=user_data,
                headers=headers,
                timeout=10
            )
            
            print(f"User creation status: {create_response.status_code}")
            if create_response.status_code == 201:
                created_user = create_response.json()
                print("✅ User created successfully!")
                print(f"   - ID: {created_user.get('id')}")
                print(f"   - Username: {created_user.get('username')}")
                print(f"   - Role: {created_user.get('role')}")
            else:
                print(f"❌ User creation failed: {create_response.text}")
                try:
                    error_data = create_response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    pass
        else:
            print("⚠️  Skipping user creation test - couldn't get current user details")
                
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_user_creation()