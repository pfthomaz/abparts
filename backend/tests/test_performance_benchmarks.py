# backend/tests/test_performance_benchmarks.py

import pytest
import time
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db
from app.auth import get_current_user
from app.performance_monitoring import performance_monitor, PerformanceBenchmark
from app import crud


class TestPartsCRUDPerformance:
    """Test performance benchmarks for parts CRUD operations"""
    
    def setup_method(self):
        """Set up test environment"""
        # Clear any existing metrics
        performance_monitor.metrics.clear()
        
        # Mock database session
        self.mock_db = Mock(spec=Session)
        
        # Mock part data
        self.mock_part = Mock()
        self.mock_part.id = "test-part-id"
        self.mock_part.part_number = "TEST-001"
        self.mock_part.name = "Test Part"
        self.mock_part.__dict__ = {
            "id": "test-part-id",
            "part_number": "TEST-001",
            "name": "Test Part"
        }
    
    def test_get_part_performance_benchmark(self):
        """Test get_part performance against benchmark"""
        # Mock database query
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_part
        
        # Execute the function
        start_time = time.time()
        result = crud.parts.get_part(self.mock_db, "test-part-id")
        execution_time = time.time() - start_time
        
        # Validate result
        assert result == self.mock_part
        
        # Check performance benchmark
        benchmark = PerformanceBenchmark.create_benchmark_thresholds()
        expected_threshold = benchmark["parts_crud"]["get_part"]  # 0.1 seconds
        
        validation = PerformanceBenchmark.validate_performance(
            "parts_crud.get_part", execution_time, benchmark
        )
        
        # The function should complete well within the benchmark
        assert validation["meets_benchmark"] is True
        assert execution_time < expected_threshold
    
    def test_get_parts_performance_benchmark(self):
        """Test get_parts performance against benchmark"""
        # Mock database query
        mock_query = Mock()
        mock_query.offset.return_value.limit.return_value.all.return_value = [self.mock_part]
        self.mock_db.query.return_value = mock_query
        
        # Execute the function
        start_time = time.time()
        result = crud.parts.get_parts(self.mock_db, skip=0, limit=100)
        execution_time = time.time() - start_time
        
        # Validate result
        assert result == [self.mock_part]
        
        # Check performance benchmark
        benchmark = PerformanceBenchmark.create_benchmark_thresholds()
        expected_threshold = benchmark["parts_crud"]["get_parts"]  # Should exist or use default
        
        # Since get_parts might not have a specific benchmark, we'll use a reasonable threshold
        assert execution_time < 0.5  # 500ms should be more than enough for a mocked call
    
    def test_create_part_performance_benchmark(self):
        """Test create_part performance against benchmark"""
        from app import schemas
        
        # Mock part creation data
        part_data = schemas.PartCreate(
            part_number="TEST-002",
            name="Test Part 2",
            part_type="consumable",
            is_proprietary=False,
            description="Test description"
        )
        
        # Mock database operations
        self.mock_db.add = Mock()
        self.mock_db.commit = Mock()
        self.mock_db.refresh = Mock()
        
        # Execute the function
        start_time = time.time()
        result = crud.parts.create_part(self.mock_db, part_data)
        execution_time = time.time() - start_time
        
        # Check performance benchmark
        benchmark = PerformanceBenchmark.create_benchmark_thresholds()
        expected_threshold = benchmark["parts_crud"]["create_part"]  # 0.3 seconds
        
        validation = PerformanceBenchmark.validate_performance(
            "parts_crud.create_part", execution_time, benchmark
        )
        
        # The function should complete within the benchmark
        assert validation["meets_benchmark"] is True
        assert execution_time < expected_threshold
    
    def test_search_parts_performance_benchmark(self):
        """Test search_parts performance against benchmark"""
        # Mock database query with search
        mock_query = Mock()
        mock_query.filter.return_value.offset.return_value.limit.return_value.all.return_value = [self.mock_part]
        self.mock_db.query.return_value = mock_query
        
        # Execute the function
        start_time = time.time()
        result = crud.parts.search_parts(self.mock_db, "test", skip=0, limit=100)
        execution_time = time.time() - start_time
        
        # Validate result
        assert result == [self.mock_part]
        
        # Search operations should be reasonably fast even with mocked data
        assert execution_time < 1.0  # 1 second threshold for search


