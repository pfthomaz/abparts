#!/usr/bin/env python3
"""
Direct test of the potential parents endpoint
"""

import sys
import os
sys.path.append('/app')

from app.database import SessionLocal
from app.auth import create_access_token
from app import models
import httpx
import asyncio

async def test_endpoint():
    """Test the potential parents endpoint directly"""
    
    # Get a user for testing
    db = SessionLocal()
    try:
        # Get the superadmin user
        user = db.query(models.User).filter(models.User.username == 'superadmin').first()
        if not user:
            print("❌ Superadmin user not found")
            return False
        
        print(f"✅ Found user: {user.username} (role: {user.role.value})")
        
        # Create a token for the user
        access_token = create_access_token(user)
        print("✅ Created access token")
        
        # Test the endpoint using httpx
        async with httpx.AsyncClient() as client:
            url = 'http://localhost:8000/organizations/potential-parents?organization_type=supplier'
            headers = {'Authorization': f'Bearer {access_token}'}
            
            try:
                response = await client.get(url, headers=headers)
                print(f"📡 API Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Found {len(data)} potential parents:")
                    for org in data:
                        print(f"   - {org['name']} ({org['organization_type']})")
                    return True
                else:
                    print(f"❌ API Error: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Request error: {e}")
                return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = asyncio.run(test_endpoint())
    sys.exit(0 if success else 1)