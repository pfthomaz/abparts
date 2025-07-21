"""
Monitoring router for ABParts.
Provides endpoints for health checks, metrics, and alerts.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional

from ..database import get_db
from ..auth import get_current_user, has_role, has_roles
from ..monitoring import get_monitoring_system

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def get_health():
    """
    Get system health status.
    
    Returns a health check report for all system components.
    This endpoint is public and does not require authentication.
    """
    monitoring = get_monitoring_system()
    if not monitoring:
        return {
            "status": "unknown",
            "message": "Monitoring system not initialized"
        }
    
    return monitoring.get_health()


@router.get("/metrics", response_model=Dict[str, Any])
async def get_metrics(current_user = Depends(has_roles(["admin", "super_admin"]))):
    """
    Get system metrics.
    
    Returns detailed metrics about system performance and usage.
    Requires admin privileges.
    """
    monitoring = get_monitoring_system()
    if not monitoring:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Monitoring system not initialized"
        )
    
    return monitoring.get_metrics()


@router.get("/alerts", response_model=Dict[str, Any])
async def get_alerts(current_user = Depends(has_roles(["admin", "super_admin"]))):
    """
    Get active alerts.
    
    Returns currently active alerts and recent alert history.
    Requires admin privileges.
    """
    monitoring = get_monitoring_system()
    if not monitoring:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Monitoring system not initialized"
        )
    
    return {
        "active_alerts": monitoring.get_active_alerts(),
        "recent_history": monitoring.get_alert_history(10)
    }


@router.get("/alert-history", response_model=List[Dict[str, Any]])
async def get_alert_history(
    limit: int = 100,
    current_user = Depends(has_roles(["admin", "super_admin"]))
):
    """
    Get alert history.
    
    Returns historical alerts up to the specified limit.
    Requires admin privileges.
    """
    monitoring = get_monitoring_system()
    if not monitoring:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Monitoring system not initialized"
        )
    
    return monitoring.get_alert_history(limit)


@router.post("/alerts/{alert_id}/resolve", response_model=Dict[str, Any])
async def resolve_alert(
    alert_id: str,
    current_user = Depends(has_role("super_admin"))
):
    """
    Manually resolve an alert.
    
    Marks the specified alert as resolved.
    Requires super admin privileges.
    """
    monitoring = get_monitoring_system()
    if not monitoring:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Monitoring system not initialized"
        )
    
    monitoring.alert_manager.resolve_alert(alert_id)
    
    return {
        "status": "success",
        "message": f"Alert {alert_id} resolved",
        "active_alerts": monitoring.get_active_alerts()
    }


@router.get("/system-info", response_model=Dict[str, Any])
async def get_system_info(current_user = Depends(has_roles(["admin", "super_admin"]))):
    """
    Get system information.
    
    Returns general information about the system configuration.
    Requires admin privileges.
    """
    import platform
    import os
    import sys
    import psutil
    
    try:
        cpu_count = os.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "python": {
                "version": sys.version,
                "implementation": platform.python_implementation(),
                "path": sys.executable
            },
            "resources": {
                "cpu_count": cpu_count,
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Error retrieving system information"
        }