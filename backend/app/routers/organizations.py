# backend/app/routers/organizations.py

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import schemas, crud
from ..database import get_db
from ..auth import get_current_user, has_role, has_roles, TokenData
from .. import models
from ..models import OrganizationType
from ..permissions import (
    ResourceType, PermissionType, require_permission, require_super_admin, require_admin,
    OrganizationScopedQueries, check_organization_access, permission_checker
)

router = APIRouter()

# --- Enhanced Organizations CRUD ---
@router.get("/", response_model=List[schemas.OrganizationResponse])
async def get_organizations(
    organization_type: Optional[schemas.OrganizationTypeEnum] = Query(None, description="Filter by organization type"),
    include_inactive: bool = Query(False, description="Include inactive organizations"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORGANIZATION, PermissionType.READ))
):
    """Get all organizations with optional filtering by type."""
    try:
        # Get base query
        if organization_type:
            # Convert schema enum to model enum
            model_type = OrganizationType(organization_type.value)
            query = db.query(models.Organization).filter(models.Organization.organization_type == model_type)
        else:
            query = db.query(models.Organization)
        
        # Apply organization-scoped filtering
        query = OrganizationScopedQueries.filter_organizations(query, current_user)
        
        # Apply inactive filter
        if not include_inactive:
            query = query.filter(models.Organization.is_active == True)
        
        organizations = query.all()
        return organizations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/types", response_model=List[schemas.OrganizationTypeFilterResponse])
async def get_organizations_by_types(
    include_inactive: bool = Query(False, description="Include inactive organizations"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORGANIZATION, PermissionType.READ))
):
    """Get organizations grouped by type."""
    try:
        result = []
        for org_type in OrganizationType:
            # Get base query and apply organization-scoped filtering
            query = db.query(models.Organization).filter(models.Organization.organization_type == org_type)
            query = OrganizationScopedQueries.filter_organizations(query, current_user)
            
            if not include_inactive:
                query = query.filter(models.Organization.is_active == True)
            
            organizations = query.all()
            result.append({
                "organization_type": org_type.value,
                "organizations": organizations,
                "count": len(organizations)
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/hierarchy/roots", response_model=List[schemas.OrganizationResponse])
async def get_root_organizations(
    include_inactive: bool = Query(False, description="Include inactive organizations"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORGANIZATION, PermissionType.READ))
):
    """Get organizations that have no parent (root level)."""
    try:
        # Get base query for root organizations
        query = db.query(models.Organization).filter(models.Organization.parent_organization_id.is_(None))
        
        # Apply organization-scoped filtering
        query = OrganizationScopedQueries.filter_organizations(query, current_user)
        
        if not include_inactive:
            query = query.filter(models.Organization.is_active == True)
        
        organizations = query.all()
        return organizations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{org_id}/hierarchy", response_model=schemas.OrganizationHierarchyResponse)
async def get_organization_hierarchy(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORGANIZATION, PermissionType.READ))
):
    """Get the complete hierarchy starting from an organization."""
    try:
        # Check if user can access this organization
        if not check_organization_access(current_user, org_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to view this organization's hierarchy")
        
        hierarchy = crud.organizations.get_organization_hierarchy(db, org_id)
        if not hierarchy:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return hierarchy
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{org_id}/children", response_model=List[schemas.OrganizationResponse])
async def get_child_organizations(
    org_id: uuid.UUID,
    include_inactive: bool = Query(False, description="Include inactive organizations"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORGANIZATION, PermissionType.READ))
):
    """Get direct children of an organization."""
    try:
        # Check if parent organization exists
        parent_org = crud.organizations.get_organization(db, org_id)
        if not parent_org:
            raise HTTPException(status_code=404, detail="Parent organization not found")
        
        # Check if user can access this organization
        if not check_organization_access(current_user, org_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to view this organization's children")
        
        children = crud.organizations.get_child_organizations(db, org_id, include_inactive)
        return children
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/potential-parents", response_model=List[schemas.OrganizationResponse])
async def get_potential_parent_organizations(
    organization_type: schemas.OrganizationTypeEnum = Query(..., description="Organization type to get potential parents for"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORGANIZATION, PermissionType.READ))
):
    """Get organizations that can serve as parents for the given organization type."""
    try:
        # Convert schema enum to model enum
        model_type = OrganizationType(organization_type.value)
        
        # Get potential parents using CRUD function
        potential_parents = crud.organizations.get_potential_parent_organizations(db, model_type)
        
        # Apply organization-scoped filtering to ensure user can only see organizations they have access to
        filtered_parents = []
        for org in potential_parents:
            if check_organization_access(current_user, org.id, db):
                filtered_parents.append(org)
        
        return filtered_parents
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate", response_model=schemas.OrganizationValidationResponse)
async def validate_organization(
    validation_request: schemas.OrganizationValidationRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORGANIZATION, PermissionType.READ))
):
    """Validate organization data without persisting it."""
    try:
        # Call the CRUD validation function
        validation_result = crud.organizations.validate_organization_data(
            db, 
            validation_request.dict(exclude={'id'}), 
            validation_request.id
        )
        
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search", response_model=List[schemas.OrganizationResponse])
async def search_organizations(
    q: str = Query(..., min_length=1, description="Search query"),
    organization_type: Optional[schemas.OrganizationTypeEnum] = Query(None, description="Filter by organization type"),
    include_inactive: bool = Query(False, description="Include inactive organizations"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORGANIZATION, PermissionType.READ))
):
    """Search organizations by name with optional type filtering."""
    try:
        # Build base query with search
        query = db.query(models.Organization).filter(models.Organization.name.ilike(f"%{q}%"))
        
        # Apply type filter if specified
        if organization_type:
            model_type = OrganizationType(organization_type.value)
            query = query.filter(models.Organization.organization_type == model_type)
        
        # Apply organization-scoped filtering
        query = OrganizationScopedQueries.filter_organizations(query, current_user)
        
        # Apply inactive filter
        if not include_inactive:
            query = query.filter(models.Organization.is_active == True)
        
        organizations = query.all()
        return organizations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{org_id}", response_model=schemas.OrganizationResponse)
