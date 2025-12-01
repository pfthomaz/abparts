#!/usr/bin/env python3
"""
Performance validation tests for ABParts system.
Tests system performance with existing data and validates scalability requirements.
"""

import time
import json
import requests
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "http://localhost:8000"
SUPERADMIN_USERNAME = "superadmin"
SUPERADMIN_PASSWORD = "superadmin"
CONCURRENT_REQUESTS = 5
PERFORMANCE_ITERATIONS = 10

class PerformanceValidator:
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
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system information."""
        print("📊 Gathering system information...")
        
        info = {}
        
        try:
            # Get parts count
            response = self.session.get(f"{BASE_URL}/parts/", params={"limit": 1000})
            if response.status_code == 200:
                parts = response.json()
                info["total_parts"] = len(parts)
                print(f"   Total parts in system: {info['total_parts']}")
            else:
                info["total_parts"] = 0
                print(f"   Could not get parts count: {response.status_code}")
            
            # Get organizations count
            try:
                response = self.session.get(f"{BASE_URL}/organizations/")
                if response.status_code == 200:
                    orgs = response.json()
                    info["total_organizations"] = len(orgs)
                    print(f"   Total organizations: {info['total_organizations']}")
            except:
                info["total_organizations"] = 0
            
            # Get warehouses count
            try:
                response = self.session.get(f"{BASE_URL}/warehouses/")
                if response.status_code == 200:
                    warehouses = response.json()
                    info["total_warehouses"] = len(warehouses)
                    print(f"   Total warehouses: {info['total_warehouses']}")
            except:
                info["total_warehouses"] = 0
            
        except Exception as e:
            print(f"   ⚠️  Error gathering system info: {str(e)}")
        
        return info
    
    def test_api_response_times(self) -> Dict[str, Any]:
        """Test API response times for various endpoints."""
        print(f"\n⚡ Testing API response times ({PERFORMANCE_ITERATIONS} iterations each)...")
        
        endpoints = [
            {"url": "/parts/", "params": {"limit": 100}, "description": "Get parts (limit 100)"},
            {"url": "/parts/", "params": {"limit": 50}, "description": "Get parts (limit 50)"},
            {"url": "/parts/", "params": {"limit": 10}, "description": "Get parts (limit 10)"},
            {"url": "/organizations/", "params": {}, "description": "Get organizations"},
            {"url": "/warehouses/", "params": {}, "description": "Get warehouses"},
        ]
        
        results = []
        
        for endpoint in endpoints:
            print(f"   Testing: {endpoint['description']}")
            
            times = []
            errors = 0
            
            for i in range(PERFORMANCE_ITERATIONS):
                start_time = time.time()
                try:
                    response = self.session.get(
                        f"{BASE_URL}{endpoint['url']}", 
                        params=endpoint['params'],
                        timeout=10
                    )
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        times.append(response_time)
                    else:
                        errors += 1
                        
                except Exception as e:
                    errors += 1
                
                # Small delay between requests
                time.sleep(0.1)
            
            if times:
                result = {
                    "endpoint": endpoint['description'],
                    "url": endpoint['url'],
                    "iterations": len(times),
                    "avg_response_time": statistics.mean(times),
                    "min_response_time": min(times),
                    "max_response_time": max(times),
                    "median_response_time": statistics.median(times),
                    "errors": errors,
                    "success_rate": (len(times) / PERFORMANCE_ITERATIONS) * 100
                }
                
                print(f"     ✅ Avg: {result['avg_response_time']:.3f}s, "
                      f"Min: {result['min_response_time']:.3f}s, "
                      f"Max: {result['max_response_time']:.3f}s")
            else:
                result = {
                    "endpoint": endpoint['description'],
                    "url": endpoint['url'],
                    "errors": errors,
                    "success_rate": 0,
                    "error": "All requests failed"
                }
                print(f"     ❌ All requests failed")
            
            results.append(result)
        
        return {"endpoint_tests": results}
    
    def test_search_performance(self) -> Dict[str, Any]:
        """Test search performance with various queries."""
        print(f"\n🔍 Testing search performance...")
        
        search_queries = [
            {"q": "", "description": "Empty search (all parts)"},
            {"q": "part", "description": "Generic search term"},
            {"q": "test", "description": "Test search term"},
            {"q": "nonexistent", "description": "No results search"},
        ]
        
        results = []
        
        for query in search_queries:
            print(f"   Testing: {query['description']}")
            
            times = []
            result_counts = []
            errors = 0
            
            for i in range(5):  # Fewer iterations for search
                start_time = time.time()
                try:
                    response = self.session.get(
                        f"{BASE_URL}/parts/",
                        params={"q": query["q"], "limit": 100},
                        timeout=10
                    )
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        times.append(response_time)
                        result_counts.append(len(data))
                    else:
                        errors += 1
                        
                except Exception as e:
                    errors += 1
                
                time.sleep(0.2)  # Longer delay for search
            
            if times:
                result = {
                    "query": query["q"],
                    "description": query["description"],
                    "avg_response_time": statistics.mean(times),
                    "avg_result_count": statistics.mean(result_counts),
                    "errors": errors,
                    "success": True
                }
                
                print(f"     ✅ Avg time: {result['avg_response_time']:.3f}s, "
                      f"Avg results: {result['avg_result_count']:.1f}")
            else:
                result = {
                    "query": query["q"],
                    "description": query["description"],
                    "errors": errors,
                    "success": False
                }
                print(f"     ❌ All searches failed")
            
            results.append(result)
        
        return {"search_tests": results}
    
    def test_pagination_performance(self) -> Dict[str, Any]:
        """Test pagination performance."""
        print(f"\n📄 Testing pagination performance...")
        
        pagination_tests = [
            {"limit": 10, "pages": 3},
            {"limit": 25, "pages": 2},
            {"limit": 50, "pages": 2},
        ]
        
        results = []
        
        for test in pagination_tests:
            print(f"   Testing: limit={test['limit']}, {test['pages']} pages")
            
            page_times = []
            
            for page in range(test["pages"]):
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
                        print(f"     Page {page + 1}: {len(data)} results in {page_time:.3f}s")
                    else:
                        print(f"     ❌ Page {page + 1} failed: {response.status_code}")
                        break
                        
                except Exception as e:
                    print(f"     ❌ Page {page + 1} error: {str(e)}")
                    break
                
                time.sleep(0.1)
            
            if page_times:
                result = {
                    "limit": test["limit"],
                    "pages_tested": len(page_times),
                    "avg_page_time": statistics.mean(page_times),
                    "min_page_time": min(page_times),
                    "max_page_time": max(page_times),
                    "success": True
                }
                
                print(f"     ✅ Average: {result['avg_page_time']:.3f}s")
            else:
                result = {
                    "limit": test["limit"],
                    "success": False,
                    "error": "No successful page loads"
                }
            
            results.append(result)
        
        return {"pagination_tests": results}
    
    def test_concurrent_access(self) -> Dict[str, Any]:
        """Test concurrent access performance."""
        print(f"\n🔄 Testing concurrent access ({CONCURRENT_REQUESTS} simultaneous requests)...")
        
        def make_request(request_id: int) -> Dict[str, Any]:
            start_time = time.time()
            try:
                response = requests.get(
                    f"{BASE_URL}/parts/",
                    params={"limit": 50},
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                    timeout=10
                )
                request_time = time.time() - start_time
                
                return {
                    "request_id": request_id,
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response_time": request_time,
                    "result_count": len(response.json()) if response.status_code == 200 else 0
                }
            except Exception as e:
                return {
                    "request_id": request_id,
                    "success": False,
                    "error": str(e),
                    "response_time": time.time() - start_time
                }
        
        # Execute concurrent requests
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS) as executor:
            futures = [executor.submit(make_request, i) for i in range(CONCURRENT_REQUESTS)]
            concurrent_results = [future.result() for future in as_completed(futures)]
        total_time = time.time() - start_time
        
        successful_requests = [r for r in concurrent_results if r["success"]]
        
        if successful_requests:
            avg_response_time = statistics.mean([r["response_time"] for r in successful_requests])
            
            summary = {
                "concurrent_requests": CONCURRENT_REQUESTS,
                "total_time": total_time,
                "successful_requests": len(successful_requests),
                "failed_requests": len(concurrent_results) - len(successful_requests),
                "average_response_time": avg_response_time,
                "requests_per_second": len(successful_requests) / total_time if total_time > 0 else 0,
                "detailed_results": concurrent_results
            }
            
            print(f"✅ Concurrent access summary:")
            print(f"   Successful requests: {len(successful_requests)}/{CONCURRENT_REQUESTS}")
            print(f"   Average response time: {avg_response_time:.3f} seconds")
            print(f"   Requests per second: {summary['requests_per_second']:.2f}")
        else:
            summary = {
                "concurrent_requests": CONCURRENT_REQUESTS,
                "successful_requests": 0,
                "failed_requests": CONCURRENT_REQUESTS,
                "error": "All concurrent requests failed"
            }
            print(f"❌ All concurrent requests failed")
        
        return summary
    
    def validate_performance_requirements(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate results against performance requirements."""
        print(f"\n✅ Validating performance against requirements...")
        
        validation = {
            "requirements_validation": {},
            "overall_status": "PASS"
        }
        
        # Requirement 2.1: API response times < 2 seconds
        api_times = []
        if "api_response_times" in results and "endpoint_tests" in results["api_response_times"]:
            for test in results["api_response_times"]["endpoint_tests"]:
                if "avg_response_time" in test:
                    api_times.append(test["avg_response_time"])
        
        if api_times:
            max_api_time = max(api_times)
            validation["requirements_validation"]["2.1"] = {
                "requirement": "API response times < 2 seconds",
                "max_response_time": max_api_time,
                "status": "PASS" if max_api_time < 2.0 else "FAIL"
            }
            if max_api_time >= 2.0:
                validation["overall_status"] = "FAIL"
        
        # Requirement 2.2: Pagination < 1 second
        pagination_times = []
        if "pagination_performance" in results and "pagination_tests" in results["pagination_performance"]:
            for test in results["pagination_performance"]["pagination_tests"]:
                if "avg_page_time" in test:
                    pagination_times.append(test["avg_page_time"])
        
        if pagination_times:
            max_pagination_time = max(pagination_times)
            validation["requirements_validation"]["2.2"] = {
                "requirement": "Pagination response time < 1 second",
                "max_pagination_time": max_pagination_time,
                "status": "PASS" if max_pagination_time < 1.0 else "FAIL"
            }
            if max_pagination_time >= 1.0:
                validation["overall_status"] = "WARNING"
        
        # Requirement 2.3: Search performance < 2 seconds
        search_times = []
        if "search_performance" in results and "search_tests" in results["search_performance"]:
            for test in results["search_performance"]["search_tests"]:
                if "avg_response_time" in test:
                    search_times.append(test["avg_response_time"])
        
        if search_times:
            max_search_time = max(search_times)
            validation["requirements_validation"]["2.3"] = {
                "requirement": "Search response time < 2 seconds",
                "max_search_time": max_search_time,
                "status": "PASS" if max_search_time < 2.0 else "FAIL"
            }
            if max_search_time >= 2.0:
                validation["overall_status"] = "WARNING"
        
        # Print validation results
        for req_id, req_data in validation["requirements_validation"].items():
            status_icon = {"PASS": "✅", "FAIL": "❌", "WARNING": "⚠️"}[req_data["status"]]
            print(f"   {status_icon} Requirement {req_id}: {req_data['requirement']}")
        
        return validation
    
    def run_performance_validation(self) -> Dict[str, Any]:
        """Run complete performance validation test suite."""
        print("🚀 ABParts Performance Validation Test Suite")
        print("=" * 60)
        
        if not self.authenticate():
            return {"error": "Authentication failed"}
        
        # Get system information
        system_info = self.get_system_info()
        
        # Run all performance tests
        test_results = {
            "system_info": system_info,
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            test_results["api_response_times"] = self.test_api_response_times()
            test_results["search_performance"] = self.test_search_performance()
            test_results["pagination_performance"] = self.test_pagination_performance()
            test_results["concurrent_access"] = self.test_concurrent_access()
            
            # Validate against requirements
            test_results["validation"] = self.validate_performance_requirements(test_results)
            
        except Exception as e:
            test_results["error"] = f"Test suite failed: {str(e)}"
        
        return test_results

def main():
    """Main execution function."""
    validator = PerformanceValidator()
    results = validator.run_performance_validation()
    
    # Save results to file
    with open("performance_validation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE VALIDATION RESULTS SUMMARY")
    print("=" * 60)
    
    if "system_info" in results:
        info = results["system_info"]
        print(f"System Information:")
        print(f"  Total Parts: {info.get('total_parts', 'Unknown')}")
        print(f"  Total Organizations: {info.get('total_organizations', 'Unknown')}")
        print(f"  Total Warehouses: {info.get('total_warehouses', 'Unknown')}")
    
    if "validation" in results:
        validation = results["validation"]
        print(f"\nOverall Performance Status: {validation['overall_status']}")
        
        if "requirements_validation" in validation:
            print("\nRequirements Validation:")
            for req_id, req_data in validation["requirements_validation"].items():
                status_icon = {"PASS": "✅", "FAIL": "❌", "WARNING": "⚠️"}[req_data["status"]]
                print(f"  {status_icon} {req_id}: {req_data['requirement']}")
    
    if "error" in results:
        print(f"❌ Test failed: {results['error']}")
    
    print(f"\n📄 Detailed results saved to: performance_validation_results.json")
    print("=" * 60)

if __name__ == "__main__":
    main()