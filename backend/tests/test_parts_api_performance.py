#!/usr/bin/env python3
"""
Comprehensive performance tests for parts API with large datasets.
Tests API response times, pagination performance, and search functionality with 1K, 5K, and 10K+ parts.
"""

import pytest
import time
import statistics
import asyncio
from typing import Dict, List, Any
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from .conftest import client, db_session, auth_headers
from .test_config_large_datasets import LargeDatasetTestConfig, get_test_scenario, should_run_large_dataset_tests
from .test_data_generators import generate_large_parts_dataset
from app.models import Part, PartType


class PartsAPIPerformanceTester:
    """Performance tester for parts API endpoints."""
    
    def __init__(self, client: TestClient, auth_headers: Dict[str, str]):
        self.client = client
        self.auth_headers = auth_headers
        self.performance_results = {}
    
    def measure_endpoint_performance(self, endpoint: str, method: str = "GET", 
                                   params: Dict = None, json_data: Dict = None,
                                   description: str = "") -> Dict[str, Any]:
        """Measure performance of a single API endpoint call."""
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = self.client.get(endpoint, params=params, headers=self.auth_headers)
            elif method.upper() == "POST":
                response = self.client.post(endpoint, json=json_data, headers=self.auth_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_time_ms": response_time_ms,
                "response_size": len(response.content) if response.content else 0,
                "description": description,
                "endpoint": endpoint
            }
            
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            return {
                "success": False,
                "status_code": 500,
                "response_time_ms": response_time_ms,
                "response_size": 0,
                "description": description,
                "endpoint": endpoint,
                "error": str(e)
            }
    
    def test_parts_list_performance(self, parts_count: int) -> Dict[str, Any]:
        """Test parts list endpoint performance with different pagination sizes."""
        print(f"\n📋 Testing parts list performance with {parts_count} parts...")
        
        results = {}
        
        # Test different pagination sizes
        pagination_tests = [
            {"limit": 50, "description": "Small page (50 items)"},
            {"limit": 100, "description": "Default page (100 items)"},
            {"limit": 500, "description": "Large page (500 items)"},
            {"limit": 1000, "description": "Max page (1000 items)"}
        ]
        
        for test_config in pagination_tests:
            limit = test_config["limit"]
            description = test_config["description"]
            
            # Test first page
            result = self.measure_endpoint_performance(
                "/parts/",
                params={"skip": 0, "limit": limit},
                description=f"{description} - First page"
            )
            
            results[f"list_limit_{limit}_first"] = result
            print(f"  {description} - First page: {result['response_time_ms']:.2f}ms")
            
            # Test middle page (if enough parts)
            if parts_count > limit * 2:
                middle_skip = parts_count // 2
                result = self.measure_endpoint_performance(
                    "/parts/",
                    params={"skip": middle_skip, "limit": limit},
                    description=f"{description} - Middle page"
                )
                
                results[f"list_limit_{limit}_middle"] = result
                print(f"  {description} - Middle page: {result['response_time_ms']:.2f}ms")
        
        # Test with count parameter (expensive operation)
        result = self.measure_endpoint_performance(
            "/parts/",
            params={"skip": 0, "limit": 100, "include_count": True},
            description="With total count"
        )
        
        results["list_with_count"] = result
        print(f"  With total count: {result['response_time_ms']:.2f}ms")
        
        return results
    
    def test_parts_search_performance(self, parts_count: int) -> Dict[str, Any]:
        """Test parts search endpoint performance."""
        print(f"\n🔍 Testing parts search performance with {parts_count} parts...")
        
        results = {}
        
        # Test different search scenarios
        search_tests = [
            {"query": "Filter", "description": "Common term search"},
            {"query": "P-000001", "description": "Specific part number"},
            {"query": "BossAqua", "description": "Manufacturer search"},
            {"query": "xyz123nonexistent", "description": "No results search"}
        ]
        
        for test_config in search_tests:
            query = test_config["query"]
            description = test_config["description"]
            
            # Test basic search
            result = self.measure_endpoint_performance(
                "/parts/search",
                params={"q": query, "limit": 100},
                description=f"Search: {description}"
            )
            
            results[f"search_{query.replace(' ', '_').lower()}"] = result
            print(f"  {description}: {result['response_time_ms']:.2f}ms")
            
            # Test search with filters
            result = self.measure_endpoint_performance(
                "/parts/search",
                params={
                    "q": query,
                    "part_type": "consumable",
                    "is_proprietary": False,
                    "limit": 100
                },
                description=f"Filtered search: {description}"
            )
            
            results[f"search_filtered_{query.replace(' ', '_').lower()}"] = result
            print(f"  {description} (filtered): {result['response_time_ms']:.2f}ms")
        
        return results
    
    def test_parts_filtering_performance(self, parts_count: int) -> Dict[str, Any]:
        """Test parts filtering performance."""
        print(f"\n🎯 Testing parts filtering performance with {parts_count} parts...")
        
        results = {}
        
        # Test different filter combinations
        filter_tests = [
            {"part_type": "consumable", "description": "Filter by consumable type"},
            {"part_type": "bulk_material", "description": "Filter by bulk material type"},
            {"is_proprietary": True, "description": "Filter by proprietary parts"},
            {"is_proprietary": False, "description": "Filter by non-proprietary parts"},
            {
                "part_type": "consumable", 
                "is_proprietary": True, 
                "description": "Combined filters"
            }
        ]
        
        for test_config in filter_tests:
            params = {k: v for k, v in test_config.items() if k != "description"}
            params["limit"] = 100
            
            result = self.measure_endpoint_performance(
                "/parts/",
                params=params,
                description=test_config["description"]
            )
            
            filter_key = "_".join([f"{k}_{v}" for k, v in params.items() if k != "limit"])
            results[f"filter_{filter_key}"] = result
            print(f"  {test_config['description']}: {result['response_time_ms']:.2f}ms")
        
        return results
    
    def test_parts_with_inventory_performance(self, parts_count: int) -> Dict[str, Any]:
        """Test parts with inventory endpoint performance."""
        print(f"\n📦 Testing parts with inventory performance with {parts_count} parts...")
        
        results = {}
        
        # Test parts with inventory endpoint
        result = self.measure_endpoint_performance(
            "/parts/with-inventory",
            params={"limit": 100},
            description="Parts with inventory"
        )
        
        results["with_inventory"] = result
        print(f"  Parts with inventory: {result['response_time_ms']:.2f}ms")
        
        # Test search with inventory
        result = self.measure_endpoint_performance(
            "/parts/search-with-inventory",
            params={"q": "Filter", "limit": 100},
            description="Search with inventory"
        )
        
        results["search_with_inventory"] = result
        print(f"  Search with inventory: {result['response_time_ms']:.2f}ms")
        
        return results
    
    def analyze_performance_results(self, results: Dict[str, Any], 
                                  scenario_name: str, parts_count: int):
        """Analyze and report performance results."""
        print(f"\n📊 Performance Analysis for {scenario_name} ({parts_count} parts)")
        print("=" * 60)
        
        # Group results by operation type
        operation_groups = {
            "List Operations": [k for k in results.keys() if k.startswith("list_")],
            "Search Operations": [k for k in results.keys() if k.startswith("search_")],
            "Filter Operations": [k for k in results.keys() if k.startswith("filter_")],
            "Inventory Operations": [k for k in results.keys() if "inventory" in k]
        }
        
        for group_name, operation_keys in operation_groups.items():
            if not operation_keys:
                continue
                
            print(f"\n{group_name}:")
            
            group_times = []
            for key in operation_keys:
                if key in results and results[key]["success"]:
                    response_time = results[key]["response_time_ms"]
                    group_times.append(response_time)
                    print(f"  {key}: {response_time:.2f}ms")
            
            if group_times:
                print(f"  Average: {statistics.mean(group_times):.2f}ms")
                print(f"  Median: {statistics.median(group_times):.2f}ms")
                print(f"  Max: {max(group_times):.2f}ms")
                print(f"  Min: {min(group_times):.2f}ms")
        
        # Check against performance thresholds
        config = LargeDatasetTestConfig()
        threshold_key = f"api_response_{parts_count//1000}k" if parts_count >= 1000 else "api_response_1k"
        threshold = config.get_performance_threshold(threshold_key)
        
        print(f"\n⚡ Performance Threshold Analysis:")
        print(f"  Target threshold: {threshold:.2f}ms")
        
        slow_operations = []
        for key, result in results.items():
            if result["success"] and result["response_time_ms"] > threshold:
                slow_operations.append((key, result["response_time_ms"]))
        
        if slow_operations:
            print(f"  ⚠️ Operations exceeding threshold:")
            for op_name, response_time in slow_operations:
                print(f"    {op_name}: {response_time:.2f}ms")
        else:
            print(f"  ✅ All operations within threshold!")


