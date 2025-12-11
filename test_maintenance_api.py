#!/usr/bin/env python3
"""Test script for Maintenance Protocols API"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

# Super admin credentials
EMAIL = "dthomaz"
PASSWORD = "amFT1999!"

def get_token():
    """Get authentication token"""
    print("🔐 Getting authentication token...")
    response = requests.post(
        f"{BASE_URL}/token",
        data={"username": EMAIL, "password": PASSWORD}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get token: {response.status_code}")
        print(response.text)
        print("\n⚠️  Please update EMAIL and PASSWORD in this script with your super admin credentials.")
        sys.exit(1)
    
    token = response.json()["access_token"]
    print("✅ Token obtained!\n")
    return token

def create_protocol(token, data):
    """Create a maintenance protocol"""
    response = requests.post(
        f"{BASE_URL}/maintenance-protocols",
        headers={"Authorization": f"Bearer {token}"},
        json=data
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to create protocol: {response.status_code}")
        print(response.text)
        return None
    
    return response.json()

def add_checklist_item(token, protocol_id, data):
    """Add a checklist item to a protocol"""
    response = requests.post(
        f"{BASE_URL}/maintenance-protocols/{protocol_id}/checklist-items",
        headers={"Authorization": f"Bearer {token}"},
        json=data
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to add checklist item: {response.status_code}")
        print(response.text)
        return None
    
    return response.json()

def list_protocols(token):
    """List all protocols"""
    response = requests.get(
        f"{BASE_URL}/maintenance-protocols",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to list protocols: {response.status_code}")
        print(response.text)
        return []
    
    return response.json()

def main():
    # Get token
    token = get_token()
    
    # Create Daily Start of Day Protocol
    print("📋 Creating 'Daily Start of Day' protocol...")
    daily_start = create_protocol(token, {
        "name": "Daily Start of Day",
        "protocol_type": "daily",
        "description": "Morning checklist before starting operations",
        "is_active": True,
        "display_order": 1
    })
    
    if daily_start:
        print(f"✅ Created protocol: {daily_start['id']}\n")
        
        # Add checklist items
        print("📝 Adding checklist items to Daily Start of Day...")
        items = [
            {
                "item_order": 1,
                "item_description": "Check water level in tank",
                "item_type": "check",
                "item_category": "Pre-operation",
                "is_critical": True,
                "estimated_duration_minutes": 2
            },
            {
                "item_order": 2,
                "item_description": "Inspect nets for damage or wear",
                "item_type": "check",
                "item_category": "Pre-operation",
                "is_critical": True,
                "estimated_duration_minutes": 5
            },
            {
                "item_order": 3,
                "item_description": "Check pump operation",
                "item_type": "check",
                "item_category": "Pre-operation",
                "is_critical": True,
                "estimated_duration_minutes": 3
            }
        ]
        
        for item in items:
            add_checklist_item(token, daily_start['id'], item)
        
        print(f"✅ Added {len(items)} checklist items\n")
    
    # Create Daily End of Day Protocol
    print("📋 Creating 'Daily End of Day' protocol...")
    daily_end = create_protocol(token, {
        "name": "Daily End of Day",
        "protocol_type": "daily",
        "description": "Evening shutdown checklist",
        "is_active": True,
        "display_order": 2
    })
    
    if daily_end:
        print(f"✅ Created protocol: {daily_end['id']}\n")
        
        # Add checklist items
        print("📝 Adding checklist items to Daily End of Day...")
        items = [
            {
                "item_order": 1,
                "item_description": "Clean nets thoroughly",
                "item_type": "service",
                "item_category": "Cleaning",
                "is_critical": True,
                "estimated_duration_minutes": 15
            },
            {
                "item_order": 2,
                "item_description": "Drain and clean water tank",
                "item_type": "service",
                "item_category": "Cleaning",
                "is_critical": True,
                "estimated_duration_minutes": 10
            },
            {
                "item_order": 3,
                "item_description": "Record machine hours",
                "item_type": "check",
                "item_category": "Documentation",
                "is_critical": True,
                "estimated_duration_minutes": 2
            }
        ]
        
        for item in items:
            add_checklist_item(token, daily_end['id'], item)
        
        print(f"✅ Added {len(items)} checklist items\n")
    
    # Create 50h Service Protocol
    print("📋 Creating '50 Hour Service' protocol...")
    service_50 = create_protocol(token, {
        "name": "50 Hour Service",
        "protocol_type": "scheduled",
        "service_interval_hours": 50.0,
        "machine_model": "V3.1B",
        "description": "First scheduled service at 50 operating hours",
        "is_active": True,
        "display_order": 10
    })
    
    if service_50:
        print(f"✅ Created protocol: {service_50['id']}\n")
        
        # Add checklist items
        print("📝 Adding checklist items to 50h Service...")
        items = [
            {
                "item_order": 1,
                "item_description": "Inspect and clean pump filter",
                "item_type": "service",
                "item_category": "Pump Maintenance",
                "is_critical": True,
                "estimated_duration_minutes": 20
            },
            {
                "item_order": 2,
                "item_description": "Check all hose connections",
                "item_type": "check",
                "item_category": "Safety Check",
                "is_critical": True,
                "estimated_duration_minutes": 10
            },
            {
                "item_order": 3,
                "item_description": "Lubricate moving parts",
                "item_type": "service",
                "item_category": "Lubrication",
                "is_critical": False,
                "estimated_duration_minutes": 15
            }
        ]
        
        for item in items:
            add_checklist_item(token, service_50['id'], item)
        
        print(f"✅ Added {len(items)} checklist items\n")
    
    # List all protocols
    print("📋 Listing all protocols...")
    protocols = list_protocols(token)
    print(json.dumps(protocols, indent=2))
    
    print("\n🎉 Sample data created successfully!")
    print("\nYou can now:")
    print("  1. View protocols at: http://localhost:8000/docs")
    print("  2. Test the endpoints in the Swagger UI")
    print("  3. Start building the frontend UI")

if __name__ == "__main__":
    main()
