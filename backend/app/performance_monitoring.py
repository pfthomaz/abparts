# backend/app/performance_monitoring.py

import time
import logging
import functools
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from dataclasses import dataclass, field
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)

class PerformanceLevel(Enum):
    """Performance level thresholds"""
    EXCELLENT = "excellent"  # < 100ms
    GOOD = "good"           # 100ms - 500ms
    ACCEPTABLE = "acceptable"  # 500ms - 1000ms
    SLOW = "slow"           # 1000ms - 3000ms
    CRITICAL = "critical"   # > 3000ms

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    operation_name: str
    execution_time: float
    timestamp: datetime
    parameters: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None

class PerformanceMonitor:
    """Thread-safe performance monitoring system"""
    
    def __init__(self, max_metrics_per_operation: int = 1000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics_per_operation))
        self.lock = threading.Lock()
        self.thresholds = {
            PerformanceLevel.EXCELLENT: 0.1,    # 100ms
            PerformanceLevel.GOOD: 0.5,         # 500ms
            PerformanceLevel.ACCEPTABLE: 1.0,   # 1000ms
            PerformanceLevel.SLOW: 3.0,         # 3000ms
        }
    
    def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric"""
        with self.lock:
            self.metrics[metric.operation_name].append(metric)
            
        # Log based on performance level
        level = self._get_performance_level(metric.execution_time)
        log_message = (
            f"Performance [{level.value.upper()}]: {metric.operation_name} "
            f"executed in {metric.execution_time:.3f}s"
        )
        
        if metric.parameters:
            log_message += f" with params: {metric.parameters}"
            
        if not metric.success:
            log_message += f" - ERROR: {metric.error_message}"
            
        if level in [PerformanceLevel.SLOW, PerformanceLevel.CRITICAL]:
            logger.warning(log_message)
        elif level == PerformanceLevel.ACCEPTABLE:
            logger.info(log_message)
        else:
            logger.debug(log_message)
    
    def _get_performance_level(self, execution_time: float) -> PerformanceLevel:
        """Determine performance level based on execution time"""
        if execution_time > self.thresholds[PerformanceLevel.SLOW]:
            return PerformanceLevel.CRITICAL
        elif execution_time > self.thresholds[PerformanceLevel.ACCEPTABLE]:
            return PerformanceLevel.SLOW
        elif execution_time > self.thresholds[PerformanceLevel.GOOD]:
            return PerformanceLevel.ACCEPTABLE
        elif execution_time > self.thresholds[PerformanceLevel.EXCELLENT]:
            return PerformanceLevel.GOOD
        else:
            return PerformanceLevel.EXCELLENT
    
    def get_operation_stats(self, operation_name: str, hours: int = 24) -> Dict[str, Any]:
        """Get statistics for a specific operation"""
        with self.lock:
            if operation_name not in self.metrics:
                return {"error": "Operation not found"}
            
            # Filter metrics by time window
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [
                m for m in self.metrics[operation_name] 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {"error": "No recent metrics found"}
            
            execution_times = [m.execution_time for m in recent_metrics]
            success_count = sum(1 for m in recent_metrics if m.success)
            
            return {
                "operation_name": operation_name,
                "total_calls": len(recent_metrics),
                "successful_calls": success_count,
                "failed_calls": len(recent_metrics) - success_count,
                "success_rate": success_count / len(recent_metrics) * 100,
                "avg_execution_time": sum(execution_times) / len(execution_times),
                "min_execution_time": min(execution_times),
                "max_execution_time": max(execution_times),
                "p95_execution_time": self._percentile(execution_times, 95),
                "p99_execution_time": self._percentile(execution_times, 99),
                "time_window_hours": hours
            }
    
    def get_all_operations_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary statistics for all operations"""
        with self.lock:
            operations = list(self.metrics.keys())
            
        summary = {
            "total_operations": len(operations),
            "time_window_hours": hours,
            "operations": {}
        }
        
        for operation in operations:
            stats = self.get_operation_stats(operation, hours)
            if "error" not in stats:
                summary["operations"][operation] = stats
        
        return summary
    
    def get_slow_operations(self, threshold_ms: float = 1000, hours: int = 24) -> list:
        """Get operations that exceed the specified threshold"""
        slow_operations = []
        
        with self.lock:
            operations = list(self.metrics.keys())
        
        for operation in operations:
            stats = self.get_operation_stats(operation, hours)
            if "error" not in stats and stats["avg_execution_time"] > (threshold_ms / 1000):
                slow_operations.append({
                    "operation": operation,
                    "avg_time": stats["avg_execution_time"],
                    "max_time": stats["max_execution_time"],
                    "total_calls": stats["total_calls"]
                })
        
        return sorted(slow_operations, key=lambda x: x["avg_time"], reverse=True)
    
    @staticmethod
    def _percentile(data: list, percentile: int) -> float:
        """Calculate percentile of a list of numbers"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def monitor_performance(operation_name: Optional[str] = None, 
                       include_params: bool = True,
                       param_keys: Optional[list] = None):
    """
    Decorator to monitor function performance
    
    Args:
        operation_name: Custom name for the operation (defaults to function name)
        include_params: Whether to include function parameters in metrics
        param_keys: Specific parameter keys to include (if None, includes all)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            # Extract parameters to include in metrics
            parameters = {}
            if include_params:
                if param_keys:
                    parameters = {k: kwargs.get(k) for k in param_keys if k in kwargs}
                else:
                    # Include basic info about parameters without sensitive data
                    parameters = {
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys())
                    }
                    # Include specific safe parameters
                    safe_params = ["skip", "limit", "part_type", "is_proprietary", "include_count"]
                    for param in safe_params:
                        if param in kwargs:
                            parameters[param] = kwargs[param]
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Record successful execution
                metric = PerformanceMetric(
                    operation_name=op_name,
                    execution_time=execution_time,
                    timestamp=datetime.now(),
                    parameters=parameters,
                    success=True
                )
                performance_monitor.record_metric(metric)
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Record failed execution
                metric = PerformanceMetric(
                    operation_name=op_name,
                    execution_time=execution_time,
                    timestamp=datetime.now(),
                    parameters=parameters,
                    success=False,
                    error_message=str(e)
                )
                performance_monitor.record_metric(metric)
                
                raise
        
        return wrapper
    return decorator

