#!/usr/bin/env python3
"""
Test script to verify stock adjustment functionality is working correctly.
This script will help debug the issue where stock adjustments don't update the current stock value.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your API is running on a different port
USERNAME = "superadmin"  # Using the superadmin user from init.sql
PASSWORD = "superadmin"  # Default password from init.sql

def get_auth_token():
    """Get authentication token"""
    # Try form data first (as expected by FastAPI OAuth2PasswordRequestForm)
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    print(f"Attempting login with username: {USERNAME}")
    
    # Try with form data
    response = requests.post(f"{BASE_URL}/token", data=login_data)
    print(f"Login response status: {response.status_code}")
    print(f"Login response headers: {dict(response.headers)}")
    print(f"Login response text: {response.text}")
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"Login successful, token data: {token_data}")
        return token_data.get("access_token")
    else:
        print(f"Failed to login: {response.status_code} - {response.text}")
        return None

def get_warehouses(token):
    """Get list of warehouses"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/warehouses", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get warehouses: {response.status_code} - {response.text}")
        return []

def get_warehouse_inventory(warehouse_id, token):
    """Get inventory for a specific warehouse"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/inventory/warehouse/{warehouse_id}", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get warehouse inventory: {response.status_code} - {response.text}")
        return []

def create_stock_adjustment(warehouse_id, part_id, quantity_change, reason, token):
    """Create a stock adjustment"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    adjustment_data = {
        "part_id": part_id,
        "quantity_change": quantity_change,
        "reason": reason,
        "notes": f"Test adjustment at {datetime.now().isoformat()}"
    }
    
    response = requests.post(
        f"{BASE_URL}/inventory/warehouse/{warehouse_id}/adjustment", 
        headers=headers,
        json=adjustment_data
    )
    
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Failed to create stock adjustment: {response.status_code} - {response.text}")
        return None

def main():
    print("Testing Stock Adjustment Fix")
    print("=" * 40)
    
    # Get authentication token
    print("1. Getting authentication token...")
    token = get_auth_token()
    if not token:
        print("Failed to authenticate. Exiting.")
        sys.exit(1)
    print("✓ Authentication successful")
    
    # Get warehouses
    print("\n2. Getting warehouses...")
    warehouses = get_warehouses(token)
    if not warehouses:
        print("No warehouses found. Exiting.")
        sys.exit(1)
    
    # Use the first warehouse
    warehouse = warehouses[0]
    warehouse_id = warehouse["id"]
    print(f"✓ Using warehouse: {warehouse['name']} (ID: {warehouse_id})")
    
    # Get warehouse inventory
    print("\n3. Getting warehouse inventory...")
    inventory = get_warehouse_inventory(warehouse_id, token)
    if not inventory:
        print("No inventory found in warehouse. Exiting.")
        sys.exit(1)
    
    # Use the first inventory item
    inventory_item = inventory[0]
    part_id = inventory_item["part_id"]
    current_stock_before = float(inventory_item["current_stock"])
    print(f"✓ Using part: {inventory_item.get('part_number', 'Unknown')} (ID: {part_id})")
    print(f"✓ Current stock before adjustment: {current_stock_before}")
    
    # Create a stock adjustment (decrease by 10)
    print("\n4. Creating stock adjustment...")
    adjustment_amount = -10.0
    adjustment = create_stock_adjustment(
        warehouse_id, 
        part_id, 
        adjustment_amount, 
        "Test adjustment", 
        token
    )
    
    if not adjustment:
        print("Failed to create stock adjustment. Exiting.")
        sys.exit(1)
    
    print(f"✓ Stock adjustment created: {adjustment['id']}")
    print(f"✓ Adjustment amount: {adjustment['quantity_change']}")
    
    # Wait a moment for the database to update
    import time
    time.sleep(1)
    
    # Get updated inventory
    print("\n5. Checking updated inventory...")
    updated_inventory = get_warehouse_inventory(warehouse_id, token)
    if not updated_inventory:
        print("Failed to get updated inventory. Exiting.")
        sys.exit(1)
    
    # Find the same inventory item
    updated_item = next((item for item in updated_inventory if item["part_id"] == part_id), None)
    if not updated_item:
        print("Could not find the updated inventory item. Exiting.")
        sys.exit(1)
    
    current_stock_after = float(updated_item["current_stock"])
    expected_stock = current_stock_before + adjustment_amount
    
    print(f"✓ Current stock after adjustment: {current_stock_after}")
    print(f"✓ Expected stock: {expected_stock}")
    
    # Verify the adjustment worked
    if abs(current_stock_after - expected_stock) < 0.001:  # Allow for small floating point differences
        print("\n🎉 SUCCESS: Stock adjustment is working correctly!")
        print(f"   Stock changed from {current_stock_before} to {current_stock_after}")
        print(f"   Adjustment of {adjustment_amount} was applied correctly")
    else:
        print("\n❌ FAILURE: Stock adjustment did not work correctly!")
        print(f"   Expected: {expected_stock}")
        print(f"   Actual: {current_stock_after}")
        print(f"   Difference: {current_stock_after - expected_stock}")
        sys.exit(1)

if __name__ == "__main__":
    main()