#!/usr/bin/env python3
"""
Test organization creation after fixing enum issues
"""
import requests
import json

def test_organization_creation():
    print("🏢 Testing Organization Creation After Enum Fix")
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
        
        # Test organization creation
        print("\n2. Testing organization creation...")
        
        org_data = {
            "name": "Test Customer Organization",
            "organization_type": "customer",
            "address": "123 Test Street, Test City",
            "contact_info": "test@example.com, +1234567890"
        }
        
        print(f"Creating organization: {org_data['name']}")
        
        create_response = requests.post(
            "http://localhost:8000/organizations/",
            json=org_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Organization creation status: {create_response.status_code}")
        if create_response.status_code == 201:
            created_org = create_response.json()
            print("✅ Organization created successfully!")
            print(f"   - ID: {created_org.get('id')}")
            print(f"   - Name: {created_org.get('name')}")
            print(f"   - Type: {created_org.get('organization_type')}")
            print(f"   - Address: {created_org.get('address')}")
        else:
            print(f"❌ Organization creation failed: {create_response.text}")
            try:
                error_data = create_response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                pass
                
        # Test getting organizations list
        print("\n3. Testing organizations list...")
        list_response = requests.get(
            "http://localhost:8000/organizations/",
            headers=headers,
            timeout=10
        )
        
        if list_response.status_code == 200:
            orgs = list_response.json()
            print(f"✅ Found {len(orgs)} organizations")
            for org in orgs:
                print(f"   - {org.get('name')} ({org.get('organization_type')})")
        else:
            print(f"❌ Organizations list failed: {list_response.status_code}")
                
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_organization_creation()