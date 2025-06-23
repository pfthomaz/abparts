# backend/app/routers/users.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, has_role, has_roles, TokenData # Import authentication dependencies

router = APIRouter()

# --- Users CRUD ---
@router.get("/", response_model=List[schemas.UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("Oraseas Admin")) # Only Oraseas Admin can list all users
):
    users = crud.users.get_users(db)
    return users

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    user = crud.users.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.role == "Oraseas Admin" or user_id == current_user.user_id:
        return user
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this user's details")

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin"])) # Admin roles can create users
):
    organization = db.query(models.Organization).filter(models.Organization.id == user.organization_id).first()
    if not organization:
        raise HTTPException(status_code=400, detail="Organization ID not found")

    if current_user.role == "Customer Admin" and user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Customer Admin can only create users within their own organization")
    
    if current_user.role == "Oraseas Admin":
        if user.role == "Oraseas Admin" and organization.type != "Warehouse":
             raise HTTPException(status_code=400, detail="Cannot assign 'Oraseas Admin' role to non-Warehouse organization user.")

    db_user = crud.users.create_user(db, user)
    if not db_user:
        raise HTTPException(status_code=400, detail="Failed to create user")
    return db_user

@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin", "Customer User"]))
):
    db_user = crud.users.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role == "Oraseas Admin":
        pass
    elif current_user.role == "Customer Admin" and db_user.organization_id == current_user.organization_id:
        if user_update.organization_id is not None and user_update.organization_id != db_user.organization_id:
            raise HTTPException(status_code=403, detail="Customer Admin cannot change user's organization.")
        if user_update.role is not None and user_update.role != db_user.role:
            raise HTTPException(status_code=403, detail="Customer Admin cannot change user's role.")
    elif user_id == current_user.user_id:
        if user_update.organization_id is not None and user_update.organization_id != db_user.organization_id:
            raise HTTPException(status_code=403, detail="You cannot change your organization.")
        if user_update.role is not None and user_update.role != db_user.role:
            raise HTTPException(status_code=403, detail="You cannot change your own role.")
    else:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    updated_user = crud.users.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=400, detail="Failed to update user")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("Oraseas Admin"))
):
    result = crud.users.delete_user(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found or could not be deleted")
    return result

