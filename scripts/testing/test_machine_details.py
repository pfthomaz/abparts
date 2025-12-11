#!/usr/bin/env python3
import requests
import json

# First login to get a token
print("Getting authentication token...")
login_url = "http://localhost:8000/token"
login_data = {
    "username": "superadmin",
    "password": "superadmin"
}

try:
    login_response = requests.post(login_url, data=login_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print("✅ Login successful!")
        
        # Test machine details endpoint
        print("\nTesting machine details endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test machine ID 1
        machine_url = "http://localhost:8000/machines/1"
        machine_response = requests.get(machine_url, headers=headers)
        
        print(f"Machine Details Status: {machine_response.status_code}")
        if machine_response.status_code == 200:
            print("✅ Machine details retrieved successfully!")
            machine_data = machine_response.json()
            print(f"Machine: {machine_data.get('name', 'N/A')} (Model: {machine_data.get('model_type', 'N/A')})")
        else:
            print("❌ Machine details failed!")
            print(f"Response: {machine_response.text}")
            
        # Test machine maintenance endpoint
        print("\nTesting machine maintenance endpoint...")
        maintenance_url = "http://localhost:8000/machines/1/maintenance"
        maintenance_response = requests.get(maintenance_url, headers=headers)
        
        print(f"Maintenance Status: {maintenance_response.status_code}")
        if maintenance_response.status_code == 200:
            print("✅ Machine maintenance retrieved successfully!")
            maintenance_data = maintenance_response.json()
            print(f"Maintenance records: {len(maintenance_data)}")
        else:
            print("❌ Machine maintenance failed!")
            print(f"Response: {maintenance_response.text}")
            
        # Test machine usage endpoint
        print("\nTesting machine usage endpoint...")
        usage_url = "http://localhost:8000/machines/1/usage"
        usage_response = requests.get(usage_url, headers=headers)
        
        print(f"Usage Status: {usage_response.status_code}")
        if usage_response.status_code == 200:
            print("✅ Machine usage retrieved successfully!")
            usage_data = usage_response.json()
            print(f"Usage records: {len(usage_data)}")
        else:
            print("❌ Machine usage failed!")
            print(f"Response: {usage_response.text}")
            
        # Test machine compatibility endpoint
        print("\nTesting machine compatibility endpoint...")
        compatibility_url = "http://localhost:8000/machines/1/compatibility"
        compatibility_response = requests.get(compatibility_url, headers=headers)
        
        print(f"Compatibility Status: {compatibility_response.status_code}")
        if compatibility_response.status_code == 200:
            print("✅ Machine compatibility retrieved successfully!")
            compatibility_data = compatibility_response.json()
            print(f"Compatible parts: {len(compatibility_data)}")
        else:
            print("❌ Machine compatibility failed!")
            print(f"Response: {compatibility_response.text}")
            
    else:
        print("❌ Login failed!")
        print(f"Response: {login_response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")