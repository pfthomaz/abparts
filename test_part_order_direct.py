#!/usr/bin/env python3

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8000"
TOKEN = "fhQOZXMspmRklLh8Oj91A7psFvdnm_umOljwZ-nFtS0"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Get organizations and parts for testing
orgs_response = requests.get(f"{BASE_URL}/organizations", headers=headers)
parts_response = requests.get(f"{BASE_URL}/parts", headers=headers)

print("Organizations:", orgs_response.status_code)
print("Parts:", parts_response.status_code)

if orgs_response.status_code == 200 and parts_response.status_code == 200:
    organizations = orgs_response.json()
    parts = parts_response.json()
    
    print(f"Found {len(organizations)} organizations and {len(parts)} parts")
    
    if len(organizations) >= 2 and len(parts) >= 1:
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
        print("Request data:", json.dumps(part_order_data, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/transactions/part-order",
            headers=headers,
            json=part_order_data
        )
        
        print(f"Part order response: {response.status_code}")
        print("Response:", response.text)
    else:
        print("Not enough test data")
else:
    print("Failed to get test data")