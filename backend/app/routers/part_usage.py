# backend/app/routers/part_usage.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, has_role, has_roles, TokenData # Import authentication dependencies

router = APIRouter()

# --- Part Usage CRUD ---
@router.get("/", response_model=List[schemas.PartUsageResponse])
async def get_part_usages(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    if current_user.role == "Oraseas Admin" or current_user.role == "Oraseas Inventory Manager":
        usages = crud.part_usage.get_part_usages(db)
    elif current_user.role in ["Customer Admin", "Customer User"]:
        usages = db.query(models.PartUsage).filter(models.PartUsage.customer_organization_id == current_user.organization_id).all()
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view part usages")
    return usages

@router.get("/{usage_id}", response_model=schemas.PartUsageResponse)
async def get_part_usage(
    usage_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    usage = crud.part_usage.get_part_usage(db, usage_id)
    if not usage:
        raise HTTPException(status_code=404, detail="Part usage record not found")

    if current_user.role in ["Oraseas Admin", "Oraseas Inventory Manager"] or \
       (current_user.role in ["Customer Admin", "Customer User"] and usage.customer_organization_id == current_user.organization_id):
        return usage
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this part usage record")

@router.post("/", response_model=schemas.PartUsageResponse, status_code=status.HTTP_201_CREATED)
async def create_part_usage(
    usage: schemas.PartUsageCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager", "Customer Admin", "Customer User"]))
):
    # Validate FKs
    customer_org = db.query(models.Organization).filter(models.Organization.id == usage.customer_organization_id).first()
    part = db.query(models.Part).filter(models.Part.id == usage.part_id).first()
    if not customer_org:
        raise HTTPException(status_code=400, detail="Customer Organization ID not found")
    if not part:
        raise HTTPException(status_code=400, detail="Part ID not found")
    if usage.recorded_by_user_id:
        user = db.query(models.User).filter(models.User.id == usage.recorded_by_user_id).first()
        if not user: raise HTTPException(status_code=400, detail="Recorded by User ID not found")

    # Authorization: Oraseas roles can create usage for any customer, Customers can only create for their own org
    if current_user.role in ["Customer Admin", "Customer User"] and usage.customer_organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Customers can only record part usage for their own organization.")
    
    if current_user.role in ["Customer Admin", "Customer User"] and usage.recorded_by_user_id and usage.recorded_by_user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Customers can only record part usage as themselves.")

    db_usage = crud.part_usage.create_part_usage(db, usage)
    if not db_usage:
        raise HTTPException(status_code=400, detail="Failed to create part usage record")
    return db_usage

@router.put("/{usage_id}", response_model=schemas.PartUsageResponse)
async def update_part_usage(
    usage_id: uuid.UUID,
    usage_update: schemas.PartUsageUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager", "Customer Admin", "Customer User"]))
):
    db_usage = crud.part_usage.get_part_usage(db, usage_id)
    if not db_usage:
        raise HTTPException(status_code=404, detail="Part usage record not found")

    # Authorization: Oraseas roles can update any, Customers can only update their own org's usage
    if current_user.role in ["Oraseas Admin", "Oraseas Inventory Manager"] or \
       (current_user.role in ["Customer Admin", "Customer User"] and db_usage.customer_organization_id == current_user.organization_id):
        
        # Prevent customers from changing key IDs or recorded user
        if current_user.role in ["Customer Admin", "Customer User"]:
            if usage_update.customer_organization_id is not None and usage_update.customer_organization_id != db_usage.customer_organization_id:
                raise HTTPException(status_code=403, detail="Cannot change customer organization ID for part usage.")
            if usage_update.part_id is not None and usage_update.part_id != db_usage.part_id:
                raise HTTPException(status_code=403, detail="Cannot change part ID for part usage.")
            if usage_update.recorded_by_user_id is not None and usage_update.recorded_by_user_id != db_usage.recorded_by_user_id:
                raise HTTPException(status_code=403, detail="Cannot change recorded by user for part usage.")

        updated_usage = crud.part_usage.update_part_usage(db, usage_id, usage_update)
        if not updated_usage:
            raise HTTPException(status_code=400, detail="Failed to update part usage record")
        return updated_usage
    else:
        raise HTTPException(status_code=403, detail="Not authorized to update this part usage record")

@router.delete("/{usage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_part_usage(
    usage_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin"])) # Only Admins can delete usage records
):
    db_usage = crud.part_usage.get_part_usage(db, usage_id)
    if not db_usage:
        raise HTTPException(status_code=404, detail="Part usage record not found")
    
    # Authorization: Oraseas Admin can delete any, Customer Admin can only delete their own org's usage
    if current_user.role == "Oraseas Admin" or \
       (current_user.role == "Customer Admin" and db_usage.customer_organization_id == current_user.organization_id):
        result = crud.part_usage.delete_part_usage(db, usage_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to delete part usage record")
        return result
    else:
        raise HTTPException(status_code=403, detail="Not authorized to delete this part usage record")
