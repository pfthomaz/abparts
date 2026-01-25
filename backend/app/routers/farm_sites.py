# backend/app/routers/farm_sites.py

import uuid
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user, TokenData
from ..schemas.net_cleaning import (
    FarmSiteCreate, FarmSiteUpdate, FarmSiteResponse, FarmSiteWithNets
)
from ..crud import farm_sites as crud_farm_sites

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[FarmSiteResponse])
async def get_farm_sites(
    active_only: bool = Query(True, description="Only return active farm sites"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all farm sites for the current user's organization."""
    try:
        organization_id = current_user.organization_id
        farm_sites = crud_farm_sites.get_farm_sites(
            db, organization_id, skip, limit, active_only
        )
        
        # Add nets count to each farm site
        result = []
        for site in farm_sites:
            site_data = crud_farm_sites.get_farm_site_with_nets_count(db, site.id)
            site_dict = FarmSiteResponse.model_validate(site).model_dump()
            site_dict['nets_count'] = site_data['nets_count'] if site_data else 0
            result.append(site_dict)
        
        return result
    except Exception as e:
        logger.error(f"Error getting farm sites: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search", response_model=List[FarmSiteResponse])
async def search_farm_sites(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Search farm sites by name or location."""
    try:
        organization_id = current_user.organization_id
        farm_sites = crud_farm_sites.search_farm_sites(
            db, organization_id, q, skip, limit
        )
        return farm_sites
    except Exception as e:
        logger.error(f"Error searching farm sites: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{farm_site_id}", response_model=FarmSiteWithNets)
async def get_farm_site(
    farm_site_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get a single farm site by ID with its nets."""
    farm_site = crud_farm_sites.get_farm_site(db, farm_site_id)
    if not farm_site:
        raise HTTPException(status_code=404, detail="Farm site not found")
    
    # Permission check: users can only access farm sites from their organization
    if current_user.role != "super_admin" and farm_site.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this farm site")
    
    return farm_site


@router.post("/", response_model=FarmSiteResponse, status_code=status.HTTP_201_CREATED)
async def create_farm_site(
    farm_site: FarmSiteCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new farm site."""
    # Permission check: only admins and super_admins can create farm sites
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create farm sites"
        )
    
    try:
        organization_id = current_user.organization_id
        db_farm_site = crud_farm_sites.create_farm_site(db, farm_site, organization_id)
        return db_farm_site
    except Exception as e:
        logger.error(f"Error creating farm site: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{farm_site_id}", response_model=FarmSiteResponse)
async def update_farm_site(
    farm_site_id: uuid.UUID,
    farm_site_update: FarmSiteUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Update an existing farm site."""
    # Permission check: only admins and super_admins can update farm sites
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can update farm sites"
        )
    
    # Check farm site exists and belongs to user's organization
    existing_site = crud_farm_sites.get_farm_site(db, farm_site_id)
    if not existing_site:
        raise HTTPException(status_code=404, detail="Farm site not found")
    
    if current_user.role != "super_admin" and existing_site.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this farm site")
    
    try:
        updated_site = crud_farm_sites.update_farm_site(db, farm_site_id, farm_site_update)
        if not updated_site:
            raise HTTPException(status_code=404, detail="Farm site not found")
        return updated_site
    except Exception as e:
        logger.error(f"Error updating farm site: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{farm_site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farm_site(
    farm_site_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Soft delete a farm site (sets active=False)."""
    # Permission check: only admins and super_admins can delete farm sites
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can delete farm sites"
        )
    
    # Check farm site exists and belongs to user's organization
    existing_site = crud_farm_sites.get_farm_site(db, farm_site_id)
    if not existing_site:
        raise HTTPException(status_code=404, detail="Farm site not found")
    
    if current_user.role != "super_admin" and existing_site.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this farm site")
    
    try:
        success = crud_farm_sites.delete_farm_site(db, farm_site_id)
        if not success:
            raise HTTPException(status_code=404, detail="Farm site not found")
        return None
    except Exception as e:
        logger.error(f"Error deleting farm site: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
