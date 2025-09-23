# backend/app/routers/performance.py

import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..auth import TokenData
from ..permissions import require_super_admin
from ..performance_monitoring import performance_monitor, PerformanceBenchmark

router = APIRouter()

@router.get("/metrics/operations", response_model=Dict[str, Any])
async def get_performance_metrics(
    hours: int = Query(24, ge=1, le=168, description="Time window in hours (max 1 week)"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_super_admin())
):
    """
    Get performance metrics for all operations.
    Only super admins can access performance metrics.
    """
    return performance_monitor.get_all_operations_summary(hours)

@router.get("/metrics/operations/{operation_name}", response_model=Dict[str, Any])
async def get_operation_performance(
    operation_name: str,
    hours: int = Query(24, ge=1, le=168, description="Time window in hours (max 1 week)"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_super_admin())
):
    """
    Get performance metrics for a specific operation.
    Only super admins can access performance metrics.
    """
    stats = performance_monitor.get_operation_stats(operation_name, hours)
    if "error" in stats:
        raise HTTPException(status_code=404, detail=stats["error"])
    return stats

@router.get("/metrics/slow-operations", response_model=List[Dict[str, Any]])
async def get_slow_operations(
    threshold_ms: float = Query(1000, ge=100, le=10000, description="Threshold in milliseconds"),
    hours: int = Query(24, ge=1, le=168, description="Time window in hours (max 1 week)"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_super_admin())
):
    """
    Get operations that exceed the specified performance threshold.
    Only super admins can access performance metrics.
    """
    return performance_monitor.get_slow_operations(threshold_ms, hours)

@router.get("/benchmarks", response_model=Dict[str, Dict[str, float]])
async def get_performance_benchmarks(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_super_admin())
):
    """
    Get performance benchmarks for all operations.
    Only super admins can access performance benchmarks.
    """
    return PerformanceBenchmark.create_benchmark_thresholds()

@router.post("/benchmarks/validate", response_model=List[Dict[str, Any]])
async def validate_performance_benchmarks(
    hours: int = Query(24, ge=1, le=168, description="Time window in hours (max 1 week)"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_super_admin())
):
    """
    Validate current performance against benchmarks.
    Only super admins can access performance validation.
    """
    benchmarks = PerformanceBenchmark.create_benchmark_thresholds()
    summary = performance_monitor.get_all_operations_summary(hours)
    
    validation_results = []
    
    for operation_name, stats in summary.get("operations", {}).items():
        if "error" not in stats:
            validation = PerformanceBenchmark.validate_performance(
                operation_name, 
                stats["avg_execution_time"], 
                benchmarks
            )
            validation_results.append(validation)
    
    return validation_results

@router.get("/health", response_model=Dict[str, Any])
async def get_performance_health(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_super_admin())
):
    """
    Get overall performance health status.
    Only super admins can access performance health.
    """
    # Get recent performance data
    summary = performance_monitor.get_all_operations_summary(1)  # Last hour
    slow_operations = performance_monitor.get_slow_operations(1000, 1)  # > 1 second in last hour
    
    # Calculate health metrics
    total_operations = summary.get("total_operations", 0)
    critical_operations = len([op for op in slow_operations if op["avg_time"] > 3.0])  # > 3 seconds
    warning_operations = len([op for op in slow_operations if 1.0 < op["avg_time"] <= 3.0])  # 1-3 seconds
    
    # Determine health status
    if critical_operations > 0:
        health_status = "critical"
    elif warning_operations > total_operations * 0.2:  # More than 20% of operations are slow
        health_status = "warning"
    elif warning_operations > 0:
        health_status = "degraded"
    else:
        health_status = "healthy"
    
    return {
        "status": health_status,
        "total_operations": total_operations,
        "critical_operations": critical_operations,
        "warning_operations": warning_operations,
        "healthy_operations": total_operations - critical_operations - warning_operations,
        "slow_operations_details": slow_operations[:5],  # Top 5 slowest
        "timestamp": summary.get("time_window_hours", 1)
    }