#!/usr/bin/env python3

import requests
import json
import uuid
from datetime import datetime

# Test the Machine Management API Implementation

def get_auth_token():
    """Get authentication token for superadmin user"""
    url = "http://localhost:8000/token"
    data = {
        "username": "superadmin",
        "password": "superadmin"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"Authentication failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting auth token: {e}")
        return None

def test_machine_endpoints():
    """Test machine management endpoints"""
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("=== Testing Machine Management API ===")
    
    # Test 1: Get all machines
    print("\n1. Testing GET /machines")
    try:
        response = requests.get("http://localhost:8000/machines/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            machines = response.json()
            print(f"Found {len(machines)} machines")
            if machines:
                machine_id = machines[0]["id"]
                print(f"First machine ID: {machine_id}")
                
                # Test 2: Get machine hours history
                print(f"\n2. Testing GET /machines/{machine_id}/hours")
                hours_response = requests.get(f"http://localhost:8000/machines/{machine_id}/hours", headers=headers)
                print(f"Status: {hours_response.status_code}")
                if hours_response.status_code == 200:
                    hours_history = hours_response.json()
                    print(f"Found {len(hours_history)} hours records")
                else:
                    print(f"Error: {hours_response.text}")
                
                # Test 3: Record machine hours
                print(f"\n3. Testing POST /machines/{machine_id}/hours")
                hours_data = {
                    "hours_value": 150.5,
                    "recorded_date": datetime.now().isoformat(),
                    "notes": "Test hours recording from API test"
                }
                hours_create_response = requests.post(
                    f"http://localhost:8000/machines/{machine_id}/hours", 
                    headers=headers,
                    json=hours_data
                )
                print(f"Status: {hours_create_response.status_code}")
                if hours_create_response.status_code == 201:
                    created_hours = hours_create_response.json()
                    print(f"Created hours record: {created_hours['id']}")
                else:
                    print(f"Error: {hours_create_response.text}")
                
                # Test 4: Update machine name
                print(f"\n4. Testing PUT /machines/{machine_id}/name")
                name_data = {
                    "name": f"Updated Machine Name - {datetime.now().strftime('%H:%M:%S')}"
                }
                name_response = requests.put(
                    f"http://localhost:8000/machines/{machine_id}/name",
                    headers=headers,
                    json=name_data
                )
                print(f"Status: {name_response.status_code}")
                if name_response.status_code == 200:
                    updated_machine = name_response.json()
                    print(f"Updated machine name: {updated_machine['name']}")
                else:
                    print(f"Error: {name_response.text}")
                
        else:
            print(f"Error getting machines: {response.text}")
    except Exception as e:
        print(f"Error testing machine endpoints: {e}")
    
    # Test 5: Get supported model types
    print("\n5. Testing GET /machines/supported-model-types")
    try:
        response = requests.get("http://localhost:8000/machines/supported-model-types", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            model_types = response.json()
            print(f"Supported model types: {model_types}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_machine_endpoints()