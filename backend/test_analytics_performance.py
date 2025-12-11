#!/usr/bin/env python3
"""
Performance testing script for warehouse analytics API endpoints.
Tests performance with large datasets and concurrent requests.
"""

import asyncio
import aiohttp
import time
import json
import statistics
from typing import List, Dict, Any
from datetime import datetime, timedelta
import uuid

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_CREDENTIALS = {
    "username": "superadmin",
    "password": "superadmin"
}

class PerformanceTestRunner:
    """Performance test runner for analytics endpoints."""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_warehouse_id = None
        
    async def setup(self):
        """Setup test session and authentication."""
        self.session = aiohttp.ClientSession()
        
        # Authenticate and get token
        async with self.session.post(
            f"{BASE_URL}/auth/login",
            json=TEST_USER_CREDENTIALS
        ) as response:
            if response.status == 200:
                data = await response.json()
                self.auth_token = data.get("access_token")
                print(f"✓ Authenticated successfully")
            else:
                raise Exception(f"Authentication failed: {response.status}")
        
        # Get a test warehouse ID
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        async with self.session.get(f"{BASE_URL}/warehouses/", headers=headers) as response:
            if response.status == 200:
                warehouses = await response.json()
                if warehouses:
                    self.test_warehouse_id = warehouses[0]["id"]
                    print(f"✓ Using test warehouse: {self.test_warehouse_id}")
                else:
                    raise Exception("No warehouses found for testing")
            else:
                raise Exception(f"Failed to get warehouses: {response.status}")
    
    async def cleanup(self):
        """Cleanup test session."""
        if self.session:
            await self.session.close()
    
    async def test_single_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Test a single request and measure performance."""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        start_time = time.time()
        
        try:
            async with self.session.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                params=params or {}
            ) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "response_time_ms": response_time,
                        "status_code": response.status,
                        "data_size": len(json.dumps(data))
                    }
                else:
                    return {
                        "success": False,
                        "response_time_ms": response_time,
                        "status_code": response.status,
                        "error": await response.text()
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
    
    async def test_concurrent_requests(self, endpoint: str, concurrent_count: int = 10, params: Dict = None) -> List[Dict[str, Any]]:
        """Test concurrent requests to an endpoint."""
        print(f"  Testing {concurrent_count} concurrent requests...")
        
        tasks = []
        for _ in range(concurrent_count):
            task = asyncio.create_task(self.test_single_request(endpoint, params))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    def analyze_results(self, results: List[Dict[str, Any]], test_name: str):
        """Analyze and print test results."""
        successful_results = [r for r in results if r["success"]]
        failed_results = [r for r in results if not r["success"]]
        
        if successful_results:
            response_times = [r["response_time_ms"] for r in successful_results]
            data_sizes = [r["data_size"] for r in successful_results]
            
            print(f"\n📊 {test_name} Results:")
            print(f"  ✓ Successful requests: {len(successful_results)}/{len(results)}")
            print(f"  ✗ Failed requests: {len(failed_results)}")
            
            if response_times:
                print(f"  📈 Response Times (ms):")
                print(f"    - Average: {statistics.mean(response_times):.2f}")
                print(f"    - Median: {statistics.median(response_times):.2f}")
                print(f"    - Min: {min(response_times):.2f}")
                print(f"    - Max: {max(response_times):.2f}")
                print(f"    - 95th percentile: {statistics.quantiles(response_times, n=20)[18]:.2f}")
            
            if data_sizes:
                print(f"  📦 Response Sizes (bytes):")
                print(f"    - Average: {statistics.mean(data_sizes):.0f}")
                print(f"    - Max: {max(data_sizes)}")
        
        if failed_results:
            print(f"  ❌ Failed Requests:")
            for i, result in enumerate(failed_results[:3]):  # Show first 3 failures
                print(f"    {i+1}. Status: {result['status_code']}, Error: {result.get('error', 'Unknown')[:100]}")
    
    async def test_cache_performance(self):
        """Test cache performance by making repeated requests."""
        print("\n🔄 Testing Cache Performance...")
        
        endpoint = f"/inventory/warehouse/{self.test_warehouse_id}/analytics"
        params = {"days": 30}
        
        # First request (cache miss)
        print("  First request (cache miss)...")
        first_result = await self.test_single_request(endpoint, params)
        
        # Wait a moment
        await asyncio.sleep(0.1)
        
        # Second request (cache hit)
        print("  Second request (cache hit)...")
        second_result = await self.test_single_request(endpoint, params)
        
        if first_result["success"] and second_result["success"]:
            cache_improvement = ((first_result["response_time_ms"] - second_result["response_time_ms"]) / first_result["response_time_ms"]) * 100
            print(f"  📈 Cache Performance:")
            print(f"    - First request (miss): {first_result['response_time_ms']:.2f}ms")
            print(f"    - Second request (hit): {second_result['response_time_ms']:.2f}ms")
            print(f"    - Improvement: {cache_improvement:.1f}%")
        else:
            print("  ❌ Cache performance test failed")
    
    async def run_all_tests(self):
        """Run all performance tests."""
        print("🚀 Starting Analytics Performance Tests")
        print("=" * 50)
        
        await self.setup()
        
        try:
            # Test 1: Single analytics request
            print("\n1️⃣ Testing Single Analytics Request")
            single_result = await self.test_single_request(
                f"/inventory/warehouse/{self.test_warehouse_id}/analytics",
                {"days": 30}
            )
            self.analyze_results([single_result], "Single Analytics Request")
            
            # Test 2: Concurrent analytics requests
            print("\n2️⃣ Testing Concurrent Analytics Requests")
            concurrent_results = await self.test_concurrent_requests(
                f"/inventory/warehouse/{self.test_warehouse_id}/analytics",
                concurrent_count=10,
                params={"days": 30}
            )
            self.analyze_results(concurrent_results, "Concurrent Analytics Requests")
            
            # Test 3: Trends endpoint
            print("\n3️⃣ Testing Trends Endpoint")
            trends_results = await self.test_concurrent_requests(
                f"/inventory/warehouse/{self.test_warehouse_id}/analytics/trends",
                concurrent_count=5,
                params={"period": "daily", "days": 30}
            )
            self.analyze_results(trends_results, "Trends Endpoint")
            
            # Test 4: Cache performance
            await self.test_cache_performance()
            
            # Test 5: Different time ranges
            print("\n4️⃣ Testing Different Time Ranges")
            time_ranges = [7, 30, 90, 180]
            for days in time_ranges:
                print(f"  Testing {days} days...")
                result = await self.test_single_request(
                    f"/inventory/warehouse/{self.test_warehouse_id}/analytics",
                    {"days": days}
                )
                if result["success"]:
                    print(f"    {days} days: {result['response_time_ms']:.2f}ms")
                else:
                    print(f"    {days} days: FAILED")
            
            # Test 6: Cache statistics
            print("\n5️⃣ Testing Cache Statistics")
            cache_stats_result = await self.test_single_request("/inventory/cache/stats")
            if cache_stats_result["success"]:
                print("  ✓ Cache statistics endpoint working")
            else:
                print("  ❌ Cache statistics endpoint failed")
            
        finally:
            await self.cleanup()
        
        print("\n✅ Performance tests completed!")


async def main():
    """Main function to run performance tests."""
    runner = PerformanceTestRunner()
    await runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())