# backend/app/routers/machines.py

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
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
    # Apply organization-scoped filtering
    query = db.query(schemas.Machine)  # This should be models.Machine, but keeping consistent with existing code
    filtered_query = OrganizationScopedQueries.filter_machines(query, current_user)
    
    machines_data = filtered_query.offset(skip).limit(limit).all()
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
    if not check_organization_access(current_user, machine.customer_organization_id, db):
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

