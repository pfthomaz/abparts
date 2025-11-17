#!/usr/bin/env python3
"""
Ultimate test for part creation after fixing the enhanced function
"""
import requests
import json

def test_part_creation():
    print("🔧 Testing Part Creation - Ultimate Fix")
    print("=" * 50)
    
    try:
        # Login first
        print("1. Authenticating...")
        login_response = requests.post(
            "http://localhost:8000/token",
            data={"username": "superadmin", "password": "superadmin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("✅ Authentication successful")
        
        # Test part creation exactly like the frontend sends it
        print("\n2. Testing part creation like frontend...")
        part_data = {
            "part_number": "ULTIMATE-001",
            "name": "Ultimate Test Part",
            "description": "Final test for part creation",
            "part_type": "consumable",
            "is_proprietary": False,
            "unit_of_measure": "pieces",
            "manufacturer_part_number": "UTP-001",
            "manufacturer_delivery_time_days": 5,
            "local_supplier_delivery_time_days": 2,
            "image_urls": []
        }
        
        print(f"Sending data: {json.dumps(part_data, indent=2)}")
        
        response = requests.post(
            "http://localhost:8000/parts/",
            json=part_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 201:
            print("🎉 SUCCESS! Part created successfully!")
            created_part = response.json()
            print(f"Created part:")
            print(f"  - ID: {created_part.get('id')}")
            print(f"  - Part Number: {created_part.get('part_number')}")
            print(f"  - Name: {created_part.get('name')}")
            print(f"  - Type: {created_part.get('part_type')}")
            print(f"  - Unit of Measure: {created_part.get('unit_of_measure')}")
            
            # Verify it's in the database
            print("\n3. Verifying part in database...")
            parts_response = requests.get(
                "http://localhost:8000/parts/?limit=10",
                headers=headers,
                timeout=10
            )
            
            if parts_response.status_code == 200:
                parts = parts_response.json()
                print(f"✅ Database now has {len(parts)} parts")
                ultimate_part = next((p for p in parts if p.get('part_number') == 'ULTIMATE-001'), None)
                if ultimate_part:
                    print("✅ Our new part is in the database!")
                else:
                    print("⚠️  Part not found in database list")
            
            print("\n🎉 Part creation is now fully working!")
            
        else:
            print(f"❌ Part creation failed")
            print(f"Response text: {response.text}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error response: {response.text}")
                
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_part_creation()