# backend/app/routers/users.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, has_role, has_roles, TokenData # Import authentication dependencies

router = APIRouter()

def _check_update_user_permissions(user_to_update: models.User, user_update: schemas.UserUpdate, current_user: TokenData):
    """Helper to centralize complex permission checks for updating a user."""
    is_oraseas_admin = current_user.role == "Oraseas Admin"
    is_customer_admin_in_own_org = (
        current_user.role == "Customer Admin" and
        user_to_update.organization_id == current_user.organization_id
    )
    is_self_update = user_to_update.id == current_user.user_id

    if is_oraseas_admin:
        return # Oraseas Admin has full permissions

    if user_update.organization_id is not None and user_update.organization_id != user_to_update.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot change a user's organization.")
    
    if user_update.role is not None and user_update.role != user_to_update.role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot change a user's role.")

    if not (is_customer_admin_in_own_org or is_self_update):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")

def _check_create_user_permissions(user_to_create: schemas.UserCreate, organization: models.Organization, current_user: TokenData):
    """Helper to centralize permission checks for creating a user."""
    if not organization:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization ID not found")

    if current_user.role == "Customer Admin":
        if user_to_create.organization_id != current_user.organization_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer Admin can only create users within their own organization")
        if user_to_create.role not in ["Customer Admin", "Customer User"]:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer Admin can only create 'Customer Admin' or 'Customer User' roles.")

    if current_user.role == "Oraseas Admin":
        if user_to_create.role == "Oraseas Admin" and organization.type != "Warehouse":
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign 'Oraseas Admin' role to non-Warehouse organization user.")


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
    organization = crud.organizations.get_organization(db, user.organization_id)
    _check_create_user_permissions(user, organization, current_user)
    db_user = crud.users.create_user(db=db, user=user)
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

    _check_update_user_permissions(db_user, user_update, current_user)
    updated_user = crud.users.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=400, detail="Failed to update user")
    return updated_user

@router.patch("/{user_id}/deactivate", response_model=schemas.UserResponse)
async def deactivate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin"]))
):
    user_to_deactivate = crud.users.get_user(db, user_id)
    if not user_to_deactivate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.role == "Customer Admin" and user_to_deactivate.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to deactivate this user")

    return crud.users.set_user_active_status(db, user_id, False)

@router.patch("/{user_id}/reactivate", response_model=schemas.UserResponse)
async def reactivate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin"]))
):
    user_to_reactivate = crud.users.get_user(db, user_id)
    if not user_to_reactivate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.role == "Customer Admin" and user_to_reactivate.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to reactivate this user")

    return crud.users.set_user_active_status(db, user_id, True)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("Oraseas Admin"))
):
    result = crud.users.delete_user(db, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found or could not be deleted")
    return # A 204 response should not have a body.
