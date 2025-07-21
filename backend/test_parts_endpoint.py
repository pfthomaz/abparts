#!/usr/bin/env python3
"""
Simple test script to verify the parts/with-inventory endpoint is working correctly.
This script tests the endpoint that the frontend is calling.
"""

import requests
import sys
import os

# Add the app directory to the path
sys.path.append('/app')

def test_parts_endpoint():
    """Test the parts/with-inventory endpoint"""
    base_url = "http://localhost:8000"
    
    print("Testing ABParts API - Parts with Inventory Endpoint")
    print("=" * 60)
    
    # Test 1: Without authentication (should fail)
    print("Test 1: Without authentication")
    try:
        response = requests.get(f"{base_url}/parts/with-inventory")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 401, "Should require authentication"
        print("✅ Correctly requires authentication")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "-" * 40 + "\n")
    
    # Test 2: Try to get a valid user from database for authentication
    print("Test 2: Getting user for authentication")
    try:
        from app.database import get_db
        from app.models import User
        from app.auth import create_access_token
        from sqlalchemy.orm import Session
        
        # Get database session
        db_gen = get_db()
        db: Session = next(db_gen)
        
        # Get first active user
        user = db.query(User).filter(User.is_active == True).first()
        if not user:
            print("❌ No active users found in database")
            return False
            
        print(f"Found user: {user.username} (role: {user.role})")
        
        # Create token
        token = create_access_token(user=user)
        headers = {"Authorization": f"Bearer {token}"}
        
        print("✅ Authentication token created")
        
    except Exception as e:
        print(f"❌ Error creating authentication: {e}")
        return False
    
    print("\n" + "-" * 40 + "\n")
    
    # Test 3: Test with authentication
    print("Test 3: With authentication")
    try:
        response = requests.get(f"{base_url}/parts/with-inventory", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Retrieved {len(data)} parts")
            
            if len(data) > 0:
                print("Sample part data:")
                sample_part = data[0]
                print(f"  - Name: {sample_part.get('name', 'N/A')}")
                print(f"  - Part Number: {sample_part.get('part_number', 'N/A')}")
                print(f"  - Type: {sample_part.get('part_type', 'N/A')}")
                print(f"  - Total Stock: {sample_part.get('total_stock', 'N/A')}")
            else:
                print("No parts returned (empty array)")
                
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "-" * 40 + "\n")
    
    # Test 4: Test basic parts endpoint
    print("Test 4: Basic parts endpoint")
    try:
        response = requests.get(f"{base_url}/parts/", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Basic parts endpoint works! Retrieved {len(data)} parts")
        else:
            print(f"❌ Basic parts endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Parts endpoint verification completed successfully!")
    return True

if __name__ == "__main__":
    success = test_parts_endpoint()
    sys.exit(0 if success else 1)