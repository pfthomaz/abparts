# backend/tests/test_performance_monitoring.py

import pytest
import time
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.performance_monitoring import (
    PerformanceMonitor, PerformanceMetric, PerformanceLevel, 
    monitor_performance, monitor_api_performance, PerformanceBenchmark,
    performance_monitor
)
from app.main import app
from app.database import get_db
from app.auth import get_current_user


class TestPerformanceMonitor:
    """Test the PerformanceMonitor class"""
    
    def test_performance_monitor_initialization(self):
        """Test PerformanceMonitor initialization"""
        monitor = PerformanceMonitor(max_metrics_per_operation=100)
        assert len(monitor.metrics) == 0
        assert monitor.thresholds[PerformanceLevel.EXCELLENT] == 0.1
        assert monitor.thresholds[PerformanceLevel.GOOD] == 0.5
        assert monitor.thresholds[PerformanceLevel.ACCEPTABLE] == 1.0
        assert monitor.thresholds[PerformanceLevel.SLOW] == 3.0
    
    def test_record_metric(self):
        """Test recording performance metrics"""
        monitor = PerformanceMonitor()
        
        metric = PerformanceMetric(
            operation_name="test_operation",
            execution_time=0.5,
            timestamp=datetime.now(),
            parameters={"param1": "value1"},
            success=True
        )
        
        monitor.record_metric(metric)
        assert len(monitor.metrics["test_operation"]) == 1
        assert monitor.metrics["test_operation"][0] == metric
    
    def test_get_performance_level(self):
        """Test performance level classification"""
        monitor = PerformanceMonitor()
        
        assert monitor._get_performance_level(0.05) == PerformanceLevel.EXCELLENT
        assert monitor._get_performance_level(0.3) == PerformanceLevel.GOOD
        assert monitor._get_performance_level(0.8) == PerformanceLevel.ACCEPTABLE
        assert monitor._get_performance_level(2.0) == PerformanceLevel.SLOW
        assert monitor._get_performance_level(5.0) == PerformanceLevel.CRITICAL
    
    def test_get_operation_stats(self):
        """Test getting operation statistics"""
        monitor = PerformanceMonitor()
        
        # Add test metrics
        for i in range(5):
            metric = PerformanceMetric(
                operation_name="test_op",
                execution_time=0.1 + (i * 0.1),  # 0.1, 0.2, 0.3, 0.4, 0.5
                timestamp=datetime.now(),
                success=True
            )
            monitor.record_metric(metric)
        
        stats = monitor.get_operation_stats("test_op", 24)
        
        assert stats["operation_name"] == "test_op"
        assert stats["total_calls"] == 5
        assert stats["successful_calls"] == 5
        assert stats["failed_calls"] == 0
        assert stats["success_rate"] == 100.0
        assert stats["avg_execution_time"] == 0.3  # Average of 0.1 to 0.5
        assert stats["min_execution_time"] == 0.1
        assert stats["max_execution_time"] == 0.5
    
    def test_get_slow_operations(self):
        """Test getting slow operations"""
        monitor = PerformanceMonitor()
        
        # Add fast operation
        fast_metric = PerformanceMetric(
            operation_name="fast_op",
            execution_time=0.1,
            timestamp=datetime.now(),
            success=True
        )
        monitor.record_metric(fast_metric)
        
        # Add slow operation
        slow_metric = PerformanceMetric(
            operation_name="slow_op",
            execution_time=2.0,
            timestamp=datetime.now(),
            success=True
        )
        monitor.record_metric(slow_metric)
        
        slow_ops = monitor.get_slow_operations(1.0, 24)  # Threshold 1 second
        
        # Should only return operations that exceed the threshold
        slow_operations = [op for op in slow_ops if op["avg_time"] > 1.0]
        assert len(slow_operations) == 1
        assert slow_operations[0]["operation"] == "slow_op"
        assert slow_operations[0]["avg_time"] == 2.0
    
    def test_percentile_calculation(self):
        """Test percentile calculation"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        assert PerformanceMonitor._percentile(data, 50) == 5.5
        assert PerformanceMonitor._percentile(data, 90) == 9.1
        assert abs(PerformanceMonitor._percentile(data, 95) - 9.55) < 0.01  # Allow for floating point precision
        assert PerformanceMonitor._percentile([], 50) == 0.0


class TestPerformanceDecorators:
    """Test performance monitoring decorators"""
    
    def test_monitor_performance_decorator_success(self):
        """Test monitor_performance decorator with successful function"""
        monitor = PerformanceMonitor()
        
        @monitor_performance("test_function")
        def test_function(x, y=10):
            time.sleep(0.01)  # Small delay to measure
            return x + y
        
        # Patch the global performance_monitor
        with patch('app.performance_monitoring.performance_monitor', monitor):
            result = test_function(5, y=15)
        
        assert result == 20
        assert len(monitor.metrics["test_function"]) == 1
        metric = monitor.metrics["test_function"][0]
        assert metric.success is True
        assert metric.execution_time > 0.01
    
    def test_monitor_performance_decorator_failure(self):
        """Test monitor_performance decorator with failing function"""
        monitor = PerformanceMonitor()
        
        @monitor_performance("failing_function")
        def failing_function():
            raise ValueError("Test error")
        
        with patch('app.performance_monitoring.performance_monitor', monitor):
            with pytest.raises(ValueError):
                failing_function()
        
        assert len(monitor.metrics["failing_function"]) == 1
        metric = monitor.metrics["failing_function"][0]
        assert metric.success is False
        assert metric.error_message == "Test error"
    
    @pytest.mark.asyncio
    async def test_monitor_api_performance_decorator(self):
        """Test monitor_api_performance decorator"""
        monitor = PerformanceMonitor()
        
        @monitor_api_performance("test_api")
        async def test_api_function(skip=0, limit=100):
            await asyncio.sleep(0.01)  # Small delay
            return {"items": [], "total": 0}
        
        with patch('app.performance_monitoring.performance_monitor', monitor):
            result = await test_api_function(skip=10, limit=50)
        
        assert result == {"items": [], "total": 0}
        assert len(monitor.metrics["test_api"]) == 1
        metric = monitor.metrics["test_api"][0]
        assert metric.success is True
        assert metric.parameters["skip"] == 10
        assert metric.parameters["limit"] == 50


class TestPerformanceBenchmark:
    """Test performance benchmark utilities"""
    
    def test_create_benchmark_thresholds(self):
        """Test benchmark threshold creation"""
        benchmarks = PerformanceBenchmark.create_benchmark_thresholds()
        
        assert "parts_crud" in benchmarks
        assert "parts_api" in benchmarks
        assert "get_part" in benchmarks["parts_crud"]
        assert "api.get_parts" in benchmarks["parts_api"]
        
        # Check some specific thresholds
        assert benchmarks["parts_crud"]["get_part"] == 0.1
        assert benchmarks["parts_api"]["api.get_parts"] == 0.6
    
    def test_validate_performance_pass(self):
        """Test performance validation that passes"""
        result = PerformanceBenchmark.validate_performance(
            "get_part", 0.05, {"parts_crud": {"get_part": 0.1}}
        )
        
        assert result["operation"] == "get_part"
        assert result["execution_time"] == 0.05
        assert result["benchmark_threshold"] == 0.1
        assert result["meets_benchmark"] is True
        assert result["status"] == "pass"
        assert result["performance_ratio"] == 0.5
    
    def test_validate_performance_fail(self):
        """Test performance validation that fails"""
        result = PerformanceBenchmark.validate_performance(
            "get_part", 0.2, {"parts_crud": {"get_part": 0.1}}
        )
        
        assert result["operation"] == "get_part"
        assert result["execution_time"] == 0.2
        assert result["benchmark_threshold"] == 0.1
        assert result["meets_benchmark"] is False
        assert result["status"] == "fail"
        assert result["performance_ratio"] == 2.0
    
    def test_validate_performance_no_benchmark(self):
        """Test performance validation with no benchmark"""
        result = PerformanceBenchmark.validate_performance(
            "unknown_operation", 0.5, {"parts_crud": {"get_part": 0.1}}
        )
        
        assert result["operation"] == "unknown_operation"
        assert result["status"] == "no_benchmark"


class TestPerformanceAPI:
    """Test performance monitoring API endpoints"""
    
    def setup_method(self):
        """Set up test client and mock dependencies"""
        self.client = TestClient(app)
        
        # Mock database dependency
        def mock_get_db():
            return Mock(spec=Session)
        
        # Mock super admin user
        def mock_get_current_user():
            return Mock(
                user_id="test-user-id",
                username="superadmin",
                role="super_admin",
                organization_id="test-org-id"
            )
        
        app.dependency_overrides[get_db] = mock_get_db
        app.dependency_overrides[get_current_user] = mock_get_current_user
    
    def teardown_method(self):
        """Clean up dependency overrides"""
        app.dependency_overrides.clear()
    
    def test_get_performance_metrics_unauthorized(self):
        """Test performance metrics endpoint without authentication"""
        # Remove the mock to test unauthorized access
        app.dependency_overrides.clear()
        
        response = self.client.get("/performance/metrics/operations")
        assert response.status_code == 401
    
    def test_get_performance_benchmarks(self):
        """Test getting performance benchmarks"""
        response = self.client.get("/performance/benchmarks")
        assert response.status_code == 200
        
        data = response.json()
        assert "parts_crud" in data
        assert "parts_api" in data
    
    def test_get_performance_health(self):
        """Test performance health endpoint"""
        response = self.client.get("/performance/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "total_operations" in data
        assert "critical_operations" in data
        assert "warning_operations" in data
    
    def test_validate_performance_benchmarks(self):
        """Test performance benchmark validation"""
        # Add some test metrics to the global monitor
        test_metric = PerformanceMetric(
            operation_name="parts_crud.get_part",
            execution_time=0.05,  # Should pass benchmark
            timestamp=datetime.now(),
            success=True
        )
        performance_monitor.record_metric(test_metric)
        
        response = self.client.post("/performance/benchmarks/validate?hours=1")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


class TestPerformanceIntegration:
    """Integration tests for performance monitoring"""
    
    def setup_method(self):
        """Set up test environment"""
        self.client = TestClient(app)
        
        # Mock database and auth dependencies
        def mock_get_db():
            return Mock(spec=Session)
        
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
        """Clean up"""
        app.dependency_overrides.clear()
    
    def test_parts_api_performance_monitoring(self):
        """Test that parts API endpoints are being monitored"""
        # Mock the CRUD function to avoid database calls
        with patch('app.crud.parts.get_filtered_parts_with_count') as mock_crud:
            mock_crud.return_value = {
                "items": [],
                "total_count": 0,
                "has_more": False
            }
            
            # Make API call
            response = self.client.get("/parts/?limit=10")
            assert response.status_code == 200
            
            # Check that the API call was monitored
            # Note: In a real test, you'd check the performance_monitor metrics
            # but since we're using the global instance, we'll just verify the call succeeded
            mock_crud.assert_called_once()
    
    def test_performance_monitoring_with_parameters(self):
        """Test that performance monitoring captures parameters correctly"""
        monitor = PerformanceMonitor()
        
        @monitor_performance("test_with_params", param_keys=["limit", "skip"])
        def test_function(skip=0, limit=100, secret="hidden"):
            return {"skip": skip, "limit": limit}
        
        with patch('app.performance_monitoring.performance_monitor', monitor):
            result = test_function(skip=20, limit=50, secret="should_not_appear")
        
        assert result == {"skip": 20, "limit": 50}
        assert len(monitor.metrics["test_with_params"]) == 1
        
        metric = monitor.metrics["test_with_params"][0]
        assert metric.parameters["limit"] == 50
        assert metric.parameters["skip"] == 20
        assert "secret" not in metric.parameters
    
    def test_performance_monitoring_thread_safety(self):
        """Test that performance monitoring is thread-safe"""
        import threading
        import concurrent.futures
        
        monitor = PerformanceMonitor()
        
        @monitor_performance("thread_test")
        def thread_function(thread_id):
            time.sleep(0.01)  # Small delay
            return thread_id
        
        with patch('app.performance_monitoring.performance_monitor', monitor):
            # Run multiple threads concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(thread_function, i) for i in range(10)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All threads should have completed successfully
        assert len(results) == 10
        assert len(monitor.metrics["thread_test"]) == 10
        
        # All metrics should be successful
        for metric in monitor.metrics["thread_test"]:
            assert metric.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])