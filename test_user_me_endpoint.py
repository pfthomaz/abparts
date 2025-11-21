#!/usr/bin/env python3
"""
Test script to verify /users/me/ endpoint returns organization data
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_users_me():
    """Test the /users/me/ endpoint"""
    
    # First login
    print("1. Logging in...")
    login_response = requests.post(
        f"{API_URL}/token",
        data={
            "username": "admin",  # Change to your username
            "password": "admin123"  # Change to your password
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    print(f"✅ Login successful! Token: {token[:50]}...")
    
    # Get user info
    print("\n2. Getting user info from /users/me/...")
    me_response = requests.get(
        f"{API_URL}/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if me_response.status_code != 200:
        print(f"❌ Failed to get user info: {me_response.status_code}")
        print(me_response.text)
        return
    
    user_data = me_response.json()
    print(f"✅ Got user data!")
    print(f"\nUser: {user_data.get('username')}")
    print(f"Name: {user_data.get('name')}")
    print(f"Email: {user_data.get('email')}")
    print(f"Role: {user_data.get('role')}")
    print(f"Profile Photo: {user_data.get('profile_photo_url', 'None')}")
    
    # Check organization
    if 'organization' in user_data and user_data['organization']:
        org = user_data['organization']
        print(f"\n✅ Organization data found!")
        print(f"Organization Name: {org.get('name')}")
        print(f"Organization Type: {org.get('organization_type')}")
        print(f"Organization Logo: {org.get('logo_url', 'None')}")
    else:
        print(f"\n❌ No organization data in response!")
        print(f"Organization ID: {user_data.get('organization_id')}")
    
    print(f"\n📄 Full response:")
    print(json.dumps(user_data, indent=2))

if __name__ == "__main__":
    test_users_me()
