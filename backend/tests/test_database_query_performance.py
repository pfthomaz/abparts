#!/usr/bin/env python3
"""
Database query performance validation tests for parts operations.
Tests database query execution times, index usage, and query optimization with large datasets.
"""

import pytest
import time
import statistics
from typing import Dict, List, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
from decimal import Decimal

from .conftest import db_session
from .test_config_large_datasets import LargeDatasetTestConfig, get_test_scenario, should_run_large_dataset_tests
from .test_data_generators import generate_large_parts_dataset
from app.models import Part, PartType, Inventory, Warehouse
from app.crud.parts import (
    get_filtered_parts_with_count, search_parts_multilingual_with_count,
    get_parts_with_inventory_with_count, monitor_query_performance
)


class DatabaseQueryPerformanceTester:
    """Performance tester for database queries."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.query_results = {}
    
    def measure_query_performance(self, query_func, *args, description: str = "", **kwargs) -> Dict[str, Any]:
        """Measure performance of a database query function."""
        start_time = time.time()
        
        try:
            result = query_func(*args, **kwargs)
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000
            
            # Get result count
            result_count = 0
            if isinstance(result, dict) and "items" in result:
                result_count = len(result["items"])
            elif isinstance(result, list):
                result_count = len(result)
            elif hasattr(result, "__len__"):
                result_count = len(result)
            
            return {
                "success": True,
                "execution_time_ms": execution_time_ms,
                "result_count": result_count,
                "description": description
            }
            
        except Exception as e:
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000
            
            return {
                "success": False,
                "execution_time_ms": execution_time_ms,
                "result_count": 0,
                "description": description,
                "error": str(e)
            }
    
    def measure_raw_sql_performance(self, sql_query: str, params: Dict = None, 
                                  description: str = "") -> Dict[str, Any]:
        """Measure performance of a raw SQL query."""
        start_time = time.time()
        
        try:
            if params:
                result = self.db_session.execute(text(sql_query), params)
            else:
                result = self.db_session.execute(text(sql_query))
            
            rows = result.fetchall()
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000
            
            return {
                "success": True,
                "execution_time_ms": execution_time_ms,
                "result_count": len(rows),
                "description": description
            }
            
        except Exception as e:
            end_time = time.time()
            execution_time_ms = (end_time - start_time) * 1000
            
            return {
                "success": False,
                "execution_time_ms": execution_time_ms,
                "result_count": 0,
                "description": description,
                "error": str(e)
            }
    
    def test_basic_parts_queries(self, parts_count: int) -> Dict[str, Any]:
        """Test basic parts query performance."""
        print(f"\n🔍 Testing basic parts queries with {parts_count} parts...")
        
        results = {}
        
        # Test 1: Simple SELECT with LIMIT
        result = self.measure_raw_sql_performance(
            "SELECT * FROM parts LIMIT 100",
            description="Simple SELECT with LIMIT"
        )
        results["simple_select"] = result
        print(f"  Simple SELECT: {result['execution_time_ms']:.2f}ms")
        
        # Test 2: COUNT query
        result = self.measure_raw_sql_performance(
            "SELECT COUNT(*) FROM parts",
            description="COUNT all parts"
        )
        results["count_all"] = result
        print(f"  COUNT all parts: {result['execution_time_ms']:.2f}ms")
        
        # Test 3: Filtered COUNT
        result = self.measure_raw_sql_performance(
            "SELECT COUNT(*) FROM parts WHERE part_type = 'consumable'",
            description="COUNT filtered by type"
        )
        results["count_filtered"] = result
        print(f"  COUNT filtered: {result['execution_time_ms']:.2f}ms")
        
        # Test 4: Complex WHERE clause
        result = self.measure_raw_sql_performance(
            """
            SELECT * FROM parts 
            WHERE part_type = 'consumable' 
            AND is_proprietary = false 
            ORDER BY created_at DESC 
            LIMIT 100
            """,
            description="Complex WHERE with ORDER BY"
        )
        results["complex_where"] = result
        print(f"  Complex WHERE: {result['execution_time_ms']:.2f}ms")
        
        return results
    
    def test_search_queries(self, parts_count: int) -> Dict[str, Any]:
        """Test search query performance."""
        print(f"\n🔎 Testing search queries with {parts_count} parts...")
        
        results = {}
        
        # Test 1: ILIKE search on name
        result = self.measure_raw_sql_performance(
            "SELECT * FROM parts WHERE name ILIKE '%Filter%' LIMIT 100",
            description="ILIKE search on name"
        )
        results["ilike_name"] = result
        print(f"  ILIKE name search: {result['execution_time_ms']:.2f}ms")
        
        # Test 2: ILIKE search on part_number
        result = self.measure_raw_sql_performance(
            "SELECT * FROM parts WHERE part_number ILIKE '%P-000001%' LIMIT 100",
            description="ILIKE search on part_number"
        )
        results["ilike_part_number"] = result
        print(f"  ILIKE part_number search: {result['execution_time_ms']:.2f}ms")
        
        # Test 3: Multi-field OR search
        result = self.measure_raw_sql_performance(
            """
            SELECT * FROM parts 
            WHERE name ILIKE '%Filter%' 
            OR part_number ILIKE '%Filter%' 
            OR description ILIKE '%Filter%'
            LIMIT 100
            """,
            description="Multi-field OR search"
        )
        results["multi_field_search"] = result
        print(f"  Multi-field search: {result['execution_time_ms']:.2f}ms")
        
        # Test 4: Full-text search (if supported)
        try:
            result = self.measure_raw_sql_performance(
                """
                SELECT * FROM parts 
                WHERE to_tsvector('english', name) @@ to_tsquery('english', 'Filter')
                LIMIT 100
                """,
                description="Full-text search"
            )
            results["fulltext_search"] = result
            print(f"  Full-text search: {result['execution_time_ms']:.2f}ms")
        except Exception as e:
            print(f"  Full-text search not available: {str(e)[:50]}...")
        
        return results
    
    def test_index_usage_queries(self, parts_count: int) -> Dict[str, Any]:
        """Test queries that should use database indexes."""
        print(f"\n📊 Testing index usage with {parts_count} parts...")
        
        results = {}
        
        # Test 1: Query using part_number index (unique)
        result = self.measure_raw_sql_performance(
            "SELECT * FROM parts WHERE part_number = 'P-000001'",
            description="Query by part_number (indexed)"
        )
        results["part_number_lookup"] = result
        print(f"  Part number lookup: {result['execution_time_ms']:.2f}ms")
        
        # Test 2: Query using composite index (part_type, is_proprietary)
        result = self.measure_raw_sql_performance(
            "SELECT * FROM parts WHERE part_type = 'consumable' AND is_proprietary = false LIMIT 100",
            description="Composite index query"
        )
        results["composite_index"] = result
        print(f"  Composite index query: {result['execution_time_ms']:.2f}ms")
        
        # Test 3: Query using manufacturer index
        result = self.measure_raw_sql_performance(
            "SELECT * FROM parts WHERE manufacturer = 'BossAqua' LIMIT 100",
            description="Manufacturer index query"
        )
        results["manufacturer_index"] = result
        print(f"  Manufacturer index query: {result['execution_time_ms']:.2f}ms")
        
        # Test 4: Range query on created_at
        result = self.measure_raw_sql_performance(
            """
            SELECT * FROM parts 
            WHERE created_at >= NOW() - INTERVAL '30 days'
            ORDER BY created_at DESC 
            LIMIT 100
            """,
            description="Date range query"
        )
        results["date_range"] = result
        print(f"  Date range query: {result['execution_time_ms']:.2f}ms")
        
        return results
    
    def test_join_queries(self, parts_count: int) -> Dict[str, Any]:
        """Test JOIN query performance."""
        print(f"\n🔗 Testing JOIN queries with {parts_count} parts...")
        
        results = {}
        
        # Test 1: Parts with inventory JOIN
        result = self.measure_raw_sql_performance(
            """
            SELECT p.*, i.current_stock, w.name as warehouse_name
            FROM parts p
            LEFT JOIN inventory i ON p.id = i.part_id
            LEFT JOIN warehouses w ON i.warehouse_id = w.id
            LIMIT 100
            """,
            description="Parts with inventory JOIN"
        )
        results["parts_inventory_join"] = result
        print(f"  Parts-Inventory JOIN: {result['execution_time_ms']:.2f}ms")
        
        # Test 2: Aggregated inventory by part
        result = self.measure_raw_sql_performance(
            """
            SELECT p.id, p.name, SUM(i.current_stock) as total_stock
            FROM parts p
            LEFT JOIN inventory i ON p.id = i.part_id
            GROUP BY p.id, p.name
            LIMIT 100
            """,
            description="Aggregated inventory by part"
        )
        results["aggregated_inventory"] = result
        print(f"  Aggregated inventory: {result['execution_time_ms']:.2f}ms")
        
        # Test 3: Complex JOIN with filters
        result = self.measure_raw_sql_performance(
            """
            SELECT p.*, SUM(i.current_stock) as total_stock
            FROM parts p
            LEFT JOIN inventory i ON p.id = i.part_id
            LEFT JOIN warehouses w ON i.warehouse_id = w.id
            WHERE p.part_type = 'consumable'
            AND i.current_stock > 0
            GROUP BY p.id
            HAVING SUM(i.current_stock) > 10
            LIMIT 100
            """,
            description="Complex JOIN with filters"
        )
        results["complex_join"] = result
        print(f"  Complex JOIN: {result['execution_time_ms']:.2f}ms")
        
        return results
    
    def test_crud_operations_performance(self, parts_count: int) -> Dict[str, Any]:
        """Test CRUD operations performance using app functions."""
        print(f"\n⚙️ Testing CRUD operations with {parts_count} parts...")
        
        results = {}
        
        # Test 1: get_filtered_parts_with_count
        result = self.measure_query_performance(
            get_filtered_parts_with_count,
            self.db_session,
            part_type="consumable",
            is_proprietary=False,
            skip=0,
            limit=100,
            include_count=False,
            description="Filtered parts query"
        )
        results["filtered_parts"] = result
        print(f"  Filtered parts: {result['execution_time_ms']:.2f}ms")
        
        # Test 2: search_parts_multilingual_with_count
        result = self.measure_query_performance(
            search_parts_multilingual_with_count,
            self.db_session,
            search_term="Filter",
            part_type=None,
            is_proprietary=None,
            skip=0,
            limit=100,
            include_count=False,
            description="Multilingual search"
        )
        results["multilingual_search"] = result
        print(f"  Multilingual search: {result['execution_time_ms']:.2f}ms")
        
        # Test 3: get_parts_with_inventory_with_count
        result = self.measure_query_performance(
            get_parts_with_inventory_with_count,
            self.db_session,
            organization_id=None,
            part_type=None,
            is_proprietary=None,
            skip=0,
            limit=100,
            include_count=False,
            description="Parts with inventory"
        )
        results["parts_with_inventory"] = result
        print(f"  Parts with inventory: {result['execution_time_ms']:.2f}ms")
        
        return results
    
    def test_explain_analyze_queries(self, parts_count: int) -> Dict[str, Any]:
        """Test query execution plans using EXPLAIN ANALYZE."""
        print(f"\n📈 Testing query execution plans with {parts_count} parts...")
        
        results = {}
        
        # Test queries that should use indexes
        explain_queries = [
            {
                "query": "SELECT * FROM parts WHERE part_number = 'P-000001'",
                "description": "Part number lookup (should use unique index)"
            },
            {
                "query": "SELECT * FROM parts WHERE part_type = 'consumable' AND is_proprietary = false LIMIT 100",
                "description": "Composite index query (should use composite index)"
            },
            {
                "query": "SELECT * FROM parts WHERE name ILIKE '%Filter%' LIMIT 100",
                "description": "Name search (may use full-text index)"
            }
        ]
        
        for query_config in explain_queries:
            query = f"EXPLAIN ANALYZE {query_config['query']}"
            
            result = self.measure_raw_sql_performance(
                query,
                description=f"EXPLAIN: {query_config['description']}"
            )
            
            results[f"explain_{len(results)}"] = result
            print(f"  {query_config['description']}: {result['execution_time_ms']:.2f}ms")
        
        return results
    
    def analyze_query_performance(self, results: Dict[str, Any], 
                                scenario_name: str, parts_count: int):
        """Analyze and report query performance results."""
        print(f"\n📊 Query Performance Analysis for {scenario_name} ({parts_count} parts)")
        print("=" * 70)
        
        # Group results by operation type
        operation_groups = {
            "Basic Queries": [k for k in results.keys() if any(x in k for x in ["simple", "count", "complex"])],
            "Search Queries": [k for k in results.keys() if any(x in k for x in ["search", "ilike", "fulltext"])],
            "Index Queries": [k for k in results.keys() if any(x in k for x in ["index", "lookup", "composite"])],
            "JOIN Queries": [k for k in results.keys() if "join" in k],
            "CRUD Operations": [k for k in results.keys() if any(x in k for x in ["filtered", "multilingual", "inventory"])],
            "Query Plans": [k for k in results.keys() if "explain" in k]
        }
        
        for group_name, operation_keys in operation_groups.items():
            if not operation_keys:
                continue
                
            print(f"\n{group_name}:")
            
            group_times = []
            for key in operation_keys:
                if key in results and results[key]["success"]:
                    execution_time = results[key]["execution_time_ms"]
                    result_count = results[key]["result_count"]
                    group_times.append(execution_time)
                    print(f"  {key}: {execution_time:.2f}ms ({result_count} results)")
            
            if group_times:
                print(f"  Group Average: {statistics.mean(group_times):.2f}ms")
                print(f"  Group Median: {statistics.median(group_times):.2f}ms")
                print(f"  Group Max: {max(group_times):.2f}ms")
        
        # Check against performance thresholds
        config = LargeDatasetTestConfig()
        threshold_key = f"db_query_{parts_count//1000}k" if parts_count >= 1000 else "db_query_1k"
        threshold = config.get_performance_threshold(threshold_key)
        
        print(f"\n⚡ Database Performance Threshold Analysis:")
        print(f"  Target threshold: {threshold:.2f}ms")
        
        slow_queries = []
        for key, result in results.items():
            if result["success"] and result["execution_time_ms"] > threshold:
                slow_queries.append((key, result["execution_time_ms"]))
        
        if slow_queries:
            print(f"  ⚠️ Queries exceeding threshold:")
            for query_name, execution_time in slow_queries:
                print(f"    {query_name}: {execution_time:.2f}ms")
        else:
            print(f"  ✅ All queries within threshold!")


@pytest.mark.skipif(not should_run_large_dataset_tests(), reason="Large dataset tests disabled")
@pytest.mark.large_dataset
@pytest.mark.performance
class TestDatabaseQueryPerformance:
    """Test class for database query performance with large datasets."""
    
    def test_database_performance_1k(self, db_session: Session):
        """Test database query performance with 1,000 parts."""
        scenario = get_test_scenario("basic_performance")
        parts_count = scenario["parts_count"]
        
        print(f"\n🚀 Testing Database Query Performance - {parts_count} parts")
        
        # Generate test data
        print("Generating test dataset...")
        dataset = generate_large_parts_dataset(
            db_session, 
            parts_count=parts_count,
            include_inventory=scenario["include_inventory"],
            include_transactions=scenario["include_transactions"]
        )
        
        # Initialize performance tester
        tester = DatabaseQueryPerformanceTester(db_session)
        
        # Run performance tests
        all_results = {}
        
        # Test 1: Basic queries
        basic_results = tester.test_basic_parts_queries(parts_count)
        all_results.update(basic_results)
        
        # Test 2: Search queries
        search_results = tester.test_search_queries(parts_count)
        all_results.update(search_results)
        
        # Test 3: Index usage
        index_results = tester.test_index_usage_queries(parts_count)
        all_results.update(index_results)
        
        # Test 4: JOIN queries
        join_results = tester.test_join_queries(parts_count)
        all_results.update(join_results)
        
        # Test 5: CRUD operations
        crud_results = tester.test_crud_operations_performance(parts_count)
        all_results.update(crud_results)
        
        # Test 6: Query plans
        explain_results = tester.test_explain_analyze_queries(parts_count)
        all_results.update(explain_results)
        
        # Analyze results
        tester.analyze_query_performance(all_results, "1K Parts", parts_count)
        
        # Assert performance requirements
        config = LargeDatasetTestConfig()
        threshold = config.get_performance_threshold("db_query_1k")
        
        # Check that basic queries are within threshold
        assert all_results["simple_select"]["execution_time_ms"] < threshold, \
            f"Simple SELECT too slow: {all_results['simple_select']['execution_time_ms']:.2f}ms > {threshold:.2f}ms"
        
        # Check that indexed queries are fast
        if "part_number_lookup" in all_results:
            lookup_time = all_results["part_number_lookup"]["execution_time_ms"]
            assert lookup_time < threshold * 0.5, \
                f"Indexed lookup too slow: {lookup_time:.2f}ms > {threshold * 0.5:.2f}ms"
    
    @pytest.mark.slow
    def test_database_performance_5k(self, db_session: Session):
        """Test database query performance with 5,000 parts."""
        scenario = get_test_scenario("moderate_scale")
        parts_count = scenario["parts_count"]
        
        print(f"\n🚀 Testing Database Query Performance - {parts_count} parts")
        
        # Generate test data
        print("Generating test dataset...")
        dataset = generate_large_parts_dataset(
            db_session, 
            parts_count=parts_count,
            include_inventory=scenario["include_inventory"],
            include_transactions=scenario["include_transactions"]
        )
        
        # Initialize performance tester
        tester = DatabaseQueryPerformanceTester(db_session)
        
        # Run performance tests (limited scope for larger dataset)
        all_results = {}
        
        # Test 1: Basic queries
        basic_results = tester.test_basic_parts_queries(parts_count)
        all_results.update(basic_results)
        
        # Test 2: Index usage
        index_results = tester.test_index_usage_queries(parts_count)
        all_results.update(index_results)
        
        # Test 3: CRUD operations
        crud_results = tester.test_crud_operations_performance(parts_count)
        all_results.update(crud_results)
        
        # Analyze results
        tester.analyze_query_performance(all_results, "5K Parts", parts_count)
        
        # Assert performance requirements
        config = LargeDatasetTestConfig()
        threshold = config.get_performance_threshold("db_query_5k")
        
        # Check that basic queries are within threshold
        assert all_results["simple_select"]["execution_time_ms"] < threshold, \
            f"Simple SELECT too slow: {all_results['simple_select']['execution_time_ms']:.2f}ms > {threshold:.2f}ms"
    
    @pytest.mark.slow
    def test_database_performance_10k(self, db_session: Session):
        """Test database query performance with 10,000+ parts."""
        scenario = get_test_scenario("high_scale")
        parts_count = scenario["parts_count"]
        
        print(f"\n🚀 Testing Database Query Performance - {parts_count} parts")
        
        # Generate test data
        print("Generating test dataset...")
        dataset = generate_large_parts_dataset(
            db_session, 
            parts_count=parts_count,
            include_inventory=scenario["include_inventory"],
            include_transactions=scenario["include_transactions"]
        )
        
        # Initialize performance tester
        tester = DatabaseQueryPerformanceTester(db_session)
        
        # Run performance tests (minimal scope for large dataset)
        all_results = {}
        
        # Test 1: Basic queries only
        basic_results = tester.test_basic_parts_queries(parts_count)
        all_results.update(basic_results)
        
        # Test 2: Index usage
        index_results = tester.test_index_usage_queries(parts_count)
        all_results.update(index_results)
        
        # Analyze results
        tester.analyze_query_performance(all_results, "10K Parts", parts_count)
        
        # Assert performance requirements
        config = LargeDatasetTestConfig()
        threshold = config.get_performance_threshold("db_query_10k")
        
        # Check that basic queries are within threshold
        assert all_results["simple_select"]["execution_time_ms"] < threshold, \
            f"Simple SELECT too slow: {all_results['simple_select']['execution_time_ms']:.2f}ms > {threshold:.2f}ms"


if __name__ == "__main__":
    # Run performance tests directly
    pytest.main([__file__, "-v", "-s", "--tb=short"])