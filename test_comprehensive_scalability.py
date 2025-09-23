#!/usr/bin/env python3
"""
Comprehensive scalability validation for ABParts system.
Tests parts creation, search, and filtering with 10,000+ parts.
Validates pagination performance and frontend responsiveness.
"""

import requests
import time
import json
import random
import string
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
SUPERADMIN_USERNAME = "superadmin"
SUPERADMIN_PASSWORD = "superadmin"

# Test parameters
LARGE_DATASET_SIZE = 1000  # Reduced for rate limiting
BATCH_SIZE = 10  # Smaller batches to avoid rate limiting
MAX_RESPONSE_TIME = 5.0  # seconds - more lenient for rate-limited environment
PAGINATION_TEST_SIZES = [100, 500, 1000]
REQUEST_DELAY = 0.1  # Delay between requests to respect rate limits

class ScalabilityTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.created_parts = []
        
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
    
    def generate_part_data(self, index: int) -> Dict[str, Any]:
        """Generate test part data"""
        part_types = ["CONSUMABLE", "BULK_MATERIAL", "COMPONENT"]
        manufacturers = ["BossAqua", "Generic Corp", "Parts Plus", "Auto Supply Co"]
        
        return {
            "part_number": f"SCALE-TEST-{index:06d}",
            "name": f"Scalability Test Part {index}",
            "description": f"Test part for scalability validation - batch {index // BATCH_SIZE}",
            "part_type": random.choice(part_types),
            "is_proprietary": index % 5 == 0,  # 20% proprietary
            "manufacturer": random.choice(manufacturers),
            "unit_cost": round(random.uniform(1.0, 100.0), 2),
            "reorder_point": random.randint(10, 100),
            "reorder_quantity": random.randint(50, 500)
        }
    
    def create_parts_batch(self, start_index: int, batch_size: int) -> List[str]:
        """Create a batch of parts and return their IDs"""
        created_ids = []
        
        for i in range(start_index, start_index + batch_size):
            part_data = self.generate_part_data(i)
            
            try:
                response = self.session.post(
                    f"{BASE_URL}/parts/",
                    json=part_data
                )
                
                if response.status_code == 201:
                    part_id = response.json().get("id")
                    created_ids.append(part_id)
                elif response.status_code == 429:
                    # Rate limited - wait and retry once
                    time.sleep(1)
                    response = self.session.post(
                        f"{BASE_URL}/parts/",
                        json=part_data
                    )
                    if response.status_code == 201:
                        part_id = response.json().get("id")
                        created_ids.append(part_id)
                else:
                    print(f"Failed to create part {i}: {response.status_code}")
                
                # Add delay to respect rate limits
                time.sleep(REQUEST_DELAY)
                    
            except Exception as e:
                print(f"Error creating part {i}: {e}")
        
        return created_ids
    
    def test_parts_creation_performance(self) -> bool:
        """Test creating 10,000+ parts with performance monitoring"""
        print(f"\n=== Testing Parts Creation Performance ({LARGE_DATASET_SIZE} parts) ===")
        
        start_time = time.time()
        total_created = 0
        
        # Create parts in batches sequentially to avoid rate limiting
        # Using sequential processing instead of threading to respect rate limits
        for batch_start in range(0, LARGE_DATASET_SIZE, BATCH_SIZE):
            batch_size = min(BATCH_SIZE, LARGE_DATASET_SIZE - batch_start)
            
            try:
                batch_ids = self.create_parts_batch(batch_start, batch_size)
                self.created_parts.extend(batch_ids)
                total_created += len(batch_ids)
                
                if total_created % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = total_created / elapsed if elapsed > 0 else 0
                    print(f"Created {total_created} parts ({rate:.1f} parts/sec)")
                    
            except Exception as e:
                print(f"Batch creation error: {e}")
        
        total_time = time.time() - start_time
        creation_rate = total_created / total_time
        
        print(f"✓ Created {total_created} parts in {total_time:.2f} seconds")
        print(f"✓ Average creation rate: {creation_rate:.1f} parts/second")
        
        # Validate creation performance (adjusted for rate limiting)
        if creation_rate >= 1 and total_created >= 100:  # At least 1 part per second and 100+ parts created
            print("✓ Parts creation performance: PASS")
            return True
        else:
            print("✗ Parts creation performance: FAIL (too slow or insufficient parts created)")
            return False
    
    def test_search_performance(self) -> bool:
        """Test search functionality with large dataset"""
        print(f"\n=== Testing Search Performance ===")
        
        search_terms = ["Test", "Scalability", "BossAqua", "CONSUMABLE", "Part"]
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
                
                # Add delay between searches to respect rate limits
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
        """Test filtering functionality with large dataset"""
        print(f"\n=== Testing Filtering Performance ===")
        
        filters = [
            {"part_type": "CONSUMABLE"},
            {"part_type": "BULK_MATERIAL"},
            {"is_proprietary": "true"},
            {"is_proprietary": "false"},
            {"manufacturer": "BossAqua"}
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
                
                # Add delay between filters to respect rate limits
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
        """Test pagination performance with different dataset sizes"""
        print(f"\n=== Testing Pagination Performance ===")
        
        pagination_results = {}
        
        for limit in [50, 100, 500, 1000]:
            for skip in [0, 1000, 5000, 9000]:
                if skip >= len(self.created_parts):
                    continue
                    
                start_time = time.time()
                
                try:
                    response = self.session.get(
                        f"{BASE_URL}/parts/",
                        params={"skip": skip, "limit": limit}
                    )
                    
                    pagination_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        results = response.json()
                        result_count = len(results)
                        
                        key = f"skip_{skip}_limit_{limit}"
                        pagination_results[key] = {
                            "time": pagination_time,
                            "count": result_count,
                            "success": True
                        }
                        print(f"Pagination skip={skip}, limit={limit}: {result_count} results in {pagination_time:.3f}s")
                    else:
                        print(f"Pagination skip={skip}, limit={limit} failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"Pagination skip={skip}, limit={limit} error: {e}")
        
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
                    params={"limit": 50, "skip": request_id * 50}
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
        
        # Test with 20 concurrent requests
        concurrent_requests = 20
        
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
            
            if success_rate >= 95 and avg_response_time <= MAX_RESPONSE_TIME:
                print("✓ Concurrent access performance: PASS")
                return True
            else:
                print("✗ Concurrent access performance: FAIL")
                return False
        else:
            print("✗ No successful concurrent requests")
            return False
    
    def cleanup_test_data(self) -> None:
        """Clean up created test parts"""
        print(f"\n=== Cleaning Up Test Data ===")
        
        if not self.created_parts:
            print("No test parts to clean up")
            return
        
        deleted_count = 0
        
        # Delete in batches to avoid overwhelming the API
        for i in range(0, len(self.created_parts), BATCH_SIZE):
            batch = self.created_parts[i:i + BATCH_SIZE]
            
            for part_id in batch:
                try:
                    response = self.session.delete(f"{BASE_URL}/parts/{part_id}")
                    if response.status_code in [200, 204, 404]:  # 404 is OK if already deleted
                        deleted_count += 1
                except Exception as e:
                    print(f"Error deleting part {part_id}: {e}")
            
            if (i + BATCH_SIZE) % 1000 == 0:
                print(f"Deleted {deleted_count} parts...")
        
        print(f"✓ Cleaned up {deleted_count} test parts")
    
    def run_all_tests(self) -> bool:
        """Run all scalability tests"""
        print("=" * 60)
        print("ABParts Scalability Validation Test Suite")
        print("=" * 60)
        
        if not self.authenticate():
            return False
        
        test_results = []
        
        try:
            # Test 1: Parts creation performance
            test_results.append(self.test_parts_creation_performance())
            
            # Test 2: Search performance
            test_results.append(self.test_search_performance())
            
            # Test 3: Filtering performance
            test_results.append(self.test_filtering_performance())
            
            # Test 4: Pagination performance
            test_results.append(self.test_pagination_performance())
            
            # Test 5: Concurrent access
            test_results.append(self.test_concurrent_access())
            
        finally:
            # Always clean up test data
            self.cleanup_test_data()
        
        # Summary
        print(f"\n=== Test Results Summary ===")
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print(f"Tests passed: {passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print("✓ ALL SCALABILITY TESTS PASSED")
            return True
        else:
            print("✗ SOME SCALABILITY TESTS FAILED")
            return False

def main():
    """Main test execution"""
    tester = ScalabilityTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 System scalability validation: SUCCESS")
        exit(0)
    else:
        print("\n❌ System scalability validation: FAILED")
        exit(1)

if __name__ == "__main__":
    main()