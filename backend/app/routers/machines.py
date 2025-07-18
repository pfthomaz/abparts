# backend/app/routers/machines.py

import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import schemas # Import schemas
from ..crud import machines # Corrected: Import machines directly from crud
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, TokenData # Import authentication dependencies
from ..permissions import (
    ResourceType, PermissionType, require_permission, require_super_admin,
    OrganizationScopedQueries, check_organization_access, permission_checker
)

router = APIRouter()

# --- Machines CRUD ---
@router.get("/", response_model=List[schemas.MachineResponse])
async def get_machines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Retrieve a list of machines with organization-scoped filtering.
    Super admins see all machines, regular users see only their organization's machines.
    """
    # If user is not a super_admin, filter machines by organization
    if not permission_checker.is_super_admin(current_user):
        machines_data = machines.get_machines(db, skip, limit, current_user.organization_id)
    else:
        machines_data = machines.get_machines(db, skip, limit)
    
    return machines_data

@router.get("/{machine_id}", response_model=schemas.MachineResponse)
async def get_machine(
    machine_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Retrieve a single machine by ID with organization access control.
    """
    machine = machines.get_machine(db, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    # Check if user can access this machine's organization
    if not check_organization_access(current_user, machine["customer_organization_id"], db):
        raise HTTPException(status_code=403, detail="Not authorized to view this machine")

    return machine

@router.post("/", response_model=schemas.MachineResponse, status_code=status.HTTP_201_CREATED)
async def create_machine(
    machine: schemas.MachineCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Create a new machine. Only super admins can register machines.
    """
    # Additional validation: ensure the target organization exists and user can access it
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can register machines")
    
    db_machine = machines.create_machine(db, machine)
    if not db_machine:
        raise HTTPException(status_code=400, detail="Failed to create machine")
    return db_machine

@router.put("/{machine_id}", response_model=schemas.MachineResponse)
async def update_machine(
    machine_id: uuid.UUID,
    machine_update: schemas.MachineUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Update an existing machine. Only super admins can update machines.
    """
    db_machine = machines.get_machine(db, machine_id)
    if not db_machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    # Only super admins can update machines
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can update machines")

    updated_machine = machines.update_machine(db, machine_id, machine_update)
    if not updated_machine:
        raise HTTPException(status_code=400, detail="Failed to update machine")
    return updated_machine

@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_machine(
    machine_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.DELETE))
):
    """
    Delete a machine by ID. Only super admins can delete machines.
    """
    db_machine = machines.get_machine(db, machine_id)
    if not db_machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    # Only super admins can delete machines
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can delete machines")

    result = machines.delete_machine(db, machine_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to delete machine. Check for dependent records.")
    return result

# --- Machine Transfer ---
@router.post("/transfer", response_model=schemas.MachineResponse)
async def transfer_machine(
    transfer: schemas.MachineTransferRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Transfer a machine to a new customer organization.
    Only super admins can transfer machines.
    """
    # Check if machine exists
    machine = machines.get_machine(db, transfer.machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Only super admins can transfer machines
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can transfer machines")
    
    # Transfer the machine
    transferred_machine = machines.transfer_machine(db, transfer)
    if not transferred_machine:
        raise HTTPException(status_code=400, detail="Failed to transfer machine")
    
    return transferred_machine

# --- Machine Maintenance ---
@router.get("/{machine_id}/maintenance", response_model=List[schemas.MaintenanceResponse])
async def get_machine_maintenance_history(
    machine_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get maintenance history for a specific machine.
    Users can only view maintenance history for machines owned by their organization.
    """
    # Check if machine exists and user has access to it
    machine = machines.get_machine(db, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Check if user can access this machine's organization
    if not check_organization_access(current_user, machine["customer_organization_id"], db):
        raise HTTPException(status_code=403, detail="Not authorized to view this machine's maintenance history")
    
    # Get maintenance history
    maintenance_history = machines.get_machine_maintenance_history(db, machine_id, skip, limit)
    return maintenance_history

@router.post("/{machine_id}/maintenance", response_model=schemas.MaintenanceResponse, status_code=status.HTTP_201_CREATED)
async def create_machine_maintenance(
    machine_id: uuid.UUID,
    maintenance: schemas.MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Create a new maintenance record for a machine.
    Users can only create maintenance records for machines owned by their organization.
    """
    # Check if machine exists and user has access to it
    machine = machines.get_machine(db, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Check if user can access this machine's organization
    if not check_organization_access(current_user, machine["customer_organization_id"], db):
        raise HTTPException(status_code=403, detail="Not authorized to create maintenance records for this machine")
    
    # Ensure the machine_id in the path matches the machine_id in the request body
    if maintenance.machine_id != machine_id:
        maintenance.machine_id = machine_id
    
    # Set performed_by_user_id to current user if not provided
    if not maintenance.performed_by_user_id:
        maintenance.performed_by_user_id = current_user.user_id
    
    # Create maintenance record
    maintenance_record = machines.create_machine_maintenance(db, maintenance)
    if not maintenance_record:
        raise HTTPException(status_code=400, detail="Failed to create maintenance record")
    
    return maintenance_record

@router.post("/{machine_id}/maintenance/{maintenance_id}/parts", response_model=schemas.MaintenancePartUsageResponse, status_code=status.HTTP_201_CREATED)
async def add_part_to_maintenance(
    machine_id: uuid.UUID,
    maintenance_id: uuid.UUID,
    part_usage: schemas.MaintenancePartUsageCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Add a part to a maintenance record.
    Users can only add parts to maintenance records for machines owned by their organization.
    """
    # Check if machine exists and user has access to it
    machine = machines.get_machine(db, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Check if user can access this machine's organization
    if not check_organization_access(current_user, machine["customer_organization_id"], db):
        raise HTTPException(status_code=403, detail="Not authorized to add parts to maintenance records for this machine")
    
    # Ensure the maintenance_id in the path matches the maintenance_id in the request body
    if part_usage.maintenance_id != maintenance_id:
        part_usage.maintenance_id = maintenance_id
    
    # Add part to maintenance record
    part_usage_record = machines.add_part_to_maintenance(db, part_usage)
    if not part_usage_record:
        raise HTTPException(status_code=400, detail="Failed to add part to maintenance record")
    
    return part_usage_record

# --- Machine Part Compatibility ---
@router.get("/{machine_id}/compatible-parts", response_model=List[schemas.MachinePartCompatibilityResponse])
async def get_machine_part_compatibility(
    machine_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get compatible parts for a specific machine.
    Users can only view compatible parts for machines owned by their organization.
    """
    # Check if machine exists and user has access to it
    machine = machines.get_machine(db, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Check if user can access this machine's organization
    if not check_organization_access(current_user, machine["customer_organization_id"], db):
        raise HTTPException(status_code=403, detail="Not authorized to view compatible parts for this machine")
    
    # Get compatible parts
    compatible_parts = machines.get_machine_part_compatibility(db, machine_id, skip, limit)
    return compatible_parts

@router.post("/{machine_id}/compatible-parts", response_model=schemas.MachinePartCompatibilityResponse, status_code=status.HTTP_201_CREATED)
async def add_compatible_part(
    machine_id: uuid.UUID,
    compatibility: schemas.MachinePartCompatibilityCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.WRITE))
):
    """
    Add a compatible part to a machine.
    Only super admins can add compatible parts to machines.
    """
    # Check if machine exists
    machine = machines.get_machine(db, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Only super admins can add compatible parts to machines
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can add compatible parts to machines")
    
    # Ensure the machine_id in the path matches the machine_id in the request body
    if compatibility.machine_id != machine_id:
        compatibility.machine_id = machine_id
    
    # Add compatible part
    compatible_part = machines.add_compatible_part(db, compatibility)
    if not compatible_part:
        raise HTTPException(status_code=400, detail="Failed to add compatible part")
    
    return compatible_part

@router.delete("/{machine_id}/compatible-parts/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_compatible_part(
    machine_id: uuid.UUID,
    part_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.DELETE))
):
    """
    Remove a compatible part from a machine.
    Only super admins can remove compatible parts from machines.
    """
    # Check if machine exists
    machine = machines.get_machine(db, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Only super admins can remove compatible parts from machines
    if not permission_checker.is_super_admin(current_user):
        raise HTTPException(status_code=403, detail="Only super admins can remove compatible parts from machines")
    
    # Remove compatible part
    result = machines.remove_compatible_part(db, machine_id, part_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to remove compatible part")
    
    return result

# --- Machine Usage History ---
@router.get("/{machine_id}/usage-history", response_model=List[schemas.PartUsageResponse])
async def get_machine_usage_history(
    machine_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.MACHINE, PermissionType.READ))
):
    """
    Get part usage history for a specific machine.
    Users can only view usage history for machines owned by their organization.
    """
    # Check if machine exists and user has access to it
    machine = machines.get_machine(db, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Check if user can access this machine's organization
    if not check_organization_access(current_user, machine["customer_organization_id"], db):
        raise HTTPException(status_code=403, detail="Not authorized to view usage history for this machine")
    
    # Get usage history
    usage_history = machines.get_machine_usage_history(db, machine_id, skip, limit)
    return usage_history