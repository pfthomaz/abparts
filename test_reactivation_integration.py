#!/usr/bin/env python3
"""
Integration test script to validate the user reactivation fix
Tests the complete flow from frontend to backend
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# Configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

class ReactivationIntegrationTest:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        
    def authenticate(self) -> bool:
        """Authenticate as admin user for testing"""
        try:
            # Try to login with default admin credentials
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/auth/login",
                data=login_data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def create_test_user(self) -> Optional[str]:
        """Create a test user for reactivation testing"""
        try:
            user_data = {
                "username": "test_reactivation_user",
                "email": "test.reactivation@example.com",
                "name": "Test Reactivation User",
                "role": "user",
                "is_active": True
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/users",
                json=user_data
            )
            
            if response.status_code == 201:
                user = response.json()
                user_id = user.get("id")
                print(f"✅ Test user created with ID: {user_id}")
                return user_id
            else:
                print(f"❌ Failed to create test user: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            return None
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate the test user"""
        try:
            response = self.session.delete(f"{API_BASE_URL}/users/{user_id}")
            
            if response.status_code == 200:
                print("✅ User deactivated successfully")
                return True
            else:
                print(f"❌ Failed to deactivate user: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error deactivating user: {e}")
            return False
    
    def get_user_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get current user status"""
        try:
            response = self.session.get(f"{API_BASE_URL}/users/{user_id}")
            
            if response.status_code == 200:
                user = response.json()
                return {
                    "is_active": user.get("is_active"),
                    "user_status": user.get("user_status"),
                    "id": user.get("id"),
                    "username": user.get("username")
                }
            else:
                print(f"❌ Failed to get user status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting user status: {e}")
            return None
    
    def reactivate_user(self, user_id: str) -> bool:
        """Test the reactivation endpoint"""
        try:
            response = self.session.post(f"{API_BASE_URL}/users/{user_id}/reactivate")
            
            if response.status_code == 200:
                print("✅ User reactivation API call successful")
                return True
            else:
                print(f"❌ Failed to reactivate user: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error reactivating user: {e}")
            return False
    
    def test_status_synchronization(self, user_id: str) -> bool:
        """Test that both is_active and user_status are properly synchronized"""
        print("\n🔍 Testing status field synchronization...")
        
        # Get initial status (should be inactive)
        status = self.get_user_status(user_id)
        if not status:
            return False
            
        print(f"Before reactivation: is_active={status['is_active']}, user_status={status['user_status']}")
        
        if status['is_active'] or status['user_status'] == 'active':
            print("❌ User should be inactive before reactivation test")
            return False
        
        # Reactivate user
        if not self.reactivate_user(user_id):
            return False
        
        # Check status after reactivation
        time.sleep(0.5)  # Brief delay to ensure database update
        status_after = self.get_user_status(user_id)
        if not status_after:
            return False
            
        print(f"After reactivation: is_active={status_after['is_active']}, user_status={status_after['user_status']}")
        
        # Validate both fields are synchronized
        if status_after['is_active'] and status_after['user_status'] == 'active':
            print("✅ Status fields are properly synchronized")
            return True
        else:
            print("❌ Status fields are NOT synchronized properly")
            print(f"Expected: is_active=True, user_status='active'")
            print(f"Got: is_active={status_after['is_active']}, user_status={status_after['user_status']}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling for various scenarios"""
        print("\n🔍 Testing error handling...")
        
        # Test reactivation of non-existent user
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        response = self.session.post(f"{API_BASE_URL}/users/{fake_user_id}/reactivate")
        
        if response.status_code == 404:
            print("✅ Proper 404 error for non-existent user")
        else:
            print(f"❌ Expected 404 for non-existent user, got {response.status_code}")
            return False
        
        # Test invalid user ID format
        response = self.session.post(f"{API_BASE_URL}/users/invalid-id/reactivate")
        
        if response.status_code in [400, 422]:
            print("✅ Proper error for invalid user ID format")
        else:
            print(f"❌ Expected 400/422 for invalid ID, got {response.status_code}")
            return False
        
        return True
    
    def test_user_list_refresh(self) -> bool:
        """Test that user list endpoint returns updated status"""
        print("\n🔍 Testing user list refresh...")
        
        try:
            response = self.session.get(f"{API_BASE_URL}/users")
            
            if response.status_code == 200:
                users = response.json()
                test_user = next((u for u in users if u.get("id") == self.test_user_id), None)
                
                if test_user:
                    if test_user.get("is_active") and test_user.get("user_status") == "active":
                        print("✅ User list shows correct updated status")
                        return True
                    else:
                        print("❌ User list does not show updated status")
                        print(f"User in list: is_active={test_user.get('is_active')}, user_status={test_user.get('user_status')}")
                        return False
                else:
                    print("❌ Test user not found in user list")
                    return False
            else:
                print(f"❌ Failed to get user list: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing user list refresh: {e}")
            return False
    
    def cleanup_test_user(self, user_id: str):
        """Clean up the test user"""
        try:
            # Try to delete the test user
            response = self.session.delete(f"{API_BASE_URL}/users/{user_id}")
            if response.status_code in [200, 204]:
                print("✅ Test user cleaned up")
            else:
                print(f"⚠️ Could not clean up test user: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")
    
    def run_integration_tests(self) -> bool:
        """Run all integration tests"""
        print("🚀 Starting User Reactivation Integration Tests")
        print("=" * 50)
        
        # Step 1: Authenticate
        if not self.authenticate():
            return False
        
        # Step 2: Create test user
        self.test_user_id = self.create_test_user()
        if not self.test_user_id:
            return False
        
        try:
            # Step 3: Deactivate user
            if not self.deactivate_user(self.test_user_id):
                return False
            
            # Step 4: Test status synchronization
            if not self.test_status_synchronization(self.test_user_id):
                return False
            
            # Step 5: Test user list refresh
            if not self.test_user_list_refresh():
                return False
            
            # Step 6: Test error handling
            if not self.test_error_handling():
                return False
            
            print("\n" + "=" * 50)
            print("🎉 All integration tests passed!")
            return True
            
        finally:
            # Cleanup
            if self.test_user_id:
                self.cleanup_test_user(self.test_user_id)

def main():
    """Main test execution"""
    tester = ReactivationIntegrationTest()
    
    try:
        success = tester.run_integration_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()