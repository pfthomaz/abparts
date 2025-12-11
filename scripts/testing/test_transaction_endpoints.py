#!/usr/bin/env python3

import requests
import json
from datetime import datetime
from decimal import Decimal

# Base URL for the API
BASE_URL = "http://localhost:8000"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/token",
        data={
            "username": "superadmin",
            "password": "superadmin"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Authentication failed: {response.status_code} - {response.text}")
        return None

def test_machine_sale_endpoint():
    """Test the machine sale endpoint"""
    token = get_auth_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # First, let's get some organizations and machines to use in the test
    orgs_response = requests.get(f"{BASE_URL}/organizations", headers=headers)
    if orgs_response.status_code != 200:
        print(f"Failed to get organizations: {orgs_response.status_code} - {orgs_response.text}")
        return
    
    organizations = orgs_response.json()
    print(f"Found {len(organizations)} organizations")
    
    machines_response = requests.get(f"{BASE_URL}/machines", headers=headers)
    if machines_response.status_code != 200:
        print(f"Failed to get machines: {machines_response.status_code} - {machines_response.text}")
        return
    
    machines = machines_response.json()
    print(f"Found {len(machines)} machines")
    
    if len(organizations) < 2 or len(machines) < 1:
        print("Not enough test data available")
        return
    
    # Create a test machine sale
    machine_sale_data = {
        "machine_id": machines[0]["id"],
        "from_organization_id": organizations[0]["id"],
        "to_organization_id": organizations[1]["id"],
        "sale_price": 50000.00,
        "sale_date": datetime.now().isoformat(),
        "notes": "Test machine sale",
        "reference_number": "TEST-SALE-001"
    }
    
    print("Testing machine sale endpoint...")
    response = requests.post(
        f"{BASE_URL}/transactions/machine-sale",
        headers=headers,
        json=machine_sale_data
    )
    
    print(f"Machine sale response: {response.status_code}")
    if response.status_code == 201:
        print("Machine sale created successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Machine sale failed: {response.text}")

def test_part_order_endpoint():
    """Test the part order endpoint"""
    token = get_auth_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Get organizations and parts for testing
    orgs_response = requests.get(f"{BASE_URL}/organizations", headers=headers)
    parts_response = requests.get(f"{BASE_URL}/parts", headers=headers)
    
    if orgs_response.status_code != 200 or parts_response.status_code != 200:
        print("Failed to get test data for part order")
        return
    
    organizations = orgs_response.json()
    parts = parts_response.json()
    
    if len(organizations) < 2 or len(parts) < 1:
        print("Not enough test data for part order")
        return
    
    # Create a test part order
    part_order_data = {
        "from_organization_id": organizations[0]["id"],
        "to_organization_id": organizations[1]["id"],
        "order_items": [
            {
                "part_id": parts[0]["id"],
                "quantity": 10.0,
                "unit_price": 25.50,
                "notes": "Test part order item"
            }
        ],
        "order_date": datetime.now().isoformat(),
        "expected_delivery_date": datetime.now().isoformat(),
        "notes": "Test part order",
        "reference_number": "TEST-ORDER-001"
    }
    
    print("Testing part order endpoint...")
    response = requests.post(
        f"{BASE_URL}/transactions/part-order",
        headers=headers,
        json=part_order_data
    )
    
    print(f"Part order response: {response.status_code}")
    if response.status_code == 201:
        print("Part order created successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Part order failed: {response.text}")

def test_part_usage_endpoint():
    """Test the part usage endpoint"""
    token = get_auth_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Get machines, warehouses, and parts for testing
    machines_response = requests.get(f"{BASE_URL}/machines", headers=headers)
    warehouses_response = requests.get(f"{BASE_URL}/warehouses", headers=headers)
    parts_response = requests.get(f"{BASE_URL}/parts", headers=headers)
    
    if machines_response.status_code != 200 or warehouses_response.status_code != 200 or parts_response.status_code != 200:
        print("Failed to get test data for part usage")
        return
    
    machines = machines_response.json()
    warehouses = warehouses_response.json()
    parts = parts_response.json()
    
    if len(machines) < 1 or len(warehouses) < 1 or len(parts) < 1:
        print("Not enough test data for part usage")
        return
    
    # Create a test part usage
    part_usage_data = {
        "machine_id": machines[0]["id"],
        "from_warehouse_id": warehouses[0]["id"],
        "usage_items": [
            {
                "part_id": parts[0]["id"],
                "quantity": 2.0,
                "notes": "Test part usage item"
            }
        ],
        "usage_date": datetime.now().isoformat(),
        "service_type": "50h",
        "machine_hours": 50.5,
        "notes": "Test part usage",
        "reference_number": "TEST-USAGE-001"
    }
    
    print("Testing part usage endpoint...")
    response = requests.post(
        f"{BASE_URL}/transactions/part-usage",
        headers=headers,
        json=part_usage_data
    )
    
    print(f"Part usage response: {response.status_code}")
    if response.status_code == 201:
        print("Part usage created successfully!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Part usage failed: {response.text}")

if __name__ == "__main__":
    print("Testing Transaction Management API Extensions...")
    print("=" * 50)
    
    test_machine_sale_endpoint()
    print("\n" + "=" * 50)
    
    test_part_order_endpoint()
    print("\n" + "=" * 50)
    
    test_part_usage_endpoint()
    print("\n" + "=" * 50)
    
    print("Testing completed!")