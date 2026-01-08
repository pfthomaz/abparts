"""
Machine-related API endpoints for the AI Assistant.

This module provides endpoints for retrieving machine information
and context for troubleshooting sessions.
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.abparts_integration import abparts_integration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai/machines", tags=["machines"])


@router.get("/{user_id}")
async def get_user_machines(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all machines accessible to a user.
    
    Args:
        user_id: UUID of the user
        
    Returns:
        List of machines accessible to the user
    """
    try:
        machines = await abparts_integration.get_user_machines(user_id)
        return machines
    except Exception as e:
        logger.error(f"Error retrieving machines for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve machines")


@router.get("/{machine_id}/details")
async def get_machine_details(machine_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific machine.
    
    Args:
        machine_id: UUID of the machine
        
    Returns:
        Detailed machine information
    """
    try:
        machine_details = await abparts_integration.get_machine_details(machine_id)
        if not machine_details:
            raise HTTPException(status_code=404, detail="Machine not found")
        return machine_details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving machine details for {machine_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve machine details")


@router.get("/{machine_id}/maintenance")
async def get_machine_maintenance_history(
    machine_id: str, 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get maintenance history for a specific machine.
    
    Args:
        machine_id: UUID of the machine
        limit: Maximum number of records to return
        
    Returns:
        List of maintenance records
    """
    try:
        maintenance_history = await abparts_integration.get_maintenance_history(machine_id, limit)
        return maintenance_history
    except Exception as e:
        logger.error(f"Error retrieving maintenance history for {machine_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve maintenance history")


@router.get("/{machine_id}/parts-usage")
async def get_machine_parts_usage(
    machine_id: str, 
    days: int = 90
) -> List[Dict[str, Any]]:
    """
    Get parts usage data for a specific machine.
    
    Args:
        machine_id: UUID of the machine
        days: Number of days to look back
        
    Returns:
        List of parts usage records
    """
    try:
        parts_usage = await abparts_integration.get_parts_usage_data(machine_id, days)
        return parts_usage
    except Exception as e:
        logger.error(f"Error retrieving parts usage for {machine_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve parts usage data")


@router.get("/{machine_id}/hours")
async def get_machine_hours_history(
    machine_id: str, 
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Get machine hours history for trend analysis.
    
    Args:
        machine_id: UUID of the machine
        limit: Maximum number of records to return
        
    Returns:
        List of machine hours records
    """
    try:
        hours_history = await abparts_integration.get_machine_hours_history(machine_id, limit)
        return hours_history
    except Exception as e:
        logger.error(f"Error retrieving hours history for {machine_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve hours history")


@router.get("/{machine_id}/maintenance-suggestions")
async def get_machine_maintenance_suggestions(machine_id: str) -> List[Dict[str, Any]]:
    """
    Get preventive maintenance suggestions for a specific machine.
    
    Args:
        machine_id: UUID of the machine
        
    Returns:
        List of maintenance suggestions
    """
    try:
        suggestions = await abparts_integration.get_preventive_maintenance_suggestions(machine_id)
        return suggestions
    except Exception as e:
        logger.error(f"Error retrieving maintenance suggestions for {machine_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve maintenance suggestions")