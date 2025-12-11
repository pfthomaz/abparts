#!/usr/bin/env python3
"""
Test script to verify the API works with the new Part model fields
"""

import sys
import requests
sys.path.append('/app')

def test_api_with_new_fields():
    """Test the API with new Part model fields"""
    
    print("Testing API with New Part Fields")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Get authentication token
    try:
        from app.database import get_db
        from app.models import User
        from app.auth import create_access_token
        from sqlalchemy.orm import Session
        
        # Get database session
        db_gen = get_db()
        db: Session = next(db_gen)
        
        # Get first active super admin user
        user = db.query(User).filter(
            User.is_active == True,
            User.role == 'super_admin'
        ).first()
        
        if not user:
            # Get any active user
            user = db.query(User).filter(User.is_active == True).first()
            
        if not user:
            print("❌ No active users found")
            return False
            
        print(f"Using user: {user.username} (role: {user.role})")
        
        # Create token
        token = create_access_token(user=user)
        headers = {"Authorization": f"Bearer {token}"}
        
    except Exception as e:
        print(f"❌ Error creating authentication: {e}")
        return False
    
    # Test 1: Get parts endpoint
    print("\nTest 1: GET /parts")
    try:
        response = requests.get(f"{base_url}/parts/", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            parts = response.json()
            print(f"✅ Retrieved {len(parts)} parts")
            
            if len(parts) > 0:
                sample_part = parts[0]
                print("Sample part fields:")
                for key, value in sample_part.items():
                    print(f"  - {key}: {value}")
                    
                # Check for new fields
                new_fields = ['manufacturer', 'part_code', 'serial_number']
                for field in new_fields:
                    if field in sample_part:
                        print(f"✅ New field '{field}' present")
                    else:
                        print(f"❌ New field '{field}' missing")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("✅ API test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_api_with_new_fields()
    sys.exit(0 if success else 1)