def monitor_api_performance(endpoint_name: Optional[str] = None):
    """
    Decorator specifically for API endpoint performance monitoring
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            op_name = endpoint_name or f"api.{func.__name__}"
            start_time = time.time()
            
            # Extract safe parameters for API monitoring
            parameters = {}
            if kwargs:
                safe_api_params = [
                    "skip", "limit", "part_type", "is_proprietary", "include_count",
                    "search", "q", "organization_id", "days", "threshold_days"
                ]
                for param in safe_api_params:
                    if param in kwargs and kwargs[param] is not None:
                        parameters[param] = kwargs[param]
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Record successful API call
                metric = PerformanceMetric(
                    operation_name=op_name,
                    execution_time=execution_time,
                    timestamp=datetime.now(),
                    parameters=parameters,
                    success=True
                )
                performance_monitor.record_metric(metric)
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Record failed API call
                metric = PerformanceMetric(
                    operation_name=op_name,
                    execution_time=execution_time,
                    timestamp=datetime.now(),
                    parameters=parameters,
                    success=False,
                    error_message=str(e)
                )
                performance_monitor.record_metric(metric)
                
                raise
        
        return async_wrapper
    return decorator

# Performance benchmark utilities
class PerformanceBenchmark:
    """Utility class for performance benchmarking"""
    
    @staticmethod
    def create_benchmark_thresholds() -> Dict[str, Dict[str, float]]:
        """Define performance benchmarks for different operations"""
        return {
            "parts_crud": {
                "get_part": 0.1,                    # 100ms
                "get_parts": 0.5,                   # 500ms
                "search_parts": 0.8,                # 800ms
                "create_part": 0.3,                 # 300ms
                "update_part": 0.3,                 # 300ms
                "delete_part": 0.2,                 # 200ms
            },
            "parts_api": {
                "api.get_parts": 0.6,               # 600ms
                "api.search_parts": 1.0,            # 1000ms
                "api.get_part": 0.2,                # 200ms
                "api.create_part": 0.4,             # 400ms
                "api.update_part": 0.4,             # 400ms
                "api.delete_part": 0.3,             # 300ms
                "api.get_parts_with_inventory": 1.5, # 1500ms
                "api.search_parts_with_inventory": 2.0, # 2000ms
            }
        }
    
    @staticmethod
    def validate_performance(operation_name: str, execution_time: float, 
                           benchmarks: Optional[Dict] = None) -> Dict[str, Any]:
        """Validate if operation performance meets benchmarks"""
        if benchmarks is None:
            benchmarks = PerformanceBenchmark.create_benchmark_thresholds()
        
        # Find the benchmark for this operation
        benchmark_threshold = None
        category = None
        
        for cat, ops in benchmarks.items():
            if operation_name in ops:
                benchmark_threshold = ops[operation_name]
                category = cat
                break
        
        if benchmark_threshold is None:
            return {
                "operation": operation_name,
                "execution_time": execution_time,
                "status": "no_benchmark",
                "message": "No benchmark defined for this operation"
            }
        
        meets_benchmark = execution_time <= benchmark_threshold
        performance_ratio = execution_time / benchmark_threshold
        
        return {
            "operation": operation_name,
            "category": category,
            "execution_time": execution_time,
            "benchmark_threshold": benchmark_threshold,
            "meets_benchmark": meets_benchmark,
            "performance_ratio": performance_ratio,
            "status": "pass" if meets_benchmark else "fail",
            "message": (
                f"Performance {'meets' if meets_benchmark else 'exceeds'} "
                f"benchmark by {performance_ratio:.2f}x"
            )
        }