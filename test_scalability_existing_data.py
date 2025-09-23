#!/usr/bin/env python3
"""
Scalability validation for ABParts system using existing data.
Tests search, filtering, and pagination performance with current dataset.
"""

import requests
import time
import json
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "http://localhost:8000"
SUPERADMIN_USERNAME = "superadmin"
SUPERADMIN_PASSWORD = "superadmin"

# Test parameters
MAX_RESPONSE_TIME = 5.0  # seconds
REQUEST_DELAY = 0.1  # Delay between requests

class ScalabilityTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.total_parts = 0
        
    def authenticate(self) -> bool:
        """Authenticate with the superadmin user"""
        print("Authenticating with superadmin user...")
        
        auth_data = {
            "username": SUPERADMIN_USERNAME,
            "password": SUPERADMIN_PASSWORD
        }
        
        try:
            response = self.session.post(
                f"{BASE_URL}/token",
                data=auth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                print("✓ Authentication successful")
                return True
            else:
                print(f"✗ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Authentication error: {e}")
            return False
    
    def get_total_parts_count(self) -> int:
        """Get the total number of parts in the system"""
        try:
            # Get a large page to estimate total count
            response = self.session.get(
                f"{BASE_URL}/parts/",
                params={"limit": 1000, "skip": 0}
            )
            
            if response.status_code == 200:
                parts = response.json()
                count = len(parts)
                
                # If we got 1000 parts, there might be more
                if count == 1000:
                    # Try to get more to estimate total
                    response2 = self.session.get(
                        f"{BASE_URL}/parts/",
                        params={"limit": 1000, "skip": 1000}
                    )
                    if response2.status_code == 200:
                        count += len(response2.json())
                
                self.total_parts = count
                print(f"Found {count} parts in the system")
                return count
            else:
                print(f"Failed to get parts count: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"Error getting parts count: {e}")
            return 0
    
    def test_search_performance(self) -> bool:
        """Test search functionality performance"""
        print(f"\n=== Testing Search Performance ===")
        
        search_terms = ["part", "test", "auto", "boss", "filter", "pump", "valve"]
        search_results = {}
        
        for term in search_terms:
            start_time = time.time()
            
            try:
                response = self.session.get(
                    f"{BASE_URL}/parts/",
                    params={"search": term, "limit": 100}
                )
                
                search_time = time.time() - start_time
                
                if response.status_code == 200:
                    results = response.json()
                    result_count = len(results)
                    search_results[term] = {
                        "time": search_time,
                        "count": result_count,
                        "success": True
                    }
                    print(f"Search '{term}': {result_count} results in {search_time:.3f}s")
                else:
                    search_results[term] = {"success": False, "error": response.status_code}
                    print(f"Search '{term}' failed: {response.status_code}")
                
                time.sleep(REQUEST_DELAY)
                    
            except Exception as e:
                search_results[term] = {"success": False, "error": str(e)}
                print(f"Search '{term}' error: {e}")
        
        # Validate search performance
        successful_searches = [r for r in search_results.values() if r.get("success")]
        if successful_searches:
            avg_search_time = sum(r["time"] for r in successful_searches) / len(successful_searches)
            
            if avg_search_time <= MAX_RESPONSE_TIME:
                print(f"✓ Average search time: {avg_search_time:.3f}s (PASS)")
                return True
            else:
                print(f"✗ Average search time: {avg_search_time:.3f}s (FAIL - too slow)")
                return False
        else:
            print("✗ No successful searches")
            return False
    
    def test_filtering_performance(self) -> bool:
        """Test filtering functionality performance"""
        print(f"\n=== Testing Filtering Performance ===")
        
        filters = [
            {"part_type": "CONSUMABLE"},
            {"part_type": "BULK_MATERIAL"},
            {"part_type": "COMPONENT"},
            {"is_proprietary": "true"},
            {"is_proprietary": "false"}
        ]
        
        filter_results = {}
        
        for i, filter_params in enumerate(filters):
            start_time = time.time()
            
            try:
                params = {**filter_params, "limit": 100}
                response = self.session.get(f"{BASE_URL}/parts/", params=params)
                
                filter_time = time.time() - start_time
                
                if response.status_code == 200:
                    results = response.json()
                    result_count = len(results)
                    filter_results[i] = {
                        "time": filter_time,
                        "count": result_count,
                        "success": True,
                        "filter": filter_params
                    }
                    print(f"Filter {filter_params}: {result_count} results in {filter_time:.3f}s")
                else:
                    filter_results[i] = {"success": False, "error": response.status_code}
                    print(f"Filter {filter_params} failed: {response.status_code}")
                
                time.sleep(REQUEST_DELAY)
                    
            except Exception as e:
                filter_results[i] = {"success": False, "error": str(e)}
                print(f"Filter {filter_params} error: {e}")
        
        # Validate filtering performance
        successful_filters = [r for r in filter_results.values() if r.get("success")]
        if successful_filters:
            avg_filter_time = sum(r["time"] for r in successful_filters) / len(successful_filters)
            
            if avg_filter_time <= MAX_RESPONSE_TIME:
                print(f"✓ Average filter time: {avg_filter_time:.3f}s (PASS)")
                return True
            else:
                print(f"✗ Average filter time: {avg_filter_time:.3f}s (FAIL - too slow)")
                return False
        else:
            print("✗ No successful filters")
            return False
    
    def test_pagination_performance(self) -> bool:
        """Test pagination performance with different page sizes and offsets"""
        print(f"\n=== Testing Pagination Performance ===")
        
        pagination_results = {}
        
        # Test different page sizes and offsets
        test_cases = [
            {"skip": 0, "limit": 50},
            {"skip": 0, "limit": 100},
            {"skip": 0, "limit": 500},
            {"skip": 100, "limit": 100},
            {"skip": 500, "limit": 100},
        ]
        
        # Only test offsets that make sense with our data
        if self.total_parts > 1000:
            test_cases.append({"skip": 1000, "limit": 100})
        
        for i, params in enumerate(test_cases):
            if params["skip"] >= self.total_parts:
                continue
                
            start_time = time.time()
            
            try:
                response = self.session.get(
                    f"{BASE_URL}/parts/",
                    params=params
                )
                
                pagination_time = time.time() - start_time
                
                if response.status_code == 200:
                    results = response.json()
                    result_count = len(results)
                    
                    key = f"skip_{params['skip']}_limit_{params['limit']}"
                    pagination_results[key] = {
                        "time": pagination_time,
                        "count": result_count,
                        "success": True
                    }
                    print(f"Pagination skip={params['skip']}, limit={params['limit']}: {result_count} results in {pagination_time:.3f}s")
                else:
                    print(f"Pagination {params} failed: {response.status_code}")
                
                time.sleep(REQUEST_DELAY)
                    
            except Exception as e:
                print(f"Pagination {params} error: {e}")
        
        # Validate pagination performance
        successful_pages = [r for r in pagination_results.values() if r.get("success")]
        if successful_pages:
            avg_pagination_time = sum(r["time"] for r in successful_pages) / len(successful_pages)
            
            if avg_pagination_time <= MAX_RESPONSE_TIME:
                print(f"✓ Average pagination time: {avg_pagination_time:.3f}s (PASS)")
                return True
            else:
                print(f"✗ Average pagination time: {avg_pagination_time:.3f}s (FAIL - too slow)")
                return False
        else:
            print("✗ No successful pagination requests")
            return False
    
    def test_concurrent_access(self) -> bool:
        """Test concurrent access to parts API"""
        print(f"\n=== Testing Concurrent Access Performance ===")
        
        def make_concurrent_request(request_id: int) -> Dict[str, Any]:
            try:
                start_time = time.time()
                response = self.session.get(
                    f"{BASE_URL}/parts/",
                    params={"limit": 50, "skip": request_id * 10}
                )
                request_time = time.time() - start_time
                
                return {
                    "id": request_id,
                    "success": response.status_code == 200,
                    "time": request_time,
                    "status_code": response.status_code
                }
            except Exception as e:
                return {
                    "id": request_id,
                    "success": False,
                    "error": str(e)
                }
        
        # Test with 10 concurrent requests (reduced to avoid rate limiting)
        concurrent_requests = 10
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(make_concurrent_request, i) for i in range(concurrent_requests)]
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        
        successful_requests = [r for r in results if r.get("success")]
        success_rate = len(successful_requests) / len(results) * 100
        
        if successful_requests:
            avg_response_time = sum(r["time"] for r in successful_requests) / len(successful_requests)
            print(f"✓ Concurrent requests: {len(successful_requests)}/{len(results)} successful ({success_rate:.1f}%)")
            print(f"✓ Average response time: {avg_response_time:.3f}s")
            print(f"✓ Total execution time: {total_time:.3f}s")
            
            if success_rate >= 80 and avg_response_time <= MAX_RESPONSE_TIME:
                print("✓ Concurrent access performance: PASS")
                return True
            else:
                print("✗ Concurrent access performance: FAIL")
                return False
        else:
            print("✗ No successful concurrent requests")
            return False
    
    def test_large_page_performance(self) -> bool:
        """Test performance with large page sizes"""
        print(f"\n=== Testing Large Page Performance ===")
        
        page_sizes = [100, 500, 1000]
        if self.total_parts < 1000:
            page_sizes = [min(size, self.total_parts) for size in page_sizes if size <= self.total_parts]
        
        large_page_results = {}
        
        for limit in page_sizes:
            start_time = time.time()
            
            try:
                response = self.session.get(
                    f"{BASE_URL}/parts/",
                    params={"limit": limit, "skip": 0}
                )
                
                page_time = time.time() - start_time
                
                if response.status_code == 200:
                    results = response.json()
                    result_count = len(results)
                    
                    large_page_results[limit] = {
                        "time": page_time,
                        "count": result_count,
                        "success": True
                    }
                    print(f"Large page limit={limit}: {result_count} results in {page_time:.3f}s")
                else:
                    print(f"Large page limit={limit} failed: {response.status_code}")
                
                time.sleep(REQUEST_DELAY)
                    
            except Exception as e:
                print(f"Large page limit={limit} error: {e}")
        
        # Validate large page performance
        successful_pages = [r for r in large_page_results.values() if r.get("success")]
        if successful_pages:
            avg_page_time = sum(r["time"] for r in successful_pages) / len(successful_pages)
            
            if avg_page_time <= MAX_RESPONSE_TIME:
                print(f"✓ Average large page time: {avg_page_time:.3f}s (PASS)")
                return True
            else:
                print(f"✗ Average large page time: {avg_page_time:.3f}s (FAIL - too slow)")
                return False
        else:
            print("✗ No successful large page requests")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all scalability tests"""
        print("=" * 60)
        print("ABParts Scalability Validation Test Suite")
        print("Testing with Existing Data")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        # Get current data size
        parts_count = self.get_total_parts_count()
        if parts_count == 0:
            print("⚠️  No parts found in system. Cannot test scalability.")
            return False
        
        test_results = []
        
        # Test 1: Search performance
        test_results.append(self.test_search_performance())
        
        # Test 2: Filtering performance
        test_results.append(self.test_filtering_performance())
        
        # Test 3: Pagination performance
        test_results.append(self.test_pagination_performance())
        
        # Test 4: Concurrent access
        test_results.append(self.test_concurrent_access())
        
        # Test 5: Large page performance
        test_results.append(self.test_large_page_performance())
        
        # Summary
        print(f"\n=== Test Results Summary ===")
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"Tests passed: {passed_tests}/{total_tests}")
        print(f"Total parts in system: {self.total_parts}")
        
        if passed_tests >= 4:  # Allow one test to fail
            print("✓ SCALABILITY TESTS PASSED")
            return True
        else:
            print("✗ SCALABILITY TESTS FAILED")
            return False

def main():
    """Main test execution"""
    tester = ScalabilityTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 System scalability validation: SUCCESS")
        print("The system demonstrates good performance with existing data.")
        exit(0)
    else:
        print("\n❌ System scalability validation: FAILED")
        exit(1)

if __name__ == "__main__":
    main()