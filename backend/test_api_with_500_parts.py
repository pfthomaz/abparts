#!/usr/bin/env python3
"""
Test script to validate API endpoints work correctly with 500+ parts.
Tests authentication, parts retrieval, search, and pagination via API.
"""

import requests
import json
import time
import sys


class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {}
    
    def authenticate(self, username="superadmin", password="superadmin"):
        """Authenticate with the API and get access token."""
        print(f"🔐 Authenticating as {username}...")
        
        auth_data = {
            "username": username,
            "password": password
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/token",
                data=auth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_parts_endpoint(self):
        """Test the basic parts endpoint."""
        print("\n🔍 Testing /parts endpoint...")
        
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/parts",
                headers=self.headers,
                params={"limit": 100}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                parts_count = len(data.get("items", data))  # Handle both formats
                print(f"✅ Retrieved {parts_count} parts")
                print(f"⏱️  Response time: {response_time:.3f}s")
                return parts_count, response_time
            else:
                print(f"❌ Parts endpoint failed: {response.status_code} - {response.text}")
                return 0, response_time
                
        except Exception as e:
            print(f"❌ Parts endpoint error: {e}")
            return 0, 0
    
    def test_parts_with_inventory(self):
        """Test the parts with inventory endpoint."""
        print("\n📦 Testing /parts/with-inventory endpoint...")
        
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/parts/with-inventory",
                headers=self.headers,
                params={"limit": 100}
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                parts_count = len(data.get("items", data))
                print(f"✅ Retrieved {parts_count} parts with inventory")
                print(f"⏱️  Response time: {response_time:.3f}s")
                
                # Check if parts have inventory data
                if parts_count > 0:
                    first_part = data.get("items", data)[0]
                    has_inventory = "total_stock" in first_part or "warehouse_inventory" in first_part
                    print(f"📊 Inventory data present: {'Yes' if has_inventory else 'No'}")
                
                return parts_count, response_time
            else:
                print(f"❌ Parts with inventory endpoint failed: {response.status_code} - {response.text}")
                return 0, response_time
                
        except Exception as e:
            print(f"❌ Parts with inventory error: {e}")
            return 0, 0
    
    def test_parts_search(self):
        """Test the parts search functionality."""
        print("\n🔍 Testing parts search...")
        
        search_terms = ["Filter", "Pump", "Oil", "PERF"]
        
        for term in search_terms:
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.base_url}/parts/search",
                    headers=self.headers,
                    params={"q": term, "limit": 50}
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    results_count = len(data.get("items", data))
                    print(f"🔍 Search '{term}': {results_count} results ({response_time:.3f}s)")
                else:
                    print(f"❌ Search '{term}' failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Search '{term}' error: {e}")
    
    def test_pagination(self):
        """Test pagination with different page sizes."""
        print("\n📄 Testing pagination...")
        
        page_sizes = [20, 50, 100]
        
        for page_size in page_sizes:
            try:
                # Test first page
                start_time = time.time()
                response = requests.get(
                    f"{self.base_url}/parts/with-inventory",
                    headers=self.headers,
                    params={"skip": 0, "limit": page_size}
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    parts_count = len(data.get("items", data))
                    print(f"📄 Page size {page_size}: {parts_count} parts ({response_time:.3f}s)")
                else:
                    print(f"❌ Pagination test failed for page size {page_size}")
                    
            except Exception as e:
                print(f"❌ Pagination error for page size {page_size}: {e}")
    
    def test_create_part(self):
        """Test creating a new part via API."""
        print("\n🔧 Testing part creation...")
        
        # Generate unique part number
        import time
        timestamp = int(time.time() * 1000) % 1000000
        
        new_part = {
            "part_number": f"API-TEST-{timestamp}",
            "name": f"API Test Part {timestamp}",
            "description": "Test part created via API to validate 500+ parts functionality",
            "part_type": "consumable",
            "is_proprietary": False,
            "unit_of_measure": "pieces"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/parts",
                headers=self.headers,
                json=new_part
            )
            response_time = time.time() - start_time
            
            if response.status_code == 201:
                created_part = response.json()
                print(f"✅ Created part: {created_part['part_number']}")
                print(f"⏱️  Creation time: {response_time:.3f}s")
                return created_part
            else:
                print(f"❌ Part creation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Part creation error: {e}")
            return None
    
    def run_all_tests(self):
        """Run all API tests."""
        print("🚀 Starting API Tests with 500+ Parts")
        print("=" * 50)
        
        # Authenticate
        if not self.authenticate():
            return False
        
        # Test basic parts endpoint
        parts_count, response_time = self.test_parts_endpoint()
        
        # Test parts with inventory
        inventory_count, inventory_time = self.test_parts_with_inventory()
        
        # Test search functionality
        self.test_parts_search()
        
        # Test pagination
        self.test_pagination()
        
        # Test part creation
        created_part = self.test_create_part()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 API TEST SUMMARY")
        print("=" * 50)
        print(f"🔐 Authentication: {'✅ Success' if self.token else '❌ Failed'}")
        print(f"📊 Parts retrieved: {parts_count}")
        print(f"📦 Parts with inventory: {inventory_count}")
        print(f"⏱️  Average response time: {(response_time + inventory_time) / 2:.3f}s")
        print(f"🔧 Part creation: {'✅ Success' if created_part else '❌ Failed'}")
        
        # Performance assessment
        avg_time = (response_time + inventory_time) / 2
        if avg_time < 1.0:
            print("🎉 EXCELLENT: API performance is great!")
        elif avg_time < 3.0:
            print("✅ GOOD: API performance is acceptable")
        else:
            print("⚠️  WARNING: API performance needs optimization")
        
        return True


def main():
    """Main test function."""
    tester = APITester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎯 Next steps:")
            print("1. Open the web interface: http://localhost:3000")
            print("2. Login with username: superadmin, password: superadmin")
            print("3. Navigate to the Parts page")
            print("4. Verify you can see the parts and test the interface")
            return 0
        else:
            print("\n❌ API tests failed!")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())