# backend/app/routers/organizations.py

import uuid
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

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
    for_orders: bool = Query(False, description="Include organizations needed for order creation"),
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
        if for_orders:
            # For order forms, allow broader access to necessary organizations
            if not permission_checker.is_super_admin(current_user):
                # Get user's organization to check type
                user_org = db.query(models.Organization).filter(models.Organization.id == current_user.organization_id).first()
                
                if user_org and user_org.organization_type == models.OrganizationType.oraseas_ee:
                    # Oraseas EE users can see:
                    # 1. Their own organization (Oraseas EE)
                    # 2. Supplier organizations (for supplier orders)
                    # 3. Customer organizations (for customer orders)
                    query = query.filter(
                        or_(
                            models.Organization.id == current_user.organization_id,  # Own organization
                            models.Organization.organization_type == models.OrganizationType.supplier,  # Suppliers
                            models.Organization.organization_type == models.OrganizationType.customer  # Customers
                        )
                    )
                else:
                    # Customer users can see:
                    # 1. Their own organization
                    # 2. Oraseas EE (needed for customer orders)
                    query = query.filter(
                        or_(
                            models.Organization.id == current_user.organization_id,  # Own organization
                            models.Organization.organization_type == models.OrganizationType.oraseas_ee  # Oraseas EE
                        )
                    )
        else:
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

@router.get("/hierarchy", response_model=List[schemas.OrganizationHierarchyNode])
async def get_organization_hierarchy_tree(
    include_inactive: bool = Query(False, description="Include inactive organizations"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORGANIZATION, PermissionType.READ))
):
    """Get the complete organization hierarchy as a nested tree structure."""
    try:
        # Validate query parameters
        if not isinstance(include_inactive, bool):
            raise HTTPException(
                status_code=422, 
                detail="Invalid value for include_inactive parameter. Must be true or false."
            )
        
        # Build base query for organizations
        query = db.query(models.Organization)
        
        # Apply organization-scoped filtering
        query = OrganizationScopedQueries.filter_organizations(query, current_user)
        
        # Apply inactive filter
        if not include_inactive:
            query = query.filter(models.Organization.is_active == True)
        
        # Get all accessible organizations
        accessible_orgs = query.all()
        
        # Extract IDs for the CRUD function
        accessible_org_ids = {org.id for org in accessible_orgs}
        
        # Get the hierarchy tree using the CRUD function
        hierarchy_tree = crud.organizations.get_organization_hierarchy_tree(
            db=db,
            include_inactive=include_inactive,
            accessible_org_ids=accessible_org_ids
        )
        
        # Return empty array with 200 status when no organizations exist
        return hierarchy_tree if hierarchy_tree else []
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors, permission errors)
        raise
    except PermissionError as e:
        # Handle permission-related errors
        raise HTTPException(status_code=403, detail=f"Permission denied: {str(e)}")
    except ValueError as e:
        # Handle validation errors from CRUD functions
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except Exception as e:
        # Handle database errors and other unexpected errors
        db.rollback()
        logging.error(f"Error retrieving organization hierarchy: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="Internal server error occurred while retrieving organization hierarchy"
        )

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
        
        # If validation failed, return HTTP 400 with the validation errors
        if not validation_result.get("valid", True):
            # Format errors for better display
            error_messages = []
            for error in validation_result.get("errors", []):
                error_messages.append(f"{error.get('field', 'Unknown')}: {error.get('message', 'Unknown error')}")
            
            raise HTTPException(
                status_code=400, 
                detail="; ".join(error_messages) if error_messages else "Validation failed"
            )
        
        return validation_result
    except HTTPException:
        # Re-raise HTTP exceptions (like the validation error above)
        raise
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

# --- Country Support ---
@router.get("/countries", response_model=List[str])
async def get_supported_countries(
    current_user: TokenData = Depends(require_permission(ResourceType.ORGANIZATION, PermissionType.READ))
):
    """Get list of supported countries for organization creation."""
    try:
        # Return the supported countries from the CountryEnum
        return [country.value for country in schemas.CountryEnum]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve supported countries")

# --- Default Organization Management ---
@router.post("/initialize-defaults", response_model=dict)
async def initialize_default_organizations(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_super_admin())
):
    """Initialize default organizations (Oraseas EE and BossAqua) if they don't exist."""
    try:
        result = crud.organizations.initialize_default_organizations(db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to initialize default organizations")

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
        # Log the actual error for debugging
        import logging
        logging.error(f"Error deleting organization {org_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete organization: {str(e)}")



# --- Organization-Specific Supplier Management ---
@router.get("/{org_id}/suppliers", response_model=List[schemas.OrganizationResponse])
async def get_organization_suppliers(
    org_id: uuid.UUID,
    include_inactive: bool = Query(False, description="Include inactive suppliers"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORGANIZATION, PermissionType.READ))
):
    """Get all suppliers belonging to a specific organization."""
    try:
        # Check if parent organization exists
        parent_org = crud.organizations.get_organization(db, org_id)
        if not parent_org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Check if user can access this organization
        if not check_organization_access(current_user, org_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to view this organization's suppliers")
        
        suppliers = crud.organizations.get_organization_suppliers(db, org_id, include_inactive)
        return suppliers
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{org_id}/activate", response_model=schemas.OrganizationResponse)
async def toggle_organization_active_status(
    org_id: uuid.UUID,
    activate: bool = Query(..., description="True to activate, False to deactivate"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORGANIZATION, PermissionType.WRITE))
):
    """Toggle the active status of an organization (primarily for suppliers)."""
    try:
        # Check if organization exists
        organization = crud.organizations.get_organization(db, org_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Check permissions - super admin can activate/deactivate any org, 
        # admin can only activate/deactivate suppliers under their organization
        if permission_checker.is_super_admin(current_user):
            # Super admin can activate/deactivate any organization
            pass
        elif permission_checker.is_admin(current_user):
            # Admin can only activate/deactivate suppliers under their organization
            if organization.organization_type != models.OrganizationType.supplier:
                raise HTTPException(status_code=403, detail="Admins can only activate/deactivate supplier organizations")
            if organization.parent_organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Not authorized to modify this supplier organization")
        else:
            raise HTTPException(status_code=403, detail="Not authorized to modify organization status")
        
        # Update the active status
        update_data = schemas.OrganizationUpdate(is_active=activate)
        updated_org = crud.organizations.update_organization(db, org_id, update_data)
        return updated_org
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update organization status")

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