@pytest.mark.skipif(not should_run_large_dataset_tests(), reason="Large dataset tests disabled")
@pytest.mark.large_dataset
@pytest.mark.performance
class TestPartsAPIPerformance:
    """Test class for parts API performance with large datasets."""
    
    def test_parts_api_performance_1k(self, client: TestClient, db_session: Session, auth_headers: Dict[str, str]):
        """Test parts API performance with 1,000 parts."""
        scenario = get_test_scenario("basic_performance")
        parts_count = scenario["parts_count"]
        
        print(f"\n🚀 Testing Parts API Performance - {parts_count} parts")
        
        # Generate test data
        print("Generating test dataset...")
        dataset = generate_large_parts_dataset(
            db_session, 
            parts_count=parts_count,
            include_inventory=scenario["include_inventory"],
            include_transactions=scenario["include_transactions"]
        )
        
        # Initialize performance tester
        tester = PartsAPIPerformanceTester(client, auth_headers["super_admin"])
        
        # Run performance tests
        all_results = {}
        
        # Test 1: List operations
        list_results = tester.test_parts_list_performance(parts_count)
        all_results.update(list_results)
        
        # Test 2: Search operations
        search_results = tester.test_parts_search_performance(parts_count)
        all_results.update(search_results)
        
        # Test 3: Filter operations
        filter_results = tester.test_parts_filtering_performance(parts_count)
        all_results.update(filter_results)
        
        # Test 4: Inventory operations
        inventory_results = tester.test_parts_with_inventory_performance(parts_count)
        all_results.update(inventory_results)
        
        # Analyze results
        tester.analyze_performance_results(all_results, "1K Parts", parts_count)
        
        # Assert performance requirements
        config = LargeDatasetTestConfig()
        threshold = config.get_performance_threshold("api_response_1k")
        
        # Check that basic list operation is within threshold
        basic_list_time = all_results["list_limit_100_first"]["response_time_ms"]
        assert basic_list_time < threshold, f"Basic list operation too slow: {basic_list_time:.2f}ms > {threshold:.2f}ms"
        
        # Check that search is reasonably fast
        search_time = all_results["search_filter"]["response_time_ms"]
        assert search_time < threshold, f"Search operation too slow: {search_time:.2f}ms > {threshold:.2f}ms"
    
    @pytest.mark.slow
    def test_parts_api_performance_5k(self, client: TestClient, db_session: Session, auth_headers: Dict[str, str]):
        """Test parts API performance with 5,000 parts."""
        scenario = get_test_scenario("moderate_scale")
        parts_count = scenario["parts_count"]
        
        print(f"\n🚀 Testing Parts API Performance - {parts_count} parts")
        
        # Generate test data
        print("Generating test dataset...")
        dataset = generate_large_parts_dataset(
            db_session, 
            parts_count=parts_count,
            include_inventory=scenario["include_inventory"],
            include_transactions=scenario["include_transactions"]
        )
        
        # Initialize performance tester
        tester = PartsAPIPerformanceTester(client, auth_headers["super_admin"])
        
        # Run performance tests
        all_results = {}
        
        # Test 1: List operations
        list_results = tester.test_parts_list_performance(parts_count)
        all_results.update(list_results)
        
        # Test 2: Search operations
        search_results = tester.test_parts_search_performance(parts_count)
        all_results.update(search_results)
        
        # Test 3: Filter operations
        filter_results = tester.test_parts_filtering_performance(parts_count)
        all_results.update(filter_results)
        
        # Analyze results
        tester.analyze_performance_results(all_results, "5K Parts", parts_count)
        
        # Assert performance requirements
        config = LargeDatasetTestConfig()
        threshold = config.get_performance_threshold("api_response_5k")
        
        # Check that basic operations are within threshold
        basic_list_time = all_results["list_limit_100_first"]["response_time_ms"]
        assert basic_list_time < threshold, f"Basic list operation too slow: {basic_list_time:.2f}ms > {threshold:.2f}ms"
    
    @pytest.mark.slow
    def test_parts_api_performance_10k(self, client: TestClient, db_session: Session, auth_headers: Dict[str, str]):
        """Test parts API performance with 10,000+ parts."""
        scenario = get_test_scenario("high_scale")
        parts_count = scenario["parts_count"]
        
        print(f"\n🚀 Testing Parts API Performance - {parts_count} parts")
        
        # Generate test data
        print("Generating test dataset...")
        dataset = generate_large_parts_dataset(
            db_session, 
            parts_count=parts_count,
            include_inventory=scenario["include_inventory"],
            include_transactions=scenario["include_transactions"]
        )
        
        # Initialize performance tester
        tester = PartsAPIPerformanceTester(client, auth_headers["super_admin"])
        
        # Run performance tests (limited scope for large dataset)
        all_results = {}
        
        # Test 1: Basic list operations only
        list_results = tester.test_parts_list_performance(parts_count)
        all_results.update(list_results)
        
        # Test 2: Basic search operations
        search_results = tester.test_parts_search_performance(parts_count)
        all_results.update(search_results)
        
        # Analyze results
        tester.analyze_performance_results(all_results, "10K Parts", parts_count)
        
        # Assert performance requirements
        config = LargeDatasetTestConfig()
        threshold = config.get_performance_threshold("api_response_10k")
        
        # Check that basic operations are within threshold
        basic_list_time = all_results["list_limit_100_first"]["response_time_ms"]
        assert basic_list_time < threshold, f"Basic list operation too slow: {basic_list_time:.2f}ms > {threshold:.2f}ms"


if __name__ == "__main__":
    # Run performance tests directly
    pytest.main([__file__, "-v", "-s", "--tb=short"])