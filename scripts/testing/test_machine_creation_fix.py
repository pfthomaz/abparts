#!/usr/bin/env python3

import requests
import json

def test_machine_creation():
    """Test machine creation with the fix applied"""
    
    # First, get organizations to find a customer organization
    orgs_url = "http://localhost:8000/organizations/"
    
    try:
        # Get auth token (you'll need to replace this with a valid token)
        token = "YOUR_TOKEN_HERE"  # Replace with actual token
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Get organizations
        response = requests.get(orgs_url, headers=headers)
        if response.status_code == 200:
            organizations = response.json()
            
            # Find a customer organization
            customer_org = None
            for org in organizations:
                if org.get('organization_type') == 'customer':
                    customer_org = org
                    break
            
            if not customer_org:
                print("❌ No customer organization found")
                return False
            
            print(f"🏢 Found customer organization: {customer_org['name']} (ID: {customer_org['id']})")
            
            # Test machine creation
            machine_url = "http://localhost:8000/machines/"
            test_machine = {
                "customer_organization_id": customer_org['id'],
                "model_type": "V4.0",
                "name": "Test Machine Fix",
                "serial_number": f"TEST-{int(time.time())}",  # Unique serial
                "status": "active",  # This should be filtered out
                "location": "Test Location",  # This should be filtered out
                "notes": "Test notes"  # This should be filtered out
            }
            
            print("🧪 Testing machine creation with filtered fields...")
            print(f"📤 Sending: {json.dumps(test_machine, indent=2)}")
            
            response = requests.post(machine_url, json=test_machine, headers=headers)
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 201:
                print("✅ SUCCESS! Machine created successfully")
                print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
                return True
            else:
                print(f"❌ FAILED! Status: {response.status_code}")
                print(f"📄 Error: {response.text}")
                return False
                
        else:
            print(f"❌ Failed to get organizations: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Make sure the backend is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    import time
    test_machine_creation()