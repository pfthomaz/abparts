# backend/app/routers/nets.py

import uuid
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user, TokenData
from ..schemas.net_cleaning import (
    NetCreate, NetUpdate, NetResponse, NetWithCleaningHistory
)
from ..crud import nets as crud_nets
from ..crud import farm_sites as crud_farm_sites

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[NetResponse])
async def get_nets(
    farm_site_id: Optional[uuid.UUID] = Query(None, description="Filter by farm site ID"),
    active_only: bool = Query(True, description="Only return active nets"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all nets for the current user's organization."""
    try:
        organization_id = current_user.organization_id
        nets = crud_nets.get_nets(
            db, organization_id, farm_site_id, skip, limit, active_only
        )
        
        # Add cleaning stats to each net
        result = []
        for net in nets:
            net_data = crud_nets.get_net_with_cleaning_stats(db, net.id)
            net_dict = NetResponse.model_validate(net).model_dump()
            if net_data:
                net_dict['cleaning_records_count'] = net_data['cleaning_records_count']
                net_dict['last_cleaning_date'] = net_data['last_cleaning_date']
            result.append(net_dict)
        
        return result
    except Exception as e:
        logger.error(f"Error getting nets: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search", response_model=List[NetResponse])
async def search_nets(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Search nets by name."""
    try:
        organization_id = current_user.organization_id
        nets = crud_nets.search_nets(db, organization_id, q, skip, limit)
        return nets
    except Exception as e:
        logger.error(f"Error searching nets: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{net_id}", response_model=NetWithCleaningHistory)
async def get_net(
    net_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get a single net by ID with its cleaning history."""
    net = crud_nets.get_net(db, net_id)
    if not net:
        raise HTTPException(status_code=404, detail="Net not found")
    
    # Permission check: verify net belongs to user's organization
    farm_site = crud_farm_sites.get_farm_site(db, net.farm_site_id)
    if not farm_site:
        raise HTTPException(status_code=404, detail="Farm site not found")
    
    if current_user.role != "super_admin" and farm_site.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this net")
    
    return net


@router.post("/", response_model=NetResponse, status_code=status.HTTP_201_CREATED)
async def create_net(
    net: NetCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new net."""
    # Permission check: only admins and super_admins can create nets
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create nets"
        )
    
    # Verify farm site exists and belongs to user's organization
    farm_site = crud_farm_sites.get_farm_site(db, net.farm_site_id)
    if not farm_site:
        raise HTTPException(status_code=404, detail="Farm site not found")
    
    if current_user.role != "super_admin" and farm_site.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to create nets in this farm site")
    
    try:
        db_net = crud_nets.create_net(db, net)
        return db_net
    except Exception as e:
        logger.error(f"Error creating net: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{net_id}", response_model=NetResponse)
async def update_net(
    net_id: uuid.UUID,
    net_update: NetUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Update an existing net."""
    # Permission check: only admins and super_admins can update nets
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can update nets"
        )
    
    # Check net exists and belongs to user's organization
    existing_net = crud_nets.get_net(db, net_id)
    if not existing_net:
        raise HTTPException(status_code=404, detail="Net not found")
    
    farm_site = crud_farm_sites.get_farm_site(db, existing_net.farm_site_id)
    if not farm_site:
        raise HTTPException(status_code=404, detail="Farm site not found")
    
    if current_user.role != "super_admin" and farm_site.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this net")
    
    # If farm_site_id is being changed, verify new farm site
    if net_update.farm_site_id and net_update.farm_site_id != existing_net.farm_site_id:
        new_farm_site = crud_farm_sites.get_farm_site(db, net_update.farm_site_id)
        if not new_farm_site:
            raise HTTPException(status_code=404, detail="New farm site not found")
        
        if current_user.role != "super_admin" and new_farm_site.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to move net to this farm site")
    
    try:
        updated_net = crud_nets.update_net(db, net_id, net_update)
        if not updated_net:
            raise HTTPException(status_code=404, detail="Net not found")
        return updated_net
    except Exception as e:
        logger.error(f"Error updating net: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{net_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_net(
    net_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Soft delete a net (sets active=False)."""
    # Permission check: only admins and super_admins can delete nets
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can delete nets"
        )
    
    # Check net exists and belongs to user's organization
    existing_net = crud_nets.get_net(db, net_id)
    if not existing_net:
        raise HTTPException(status_code=404, detail="Net not found")
    
    farm_site = crud_farm_sites.get_farm_site(db, existing_net.farm_site_id)
    if not farm_site:
        raise HTTPException(status_code=404, detail="Farm site not found")
    
    if current_user.role != "super_admin" and farm_site.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this net")
    
    try:
        success = crud_nets.delete_net(db, net_id)
        if not success:
            raise HTTPException(status_code=404, detail="Net not found")
        return None
    except Exception as e:
        logger.error(f"Error deleting net: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
