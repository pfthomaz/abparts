#!/usr/bin/env python3
"""
Frontend Integration Test for Machine API Endpoints

This test validates that all machine endpoints work correctly from a frontend perspective,
ensuring no 500 errors occur and proper data is returned.

Requirements tested:
- 1.1: Machine details endpoint returns data without 500 errors
- 1.4: Machine operations work without 500 errors  
- 2.1: Machine endpoints handle database queries without unhandled exceptions
"""

import os
import sys
import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import pytest
import requests
from requests.auth import HTTPBasicAuth

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MachineEndpointTester:
    """Test class for validating machine endpoints from frontend perspective."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.auth_token = None
        self.test_machine_id = None
        self.test_organization_id = None
        self.test_user_id = None
        
    def authenticate(self, username: str = "superadmin", password: str = "superadmin") -> bool:
        """Authenticate and get JWT token."""
        try:
            auth_url = f"{self.base_url}/token"
            response = requests.post(
                auth_url,
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                logger.info("Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token."""
        if not self.auth_token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    def setup_test_data(self) -> bool:
        """Set up test data needed for machine endpoint testing."""
        try:
            # Get organizations to find a test organization
            org_response = requests.get(
                f"{self.base_url}/organizations/",
                headers=self.get_headers(),
                timeout=10
            )
            
            if org_response.status_code == 200:
                organizations = org_response.json()
                if organizations:
                    self.test_organization_id = organizations[0]["id"]
                    logger.info(f"Using test organization: {self.test_organization_id}")
                else:
                    logger.error("No organizations found for testing")
                    return False
            else:
                logger.error(f"Failed to get organizations: {org_response.status_code}")
                return False
            
            # Get users to find a test user
            user_response = requests.get(
                f"{self.base_url}/users/",
                headers=self.get_headers(),
                timeout=10
            )
            
            if user_response.status_code == 200:
                users = user_response.json()
                if users:
                    self.test_user_id = users[0]["id"]
                    logger.info(f"Using test user: {self.test_user_id}")
                else:
                    logger.error("No users found for testing")
                    return False
            else:
                logger.error(f"Failed to get users: {user_response.status_code}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Setup test data error: {str(e)}")
            return False
    
    def test_machine_list_endpoint(self) -> Dict[str, Any]:
        """Test machine list endpoint - simulates frontend loading machine list."""
        logger.info("Testing machine list endpoint...")
        
        try:
            response = requests.get(
                f"{self.base_url}/machines/",
                headers=self.get_headers(),
                params={"skip": 0, "limit": 50},
                timeout=10
            )
            
            result = {
                "endpoint": "GET /machines/",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "error": None,
                "data_count": 0,
                "has_required_fields": False
            }
            
            if response.status_code == 200:
                data = response.json()
                result["data_count"] = len(data)
                
                # Check if machines have required fields for frontend
                if data:
                    machine = data[0]
                    required_fields = ["id", "name", "serial_number", "status", "customer_organization_id"]
                    result["has_required_fields"] = all(field in machine for field in required_fields)
                    
                    # Store a test machine ID for other tests
                    self.test_machine_id = machine["id"]
                    logger.info(f"Found {len(data)} machines, using {self.test_machine_id} for detailed tests")
                else:
                    result["has_required_fields"] = True  # Empty list is valid
                    logger.info("No machines found, but endpoint works correctly")
                    
            else:
                result["error"] = response.text
                logger.error(f"Machine list endpoint failed: {response.status_code} - {response.text}")
            
            return result
            
        except Exception as e:
            logger.error(f"Machine list endpoint test error: {str(e)}")
            return {
                "endpoint": "GET /machines/",
                "status_code": 0,
                "success": False,
                "error": str(e),
                "data_count": 0,
                "has_required_fields": False
            }
    
    def test_machine_details_endpoint(self) -> Dict[str, Any]:
        """Test machine details endpoint - simulates frontend loading specific machine."""
        logger.info("Testing machine details endpoint...")
        
        if not self.test_machine_id:
            return {
                "endpoint": "GET /machines/{id}",
                "status_code": 0,
                "success": False,
                "error": "No test machine ID available",
                "has_required_fields": False
            }
        
        try:
            response = requests.get(
                f"{self.base_url}/machines/{self.test_machine_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            result = {
                "endpoint": f"GET /machines/{self.test_machine_id}",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "error": None,
                "has_required_fields": False
            }
            
            if response.status_code == 200:
                machine = response.json()
                
                # Check if machine has required fields for frontend display
                required_fields = [
                    "id", "name", "serial_number", "status", "model_type",
                    "customer_organization_id", "created_at", "updated_at"
                ]
                result["has_required_fields"] = all(field in machine for field in required_fields)
                
                # Check if enum fields are properly serialized
                if "status" in machine:
                    result["status_serialized"] = isinstance(machine["status"], str)
                
                logger.info(f"Machine details retrieved successfully: {machine.get('name', 'Unknown')}")
                
            else:
                result["error"] = response.text
                logger.error(f"Machine details endpoint failed: {response.status_code} - {response.text}")
            
            return result
            
        except Exception as e:
            logger.error(f"Machine details endpoint test error: {str(e)}")
            return {
                "endpoint": f"GET /machines/{self.test_machine_id}",
                "status_code": 0,
                "success": False,
                "error": str(e),
                "has_required_fields": False
            }
    
    def test_machine_maintenance_history_endpoint(self) -> Dict[str, Any]:
        """Test machine maintenance history endpoint."""
        logger.info("Testing machine maintenance history endpoint...")
        
        if not self.test_machine_id:
            return {
                "endpoint": "GET /machines/{id}/maintenance",
                "status_code": 0,
                "success": False,
                "error": "No test machine ID available",
                "data_count": 0
            }
        
        try:
            response = requests.get(
                f"{self.base_url}/machines/{self.test_machine_id}/maintenance",
                headers=self.get_headers(),
                params={"skip": 0, "limit": 20},
                timeout=10
            )
            
            result = {
                "endpoint": f"GET /machines/{self.test_machine_id}/maintenance",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "error": None,
                "data_count": 0
            }
            
            if response.status_code == 200:
                maintenance_records = response.json()
                result["data_count"] = len(maintenance_records)
                logger.info(f"Retrieved {len(maintenance_records)} maintenance records")
                
            else:
                result["error"] = response.text
                logger.error(f"Machine maintenance history endpoint failed: {response.status_code} - {response.text}")
            
            return result
            
        except Exception as e:
            logger.error(f"Machine maintenance history endpoint test error: {str(e)}")
            return {
                "endpoint": f"GET /machines/{self.test_machine_id}/maintenance",
                "status_code": 0,
                "success": False,
                "error": str(e),
                "data_count": 0
            }
    
    def test_machine_usage_history_endpoint(self) -> Dict[str, Any]:
        """Test machine usage history endpoint."""
        logger.info("Testing machine usage history endpoint...")
        
        if not self.test_machine_id:
            return {
                "endpoint": "GET /machines/{id}/usage-history",
                "status_code": 0,
                "success": False,
                "error": "No test machine ID available",
                "data_count": 0
            }
        
        try:
            response = requests.get(
                f"{self.base_url}/machines/{self.test_machine_id}/usage-history",
                headers=self.get_headers(),
                params={"skip": 0, "limit": 20},
                timeout=10
            )
            
            result = {
                "endpoint": f"GET /machines/{self.test_machine_id}/usage-history",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "error": None,
                "data_count": 0
            }
            
            if response.status_code == 200:
                usage_records = response.json()
                result["data_count"] = len(usage_records)
                logger.info(f"Retrieved {len(usage_records)} usage history records")
                
            else:
                result["error"] = response.text
                logger.error(f"Machine usage history endpoint failed: {response.status_code} - {response.text}")
            
            return result
            
        except Exception as e:
            logger.error(f"Machine usage history endpoint test error: {str(e)}")
            return {
                "endpoint": f"GET /machines/{self.test_machine_id}/usage-history",
                "status_code": 0,
                "success": False,
                "error": str(e),
                "data_count": 0
            }
    
    def test_machine_compatible_parts_endpoint(self) -> Dict[str, Any]:
        """Test machine compatible parts endpoint."""
        logger.info("Testing machine compatible parts endpoint...")
        
        if not self.test_machine_id:
            return {
                "endpoint": "GET /machines/{id}/compatible-parts",
                "status_code": 0,
                "success": False,
                "error": "No test machine ID available",
                "data_count": 0
            }
        
        try:
            response = requests.get(
                f"{self.base_url}/machines/{self.test_machine_id}/compatible-parts",
                headers=self.get_headers(),
                params={"skip": 0, "limit": 20},
                timeout=10
            )
            
            result = {
                "endpoint": f"GET /machines/{self.test_machine_id}/compatible-parts",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "error": None,
                "data_count": 0
            }
            
            if response.status_code == 200:
                compatible_parts = response.json()
                result["data_count"] = len(compatible_parts)
                logger.info(f"Retrieved {len(compatible_parts)} compatible parts")
                
            else:
                result["error"] = response.text
                logger.error(f"Machine compatible parts endpoint failed: {response.status_code} - {response.text}")
            
            return result
            
        except Exception as e:
            logger.error(f"Machine compatible parts endpoint test error: {str(e)}")
            return {
                "endpoint": f"GET /machines/{self.test_machine_id}/compatible-parts",
                "status_code": 0,
                "success": False,
                "error": str(e),
                "data_count": 0
            }
    
    def test_create_machine_maintenance(self) -> Dict[str, Any]:
        """Test creating a maintenance record - simulates frontend maintenance form submission."""
        logger.info("Testing create machine maintenance endpoint...")
        
        if not self.test_machine_id or not self.test_user_id:
            return {
                "endpoint": "POST /machines/{id}/maintenance",
                "status_code": 0,
                "success": False,
                "error": "Missing test machine ID or user ID",
                "created_id": None
            }
        
        try:
            maintenance_data = {
                "machine_id": self.test_machine_id,
                "performed_by_user_id": self.test_user_id,
                "maintenance_type": "scheduled",
                "description": "Frontend integration test maintenance",
                "maintenance_date": datetime.utcnow().isoformat(),
                "cost": 50.00,
                "notes": "Test maintenance record created by frontend integration test"
            }
            
            response = requests.post(
                f"{self.base_url}/machines/{self.test_machine_id}/maintenance",
                headers=self.get_headers(),
                json=maintenance_data,
                timeout=10
            )
            
            result = {
                "endpoint": f"POST /machines/{self.test_machine_id}/maintenance",
                "status_code": response.status_code,
                "success": response.status_code == 201,
                "error": None,
                "created_id": None
            }
            
            if response.status_code == 201:
                maintenance_record = response.json()
                result["created_id"] = maintenance_record.get("id")
                logger.info(f"Maintenance record created successfully: {result['created_id']}")
                
            else:
                result["error"] = response.text
                logger.error(f"Create maintenance endpoint failed: {response.status_code} - {response.text}")
            
            return result
            
        except Exception as e:
            logger.error(f"Create maintenance endpoint test error: {str(e)}")
            return {
                "endpoint": f"POST /machines/{self.test_machine_id}/maintenance",
                "status_code": 0,
                "success": False,
                "error": str(e),
                "created_id": None
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all machine endpoint tests and return comprehensive results."""
        logger.info("Starting comprehensive machine endpoint validation...")
        
        # Authenticate first
        if not self.authenticate():
            return {
                "overall_success": False,
                "error": "Authentication failed",
                "tests": {}
            }
        
        # Set up test data
        if not self.setup_test_data():
            return {
                "overall_success": False,
                "error": "Test data setup failed",
                "tests": {}
            }
        
        # Run all endpoint tests
        tests = {
            "machine_list": self.test_machine_list_endpoint(),
            "machine_details": self.test_machine_details_endpoint(),
            "machine_maintenance_history": self.test_machine_maintenance_history_endpoint(),
            "machine_usage_history": self.test_machine_usage_history_endpoint(),
            "machine_compatible_parts": self.test_machine_compatible_parts_endpoint(),
            "create_maintenance": self.test_create_machine_maintenance()
        }
        
        # Calculate overall success
        overall_success = all(test["success"] for test in tests.values())
        
        # Count 500 errors
        server_errors = sum(1 for test in tests.values() if test["status_code"] >= 500)
        
        results = {
            "overall_success": overall_success,
            "server_errors_count": server_errors,
            "tests_passed": sum(1 for test in tests.values() if test["success"]),
            "total_tests": len(tests),
            "tests": tests,
            "summary": {
                "no_500_errors": server_errors == 0,
                "all_endpoints_accessible": all(test["status_code"] > 0 for test in tests.values()),
                "data_properly_formatted": all(
                    test.get("has_required_fields", True) for test in tests.values()
                )
            }
        }
        
        return results


def main():
    """Main function to run the machine endpoint validation."""
    print("=" * 60)
    print("Machine API Endpoints Frontend Integration Test")
    print("=" * 60)
    
    # Check if the API is running
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code != 200:
            print("❌ API server is not running on http://localhost:8000")
            print("Please start the API server using: docker-compose up api")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API server on http://localhost:8000")
        print("Please start the API server using: docker-compose up api")
        return False
    
    print("✅ API server is running")
    
    # Run the tests
    tester = MachineEndpointTester()
    results = tester.run_all_tests()
    
    # Print results
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    if results.get("error"):
        print(f"❌ Test execution failed: {results['error']}")
        return False
    
    print(f"Tests passed: {results['tests_passed']}/{results['total_tests']}")
    print(f"Server errors (500+): {results['server_errors_count']}")
    print(f"Overall success: {'✅' if results['overall_success'] else '❌'}")
    
    print("\nDetailed Results:")
    print("-" * 40)
    
    for test_name, test_result in results["tests"].items():
        status_icon = "✅" if test_result["success"] else "❌"
        print(f"{status_icon} {test_name}")
        print(f"   Endpoint: {test_result['endpoint']}")
        print(f"   Status: {test_result['status_code']}")
        
        if test_result.get("error"):
            print(f"   Error: {test_result['error']}")
        
        if test_result.get("data_count") is not None:
            print(f"   Data count: {test_result['data_count']}")
        
        if test_result.get("has_required_fields") is not None:
            fields_icon = "✅" if test_result["has_required_fields"] else "❌"
            print(f"   Required fields: {fields_icon}")
        
        print()
    
    print("Summary:")
    print("-" * 40)
    summary = results["summary"]
    print(f"✅ No 500 errors: {summary['no_500_errors']}")
    print(f"✅ All endpoints accessible: {summary['all_endpoints_accessible']}")
    print(f"✅ Data properly formatted: {summary['data_properly_formatted']}")
    
    # Requirements validation
    print("\nRequirements Validation:")
    print("-" * 40)
    
    # Requirement 1.1: Machine details endpoint returns data without 500 errors
    machine_details_success = (
        results["tests"]["machine_details"]["success"] and 
        results["tests"]["machine_details"]["status_code"] != 500
    )
    print(f"{'✅' if machine_details_success else '❌'} Req 1.1: Machine details endpoint works without 500 errors")
    
    # Requirement 1.4: Machine operations work without 500 errors
    no_500_errors = results["server_errors_count"] == 0
    print(f"{'✅' if no_500_errors else '❌'} Req 1.4: All machine operations work without 500 errors")
    
    # Requirement 2.1: Machine endpoints handle database queries without unhandled exceptions
    all_accessible = summary["all_endpoints_accessible"]
    print(f"{'✅' if all_accessible else '❌'} Req 2.1: Machine endpoints handle database queries properly")
    
    print("\n" + "=" * 60)
    
    if results["overall_success"]:
        print("🎉 All machine endpoints are working correctly from frontend perspective!")
        return True
    else:
        print("❌ Some machine endpoints have issues that need to be addressed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)