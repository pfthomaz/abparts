# backend/app/routers/machines.py

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas # Import schemas
from ..crud import machines # Corrected: Import machines directly from crud
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, has_role, has_roles, TokenData # Import authentication dependencies

router = APIRouter()

# --- Machines CRUD ---
@router.get("/", response_model=List[schemas.MachineResponse])
async def get_machines(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Retrieve a list of machines.
    - Oraseas Admin: Can see all machines.
    - Customer Admin/User: Can only see machines belonging to their organization.
    - Supplier User: Not authorized to view machines.
    """
    if current_user.role == "Oraseas Admin":
        machines_data = machines.get_machines(db, skip, limit) # No await here, crud function is synchronous
    elif current_user.role in ["Customer Admin", "Customer User"]:
        # Pass the organization_id to filter machines for customer roles
        machines_data = machines.get_machines(db, skip, limit, organization_id=current_user.organization_id) # No await
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view machines")
    return machines_data

@router.get("/{machine_id}", response_model=schemas.MachineResponse)
async def get_machine(
    machine_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Retrieve a single machine by ID.
    - Oraseas Admin: Can see any machine.
    - Customer Admin/User: Can only see machines belonging to their organization.
    """
    machine = machines.get_machine(db, machine_id) # This crud function is synchronous, no await needed here.
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    if current_user.role == "Oraseas Admin" or (
        current_user.role in ["Customer Admin", "Customer User"] and machine.organization_id == current_user.organization_id
    ):
        return machine
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this machine's details")

@router.post("/", response_model=schemas.MachineResponse, status_code=status.HTTP_201_CREATED)
async def create_machine(
    machine: schemas.MachineCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin"]))
):
    """
    Create a new machine.
    - Oraseas Admin: Can create machines for any organization.
    - Customer Admin: Can only create machines for their own organization.
    """
    if current_user.role == "Customer Admin" and machine.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Customer Admin can only create machines within their own organization")
    
    db_machine = machines.create_machine(db, machine) # This crud function is synchronous, no await needed here.
    if not db_machine: # Error handled in CRUD layer
        raise HTTPException(status_code=400, detail="Failed to create machine")
    return db_machine

@router.put("/{machine_id}", response_model=schemas.MachineResponse)
async def update_machine(
    machine_id: uuid.UUID,
    machine_update: schemas.MachineUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin"]))
):
    """
    Update an existing machine.
    - Oraseas Admin: Can update any machine.
    - Customer Admin: Can only update machines belonging to their own organization.
    """
    db_machine = machines.get_machine(db, machine_id) # This crud function is synchronous, no await needed here.
    if not db_machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    if current_user.role == "Oraseas Admin":
        pass # Oraseas Admin has full access
    elif current_user.role == "Customer Admin" and db_machine.organization_id == current_user.organization_id:
        # Customer Admin can update their own organization's machines, but cannot change the organization_id
        if machine_update.organization_id is not None and machine_update.organization_id != db_machine.organization_id:
            raise HTTPException(status_code=403, detail="Customer Admin cannot change a machine's organization.")
    else:
        raise HTTPException(status_code=403, detail="Not authorized to update this machine")

    updated_machine = machines.update_machine(db, machine_id, machine_update) # This crud function is synchronous, no await needed here.
    if not updated_machine: # Error handled in CRUD layer
        raise HTTPException(status_code=400, detail="Failed to update machine")
    return updated_machine

@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_machine(
    machine_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin"]))
):
    """
    Delete a machine by ID.
    - Oraseas Admin: Can delete any machine.
    - Customer Admin: Can only delete machines belonging to their own organization.
    """
    db_machine = machines.get_machine(db, machine_id) # This crud function is synchronous, no await needed here.
    if not db_machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    if current_user.role == "Oraseas Admin" or (
        current_user.role == "Customer Admin" and db_machine.organization_id == current_user.organization_id
    ):
        result = machines.delete_machine(db, machine_id) # This crud function is synchronous, no await needed here.
        if not result: # Error handled in CRUD layer
            raise HTTPException(status_code=400, detail="Failed to delete machine. Check for dependent records.")
        return result
    else:
        raise HTTPException(status_code=403, detail="Not authorized to delete this machine")