class TestPartsAPIPerformance:
    """Test performance benchmarks for parts API endpoints"""
    
    def setup_method(self):
        """Set up test client and dependencies"""
        self.client = TestClient(app)
        
        # Clear any existing metrics
        performance_monitor.metrics.clear()
        
        # Mock database dependency
        def mock_get_db():
            return Mock(spec=Session)
        
        # Mock authenticated user
        def mock_get_current_user():
            return Mock(
                user_id="test-user-id",
                username="testuser",
                role="user",
                organization_id="test-org-id"
            )
        
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[get_current_user] = mock_get_current_user
    
    def teardown_method(self):
        """Clean up dependency overrides"""
        app.dependency_overrides.clear()
    
    def test_get_parts_api_performance_benchmark(self):
        """Test GET /parts API performance"""
        # Mock the CRUD function
        with patch('app.crud.parts.get_filtered_parts_with_count') as mock_crud:
            mock_crud.return_value = {
                "items": [],
                "total_count": 0,
                "has_more": False
            }
            
            # Make API call and measure time
            start_time = time.time()
            response = self.client.get("/parts/?limit=100")
            execution_time = time.time() - start_time
            
            # Validate response
            assert response.status_code == 200
            
            # Check performance benchmark
            benchmark = PerformanceBenchmark.create_benchmark_thresholds()
            expected_threshold = benchmark["parts_api"]["api.get_parts"]  # 0.6 seconds
            
            validation = PerformanceBenchmark.validate_performance(
                "api.get_parts", execution_time, benchmark
            )
            
            # API should complete within benchmark
            assert validation["meets_benchmark"] is True
            assert execution_time < expected_threshold
    
    def test_search_parts_api_performance_benchmark(self):
        """Test GET /parts/search API performance"""
        # Mock the CRUD function
        with patch('app.crud.parts.search_parts_multilingual_with_count') as mock_crud:
            mock_crud.return_value = {
                "items": [],
                "total_count": 0,
                "has_more": False
            }
            
            # Make API call and measure time
            start_time = time.time()
            response = self.client.get("/parts/search?q=test")
            execution_time = time.time() - start_time
            
            # Validate response
            assert response.status_code == 200
            
            # Check performance benchmark
            benchmark = PerformanceBenchmark.create_benchmark_thresholds()
            expected_threshold = benchmark["parts_api"]["api.search_parts"]  # 1.0 seconds
            
            validation = PerformanceBenchmark.validate_performance(
                "api.search_parts", execution_time, benchmark
            )
            
            # Search API should complete within benchmark
            assert validation["meets_benchmark"] is True
            assert execution_time < expected_threshold
    
    def test_get_part_api_performance_benchmark(self):
        """Test GET /parts/{id} API performance"""
        # Mock the CRUD function
        with patch('app.crud.parts.get_part_with_monitoring') as mock_crud:
            mock_part = Mock()
            mock_part.__dict__ = {"id": "test-id", "name": "Test Part"}
            mock_crud.return_value = mock_part
            
            # Make API call and measure time
            start_time = time.time()
            response = self.client.get("/parts/test-part-id")
            execution_time = time.time() - start_time
            
            # Validate response
            assert response.status_code == 200
            
            # Check performance benchmark
            benchmark = PerformanceBenchmark.create_benchmark_thresholds()
            expected_threshold = benchmark["parts_api"]["api.get_part"]  # 0.2 seconds
            
            validation = PerformanceBenchmark.validate_performance(
                "api.get_part", execution_time, benchmark
            )
            
            # Single part API should complete within benchmark
            assert validation["meets_benchmark"] is True
            assert execution_time < expected_threshold
    
    def test_parts_with_inventory_api_performance_benchmark(self):
        """Test GET /parts/with-inventory API performance"""
        # Mock the CRUD function
        with patch('app.crud.parts.get_parts_with_inventory_with_count') as mock_crud:
            mock_crud.return_value = {
                "items": [],
                "total_count": 0,
                "has_more": False
            }
            
            # Make API call and measure time
            start_time = time.time()
            response = self.client.get("/parts/with-inventory")
            execution_time = time.time() - start_time
            
            # Validate response
            assert response.status_code == 200
            
            # Check performance benchmark
            benchmark = PerformanceBenchmark.create_benchmark_thresholds()
            expected_threshold = benchmark["parts_api"]["api.get_parts_with_inventory"]  # 1.5 seconds
            
            validation = PerformanceBenchmark.validate_performance(
                "api.get_parts_with_inventory", execution_time, benchmark
            )
            
            # Inventory API should complete within benchmark
            assert validation["meets_benchmark"] is True
            assert execution_time < expected_threshold


