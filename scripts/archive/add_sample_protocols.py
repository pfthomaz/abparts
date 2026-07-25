#!/usr/bin/env python3
"""
Quick script to add sample maintenance protocols
"""
import requests
import json

API_BASE = "http://localhost:8000"

# Login credentials - update these with your actual credentials
LOGIN_DATA = {
    "username": "diogothomaz@oraseas.com",  # Update with your admin email
    "password": "letmein"  # Update with your admin password
}

def login():
    """Login and get auth token"""
    response = requests.post(f"{API_BASE}/auth/login", json=LOGIN_DATA)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def create_protocol(token, protocol_data):
    """Create a maintenance protocol"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE}/maintenance-protocols/",
        json=protocol_data,
        headers=headers
    )
    if response.status_code == 200:
        protocol = response.json()
        print(f"✓ Created protocol: {protocol['name']}")
        return protocol
    else:
        print(f"✗ Failed to create protocol: {response.status_code} - {response.text}")
        return None

def add_checklist_item(token, protocol_id, item_data):
    """Add a checklist item to a protocol"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE}/maintenance-protocols/{protocol_id}/checklist-items",
        json=item_data,
        headers=headers
    )
    if response.status_code == 200:
        print(f"  ✓ Added item: {item_data['item_description']}")
        return response.json()
    else:
        print(f"  ✗ Failed to add item: {response.status_code}")
        return None

def main():
    print("Adding sample maintenance protocols...\n")
    
    token = login()
    if not token:
        print("Failed to login. Please update credentials in the script.")
        return
    
    # Protocol 1: 50 Hour Service
    protocol1 = create_protocol(token, {
        "name": "50 Hour Service",
        "protocol_type": "scheduled",
        "service_interval_hours": 50,
        "is_recurring": True,
        "machine_model": None,  # All models
        "description": "Regular 50-hour maintenance service",
        "is_active": True,
        "display_order": 1
    })
    
    if protocol1:
        add_checklist_item(token, protocol1['id'], {
            "item_description": "Check oil level and top up if needed",
            "item_type": "check",
            "item_category": "Lubrication",
            "is_critical": True,
            "estimated_duration_minutes": 5,
            "item_order": 1
        })
        
        add_checklist_item(token, protocol1['id'], {
            "item_description": "Check all hose connections",
            "item_type": "check",
            "item_category": "Safety Check",
            "is_critical": True,
            "estimated_duration_minutes": 10,
            "item_order": 2
        })
        
        add_checklist_item(token, protocol1['id'], {
            "item_description": "Lubricate moving parts",
            "item_type": "service",
            "item_category": "Lubrication",
            "is_critical": False,
            "estimated_duration_minutes": 15,
            "item_order": 3
        })
    
    # Protocol 2: 200 Hour Service
    protocol2 = create_protocol(token, {
        "name": "200 Hour Service",
        "protocol_type": "scheduled",
        "service_interval_hours": 200,
        "is_recurring": True,
        "machine_model": None,
        "description": "Major 200-hour maintenance service",
        "is_active": True,
        "display_order": 2
    })
    
    if protocol2:
        add_checklist_item(token, protocol2['id'], {
            "item_description": "Full replacement of hydraulic oil ISO 32 - AW32",
            "item_type": "replacement",
            "item_category": "Mechanical",
            "is_critical": True,
            "estimated_duration_minutes": 30,
            "item_order": 1
        })
        
        add_checklist_item(token, protocol2['id'], {
            "item_description": "Inspect and clean filters",
            "item_type": "service",
            "item_category": "Mechanical",
            "is_critical": True,
            "estimated_duration_minutes": 20,
            "item_order": 2
        })
        
        add_checklist_item(token, protocol2['id'], {
            "item_description": "Check electrical connections",
            "item_type": "check",
            "item_category": "Electrical",
            "is_critical": False,
            "estimated_duration_minutes": 15,
            "item_order": 3
        })
    
    # Protocol 3: Daily Check
    protocol3 = create_protocol(token, {
        "name": "Daily Pre-Operation Check",
        "protocol_type": "daily",
        "service_interval_hours": None,
        "is_recurring": True,
        "machine_model": None,
        "description": "Daily safety and operational checks",
        "is_active": True,
        "display_order": 0
    })
    
    if protocol3:
        add_checklist_item(token, protocol3['id'], {
            "item_description": "Visual inspection for leaks",
            "item_type": "check",
            "item_category": "Safety Check",
            "is_critical": True,
            "estimated_duration_minutes": 2,
            "item_order": 1
        })
        
        add_checklist_item(token, protocol3['id'], {
            "item_description": "Check emergency stop functionality",
            "item_type": "check",
            "item_category": "Safety Check",
            "is_critical": True,
            "estimated_duration_minutes": 1,
            "item_order": 2
        })
        
        add_checklist_item(token, protocol3['id'], {
            "item_description": "Verify pressure gauges are in normal range",
            "item_type": "check",
            "item_category": "Operational",
            "is_critical": True,
            "estimated_duration_minutes": 2,
            "item_order": 3
        })
    
    print("\n✓ Sample protocols added successfully!")
    print("You can now view them in the Maintenance Protocols page.")

if __name__ == "__main__":
    main()
