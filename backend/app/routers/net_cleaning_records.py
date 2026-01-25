# backend/app/routers/net_cleaning_records.py

import uuid
import logging
from typing import List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import get_current_user, TokenData
from ..schemas.net_cleaning import (
    NetCleaningRecordCreate, NetCleaningRecordUpdate,
    NetCleaningRecordResponse, NetCleaningRecordWithDetails,
    NetCleaningStats
)
from ..crud import net_cleaning_records as crud_records
from ..crud import nets as crud_nets
from ..crud import farm_sites as crud_farm_sites

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[NetCleaningRecordResponse])
async def get_cleaning_records(
    net_id: Optional[uuid.UUID] = Query(None, description="Filter by net ID"),
    farm_site_id: Optional[uuid.UUID] = Query(None, description="Filter by farm site ID"),
    machine_id: Optional[uuid.UUID] = Query(None, description="Filter by machine ID"),
    operator_name: Optional[str] = Query(None, description="Filter by operator name"),
    start_date: Optional[date] = Query(None, description="Filter by start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (exclusive)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get cleaning records with various filters."""
    try:
        organization_id = current_user.organization_id
        records = crud_records.get_cleaning_records(
            db, organization_id, net_id, farm_site_id, machine_id,
            operator_name, start_date, end_date, skip, limit
        )
        return records
    except Exception as e:
        logger.error(f"Error getting cleaning records: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats", response_model=NetCleaningStats)
async def get_cleaning_statistics(
    start_date: Optional[date] = Query(None, description="Start date for statistics"),
    end_date: Optional[date] = Query(None, description="End date for statistics"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get cleaning statistics for the organization."""
    try:
        organization_id = current_user.organization_id
        stats = crud_records.get_cleaning_statistics(
            db, organization_id, start_date, end_date
        )
        return stats
    except Exception as e:
        logger.error(f"Error getting cleaning statistics: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recent", response_model=List[NetCleaningRecordResponse])
async def get_recent_cleaning_records(
    limit: int = Query(10, ge=1, le=100, description="Number of recent records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get most recent cleaning records."""
    try:
        organization_id = current_user.organization_id
        records = crud_records.get_recent_cleaning_records(db, organization_id, limit)
        return records
    except Exception as e:
        logger.error(f"Error getting recent cleaning records: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{record_id}", response_model=NetCleaningRecordWithDetails)
async def get_cleaning_record(
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get a single cleaning record by ID with details."""
    record_data = crud_records.get_cleaning_record_with_details(db, record_id)
    if not record_data:
        raise HTTPException(status_code=404, detail="Cleaning record not found")
    
    record = record_data['record']
    
    # Permission check: verify record belongs to user's organization
    net = crud_nets.get_net(db, record.net_id)
    if not net:
        raise HTTPException(status_code=404, detail="Net not found")
    
    farm_site = crud_farm_sites.get_farm_site(db, net.farm_site_id)
    if not farm_site:
        raise HTTPException(status_code=404, detail="Farm site not found")
    
    if current_user.role != "super_admin" and farm_site.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this cleaning record")
    
    # Build response with details
    response = NetCleaningRecordWithDetails.model_validate(record)
    response_dict = response.model_dump()
    response_dict['net_name'] = record_data['net_name']
    response_dict['farm_site_name'] = record_data['farm_site_name']
    response_dict['machine_name'] = record_data['machine_name']
    response_dict['created_by_username'] = record_data['created_by_username']
    
    return response_dict


@router.post("/", response_model=NetCleaningRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_cleaning_record(
    record: NetCleaningRecordCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new cleaning record."""
    # Verify net exists and belongs to user's organization
    net = crud_nets.get_net(db, record.net_id)
    if not net:
        raise HTTPException(status_code=404, detail="Net not found")
    
    farm_site = crud_farm_sites.get_farm_site(db, net.farm_site_id)
    if not farm_site:
        raise HTTPException(status_code=404, detail="Farm site not found")
    
    if current_user.role != "super_admin" and farm_site.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to create cleaning records for this net")
    
    try:
        db_record = crud_records.create_cleaning_record(db, record, current_user.user_id)
        return db_record
    except ValueError as e:
        # Validation errors from model
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating cleaning record: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{record_id}", response_model=NetCleaningRecordResponse)
async def update_cleaning_record(
    record_id: uuid.UUID,
    record_update: NetCleaningRecordUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Update an existing cleaning record."""
    # Check record exists and belongs to user's organization
    existing_record = crud_records.get_cleaning_record(db, record_id)
    if not existing_record:
        raise HTTPException(status_code=404, detail="Cleaning record not found")
    
    net = crud_nets.get_net(db, existing_record.net_id)
    if not net:
        raise HTTPException(status_code=404, detail="Net not found")
    
    farm_site = crud_farm_sites.get_farm_site(db, net.farm_site_id)
    if not farm_site:
        raise HTTPException(status_code=404, detail="Farm site not found")
    
    if current_user.role != "super_admin" and farm_site.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this cleaning record")
    
    # If net_id is being changed, verify new net
    if record_update.net_id and record_update.net_id != existing_record.net_id:
        new_net = crud_nets.get_net(db, record_update.net_id)
        if not new_net:
            raise HTTPException(status_code=404, detail="New net not found")
        
        new_farm_site = crud_farm_sites.get_farm_site(db, new_net.farm_site_id)
        if not new_farm_site:
            raise HTTPException(status_code=404, detail="New farm site not found")
        
        if current_user.role != "super_admin" and new_farm_site.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to move record to this net")
    
    try:
        updated_record = crud_records.update_cleaning_record(db, record_id, record_update)
        if not updated_record:
            raise HTTPException(status_code=404, detail="Cleaning record not found")
        return updated_record
    except ValueError as e:
        # Validation errors from model
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating cleaning record: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cleaning_record(
    record_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a cleaning record."""
    # Permission check: only admins and super_admins can delete records
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can delete cleaning records"
        )
    
    # Check record exists and belongs to user's organization
    existing_record = crud_records.get_cleaning_record(db, record_id)
    if not existing_record:
        raise HTTPException(status_code=404, detail="Cleaning record not found")
    
    net = crud_nets.get_net(db, existing_record.net_id)
    if not net:
        raise HTTPException(status_code=404, detail="Net not found")
    
    farm_site = crud_farm_sites.get_farm_site(db, net.farm_site_id)
    if not farm_site:
        raise HTTPException(status_code=404, detail="Farm site not found")
    
    if current_user.role != "super_admin" and farm_site.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this cleaning record")
    
    try:
        success = crud_records.delete_cleaning_record(db, record_id)
        if not success:
            raise HTTPException(status_code=404, detail="Cleaning record not found")
        return None
    except Exception as e:
        logger.error(f"Error deleting cleaning record: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