class TestPerformanceMonitoringIntegration:
    """Test integration of performance monitoring with actual operations"""
    
    def setup_method(self):
        """Set up test environment"""
        # Clear metrics
        performance_monitor.metrics.clear()
    
    def test_performance_monitoring_captures_metrics(self):
        """Test that performance monitoring actually captures metrics"""
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_db.query.return_value.filter.return_value.first.return_value = Mock()
        
        # Call a monitored function
        crud.parts.get_part(mock_db, "test-id")
        
        # Check that metrics were captured
        assert "parts_crud.get_part" in performance_monitor.metrics
        assert len(performance_monitor.metrics["parts_crud.get_part"]) == 1
        
        metric = performance_monitor.metrics["parts_crud.get_part"][0]
        assert metric.success is True
        assert metric.execution_time > 0
    
    def test_performance_monitoring_captures_failures(self):
        """Test that performance monitoring captures failed operations"""
        # Mock database session that raises an exception
        mock_db = Mock(spec=Session)
        mock_db.query.side_effect = Exception("Database error")
        
        # Call a monitored function that will fail
        with pytest.raises(Exception):
            crud.parts.get_part(mock_db, "test-id")
        
        # Check that failure metrics were captured
        assert "parts_crud.get_part" in performance_monitor.metrics
        assert len(performance_monitor.metrics["parts_crud.get_part"]) == 1
        
        metric = performance_monitor.metrics["parts_crud.get_part"][0]
        assert metric.success is False
        assert metric.error_message == "Database error"
        assert metric.execution_time > 0
    
    def test_performance_monitoring_with_parameters(self):
        """Test that performance monitoring captures function parameters"""
        # Mock database session
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_db.query.return_value = mock_query
        
        # Call a monitored function with parameters
        crud.parts.get_filtered_parts(mock_db, part_type="consumable", is_proprietary=True, skip=10, limit=50)
        
        # Check that metrics were captured with parameters
        assert "parts_crud.get_filtered_parts" in performance_monitor.metrics
        metric = performance_monitor.metrics["parts_crud.get_filtered_parts"][0]
        
        assert metric.parameters["part_type"] == "consumable"
        assert metric.parameters["is_proprietary"] is True
        assert metric.parameters["skip"] == 10
        assert metric.parameters["limit"] == 50


class TestPerformanceBenchmarkValidation:
    """Test performance benchmark validation system"""
    
    def test_benchmark_validation_with_real_metrics(self):
        """Test benchmark validation using real performance metrics"""
        # Clear existing metrics
        performance_monitor.metrics.clear()
        
        # Simulate some operations with known performance
        from app.performance_monitoring import PerformanceMetric
        
        # Add a fast operation (should pass)
        fast_metric = PerformanceMetric(
            operation_name="parts_crud.get_part",
            execution_time=0.05,  # 50ms - should pass 100ms benchmark
            timestamp=datetime.now(),
            success=True
        )
        performance_monitor.record_metric(fast_metric)
        
        # Add a slow operation (should fail)
        slow_metric = PerformanceMetric(
            operation_name="parts_crud.search_parts",
            execution_time=1.5,  # 1.5s - might exceed benchmark
            timestamp=datetime.now(),
            success=True
        )
        performance_monitor.record_metric(slow_metric)
        
        # Get benchmark validation
        benchmarks = PerformanceBenchmark.create_benchmark_thresholds()
        summary = performance_monitor.get_all_operations_summary(24)
        
        validation_results = []
        for operation_name, stats in summary.get("operations", {}).items():
            if "error" not in stats:
                validation = PerformanceBenchmark.validate_performance(
                    operation_name, 
                    stats["avg_execution_time"], 
                    benchmarks
                )
                validation_results.append(validation)
        
        # Should have validation results for both operations
        assert len(validation_results) >= 2
        
        # Find the fast operation result
        fast_result = next((r for r in validation_results if r["operation"] == "parts_crud.get_part"), None)
        assert fast_result is not None
        assert fast_result["meets_benchmark"] is True
        assert fast_result["status"] == "pass"
    
    def test_performance_alerting_thresholds(self):
        """Test performance alerting based on thresholds"""
        # Clear existing metrics
        performance_monitor.metrics.clear()
        
        # Add metrics with different performance levels
        from app.performance_monitoring import PerformanceMetric
        
        # Excellent performance
        excellent_metric = PerformanceMetric(
            operation_name="fast_operation",
            execution_time=0.05,
            timestamp=datetime.now(),
            success=True
        )
        performance_monitor.record_metric(excellent_metric)
        
        # Critical performance
        critical_metric = PerformanceMetric(
            operation_name="slow_operation",
            execution_time=5.0,
            timestamp=datetime.now(),
            success=True
        )
        performance_monitor.record_metric(critical_metric)
        
        # Get slow operations
        slow_operations = performance_monitor.get_slow_operations(1.0, 24)  # 1 second threshold
        
        # Should identify the slow operation
        assert len(slow_operations) == 1
        assert slow_operations[0]["operation"] == "slow_operation"
        assert slow_operations[0]["avg_time"] == 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])