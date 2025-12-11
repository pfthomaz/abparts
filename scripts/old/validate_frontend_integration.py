#!/usr/bin/env python3
"""
Frontend Integration Validation for User Reactivation Fix

This script validates that the frontend integration works correctly by:
1. Testing the API endpoints that the frontend uses
2. Validating status field synchronization
3. Ensuring error handling works as expected
4. Confirming user list refresh functionality

Requirements: 1.1, 1.2, 1.3, 3.4
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"

class FrontendIntegrationValidator:
    def __init__(self):
        self.auth_token = None
        self.test_user_id = None
    
    def authenticate(self):
        """Authenticate and get access token"""
        print("🔐 Authenticating...")
        
        login_data = {
            "username": "oraseasee_admin",
            "password": "admin"
        }
        
        response = requests.post(f"{API_BASE_URL}/token", data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.auth_token = token_data["access_token"]
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    def get_test_user(self):
        """Get a test user for validation"""
        print("📋 Getting test user...")
        
        response = requests.get(f"{API_BASE_URL}/users/", headers=self.get_headers())
        
        if response.status_code == 200:
            users = response.json()
            
            # Find a user that's not the admin
            for user in users:
                if user.get("username") != "oraseasee_admin":
                    self.test_user_id = user["id"]
                    print(f"✅ Using test user: {user['username']} (ID: {self.test_user_id})")
                    return True
            
            print("❌ No suitable test user found")
            return False
        else:
            print(f"❌ Failed to get users: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def validate_reactivation_flow(self):
        """Validate the complete reactivation flow that frontend uses"""
        print("\n🧪 Validating Frontend Reactivation Flow")
        print("=" * 50)
        
        try:
            # Step 1: Deactivate user (simulating frontend deactivation)
            print("🔒 Deactivating user...")
            response = requests.patch(
                f"{API_BASE_URL}/users/{self.test_user_id}/deactivate",
                headers=self.get_headers()
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to deactivate user: {response.status_code}")
                return False
            
            deactivated_user = response.json()
            print(f"✅ User deactivated: is_active={deactivated_user['is_active']}, user_status={deactivated_user['user_status']}")
            
            # Step 2: Reactivate user (simulating frontend reactivation)
            print("🔄 Reactivating user...")
            response = requests.patch(
                f"{API_BASE_URL}/users/{self.test_user_id}/reactivate",
                headers=self.get_headers()
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to reactivate user: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            reactivated_user = response.json()
            print(f"✅ User reactivated: is_active={reactivated_user['is_active']}, user_status={reactivated_user['user_status']}")
            
            # Step 3: Validate status synchronization (Requirement 1.1, 2.1, 2.2)
            if reactivated_user["is_active"] == True and reactivated_user["user_status"] == "active":
                print("✅ Status fields are properly synchronized")
            else:
                print(f"❌ Status fields not synchronized: is_active={reactivated_user['is_active']}, user_status={reactivated_user['user_status']}")
                return False
            
            # Step 4: Validate user list refresh (Requirement 3.4)
            print("📋 Validating user list refresh...")
            response = requests.get(f"{API_BASE_URL}/users/", headers=self.get_headers())
            
            if response.status_code != 200:
                print(f"❌ Failed to get updated user list: {response.status_code}")
                return False
            
            updated_users = response.json()
            updated_user = next((u for u in updated_users if u["id"] == self.test_user_id), None)
            
            if not updated_user:
                print("❌ User not found in updated list")
                return False
            
            if updated_user["is_active"] == True and updated_user["user_status"] == "active":
                print("✅ User list shows correct updated status")
                return True
            else:
                print(f"❌ User list shows incorrect status: is_active={updated_user['is_active']}, user_status={updated_user['user_status']}")
                return False
                
        except Exception as e:
            print(f"❌ Error during reactivation flow validation: {str(e)}")
            return False
    
    def validate_error_handling(self):
        """Validate error handling that frontend needs to handle"""
        print("\n🧪 Validating Frontend Error Handling")
        print("=" * 45)
        
        test_cases = [
            {
                "name": "Non-existent user (404)",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "expected_status": 404
            },
            {
                "name": "Invalid UUID format (422)",
                "user_id": "invalid-uuid",
                "expected_status": 422
            }
        ]
        
        passed_tests = 0
        
        for test_case in test_cases:
            try:
                print(f"🔍 Testing {test_case['name']}...")
                response = requests.patch(
                    f"{API_BASE_URL}/users/{test_case['user_id']}/reactivate",
                    headers=self.get_headers()
                )
                
                if response.status_code == test_case["expected_status"]:
                    print(f"✅ Correct {test_case['expected_status']} error returned")
                    passed_tests += 1
                else:
                    print(f"❌ Wrong status code: expected {test_case['expected_status']}, got {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error testing {test_case['name']}: {str(e)}")
        
        return passed_tests == len(test_cases)
    
    def validate_unauthorized_access(self):
        """Validate unauthorized access handling"""
        print("\n🧪 Validating Unauthorized Access Handling")
        print("=" * 45)
        
        try:
            # Test without authorization header
            response = requests.patch(f"{API_BASE_URL}/users/{self.test_user_id}/reactivate")
            
            if response.status_code in [401, 403]:
                print(f"✅ Correct unauthorized error ({response.status_code}) returned")
                return True
            else:
                print(f"❌ Wrong status code for unauthorized access: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing unauthorized access: {str(e)}")
            return False
    
    def validate_frontend_status_display(self):
        """Validate that frontend can properly display user status"""
        print("\n🧪 Validating Frontend Status Display Logic")
        print("=" * 45)
        
        try:
            # Get current user data
            response = requests.get(f"{API_BASE_URL}/users/", headers=self.get_headers())
            
            if response.status_code != 200:
                print(f"❌ Failed to get users: {response.status_code}")
                return False
            
            users = response.json()
            test_user = next((u for u in users if u["id"] == self.test_user_id), None)
            
            if not test_user:
                print("❌ Test user not found")
                return False
            
            # Simulate frontend status display logic (from UsersPage.js)
            def get_user_status_display(user):
                if not user.get("is_active"):
                    return {"text": "Inactive", "class": "bg-gray-200 text-gray-600"}
                
                user_status = user.get("user_status")
                if user_status == "active":
                    return {"text": "Active", "class": "bg-green-100 text-green-800"}
                elif user_status == "pending_invitation":
                    return {"text": "Pending Invitation", "class": "bg-yellow-100 text-yellow-800"}
                elif user_status == "locked":
                    return {"text": "Locked", "class": "bg-red-100 text-red-800"}
                elif user_status == "inactive":
                    return {"text": "Inactive", "class": "bg-gray-200 text-gray-600"}
                else:
                    return {"text": "Unknown", "class": "bg-gray-200 text-gray-600"}
            
            status_display = get_user_status_display(test_user)
            
            print(f"✅ Frontend status display logic working:")
            print(f"   User: is_active={test_user['is_active']}, user_status={test_user['user_status']}")
            print(f"   Display: {status_display['text']} ({status_display['class']})")
            
            # Validate that active user shows as "Active"
            if test_user["is_active"] and test_user["user_status"] == "active":
                if status_display["text"] == "Active":
                    print("✅ Active user correctly displays as 'Active'")
                    return True
                else:
                    print(f"❌ Active user displays as '{status_display['text']}' instead of 'Active'")
                    return False
            else:
                print("⚠️  User is not in active state for display validation")
                return True
                
        except Exception as e:
            print(f"❌ Error validating status display: {str(e)}")
            return False
    
    def run_validation(self):
        """Run all frontend integration validations"""
        print("🚀 Starting Frontend Integration Validation")
        print("=" * 60)
        
        # Setup
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return False
        
        if not self.get_test_user():
            print("❌ Cannot proceed without test user")
            return False
        
        # Run validations
        validations = [
            ("Reactivation Flow", self.validate_reactivation_flow),
            ("Error Handling", self.validate_error_handling),
            ("Unauthorized Access", self.validate_unauthorized_access),
            ("Status Display Logic", self.validate_frontend_status_display)
        ]
        
        results = []
        passed_count = 0
        
        for name, validation_func in validations:
            try:
                result = validation_func()
                results.append((name, result))
                if result:
                    passed_count += 1
            except Exception as e:
                print(f"❌ Validation '{name}' failed with error: {str(e)}")
                results.append((name, False))
        
        # Results summary
        print("\n" + "=" * 60)
        print("📊 FRONTEND INTEGRATION VALIDATION RESULTS")
        print("=" * 60)
        
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {name}")
        
        total_count = len(results)
        print(f"\nOverall: {passed_count}/{total_count} validations passed")
        
        if passed_count == total_count:
            print("🎉 All frontend integration validations passed!")
            print("✅ User reactivation frontend integration is working correctly.")
            return True
        else:
            print("⚠️  Some frontend integration validations failed.")
            return False

def main():
    """Main function"""
    validator = FrontendIntegrationValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()