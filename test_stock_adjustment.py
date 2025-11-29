#!/usr/bin/env python3
"""
Test script to verify stock adjustment creation and retrieval.
Run this after starting the local Docker environment.
"""

import requests
import json

# Configuration
API_BASE = "http://localhost:8000"
USERNAME = "admin@oraseas.com"  # Change to your test user
PASSWORD = "admin123"  # Change to your test password

def login():
    """Login and get access token"""
    response = requests.post(
        f"{API_BASE}/token",
        data={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None
    
    token = response.json()["access_token"]
    print(f"✅ Logged in successfully")
    return token

def get_warehouses(token):
    """Get list of warehouses"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/warehouses", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get warehouses: {response.status_code}")
        return []
    
    warehouses = response.json()
    print(f"✅ Found {len(warehouses)} warehouses")
    return warehouses

def get_warehouse_inventory(token, warehouse_id):
    """Get inventory for a warehouse"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_BASE}/inventory/warehouse/{warehouse_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get inventory: {response.status_code}")
        return []
    
    inventory = response.json()
    print(f"✅ Found {len(inventory)} inventory items")
    return inventory

def create_adjustment(token, warehouse_id, part_id):
    """Create a stock adjustment"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "part_id": part_id,
        "quantity_change": 5.0,
        "reason": "Manual Adjustment",
        "notes": "Test adjustment from script"
    }
    
    print(f"\n📝 Creating adjustment:")
    print(f"   Warehouse: {warehouse_id}")
    print(f"   Part: {part_id}")
    print(f"   Quantity change: +5.0")
    
    response = requests.post(
        f"{API_BASE}/inventory/warehouse/{warehouse_id}/adjustment",
        headers=headers,
        json=data
    )
    
    if response.status_code != 201:
        print(f"❌ Failed to create adjustment: {response.status_code}")
        print(response.text)
        return None
    
    adjustment = response.json()
    print(f"✅ Adjustment created: {adjustment['id']}")
    return adjustment

def get_adjustments(token, warehouse_id):
    """Get adjustment history for a warehouse"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_BASE}/inventory/warehouse/{warehouse_id}/adjustments",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get adjustments: {response.status_code}")
        print(response.text)
        return []
    
    adjustments = response.json()
    print(f"✅ Found {len(adjustments)} adjustments")
    return adjustments

def main():
    print("=== Stock Adjustment Test ===\n")
    
    # Login
    token = login()
    if not token:
        return
    
    # Get warehouses
    warehouses = get_warehouses(token)
    if not warehouses:
        print("❌ No warehouses found")
        return
    
    # Use first warehouse
    warehouse = warehouses[0]
    warehouse_id = warehouse["id"]
    print(f"\n📦 Using warehouse: {warehouse['name']} ({warehouse_id})")
    
    # Get inventory
    inventory = get_warehouse_inventory(token, warehouse_id)
    if not inventory:
        print("❌ No inventory items found")
        return
    
    # Use first inventory item
    item = inventory[0]
    part_id = item["part_id"]
    print(f"📦 Using part: {item.get('part_name', 'Unknown')} (Stock: {item['current_stock']})")
    
    # Get adjustments BEFORE
    print(f"\n📊 Adjustments BEFORE:")
    adjustments_before = get_adjustments(token, warehouse_id)
    for adj in adjustments_before[:3]:
        print(f"   - {adj['part_name']}: {adj['quantity_change']:+.1f} ({adj['reason']})")
    
    # Create adjustment
    adjustment = create_adjustment(token, warehouse_id, part_id)
    if not adjustment:
        return
    
    # Get adjustments AFTER
    print(f"\n📊 Adjustments AFTER:")
    adjustments_after = get_adjustments(token, warehouse_id)
    for adj in adjustments_after[:3]:
        print(f"   - {adj['part_name']}: {adj['quantity_change']:+.1f} ({adj['reason']})")
    
    # Verify
    if len(adjustments_after) > len(adjustments_before):
        print(f"\n✅ SUCCESS: Adjustment was created and appears in history!")
    else:
        print(f"\n❌ PROBLEM: Adjustment was created but doesn't appear in history!")
        print(f"   Before: {len(adjustments_before)} adjustments")
        print(f"   After: {len(adjustments_after)} adjustments")

if __name__ == "__main__":
    main()
