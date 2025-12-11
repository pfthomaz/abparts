#!/usr/bin/env python3

import requests
import json

# Test organization creation with country field
def test_organization_creation():
    url = "http://localhost:8000/organizations/"
    
    # Test data with country field
    test_org = {
        "name": "Test Organization Fix",
        "organization_type": "customer",
        "country": "GR",
        "address": "123 Test Street",
        "contact_info": "test@example.com"
    }
    
    print("🧪 Testing organization creation with country field...")
    print(f"📤 Sending: {json.dumps(test_org, indent=2)}")
    
    try:
        response = requests.post(url, json=test_org)
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ SUCCESS! Organization created successfully")
            print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Make sure the backend is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_organization_creation()