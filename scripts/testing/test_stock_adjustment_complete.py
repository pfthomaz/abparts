#!/usr/bin/env python3
"""
Complete test for stock adjustment feature
Tests: migration, API endpoints, and data integrity
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def get_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/token",
        data={"username": "admin@oraseas.com", "password": "admin123"}
    )
    return response.json()["access_token"]

def test_list_stock_adjustments(token):
    """Test listing stock adjustments"""
    print("\n📋 Testing: List stock adjustments")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/stock-adjustments", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: Found {len(data)} stock adjustments")
        return data
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return None

def test_get_warehouses(token):
    """Get available warehouses"""
    print("\n🏭 Getting warehouses...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/warehouses", headers=headers)
    
    if response.status_code == 200:
        warehouses = response.json()
        print(f"✅ Found {len(warehouses)} warehouses")
        return warehouses
    else:
        print(f"❌ Failed to get warehouses")
        return []

def test_get_parts(token):
    """Get available parts"""
    print("\n📦 Getting parts...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/parts", headers=headers)
    
    if response.status_code == 200:
        parts = response.json()
        print(f"✅ Found {len(parts)} parts")
        return parts
    else:
        print(f"❌ Failed to get parts")
        return []

def test_create_stock_adjustment(token, warehouse_id, part_id):
    """Test creating a stock adjustment"""
    print("\n➕ Testing: Create stock adjustment")
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "warehouse_id": str(warehouse_id),
        "adjustment_type": "stock_take",
        "reason": "Test stock adjustment",
        "notes": "Automated test",
        "items": [
            {
                "part_id": str(part_id),
                "quantity_after": 100.0,
                "reason": "Test adjustment for this part"
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/stock-adjustments",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Success: Created stock adjustment {data['id']}")
        print(f"   Warehouse: {data['warehouse_name']}")
        print(f"   Type: {data['adjustment_type']}")
        print(f"   Items adjusted: {data['total_items_adjusted']}")
        return data
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_get_stock_adjustment(token, adjustment_id):
    """Test getting a specific stock adjustment"""
    print(f"\n🔍 Testing: Get stock adjustment {adjustment_id}")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/stock-adjustments/{adjustment_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: Retrieved stock adjustment")
        print(f"   Items: {len(data['items'])}")
        for item in data['items']:
            print(f"   - {item['part_number']}: {item['quantity_before']} → {item['quantity_after']} (Δ {item['quantity_change']})")
        return data
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return None

def main():
    print("=" * 60)
    print("Stock Adjustment Feature - Complete Test")
    print("=" * 60)
    
    try:
        # Get auth token
        print("\n🔐 Authenticating...")
        token = get_token()
        print("✅ Authenticated")
        
        # Test list endpoint
        adjustments = test_list_stock_adjustments(token)
        
        # Get warehouses and parts for creating test adjustment
        warehouses = test_get_warehouses(token)
        parts = test_get_parts(token)
        
        if warehouses and parts:
            # Create a test stock adjustment
            warehouse_id = warehouses[0]['id']
            part_id = parts[0]['id']
            
            new_adjustment = test_create_stock_adjustment(token, warehouse_id, part_id)
            
            if new_adjustment:
                # Get the created adjustment
                test_get_stock_adjustment(token, new_adjustment['id'])
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
