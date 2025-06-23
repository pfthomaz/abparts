# backend/app/routers/organizations.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud # Import schemas and CRUD functions
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, has_role, has_roles, TokenData # Import authentication dependencies
from .. import models # Needed for fetching Oraseas ID for specific auth checks

router = APIRouter()

# --- Organizations CRUD ---
@router.get("/", response_model=List[schemas.OrganizationResponse])
async def get_organizations(
    db: Session = Depends(get_db),
    # current_user: TokenData = Depends(get_current_user) # Temporarily removed for public access during development
):
    # If current_user was present, the logic would be:
    # if current_user.role == "Oraseas Admin":
    #     organizations = crud.organizations.get_organizations(db)
    # elif current_user.role in ["Customer Admin", "Customer User", "Supplier User"]:
    #     organizations = [crud.organizations.get_organization(db, current_user.organization_id)]
    #     if organizations[0] is None:
    #         raise HTTPException(status_code=404, detail="User's organization not found")
    # else:
    #     raise HTTPException(status_code=403, detail="Not authorized to view organizations")

    # For now, allow everyone to see all organizations for frontend testing
    organizations = crud.organizations.get_organizations(db)
    return organizations

@router.get("/{org_id}", response_model=schemas.OrganizationResponse)
async def get_organization(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    organization = crud.organizations.get_organization(db, org_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    if current_user.role == "Oraseas Admin" or org_id == current_user.organization_id:
        return organization
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this organization's details")

@router.post("/", response_model=schemas.OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org: schemas.OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("Oraseas Admin"))
):
    db_organization = crud.organizations.create_organization(db, org)
    if not db_organization:
        raise HTTPException(status_code=400, detail="Failed to create organization") # Error handled in CRUD
    return db_organization

@router.put("/{org_id}", response_model=schemas.OrganizationResponse)
async def update_organization(
    org_id: uuid.UUID,
    org_update: schemas.OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin"]))
):
    db_organization = crud.organizations.get_organization(db, org_id)
    if not db_organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    if current_user.role == "Oraseas Admin" or (current_user.role == "Customer Admin" and org_id == current_user.organization_id):
        updated_org = crud.organizations.update_organization(db, org_id, org_update)
        if not updated_org: # Error handled in CRUD layer
            raise HTTPException(status_code=400, detail="Failed to update organization")
        return updated_org
    else:
        raise HTTPException(status_code=403, detail="Not authorized to update this organization")

@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("Oraseas Admin"))
):
    result = crud.organizations.delete_organization(db, org_id)
    if not result: # Error handled in CRUD layer
        raise HTTPException(status_code=404, detail="Organization not found or could not be deleted")
    return result

