# backend/app/routers/warehouses.py

import uuid
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import crud, models
from ..schemas.warehouse import WarehouseBase, WarehouseCreate, WarehouseUpdate, WarehouseResponse
from ..schemas import StockResetRequest, StockResetResponse, StockAdjustmentItem
from ..database import get_db
from ..auth import get_current_user, TokenData
from ..permissions import (
    ResourceType, PermissionType, require_permission, require_admin,
    OrganizationScopedQueries, check_organization_access, permission_checker
)

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Warehouse CRUD ---
@router.get("/", response_model=List[WarehouseResponse])
async def get_warehouses(
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    include_inactive: bool = Query(False, description="Include inactive warehouses"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.WAREHOUSE, PermissionType.READ))
):
    """Get warehouses with optional organization filtering."""
    try:
        # Use organization-scoped query filtering
        base_query = db.query(models.Warehouse)
        filtered_query = OrganizationScopedQueries.filter_warehouses(base_query, current_user)
        
        if organization_id:
            # Additional filter by organization_id if specified
            if not check_organization_access(current_user, organization_id, db):
                raise HTTPException(status_code=403, detail="Not authorized to access this organization's warehouses")
            filtered_query = filtered_query.filter(models.Warehouse.organization_id == organization_id)
        
        if not include_inactive:
            filtered_query = filtered_query.filter(models.Warehouse.is_active == True)
        
        warehouses = filtered_query.offset(skip).limit(limit).all()
        return warehouses
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search", response_model=List[WarehouseResponse])
async def search_warehouses(
    q: str = Query(..., min_length=1, description="Search query"),
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    include_inactive: bool = Query(False, description="Include inactive warehouses"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Search warehouses by name, location, or description."""
    try:
        # Permission check: super_admin can search all, others only their organization
        if current_user.role != "super_admin":
            organization_id = current_user.organization_id
        
        warehouses = crud.warehouses.search_warehouses(
            db, q, organization_id, include_inactive, skip, limit
        )
        return warehouses
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get a single warehouse by ID."""
    warehouse = crud.warehouses.get_warehouse(db, warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    # Permission check: users can only access warehouses from their organization
    if current_user.role != "super_admin" and warehouse.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this warehouse")
    
    return warehouse


@router.get("/{warehouse_id}/summary")
async def get_warehouse_summary(
    warehouse_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get warehouse inventory summary."""
    warehouse = crud.warehouses.get_warehouse(db, warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    # Permission check: users can only access warehouses from their organization
    if current_user.role != "super_admin" and warehouse.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this warehouse")
    
    summary = crud.warehouses.get_warehouse_inventory_summary(db, warehouse_id)
    return summary


@router.post("/", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    warehouse: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.WAREHOUSE, PermissionType.WRITE))
):
    """Create a new warehouse."""
    try:
        # Permission check: admins can only create warehouses in their organization
        if current_user.role == "admin" and warehouse.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=403, 
                detail="You can only create warehouses in your own organization"
            )
        
        db_warehouse = crud.warehouses.create_warehouse(db, warehouse)
        return db_warehouse
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create warehouse")


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: uuid.UUID,
    warehouse_update: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.WAREHOUSE, PermissionType.WRITE))
):
    """Update an existing warehouse."""
    try:
        # Check if warehouse exists
        db_warehouse = crud.warehouses.get_warehouse(db, warehouse_id)
        if not db_warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        
        # Permission check: admins can only update warehouses in their organization
        if current_user.role == "admin" and db_warehouse.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=403, 
                detail="You can only update warehouses in your own organization"
            )
        
        # Prevent changing organization_id for non-super_admin users
        if current_user.role != "super_admin" and warehouse_update.organization_id is not None:
            if warehouse_update.organization_id != db_warehouse.organization_id:
                raise HTTPException(
                    status_code=403, 
                    detail="You cannot change the warehouse organization"
                )
        
        updated_warehouse = crud.warehouses.update_warehouse(db, warehouse_id, warehouse_update)
        return updated_warehouse
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update warehouse")


@router.patch("/{warehouse_id}/activate", response_model=WarehouseResponse)
async def activate_warehouse(
    warehouse_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.WAREHOUSE, PermissionType.WRITE))
):
    """Activate a warehouse."""
    try:
        # Check if warehouse exists
        db_warehouse = crud.warehouses.get_warehouse(db, warehouse_id)
        if not db_warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        
        # Permission check: admins can only activate warehouses in their organization
        if current_user.role == "admin" and db_warehouse.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=403, 
                detail="You can only activate warehouses in your own organization"
            )
        
        activated_warehouse = crud.warehouses.activate_warehouse(db, warehouse_id)
        return activated_warehouse
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to activate warehouse")


@router.patch("/{warehouse_id}/deactivate", response_model=WarehouseResponse)
async def deactivate_warehouse(
    warehouse_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.WAREHOUSE, PermissionType.WRITE))
):
    """Deactivate a warehouse."""
    try:
        # Check if warehouse exists
        db_warehouse = crud.warehouses.get_warehouse(db, warehouse_id)
        if not db_warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        
        # Permission check: admins can only deactivate warehouses in their organization
        if current_user.role == "admin" and db_warehouse.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=403, 
                detail="You can only deactivate warehouses in your own organization"
            )
        
        deactivated_warehouse = crud.warehouses.deactivate_warehouse(db, warehouse_id)
        return deactivated_warehouse
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to deactivate warehouse")


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_warehouse(
    warehouse_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.WAREHOUSE, PermissionType.DELETE))
):
    """Delete a warehouse (only if no inventory or transactions exist)."""
    try:
        # Check if warehouse exists
        db_warehouse = crud.warehouses.get_warehouse(db, warehouse_id)
        if not db_warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        
        # Permission check: admins can only delete warehouses in their organization
        if current_user.role == "admin" and db_warehouse.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=403, 
                detail="You can only delete warehouses in your own organization"
            )
        
        result = crud.warehouses.delete_warehouse(db, warehouse_id)
        if not result:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete warehouse")


# --- Organization-specific warehouse endpoints ---
@router.get("/organization/{organization_id}/warehouses", response_model=List[WarehouseResponse])
async def get_organization_warehouses(
    organization_id: uuid.UUID,
    include_inactive: bool = Query(False, description="Include inactive warehouses"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all warehouses for a specific organization."""
    try:
        # Permission check: users can only access warehouses from their organization
        if current_user.role != "super_admin" and organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=403, 
                detail="You can only view warehouses from your own organization"
            )
        
        warehouses = crud.warehouses.get_warehouses_by_organization(
            db, organization_id, include_inactive, skip, limit
        )
        return warehouses
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Stock Reset Endpoint ---

@router.post("/{warehouse_id}/stock-reset")
def reset_warehouse_stock(
    warehouse_id: str,
    reset_data: StockResetRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.WRITE))
):
    """
    Reset stock levels for multiple parts in a warehouse.
    Now creates stock adjustment records for proper audit trail.
    """
    from decimal import Decimal
    from datetime import datetime
    from ..crud import stock_adjustments as stock_adj_crud
    
    # Verify warehouse exists and user has access
    warehouse = db.query(models.Warehouse).filter(
        models.Warehouse.id == warehouse_id
    ).first()
    
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    # Check organization access
    if not permission_checker.is_super_admin(current_user):
        if warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied to this warehouse")
    
    logger.info(f"📥 Stock reset request for warehouse {warehouse_id}: {len(reset_data.adjustments)} adjustments")
    
    # Convert to stock adjustment format
    from ..schemas.stock_adjustment import (
        StockAdjustmentCreate, 
        StockAdjustmentItemCreate,
        AdjustmentTypeEnum
    )
    
    adjustment_items = []
    for adjustment in reset_data.adjustments:
        adjustment_items.append(
            StockAdjustmentItemCreate(
                part_id=adjustment.part_id,
                quantity_after=adjustment.new_quantity,
                reason=None  # Individual item reason (optional)
            )
        )
    
    # Create stock adjustment using the new system
    adjustment_data = StockAdjustmentCreate(
        warehouse_id=warehouse_id,
        adjustment_type=AdjustmentTypeEnum.STOCK_TAKE,  # Stock reset is essentially a stock take
        reason=reset_data.reason if reset_data.reason else "Stock reset via warehouse interface",
        notes=reset_data.notes,
        items=adjustment_items
    )
    
    try:
        # Use the stock adjustments CRUD to create the adjustment
        # This will handle inventory updates and create proper audit trail
        stock_adjustment = stock_adj_crud.create_stock_adjustment(
            db=db,
            adjustment_data=adjustment_data,
            current_user_id=current_user.user_id
        )
        
        logger.info(f"✅ Created stock adjustment {stock_adjustment.id} with {len(stock_adjustment.items)} items")
        
        # Return response in the format expected by the frontend
        results = []
        for item in stock_adjustment.items:
            results.append({
                "part_id": str(item.part_id),
                "old_quantity": float(item.quantity_before),
                "new_quantity": float(item.quantity_after),
                "difference": float(item.quantity_change)
            })
        
        return {
            "warehouse_id": warehouse_id,
            "adjustments_made": len(results),
            "details": results,
            "stock_adjustment_id": str(stock_adjustment.id)  # Include the adjustment ID for reference
        }
    except Exception as e:
        logger.error(f"❌ Error creating stock adjustment: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create stock adjustment: {str(e)}")
