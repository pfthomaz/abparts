#!/usr/bin/env python3
"""
Simple load test for warehouse analytics endpoints.
Tests the performance improvements with caching and database optimizations.
"""

import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "superadmin"
PASSWORD = "superadmin"

def authenticate():
    """Authenticate and get access token."""
    response = requests.post(
        f"{BASE_URL}/token",
        data={"username": USERNAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Authentication failed: {response.status_code} - {response.text}")

def get_test_warehouse():
    """Get a warehouse ID for testing."""
    token = authenticate()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/warehouses/", headers=headers)
    if response.status_code == 200:
        warehouses = response.json()
        if warehouses:
            return warehouses[0]["id"], token
        else:
            raise Exception("No warehouses found")
    else:
        raise Exception(f"Failed to get warehouses: {response.status_code}")

def test_analytics_endpoint(warehouse_id, token, days=30):
    """Test the analytics endpoint and measure response time."""
    headers = {"Authorization": f"Bearer {token}"}
    
    start_time = time.time()
    try:
        response = requests.get(
            f"{BASE_URL}/inventory/warehouse/{warehouse_id}/analytics",
            headers=headers,
            params={"days": days},
            timeout=30
        )
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        return {
            "success": response.status_code == 200,
            "response_time_ms": response_time,
            "status_code": response.status_code,
            "data_size": len(response.text) if response.status_code == 200 else 0
        }
    except Exception as e:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        return {
            "success": False,
            "response_time_ms": response_time,
            "status_code": 0,
            "error": str(e)
        }

def run_concurrent_test(warehouse_id, token, num_requests=10):
    """Run concurrent requests to test performance."""
    print(f"Running {num_requests} concurrent requests...")
    
    results = []
    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        # Submit all requests
        futures = [
            executor.submit(test_analytics_endpoint, warehouse_id, token)
            for _ in range(num_requests)
        ]
        
        # Collect results
        for future in as_completed(futures):
            results.append(future.result())
    
    return results

def analyze_results(results, test_name):
    """Analyze and print test results."""
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"\n{test_name} Results:")
    print(f"  Successful: {len(successful)}/{len(results)}")
    print(f"  Failed: {len(failed)}")
    
    if successful:
        response_times = [r["response_time_ms"] for r in successful]
        data_sizes = [r["data_size"] for r in successful]
        
        print(f"  Response Times (ms):")
        print(f"    Average: {statistics.mean(response_times):.2f}")
        print(f"    Median: {statistics.median(response_times):.2f}")
        print(f"    Min: {min(response_times):.2f}")
        print(f"    Max: {max(response_times):.2f}")
        
        if len(response_times) > 1:
            print(f"    Std Dev: {statistics.stdev(response_times):.2f}")
        
        print(f"  Data Size (bytes): {statistics.mean(data_sizes):.0f}")
    
    if failed:
        print(f"  Failures:")
        for i, result in enumerate(failed[:3]):
            print(f"    {i+1}. Status: {result['status_code']}, Error: {result.get('error', 'Unknown')[:50]}")

def test_cache_effectiveness(warehouse_id, token):
    """Test cache effectiveness by comparing first and subsequent requests."""
    print("\nTesting cache effectiveness...")
    
    # Clear cache first (if possible)
    headers = {"Authorization": f"Bearer {token}"}
    try:
        requests.delete(f"{BASE_URL}/inventory/cache/warehouse/{warehouse_id}", headers=headers)
        print("  Cache cleared")
    except:
        print("  Could not clear cache (continuing anyway)")
    
    # First request (cache miss)
    print("  Making first request (cache miss)...")
    first_result = test_analytics_endpoint(warehouse_id, token)
    
    # Wait a moment
    time.sleep(0.1)
    
    # Second request (cache hit)
    print("  Making second request (cache hit)...")
    second_result = test_analytics_endpoint(warehouse_id, token)
    
    if first_result["success"] and second_result["success"]:
        improvement = ((first_result["response_time_ms"] - second_result["response_time_ms"]) / first_result["response_time_ms"]) * 100
        print(f"  Cache Performance:")
        print(f"    First request: {first_result['response_time_ms']:.2f}ms")
        print(f"    Second request: {second_result['response_time_ms']:.2f}ms")
        print(f"    Improvement: {improvement:.1f}%")
        
        if improvement > 0:
            print("  ✓ Cache is working effectively!")
        else:
            print("  ⚠ Cache may not be providing expected performance benefit")
    else:
        print("  ❌ Cache test failed")

def main():
    """Main function to run load tests."""
    print("🚀 Starting Simple Load Test for Warehouse Analytics")
    print("=" * 60)
    
    try:
        # Setup
        warehouse_id, token = get_test_warehouse()
        print(f"✓ Using warehouse: {warehouse_id}")
        
        # Test 1: Single request baseline
        print("\n1. Baseline single request test")
        single_result = test_analytics_endpoint(warehouse_id, token)
        analyze_results([single_result], "Single Request")
        
        # Test 2: Cache effectiveness
        test_cache_effectiveness(warehouse_id, token)
        
        # Test 3: Concurrent requests (light load)
        print("\n2. Light concurrent load (5 requests)")
        light_results = run_concurrent_test(warehouse_id, token, 5)
        analyze_results(light_results, "Light Load")
        
        # Test 4: Concurrent requests (medium load)
        print("\n3. Medium concurrent load (10 requests)")
        medium_results = run_concurrent_test(warehouse_id, token, 10)
        analyze_results(medium_results, "Medium Load")
        
        # Test 5: Different time ranges
        print("\n4. Testing different time ranges")
        time_ranges = [7, 30, 90]
        for days in time_ranges:
            result = test_analytics_endpoint(warehouse_id, token, days)
            if result["success"]:
                print(f"  {days} days: {result['response_time_ms']:.2f}ms")
            else:
                print(f"  {days} days: FAILED")
        
        # Test 6: Cache statistics
        print("\n5. Cache statistics")
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(f"{BASE_URL}/inventory/cache/stats", headers=headers)
            if response.status_code == 200:
                stats = response.json()
                print("  ✓ Cache statistics retrieved:")
                cache_stats = stats.get("cache_statistics", {})
                print(f"    Analytics entries: {cache_stats.get('analytics_cache_entries', 'N/A')}")
                print(f"    Trends entries: {cache_stats.get('trends_cache_entries', 'N/A')}")
                print(f"    Memory used: {cache_stats.get('redis_memory_used', 'N/A')}")
            else:
                print(f"  ❌ Failed to get cache stats: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error getting cache stats: {e}")
        
        print("\n✅ Load test completed successfully!")
        
    except Exception as e:
        print(f"❌ Load test failed: {e}")

if __name__ == "__main__":
    main()