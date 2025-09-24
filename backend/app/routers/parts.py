# backend/app/routers/parts.py

import uuid
from typing import List, Optional
import os
import shutil # For saving files
import time
import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Response # Added: Query, Response
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, TokenData # Import authentication dependencies
from ..permissions import (
    ResourceType, PermissionType, require_permission, require_super_admin,
    OrganizationScopedQueries, check_organization_access, permission_checker
)
from ..performance_monitoring import monitor_api_performance
from datetime import datetime, timedelta

# Set up logging for performance monitoring
logger = logging.getLogger(__name__)

router = APIRouter()

# Define the directory where uploaded images will be stored
# IMPORTANT: In a production environment, this should be a cloud storage service like AWS S3.
# For local Docker, this path needs to be accessible/writable.
UPLOAD_DIRECTORY = "/app/static/images" # This path inside the container

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


# --- Image Upload Endpoint ---
@router.post("/upload-image", response_model=schemas.ImageUploadResponse, tags=["Images"]) # Define a new schema for this response
async def upload_image(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(require_super_admin()) # Only super admins can upload images
):
    """
    Uploads an image file and returns its URL.
    This is a temporary local storage solution for development.
    In production, files should be stored on a cloud storage service (e.g., AWS S3).
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (10MB limit)
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 10MB")
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
        
        # Generate a unique filename
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIRECTORY, filename)

        # Save the file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Construct the URL (assuming /static/images is served)
        # This assumes your FastAPI app serves static files from /static
        image_url = f"/static/images/{filename}"
        return {"url": image_url}
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail=f"Could not upload file: {str(e)}")

# --- Parts CRUD ---
@router.get("/", response_model=schemas.PartsListResponse)
@monitor_api_performance("api.get_parts")
async def get_parts(
    part_type: Optional[str] = Query(None, description="Filter by part type (consumable or bulk_material)"),
    is_proprietary: Optional[bool] = Query(None, description="Filter by proprietary status"),
    search: Optional[str] = Query(None, description="Search in multilingual part names, part numbers, and descriptions"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    include_count: bool = Query(False, description="Include total count of matching records (may impact performance)"),
    response: Response = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.PART, PermissionType.READ))
):
    """
    Get all parts with optional filtering by type, origin, and multilingual name search.
    All authenticated users can view parts.
    Enhanced with multilingual name search capabilities and optional result counting.
    """
    if search:
        # Use search functionality if search term provided
        result = crud.parts.search_parts_multilingual_with_count(
            db, search_term=search, part_type=part_type, is_proprietary=is_proprietary, 
            skip=skip, limit=limit, include_count=include_count
        )
    else:
        # Use regular filtering if no search term
        result = crud.parts.get_filtered_parts_with_count(
            db, part_type=part_type, is_proprietary=is_proprietary, 
            skip=skip, limit=limit, include_count=include_count
        )
    
    # Add caching headers for frequently accessed parts data
    if not search and not part_type and not is_proprietary and skip == 0:
        # Cache general parts list for 5 minutes
        response.headers["Cache-Control"] = "public, max-age=300"
        response.headers["ETag"] = f"parts-{hash(str(result['items']))}"
    elif search or part_type or is_proprietary:
        # Cache filtered results for 2 minutes
        response.headers["Cache-Control"] = "public, max-age=120"
    
    return result

@router.get("/search", response_model=schemas.PartsListResponse)
@monitor_api_performance("api.search_parts")
async def search_parts(
    q: str = Query(..., min_length=1, description="Search query for multilingual part names, part numbers, descriptions, manufacturers, and part codes"),
    part_type: Optional[str] = Query(None, description="Filter by part type (consumable or bulk_material)"),
    is_proprietary: Optional[bool] = Query(None, description="Filter by proprietary status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    include_count: bool = Query(False, description="Include total count of matching records (may impact performance)"),
    response: Response = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.PART, PermissionType.READ))
):
    """
    Enhanced search for parts with multilingual name support.
    Searches across multilingual names, part numbers, descriptions, manufacturers, and part codes.
    All authenticated users can search parts.
    """
    result = crud.parts.search_parts_multilingual_with_count(
        db, search_term=q, part_type=part_type, is_proprietary=is_proprietary, 
        skip=skip, limit=limit, include_count=include_count
    )
    
    # Add caching headers for search results (shorter cache time due to dynamic nature)
    response.headers["Cache-Control"] = "public, max-age=60"
    
    return result

# --- Parts Inventory Integration Endpoints (must be before /{part_id}) ---

@router.get("/with-inventory", response_model=schemas.PartsWithInventoryListResponse)
@monitor_api_performance("api.get_parts_with_inventory")
async def get_parts_with_inventory(
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter inventory by organization ID"),
    part_type: Optional[str] = Query(None, description="Filter by part type (consumable or bulk_material)"),
    is_proprietary: Optional[bool] = Query(None, description="Filter by proprietary status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    include_count: bool = Query(False, description="Include total count of matching records (may impact performance)"),
    response: Response = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.PART, PermissionType.READ))
):
    """
    Get all parts with inventory information across all warehouses.
    If organization_id is provided, only inventory from that organization's warehouses is included.
    Otherwise, for regular users, only inventory from their organization's warehouses is shown.
    Super admins see all inventory across all organizations if no organization_id is specified.
    """
    # If organization_id is not provided, use the current user's organization
    # unless the user is a super_admin
    if not organization_id and not permission_checker.is_super_admin(current_user):
        organization_id = current_user.organization_id
    
    # Check organization access if organization_id is provided
    if organization_id and not check_organization_access(current_user, organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this organization's inventory")
    
    result = crud.parts.get_parts_with_inventory_with_count(
        db, organization_id, part_type, is_proprietary, skip, limit, include_count
    )
    
    # Add caching headers for inventory data (shorter cache due to dynamic nature)
    response.headers["Cache-Control"] = "public, max-age=180"
    
    return result

@router.get("/search-with-inventory", response_model=schemas.PartsWithInventoryListResponse)
@monitor_api_performance("api.search_parts_with_inventory")
async def search_parts_with_inventory(
    q: str = Query(..., min_length=1, description="Search query for part name or part number"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter inventory by organization ID"),
    part_type: Optional[str] = Query(None, description="Filter by part type (consumable or bulk_material)"),
    is_proprietary: Optional[bool] = Query(None, description="Filter by proprietary status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    include_count: bool = Query(False, description="Include total count of matching records (may impact performance)"),
    response: Response = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.PART, PermissionType.READ))
):
    """
    Search parts by name or part number with inventory context.
    If organization_id is provided, only inventory from that organization's warehouses is included.
    Otherwise, for regular users, only inventory from their organization's warehouses is shown.
    Super admins see all inventory across all organizations if no organization_id is specified.
    """
    # If organization_id is not provided, use the current user's organization
    # unless the user is a super_admin
    if not organization_id and not permission_checker.is_super_admin(current_user):
        organization_id = current_user.organization_id
    
    # Check organization access if organization_id is provided
    if organization_id and not check_organization_access(current_user, organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this organization's inventory")
    
    result = crud.parts.search_parts_with_inventory_with_count(
        db, q, organization_id, part_type, is_proprietary, skip, limit, include_count
    )
    
    # Add caching headers for search with inventory results (shorter cache due to dynamic nature)
    response.headers["Cache-Control"] = "public, max-age=90"
    
    return result

@router.get("/{part_id}", response_model=schemas.PartResponse)
@monitor_api_performance("api.get_part")
async def get_part(
    part_id: uuid.UUID,
    response: Response = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.PART, PermissionType.READ))
):
    """Get a single part by ID. All authenticated users can view parts."""
    part = crud.parts.get_part_with_monitoring(db, part_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    # Add caching headers for individual part data (longer cache for static data)
    response.headers["Cache-Control"] = "public, max-age=600"
    response.headers["ETag"] = f"part-{part_id}-{hash(str(part.__dict__))}"
    
    return part

@router.post("/", response_model=schemas.PartResponse, status_code=status.HTTP_201_CREATED)
@monitor_api_performance("api.create_part")
async def create_part(
    part: schemas.PartCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_super_admin())
):
    """
    Create a new part with enhanced validation for multilingual names and new fields.
    Only super admins can create parts.
    Enhanced with multilingual name validation and new field support.
    """
    # Validate multilingual name format
    if not crud.parts.validate_multilingual_name(part.name):
        raise HTTPException(
            status_code=400, 
            detail="Invalid multilingual name format. Use format: 'English Name|Greek Name GR|Spanish Name ES' or single language."
        )
    
    # Note: Image URL limit validation is handled by Pydantic schema (max_items=4)
    # This provides automatic validation with 422 status code
    
    db_part = crud.parts.create_part_enhanced(db, part)
    if not db_part:
        raise HTTPException(status_code=400, detail="Failed to create part")
    return db_part

@router.put("/{part_id}", response_model=schemas.PartResponse)
@monitor_api_performance("api.update_part")
async def update_part(
    part_id: uuid.UUID,
    part_update: schemas.PartUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_super_admin())
):
    """
    Update an existing part with enhanced validation for multilingual names and new fields.
    Only super admins can update parts.
    Enhanced with multilingual name validation and new field support.
    """
    # Validate multilingual name format if name is being updated
    if part_update.name and not crud.parts.validate_multilingual_name(part_update.name):
        raise HTTPException(
            status_code=400, 
            detail="Invalid multilingual name format. Use format: 'English Name|Greek Name GR|Spanish Name ES' or single language."
        )
    
    # Note: Image URL limit validation is handled by Pydantic schema (max_items=4)
    # This provides automatic validation with 422 status code
    
    updated_part = crud.parts.update_part_enhanced(db, part_id, part_update)
    if not updated_part:
        raise HTTPException(status_code=404, detail="Part not found")
    return updated_part

@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
@monitor_api_performance("api.delete_part")
async def delete_part(
    part_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_super_admin())
):
    """
    Delete a part (soft delete/inactivate).
    Only super admins can delete parts.
    Enhanced with proper superadmin-only access control.
    """
    result = crud.parts.delete_part_enhanced(db, part_id)
    if not result:
        raise HTTPException(status_code=404, detail="Part not found or could not be deleted")
    return result

@router.get("/types", response_model=List[str])
async def get_part_types(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.PART, PermissionType.READ))
):
    """
    Get all available part types.
    All authenticated users can view part types.
    """
    # Return the enum values as strings
    return [part_type.value for part_type in models.PartType]

@router.get("/by-type/{part_type}", response_model=schemas.PartsListResponse)
@monitor_api_performance("api.get_parts_by_type")
async def get_parts_by_type(
    part_type: str,
    is_proprietary: Optional[bool] = Query(None, description="Filter by proprietary status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    include_count: bool = Query(False, description="Include total count of matching records (may impact performance)"),
    response: Response = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.PART, PermissionType.READ))
):
    """
    Get parts filtered by type (consumable or bulk_material).
    All authenticated users can view parts.
    """
    # Validate part_type
    try:
        models.PartType(part_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid part type: {part_type}. Valid types are: {[t.value for t in models.PartType]}")
    
    result = crud.parts.get_filtered_parts_with_count(
        db, part_type=part_type, is_proprietary=is_proprietary, 
        skip=skip, limit=limit, include_count=include_count
    )
    
    # Add caching headers for type-filtered results
    response.headers["Cache-Control"] = "public, max-age=240"
    
    return result

@router.get("/with-inventory/{part_id}", response_model=schemas.PartWithInventoryResponse)
async def get_part_with_inventory(
    part_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter inventory by organization ID"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.PART, PermissionType.READ))
):
    """
    Get a single part with inventory information across all warehouses.
    If organization_id is provided, only inventory from that organization's warehouses is included.
    Otherwise, for regular users, only inventory from their organization's warehouses is shown.
    Super admins see all inventory across all organizations if no organization_id is specified.
    """
    # If organization_id is not provided, use the current user's organization
    # unless the user is a super_admin
    if not organization_id and not permission_checker.is_super_admin(current_user):
        organization_id = current_user.organization_id
    
    # Check organization access if organization_id is provided
    if organization_id and not check_organization_access(current_user, organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this organization's inventory")
    
    part = crud.parts.get_part_with_inventory(db, part_id, organization_id)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    return part

@router.get("/with-usage/{part_id}", response_model=schemas.PartWithUsageResponse)
async def get_part_with_usage_history(
    part_id: uuid.UUID,
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    days: int = Query(90, ge=1, le=365, description="Number of days to look back for usage history"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.PART, PermissionType.READ))
):
    """
    Get a part with inventory information and usage history.
    If organization_id is provided, only data from that organization is included.
    Otherwise, for regular users, only data from their organization is shown.
    Super admins see all data across all organizations if no organization_id is specified.
    """
    # If organization_id is not provided, use the current user's organization
    # unless the user is a super_admin
    if not organization_id and not permission_checker.is_super_admin(current_user):
        organization_id = current_user.organization_id
    
    # Check organization access if organization_id is provided
    if organization_id and not check_organization_access(current_user, organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this organization's data")
    
    part = crud.parts.get_part_with_usage_history(db, part_id, organization_id, days)
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    
    return part

@router.get("/reorder-suggestions", response_model=List[schemas.PartReorderSuggestion])
async def get_parts_reorder_suggestions(
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    threshold_days: int = Query(30, ge=1, le=90, description="Threshold for days of stock remaining"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of suggestions to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.PART, PermissionType.READ))
):
    """
    Get reorder suggestions for parts based on usage patterns.
    If organization_id is provided, only data from that organization is included.
    Otherwise, for regular users, only data from their organization is shown.
    Super admins see all data across all organizations if no organization_id is specified.
    """
    # If organization_id is not provided, use the current user's organization
    # unless the user is a super_admin
    if not organization_id and not permission_checker.is_super_admin(current_user):
        organization_id = current_user.organization_id
    
    # Check organization access if organization_id is provided
    if organization_id and not check_organization_access(current_user, organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this organization's data")
    
    suggestions = crud.parts.get_parts_reorder_suggestions(db, organization_id, threshold_days, limit)
    return suggestions

