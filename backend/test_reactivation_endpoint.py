#!/usr/bin/env python3
"""
Test script for user reactivation API endpoint integration.
Tests the /users/{user_id}/reactivate endpoint with updated CRUD function.

Requirements: 1.2, 3.1, 3.2, 3.3, 3.4
"""

import requests
import json
import uuid
import sys
import os
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test_reactivation@example.com"
TEST_USERNAME = "test_reactivation_user"
TEST_PASSWORD = "TestPassword123!"

class ReactivationEndpointTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.admin_token = None
        self.test_user_id = None
        self.test_org_id = None
        
    def authenticate_admin(self):
        """Authenticate as admin to get access token"""
        print("🔐 Authenticating as admin...")
        
        # Use working admin credentials
        login_data = {
            "username": "oraseasee_admin",
            "password": "admin"
        }
        
        response = requests.post(f"{self.base_url}/token", data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.admin_token = token_data["access_token"]
            print("✅ Admin authentication successful")
            return True
        else:
            print(f"❌ Admin authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}
    
    def create_test_user(self):
        """Create a test user for reactivation testing"""
        print("👤 Creating test user...")
        
        # First get organizations to find one to use
        response = requests.get(f"{self.base_url}/organizations/", headers=self.get_headers())
        if response.status_code != 200:
            print(f"❌ Failed to get organizations: {response.status_code}")
            return False
        
        orgs = response.json()
        if not orgs:
            print("❌ No organizations found")
            return False
        
        self.test_org_id = orgs[0]["id"]
        
        # Create test user
        user_data = {
            "username": TEST_USERNAME,
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": "Test Reactivation User",
            "role": "user",
            "organization_id": self.test_org_id
        }
        
        response = requests.post(f"{self.base_url}/users/", json=user_data, headers=self.get_headers())
        
        if response.status_code == 201:
            user = response.json()
            self.test_user_id = user["id"]
            print(f"✅ Test user created with ID: {self.test_user_id}")
            return True
        else:
            print(f"❌ Failed to create test user: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def deactivate_test_user(self):
        """Deactivate the test user so we can test reactivation"""
        print("🔒 Deactivating test user...")
        
        response = requests.patch(
            f"{self.base_url}/users/{self.test_user_id}/deactivate",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ User deactivated. Status: is_active={user['is_active']}, user_status={user['user_status']}")
            return True
        else:
            print(f"❌ Failed to deactivate user: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def test_successful_reactivation(self):
        """Test successful user reactivation"""
        print("\n🧪 Testing successful reactivation...")
        
        response = requests.patch(
            f"{self.base_url}/users/{self.test_user_id}/reactivate",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            user = response.json()
            
            # Verify both status fields are synchronized
            is_active = user.get("is_active")
            user_status = user.get("user_status")
            
            print(f"✅ Reactivation successful!")
            print(f"   - is_active: {is_active}")
            print(f"   - user_status: {user_status}")
            
            # Verify synchronization (Requirement 1.1, 2.1, 2.2)
            if is_active == True and user_status == "active":
                print("✅ Status fields are properly synchronized")
                return True
            else:
                print(f"❌ Status fields not synchronized: is_active={is_active}, user_status={user_status}")
                return False
        else:
            print(f"❌ Reactivation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def test_user_not_found_error(self):
        """Test 404 error for non-existent user"""
        print("\n🧪 Testing user not found error (404)...")
        
        fake_user_id = str(uuid.uuid4())
        response = requests.patch(
            f"{self.base_url}/users/{fake_user_id}/reactivate",
            headers=self.get_headers()
        )
        
        if response.status_code == 404:
            error_data = response.json()
            print(f"✅ Correct 404 error returned")
            print(f"   - Error message: {error_data.get('detail', 'No detail')}")
            return True
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def test_permission_error(self):
        """Test 403 error for insufficient permissions"""
        print("\n🧪 Testing permission error (403)...")
        
        # Try to reactivate without proper authorization
        response = requests.patch(f"{self.base_url}/users/{self.test_user_id}/reactivate")
        
        if response.status_code == 401:  # Unauthorized (no token)
            print("✅ Correct 401 error for missing authorization")
            return True
        elif response.status_code == 403:  # Forbidden
            print("✅ Correct 403 error for insufficient permissions")
            return True
        else:
            print(f"❌ Expected 401/403, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def test_invalid_user_id_format(self):
        """Test 422 error for invalid UUID format"""
        print("\n🧪 Testing invalid user ID format (422)...")
        
        response = requests.patch(
            f"{self.base_url}/users/invalid-uuid/reactivate",
            headers=self.get_headers()
        )
        
        if response.status_code == 422:
            error_data = response.json()
            print(f"✅ Correct 422 error for invalid UUID format")
            print(f"   - Error details: {error_data.get('detail', 'No detail')}")
            return True
        else:
            print(f"❌ Expected 422, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def verify_user_status_in_list(self):
        """Verify user appears as active in user list after reactivation"""
        print("\n🧪 Verifying user status in user list...")
        
        response = requests.get(f"{self.base_url}/users/", headers=self.get_headers())
        
        if response.status_code == 200:
            users = response.json()
            test_user = next((u for u in users if u["id"] == self.test_user_id), None)
            
            if test_user:
                is_active = test_user.get("is_active")
                user_status = test_user.get("user_status")
                
                print(f"✅ User found in list")
                print(f"   - is_active: {is_active}")
                print(f"   - user_status: {user_status}")
                
                if is_active == True and user_status == "active":
                    print("✅ User shows as active in user list")
                    return True
                else:
                    print(f"❌ User not showing as active in list")
                    return False
            else:
                print(f"❌ Test user not found in user list")
                return False
        else:
            print(f"❌ Failed to get user list: {response.status_code}")
            return False
    
    def cleanup_test_user(self):
        """Clean up test user"""
        print("\n🧹 Cleaning up test user...")
        
        if self.test_user_id:
            response = requests.delete(
                f"{self.base_url}/users/{self.test_user_id}",
                headers=self.get_headers()
            )
            
            if response.status_code == 204:
                print("✅ Test user cleaned up successfully")
            else:
                print(f"⚠️  Failed to clean up test user: {response.status_code}")
    
    def run_all_tests(self):
        """Run all reactivation endpoint tests"""
        print("🚀 Starting User Reactivation API Endpoint Tests")
        print("=" * 60)
        
        test_results = []
        
        # Setup
        if not self.authenticate_admin():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        if not self.create_test_user():
            print("❌ Cannot proceed without test user")
            return False
        
        if not self.deactivate_test_user():
            print("❌ Cannot proceed without deactivating test user")
            return False
        
        # Run tests
        test_results.append(("Successful Reactivation", self.test_successful_reactivation()))
        test_results.append(("User Not Found (404)", self.test_user_not_found_error()))
        test_results.append(("Permission Error (401/403)", self.test_permission_error()))
        test_results.append(("Invalid UUID Format (422)", self.test_invalid_user_id_format()))
        test_results.append(("User Status in List", self.verify_user_status_in_list()))
        
        # Cleanup
        self.cleanup_test_user()
        
        # Results summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Reactivation endpoint is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Please review the issues above.")
            return False

def main():
    """Main function to run the tests"""
    tester = ReactivationEndpointTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()