async def get_organization(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORGANIZATION, PermissionType.READ))
):
    """Get a single organization by ID."""
    try:
        organization = crud.organizations.get_organization(db, org_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Check if user can access this organization
        if not check_organization_access(current_user, org_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to view this organization's details")
        
        return organization
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=schemas.OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org: schemas.OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_super_admin())
):
    """Create a new organization with business rule validation."""
    try:
        db_organization = crud.organizations.create_organization(db, org)
        return db_organization
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create organization")

@router.put("/{org_id}", response_model=schemas.OrganizationResponse)
async def update_organization(
    org_id: uuid.UUID,
    org_update: schemas.OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORGANIZATION, PermissionType.WRITE))
):
    """Update an existing organization with business rule validation."""
    try:
        # Check if organization exists
        db_organization = crud.organizations.get_organization(db, org_id)
        if not db_organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Check permissions
        if permission_checker.is_super_admin(current_user) or (permission_checker.is_admin(current_user) and org_id == current_user.organization_id):
            updated_org = crud.organizations.update_organization(db, org_id, org_update)
            return updated_org
        else:
            raise HTTPException(status_code=403, detail="Not authorized to update this organization")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update organization")

@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_super_admin())
):
    """Delete (deactivate) an organization."""
    try:
        result = crud.organizations.delete_organization(db, org_id)
        if not result:
            raise HTTPException(status_code=404, detail="Organization not found")
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete organization")

# --- Supplier-Parent Relationship Management ---
@router.post("/{org_id}/suppliers", response_model=schemas.OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier_organization(
    org_id: uuid.UUID,
    supplier_data: schemas.OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["super_admin", "admin"]))
):
    """Create a supplier organization under a parent organization."""
    try:
        # Verify parent organization exists
        parent_org = crud.organizations.get_organization(db, org_id)
        if not parent_org:
            raise HTTPException(status_code=404, detail="Parent organization not found")
        
        # Check permissions
        if current_user.role == "super_admin" or (current_user.role == "admin" and org_id == current_user.organization_id):
            # Force supplier type and set parent
            supplier_data.organization_type = schemas.OrganizationTypeEnum.SUPPLIER
            supplier_data.parent_organization_id = org_id
            
            supplier_org = crud.organizations.create_organization(db, supplier_data)
            return supplier_org
        else:
            raise HTTPException(status_code=403, detail="Not authorized to create suppliers for this organization")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create supplier organization")

