#!/usr/bin/env python3
"""
Focused scalability validation tests for ABParts system.
Tests with smaller dataset but comprehensive performance validation.
"""

import time
import json
import requests
import random
import string
from typing import List, Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
SUPERADMIN_USERNAME = "superadmin"
SUPERADMIN_PASSWORD = "superadmin"
TEST_PARTS_COUNT = 1000  # Reduced for focused testing
BATCH_SIZE = 50  # Smaller batches
DELAY_BETWEEN_BATCHES = 0.1  # Small delay to avoid rate limiting

class FocusedScalabilityTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = {}
        
    def authenticate(self) -> bool:
        """Authenticate with the API and get access token."""
        print("🔐 Authenticating with superadmin credentials...")
        
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
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def generate_test_part(self, index: int) -> Dict[str, Any]:
        """Generate a test part with correct enum values."""
        part_types = ["consumable", "bulk_material"]  # Correct enum values
        manufacturers = ["BossAqua", "Generic Parts Co", "Premium Supplies", "Industrial Components"]
        
        return {
            "part_number": f"SCALE-TEST-{index:06d}",
            "name": f"Scalability Test Part {index}",
            "description": f"Test part for scalability validation - batch {index // BATCH_SIZE}",
            "part_type": random.choice(part_types),
            "is_proprietary": index % 5 == 0,  # 20% proprietary
            "manufacturer": random.choice(manufacturers),
            "unit_cost": round(random.uniform(1.0, 500.0), 2),
            "reorder_point": random.randint(10, 100),
            "reorder_quantity": random.randint(50, 500)
        }
    
    def create_parts_batch(self, start_index: int, batch_size: int) -> Dict[str, Any]:
        """Create a batch of parts and measure performance."""
        batch_start = time.time()
        created_count = 0
        errors = []
        
        for i in range(start_index, start_index + batch_size):
            try:
                part_data = self.generate_test_part(i)
                response = self.session.post(f"{BASE_URL}/parts/", json=part_data)
                
                if response.status_code == 201:
                    created_count += 1
                else:
                    error_msg = f"Part {i}: {response.status_code}"
                    if response.text:
                        error_msg += f" - {response.text[:100]}"
                    errors.append(error_msg)
                    
            except Exception as e:
                errors.append(f"Part {i}: Exception - {str(e)}")
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.01)
        
        batch_time = time.time() - batch_start
        
        return {
            "batch_start": start_index,
            "batch_size": batch_size,
            "created_count": created_count,
            "errors": errors,
            "batch_time": batch_time,
            "parts_per_second": created_count / batch_time if batch_time > 0 else 0
        }
    
    def test_parts_creation(self) -> Dict[str, Any]:
        """Test creating parts with performance monitoring."""
        print(f"\n📝 Testing parts creation with {TEST_PARTS_COUNT} parts...")
        
        start_time = time.time()
        total_created = 0
        all_errors = []
        batch_results = []
        
        # Create parts in batches
        for batch_start in range(0, TEST_PARTS_COUNT, BATCH_SIZE):
            batch_size = min(BATCH_SIZE, TEST_PARTS_COUNT - batch_start)
            
            print(f"   Creating batch {batch_start // BATCH_SIZE + 1}/{(TEST_PARTS_COUNT + BATCH_SIZE - 1) // BATCH_SIZE} "
                  f"(parts {batch_start + 1}-{batch_start + batch_size})")
            
            batch_result = self.create_parts_batch(batch_start, batch_size)
            batch_results.append(batch_result)
            
            total_created += batch_result["created_count"]
            all_errors.extend(batch_result["errors"])
            
            # Show errors for first failed batch
            if batch_result["errors"] and len(all_errors) <= 5:
                print(f"     ⚠️  Batch errors: {batch_result['errors'][:2]}")
            
            # Delay between batches
            time.sleep(DELAY_BETWEEN_BATCHES)
        
        total_time = time.time() - start_time
        
        result = {
            "total_parts_requested": TEST_PARTS_COUNT,
            "total_parts_created": total_created,
            "total_time": total_time,
            "average_parts_per_second": total_created / total_time if total_time > 0 else 0,
            "batch_results": batch_results,
            "error_count": len(all_errors),
            "errors": all_errors[:5] if all_errors else [],  # First 5 errors
            "success_rate": (total_created / TEST_PARTS_COUNT) * 100
        }
        
        print(f"✅ Parts creation completed:")
        print(f"   Created: {total_created}/{TEST_PARTS_COUNT} parts")
        print(f"   Time: {total_time:.2f} seconds")
        print(f"   Speed: {result['average_parts_per_second']:.2f} parts/second")
        print(f"   Success rate: {result['success_rate']:.1f}%")
        
        return result
    
    def test_search_performance(self) -> Dict[str, Any]:
        """Test search functionality with dataset."""
        print(f"\n🔍 Testing search performance...")
        
        search_tests = [
            {"query": "Scalability", "description": "Common word search"},
            {"query": "Test Part", "description": "Specific part search"},
            {"query": "BossAqua", "description": "Manufacturer search"},
            {"query": "SCALE-TEST-000", "description": "Part number search"},
            {"query": "batch", "description": "Description search"}
        ]
        
        results = []
        
        for test in search_tests:
            print(f"   Testing: {test['description']} ('{test['query']}')")
            
            start_time = time.time()
            try:
                response = self.session.get(
                    f"{BASE_URL}/parts/",
                    params={"q": test["query"], "limit": 100},
                    timeout=10
                )
                search_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    result_count = len(data)
                    
                    results.append({
                        "query": test["query"],
                        "description": test["description"],
                        "search_time": search_time,
                        "result_count": result_count,
                        "success": True
                    })
                    
                    print(f"     ✅ Found {result_count} results in {search_time:.3f}s")
                else:
                    results.append({
                        "query": test["query"],
                        "description": test["description"],
                        "search_time": search_time,
                        "error": f"{response.status_code} - {response.text[:100]}",
                        "success": False
                    })
                    print(f"     ❌ Search failed: {response.status_code}")
                    
            except Exception as e:
                search_time = time.time() - start_time
                results.append({
                    "query": test["query"],
                    "description": test["description"],
                    "search_time": search_time,
                    "error": str(e),
                    "success": False
                })
                print(f"     ❌ Search error: {str(e)}")
        
        successful_results = [r for r in results if r["success"]]
        avg_search_time = sum(r["search_time"] for r in successful_results) / len(successful_results) if successful_results else 0
        
        summary = {
            "search_tests": results,
            "average_search_time": avg_search_time,
            "successful_searches": len(successful_results),
            "total_searches": len(results)
        }
        
        print(f"✅ Search performance summary:")
        print(f"   Average search time: {avg_search_time:.3f} seconds")
        print(f"   Successful searches: {summary['successful_searches']}/{summary['total_searches']}")
        
        return summary
    
    def test_pagination_performance(self) -> Dict[str, Any]:
        """Test pagination performance."""
        print(f"\n📄 Testing pagination performance...")
        
        pagination_tests = [
            {"limit": 50, "pages_to_test": 5},
            {"limit": 100, "pages_to_test": 3},
            {"limit": 200, "pages_to_test": 2}
        ]
        
        results = []
        
        for test in pagination_tests:
            print(f"   Testing pagination with limit={test['limit']}")
            
            page_times = []
            
            for page in range(test["pages_to_test"]):
                skip = page * test["limit"]
                
                start_time = time.time()
                try:
                    response = self.session.get(
                        f"{BASE_URL}/parts/",
                        params={"skip": skip, "limit": test["limit"]},
                        timeout=10
                    )
                    page_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        page_times.append(page_time)
                        
                        if page == 0:  # First page info
                            print(f"     Page {page + 1}: {len(data)} results in {page_time:.3f}s")
                    else:
                        print(f"     ❌ Page {page + 1} failed: {response.status_code}")
                        break
                        
                except Exception as e:
                    print(f"     ❌ Page {page + 1} error: {str(e)}")
                    break
            
            if page_times:
                avg_page_time = sum(page_times) / len(page_times)
                results.append({
                    "limit": test["limit"],
                    "pages_tested": len(page_times),
                    "average_page_time": avg_page_time,
                    "min_page_time": min(page_times),
                    "max_page_time": max(page_times),
                    "success": True
                })
                
                print(f"     ✅ Average page load: {avg_page_time:.3f}s "
                      f"(min: {min(page_times):.3f}s, max: {max(page_times):.3f}s)")
            else:
                results.append({
                    "limit": test["limit"],
                    "success": False,
                    "error": "No successful page loads"
                })
        
        successful_results = [r for r in results if r["success"]]
        overall_avg = sum(r["average_page_time"] for r in successful_results) / len(successful_results) if successful_results else 0
        
        summary = {
            "pagination_tests": results,
            "overall_average_page_time": overall_avg,
            "successful_tests": len(successful_results),
            "total_tests": len(results)
        }
        
        print(f"✅ Pagination performance summary:")
        print(f"   Overall average page time: {overall_avg:.3f} seconds")
        print(f"   Successful tests: {summary['successful_tests']}/{summary['total_tests']}")
        
        return summary
    
    def test_filtering_performance(self) -> Dict[str, Any]:
        """Test filtering functionality."""
        print(f"\n🔧 Testing filtering performance...")
        
        filter_tests = [
            {"part_type": "consumable", "description": "Filter by consumable parts"},
            {"part_type": "bulk_material", "description": "Filter by bulk material parts"},
            {"is_proprietary": "true", "description": "Filter proprietary parts"},
            {"is_proprietary": "false", "description": "Filter non-proprietary parts"},
        ]
        
        results = []
        
        for test in filter_tests:
            print(f"   Testing: {test['description']}")
            
            # Remove description for API call
            params = {k: v for k, v in test.items() if k != "description"}
            params["limit"] = 100
            
            start_time = time.time()
            try:
                response = self.session.get(f"{BASE_URL}/parts/", params=params, timeout=10)
                filter_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    result_count = len(data)
                    
                    results.append({
                        "filter": params,
                        "description": test["description"],
                        "filter_time": filter_time,
                        "result_count": result_count,
                        "success": True
                    })
                    
                    print(f"     ✅ Found {result_count} results in {filter_time:.3f}s")
                else:
                    results.append({
                        "filter": params,
                        "description": test["description"],
                        "filter_time": filter_time,
                        "error": f"{response.status_code} - {response.text[:100]}",
                        "success": False
                    })
                    print(f"     ❌ Filter failed: {response.status_code}")
                    
            except Exception as e:
                filter_time = time.time() - start_time
                results.append({
                    "filter": params,
                    "description": test["description"],
                    "filter_time": filter_time,
                    "error": str(e),
                    "success": False
                })
                print(f"     ❌ Filter error: {str(e)}")
        
        successful_results = [r for r in results if r["success"]]
        avg_filter_time = sum(r["filter_time"] for r in successful_results) / len(successful_results) if successful_results else 0
        
        summary = {
            "filter_tests": results,
            "average_filter_time": avg_filter_time,
            "successful_filters": len(successful_results),
            "total_filters": len(results)
        }
        
        print(f"✅ Filtering performance summary:")
        print(f"   Average filter time: {avg_filter_time:.3f} seconds")
        print(f"   Successful filters: {summary['successful_filters']}/{summary['total_filters']}")
        
        return summary
    
    def cleanup_test_data(self) -> Dict[str, Any]:
        """Clean up test data created during scalability tests."""
        print(f"\n🧹 Cleaning up test data...")
        
        # Get all test parts (those with part numbers starting with SCALE-TEST-)
        try:
            response = self.session.get(
                f"{BASE_URL}/parts/",
                params={"q": "SCALE-TEST-", "limit": 1000}
            )
            
            if response.status_code != 200:
                return {"error": f"Failed to fetch test parts: {response.status_code}"}
            
            test_parts = response.json()
            deleted_count = 0
            errors = []
            
            print(f"   Found {len(test_parts)} test parts to delete...")
            
            for part in test_parts:
                try:
                    delete_response = self.session.delete(f"{BASE_URL}/parts/{part['id']}")
                    if delete_response.status_code in [200, 204]:
                        deleted_count += 1
                    else:
                        errors.append(f"Part {part['part_number']}: {delete_response.status_code}")
                except Exception as e:
                    errors.append(f"Part {part['part_number']}: {str(e)}")
            
            result = {
                "parts_found": len(test_parts),
                "parts_deleted": deleted_count,
                "errors": errors[:5] if errors else []  # First 5 errors
            }
            
            print(f"✅ Cleanup completed: {deleted_count}/{len(test_parts)} parts deleted")
            
            return result
            
        except Exception as e:
            return {"error": f"Cleanup failed: {str(e)}"}
    
    def run_focused_scalability_test(self) -> Dict[str, Any]:
        """Run focused scalability validation test suite."""
        print("🚀 Starting ABParts Focused Scalability Validation")
        print("=" * 60)
        
        if not self.authenticate():
            return {"error": "Authentication failed"}
        
        # Run all tests
        test_results = {}
        
        try:
            # 1. Parts Creation Test
            test_results["parts_creation"] = self.test_parts_creation()
            
            # Only continue with other tests if we created some parts
            if test_results["parts_creation"]["total_parts_created"] > 0:
                # 2. Search Performance Test
                test_results["search_performance"] = self.test_search_performance()
                
                # 3. Filtering Performance Test
                test_results["filtering_performance"] = self.test_filtering_performance()
                
                # 4. Pagination Performance Test
                test_results["pagination_performance"] = self.test_pagination_performance()
                
                # 5. Cleanup
                test_results["cleanup"] = self.cleanup_test_data()
            else:
                print("⚠️  Skipping performance tests due to parts creation failure")
            
        except Exception as e:
            test_results["error"] = f"Test suite failed: {str(e)}"
        
        # Generate summary
        test_results["summary"] = self.generate_test_summary(test_results)
        
        return test_results
    
    def generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall test summary and recommendations."""
        summary = {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_parts_tested": TEST_PARTS_COUNT,
            "performance_metrics": {},
            "recommendations": [],
            "overall_status": "PASS"
        }
        
        # Extract key metrics
        if "parts_creation" in results:
            creation = results["parts_creation"]
            summary["performance_metrics"]["parts_creation_rate"] = creation.get("average_parts_per_second", 0)
            summary["performance_metrics"]["parts_creation_success_rate"] = creation.get("success_rate", 0)
            
            if creation.get("success_rate", 0) < 95:
                summary["recommendations"].append("Parts creation success rate below 95% - investigate API errors")
                if creation.get("success_rate", 0) < 50:
                    summary["overall_status"] = "FAIL"
                else:
                    summary["overall_status"] = "WARNING"
        
        if "search_performance" in results:
            search = results["search_performance"]
            summary["performance_metrics"]["average_search_time"] = search.get("average_search_time", 0)
            
            if search.get("average_search_time", 0) > 2.0:
                summary["recommendations"].append("Search response time > 2s - consider database indexing optimization")
                summary["overall_status"] = "WARNING"
        
        if "pagination_performance" in results:
            pagination = results["pagination_performance"]
            summary["performance_metrics"]["average_page_load_time"] = pagination.get("overall_average_page_time", 0)
            
            if pagination.get("overall_average_page_time", 0) > 1.0:
                summary["recommendations"].append("Pagination response time > 1s - optimize database queries")
                summary["overall_status"] = "WARNING"
        
        if "filtering_performance" in results:
            filtering = results["filtering_performance"]
            summary["performance_metrics"]["average_filter_time"] = filtering.get("average_filter_time", 0)
            
            if filtering.get("average_filter_time", 0) > 2.0:
                summary["recommendations"].append("Filter response time > 2s - optimize database queries")
                summary["overall_status"] = "WARNING"
        
        if not summary["recommendations"]:
            summary["recommendations"].append("All performance tests passed - system scales well with datasets")
        
        return summary

def main():
    """Main execution function."""
    tester = FocusedScalabilityTester()
    results = tester.run_focused_scalability_test()
    
    # Save results to file
    with open("focused_scalability_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "=" * 60)
    print("📊 FOCUSED SCALABILITY TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if "summary" in results:
        summary = results["summary"]
        print(f"Overall Status: {summary['overall_status']}")
        print(f"Test Timestamp: {summary['test_timestamp']}")
        print(f"Parts Tested: {summary['total_parts_tested']}")
        
        print("\nPerformance Metrics:")
        for metric, value in summary["performance_metrics"].items():
            if isinstance(value, float):
                print(f"  {metric}: {value:.3f}")
            else:
                print(f"  {metric}: {value}")
        
        print("\nRecommendations:")
        for rec in summary["recommendations"]:
            print(f"  • {rec}")
    
    print(f"\n📄 Detailed results saved to: focused_scalability_results.json")
    print("=" * 60)

if __name__ == "__main__":
    main()