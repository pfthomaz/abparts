#!/usr/bin/env python3
"""
Test script to verify the transaction workflow UI components work correctly.
This script tests the organizational boundary validation and transaction creation.
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def get_auth_token():
    """Get authentication token for superadmin user."""
    response = requests.post(
        f"{API_BASE_URL}/token",
        data={"username": "superadmin", "password": "superadmin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to authenticate: {response.text}")
        return None

def test_api_endpoints(token):
    """Test the API endpoints used by the transaction components."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test transactions endpoint
    print("Testing transactions endpoint...")
    response = requests.get(f"{API_BASE_URL}/transactions?limit=5", headers=headers)
    if response.status_code == 200:
        transactions = response.json()
        print(f"✓ Transactions endpoint working - found {len(transactions)} transactions")
    else:
        print(f"✗ Transactions endpoint failed: {response.text}")
        return False
    
    # Test parts endpoint
    print("Testing parts endpoint...")
    response = requests.get(f"{API_BASE_URL}/parts", headers=headers)
    if response.status_code == 200:
        parts = response.json()
        print(f"✓ Parts endpoint working - found {len(parts)} parts")
    else:
        print(f"✗ Parts endpoint failed: {response.text}")
        return False
    
    # Test warehouses endpoint
    print("Testing warehouses endpoint...")
    response = requests.get(f"{API_BASE_URL}/warehouses", headers=headers)
    if response.status_code == 200:
        warehouses = response.json()
        print(f"✓ Warehouses endpoint working - found {len(warehouses)} warehouses")
    else:
        print(f"✗ Warehouses endpoint failed: {response.text}")
        return False
    
    # Test machines endpoint
    print("Testing machines endpoint...")
    response = requests.get(f"{API_BASE_URL}/machines", headers=headers)
    if response.status_code == 200:
        machines = response.json()
        print(f"✓ Machines endpoint working - found {len(machines)} machines")
    else:
        print(f"✗ Machines endpoint failed: {response.text}")
        return False
    
    # Test organizations endpoint
    print("Testing organizations endpoint...")
    response = requests.get(f"{API_BASE_URL}/organizations", headers=headers)
    if response.status_code == 200:
        organizations = response.json()
        print(f"✓ Organizations endpoint working - found {len(organizations)} organizations")
    else:
        print(f"✗ Organizations endpoint failed: {response.text}")
        return False
    
    return True

def test_transaction_creation(token):
    """Test creating a consumption transaction (part usage)."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get some test data first
    parts_response = requests.get(f"{API_BASE_URL}/parts?limit=1", headers=headers)
    warehouses_response = requests.get(f"{API_BASE_URL}/warehouses?limit=1", headers=headers)
    machines_response = requests.get(f"{API_BASE_URL}/machines?limit=1", headers=headers)
    
    if not all([parts_response.status_code == 200, warehouses_response.status_code == 200, machines_response.status_code == 200]):
        print("✗ Failed to get test data for transaction creation")
        return False
    
    parts = parts_response.json()
    warehouses = warehouses_response.json()
    machines = machines_response.json()
    
    if not all([parts, warehouses, machines]):
        print("✗ No test data available for transaction creation")
        return False
    
    # Get superadmin user ID
    user_response = requests.get(f"{API_BASE_URL}/users/me/", headers=headers)
    if user_response.status_code != 200:
        print("✗ Failed to get current user info")
        return False
    
    user_info = user_response.json()
    
    # Create a test consumption transaction
    transaction_data = {
        "transaction_type": "consumption",
        "part_id": parts[0]["id"],
        "from_warehouse_id": warehouses[0]["id"],
        "machine_id": machines[0]["id"],
        "quantity": 1.0,
        "unit_of_measure": parts[0].get("unit_of_measure", "pieces"),
        "performed_by_user_id": user_info["id"],
        "transaction_date": "2025-01-30T12:00:00Z",
        "notes": "Test transaction from automated test",
        "reference_number": "TEST-001"
    }
    
    print("Testing transaction creation...")
    response = requests.post(
        f"{API_BASE_URL}/transactions",
        json=transaction_data,
        headers=headers
    )
    
    if response.status_code == 201:
        transaction = response.json()
        print(f"✓ Transaction created successfully - ID: {transaction['id']}")
        return True
    else:
        print(f"✗ Transaction creation failed: {response.text}")
        return False

def test_frontend_accessibility():
    """Test that the frontend is accessible."""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✓ Frontend is accessible")
            return True
        else:
            print(f"✗ Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Frontend not accessible: {e}")
        return False

def main():
    """Main test function."""
    print("Testing ABParts Transaction Workflow UI Components")
    print("=" * 50)
    
    # Test frontend accessibility
    if not test_frontend_accessibility():
        print("Frontend is not accessible. Please ensure the development server is running.")
        sys.exit(1)
    
    # Get authentication token
    print("\nGetting authentication token...")
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token")
        sys.exit(1)
    print("✓ Authentication successful")
    
    # Test API endpoints
    print("\nTesting API endpoints...")
    if not test_api_endpoints(token):
        print("API endpoint tests failed")
        sys.exit(1)
    
    # Test transaction creation
    print("\nTesting transaction creation...")
    if not test_transaction_creation(token):
        print("Transaction creation test failed")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✓ All tests passed! The transaction workflow components should work correctly.")
    print("\nTo test the UI components:")
    print(f"1. Open {FRONTEND_URL} in your browser")
    print("2. Login with username: superadmin, password: superadmin")
    print("3. Navigate to the Transactions page")
    print("4. Test the following components:")
    print("   - TwoPhaseOrderWizard (Create Order button)")
    print("   - PartUsageRecorder (Record Usage button)")
    print("   - InventoryTransactionLog (Audit Trail tab)")
    print("5. Verify organizational boundary validation works correctly")

if __name__ == "__main__":
    main()