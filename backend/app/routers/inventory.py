# backend/app/routers/inventory.py

import uuid
import logging
from typing import List, Optional
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, TokenData # Import authentication dependencies
from ..permissions import (
    ResourceType, PermissionType, require_permission, require_admin,
    OrganizationScopedQueries, check_organization_access, permission_checker
)
from ..cache import get_analytics_cache_stats, invalidate_warehouse_analytics_cache
from ..cache import get_analytics_cache_stats, invalidate_warehouse_analytics_cache

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Helper Functions ---
def check_warehouse_access(user: TokenData, warehouse_id: uuid.UUID, db: Session) -> bool:
    """Check if user can access a specific warehouse."""
    if user.role == "super_admin":
        return True
    
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
    if not warehouse:
        return False
    
    return warehouse.organization_id == user.organization_id

def create_error_response(error_type: str, message: str, details: Optional[List[dict]] = None) -> dict:
    """Create a standardized error response."""
    return {
        "error": error_type,
        "message": message,
        "details": details or [],
        "timestamp": datetime.utcnow().isoformat()
    }

def validate_uuid_parameter(param_value: str, param_name: str) -> uuid.UUID:
    """Validate and convert a string parameter to UUID with proper error handling."""
    try:
        return uuid.UUID(param_value)
    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {param_name} format. Must be a valid UUID."
        )

# --- Temporary Compatibility Endpoint (must be before /{inventory_id}) ---
@router.get("/reports")
async def get_inventory_reports_compatibility(
    warehouse_ids: List[uuid.UUID] = Query(..., description="List of warehouse IDs"),
    report_type: str = Query("summary", description="Type of report"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    stock_status: str = Query("all", description="Stock status filter"),
    part_type: str = Query("all", description="Part type filter"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Temporary compatibility endpoint for old frontend calls.
    This redirects to the proper inventory-reports endpoints.
    """
    try:
        # For now, just use the first warehouse ID and call the valuation endpoint
        if not warehouse_ids:
            raise HTTPException(status_code=400, detail="At least one warehouse ID is required")
        
        warehouse_id = warehouse_ids[0]
        
        # Check if user can access this warehouse
        if not check_warehouse_access(current_user, warehouse_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to view this warehouse's reports")
        
        # Get valuation data directly from the database
        # Get all inventory items in the specified warehouse
        inventory_query = db.query(
            models.Inventory,
            models.Part,
            models.Warehouse.name.label("warehouse_name")
        ).join(
            models.Part, models.Inventory.part_id == models.Part.id
        ).join(
            models.Warehouse, models.Inventory.warehouse_id == models.Warehouse.id
        ).filter(
            models.Inventory.warehouse_id == warehouse_id
        )
        
        inventory_results = inventory_query.all()
        valuation_data = []
        
        for inventory, part, warehouse_name in inventory_results:
            # Get the most recent supplier order item for this part to estimate value
            supplier_order_item = db.query(
                models.SupplierOrderItem
            ).join(
                models.SupplierOrder, models.SupplierOrderItem.supplier_order_id == models.SupplierOrder.id
            ).filter(
                models.SupplierOrderItem.part_id == part.id
            ).order_by(
                models.SupplierOrder.order_date.desc()
            ).first()
            
            # Estimate unit value
            unit_value = None
            if supplier_order_item and supplier_order_item.unit_price:
                unit_value = supplier_order_item.unit_price
            
            # Calculate total value
            total_value = None
            if unit_value is not None:
                total_value = unit_value * inventory.current_stock
            
            valuation_data.append({
                "inventory_id": inventory.id,
                "part_id": part.id,
                "part_number": part.part_number,
                "part_name": part.name,
                "warehouse_id": inventory.warehouse_id,
                "warehouse_name": warehouse_name,
                "current_stock": inventory.current_stock,
                "unit_of_measure": inventory.unit_of_measure,
                "unit_value": unit_value,
                "total_value": total_value,
                "last_updated": inventory.last_updated
            })
        
        # Transform to expected format
        items = []
        for item in valuation_data:
            items.append({
                "warehouse_name": item.get("warehouse_name", "Unknown"),
                "part_number": item.get("part_number", ""),
                "part_name": item.get("part_name", ""),
                "current_stock": float(item.get("current_stock", 0)),
                "unit_of_measure": item.get("unit_of_measure", ""),
                "minimum_stock_recommendation": 0,
                "stock_status": "in_stock" if float(item.get("current_stock", 0)) > 0 else "out_of_stock",
                "estimated_value": float(item.get("total_value", 0)) if item.get("total_value") else 0
            })
        
        # Calculate summary
        total_items = len(items)
        total_value = sum(item["estimated_value"] for item in items)
        low_stock_items = sum(1 for item in items if item["stock_status"] == "low_stock")
        out_of_stock_items = sum(1 for item in items if item["stock_status"] == "out_of_stock")
        
        return {
            "items": items,
            "summary": {
                "total_items": total_items,
                "total_value": total_value,
                "low_stock_items": low_stock_items,
                "out_of_stock_items": out_of_stock_items
            },
            "warehouse_breakdown": []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in compatibility reports endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while generating report"
        )

# --- Inventory CRUD ---
@router.get("/", response_model=List[schemas.InventoryResponse])
async def get_inventory_items(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    # Apply organization-scoped filtering based on user role
    if current_user.role == "super_admin":
        inventory_items = crud.inventory.get_inventory_items(db)
    else:
        # Regular users can only see inventory from their organization's warehouses
        inventory_items = crud.inventory.get_inventory_by_organization(db, current_user.organization_id)
    return inventory_items

@router.get("/{inventory_id}", response_model=schemas.InventoryResponse)
async def get_inventory_item(
    inventory_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    inventory_item = crud.inventory.get_inventory_item(db, inventory_id)
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Check if user can access this inventory item's warehouse
    if current_user.role != "super_admin":
        # Get warehouse to check organization
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == inventory_item.warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this inventory item")
    
    return inventory_item

@router.post("/", response_model=schemas.InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item: schemas.InventoryCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.WRITE))
):
    # Check if user can access the warehouse for this inventory item
    if current_user.role != "super_admin":
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == item.warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to create inventory in this warehouse")

    db_item = crud.inventory.create_inventory_item(db, item)
    if not db_item:
        raise HTTPException(status_code=400, detail="Failed to create inventory item")
    return db_item

@router.put("/{inventory_id}", response_model=schemas.InventoryResponse)
async def update_inventory_item(
    inventory_id: uuid.UUID,
    item_update: schemas.InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.WRITE))
):
    db_item = crud.inventory.get_inventory_item(db, inventory_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Check if user can access this inventory item's warehouse
    if current_user.role != "super_admin":
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == db_item.warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this inventory item")

    updated_item = crud.inventory.update_inventory_item(db, inventory_id, item_update)
    if not updated_item:
        raise HTTPException(status_code=400, detail="Failed to update inventory item")
    return updated_item


@router.delete("/{inventory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    inventory_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.DELETE))
):
    db_item = crud.inventory.get_inventory_item(db, inventory_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    # Check if user can access this inventory item's warehouse
    if current_user.role != "super_admin":
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == db_item.warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this inventory item")

    result = crud.inventory.delete_inventory_item(db, inventory_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to delete inventory item")
    return result


@router.get("/worksheet/stocktake", response_model=List[schemas.StocktakeWorksheetItemResponse])
async def get_stocktake_worksheet(
    organization_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Generate a stocktake worksheet for a specific organization.
    Lists parts with their current system stock levels across all warehouses.
    """
    # Validate organization_id
    organization = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check if user can access this organization
    if current_user.role != "super_admin" and organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to generate stocktake worksheet for this organization")

    worksheet_items = crud.inventory.get_stocktake_worksheet_items(db, organization_id=organization_id)
    if not worksheet_items:
        # It's not an error if there are no items, just return an empty list.
        # Client can decide how to present this (e.g., "No inventory items found for this organization").
        pass # Fall through to return empty list

    return worksheet_items


# --- Warehouse-based inventory endpoints ---

@router.get("/warehouse/{warehouse_id}")
async def get_warehouse_inventory(
    warehouse_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all inventory items for a specific warehouse."""
    # Check if user can access this warehouse
    if current_user.role != "super_admin":
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
        if not warehouse or warehouse.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this warehouse's inventory")
    
    inventory_items = crud.inventory.get_inventory_by_warehouse(db, warehouse_id, skip, limit)
    return inventory_items


@router.get("/organization/{organization_id}/aggregated")
async def get_organization_inventory_aggregated(
    organization_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get inventory aggregated by part across all warehouses for an organization."""
    # Check if user can access this organization
    if current_user.role != "super_admin" and organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this organization's inventory")
    
    aggregated_inventory = crud.inventory.get_inventory_aggregation_by_organization(db, organization_id)
    return {
        "organization_id": str(organization_id),
        "inventory_summary": aggregated_inventory,
        "total_parts": len(aggregated_inventory),
        "low_stock_parts": sum(1 for item in aggregated_inventory if item['is_low_stock'])
    }


@router.get("/organization/{organization_id}/by-warehouse", response_model=List[schemas.InventoryResponse])
async def get_organization_inventory_by_warehouse(
    organization_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all inventory items for an organization across all its warehouses."""
    # Check if user can access this organization
    if current_user.role != "super_admin" and organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this organization's inventory")
    
    inventory_items = crud.inventory.get_inventory_by_organization(db, organization_id, skip, limit)
    return inventory_items


@router.post("/transfer")
async def transfer_inventory_between_warehouses(
    transfer_request: schemas.InventoryTransferRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.WRITE))
):
    """Transfer inventory between warehouses with comprehensive error handling."""
    try:
        # Validate warehouse access
        if not check_warehouse_access(current_user, transfer_request.from_warehouse_id, db):
            raise HTTPException(status_code=403, detail="Access denied to source warehouse")
        
        if not check_warehouse_access(current_user, transfer_request.to_warehouse_id, db):
            raise HTTPException(status_code=403, detail="Access denied to destination warehouse")
        
        # Perform transfer with enhanced error handling
        result = crud.inventory.transfer_inventory_between_warehouses(
            db=db,
            from_warehouse_id=transfer_request.from_warehouse_id,
            to_warehouse_id=transfer_request.to_warehouse_id,
            part_id=transfer_request.part_id,
            quantity=transfer_request.quantity,
            performed_by_user_id=current_user.user_id
        )
        
        return {
            "success": True,
            "message": "Inventory transferred successfully",
            "transfer_details": result
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Unexpected error in inventory transfer endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during transfer")


@router.get("/warehouse/{warehouse_id}/balance-calculations")
async def get_warehouse_inventory_balance_calculations(
    warehouse_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.READ))
):
    """Get inventory balance calculations based on transactions for a warehouse."""
    # Check if user can access this warehouse
    if not check_warehouse_access(current_user, warehouse_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to view this warehouse's balance calculations")
    
    balance_calculations = crud.inventory.get_inventory_balance_calculations(db, warehouse_id)
    return {
        "warehouse_id": str(warehouse_id),
        "balance_calculations": balance_calculations,
        "total_parts": len(balance_calculations)
    }


@router.get("/warehouse/{warehouse_id}/analytics", response_model=schemas.WarehouseAnalyticsResponse)
async def get_warehouse_analytics(
    warehouse_id: uuid.UUID,
    start_date: Optional[date] = Query(None, description="Start date for analytics period (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date for analytics period (YYYY-MM-DD)"),
    days: int = Query(30, ge=1, le=365, description="Number of days to include in analytics (default: 30)"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get comprehensive analytics for a specific warehouse including inventory summary,
    top parts by value, stock movements, and turnover metrics.
    """
    try:
        # Validate warehouse_id format
        if not isinstance(warehouse_id, uuid.UUID):
            raise HTTPException(
                status_code=400,
                detail="Invalid warehouse ID format. Must be a valid UUID."
            )
        
        # Validate days parameter
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=400,
                detail="Days parameter must be between 1 and 365"
            )
        
        # Check if user can access this warehouse
        try:
            if not check_warehouse_access(current_user, warehouse_id, db):
                raise HTTPException(
                    status_code=403, 
                    detail="Not authorized to view analytics for this warehouse"
                )
        except Exception as e:
            logger.error(f"Error checking warehouse access for user {current_user.user_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error validating warehouse access permissions"
            )
        
        # Convert date objects to datetime objects if provided with validation
        start_datetime = None
        end_datetime = None
        
        try:
            if start_date:
                start_datetime = datetime.combine(start_date, datetime.min.time())
                # Validate start date is not in the future (allow current day)
                current_date = datetime.utcnow().date()
                if start_date > current_date:
                    raise HTTPException(
                        status_code=400,
                        detail="Start date cannot be in the future"
                    )
            
            if end_date:
                end_datetime = datetime.combine(end_date, datetime.max.time())
                # Validate end date is not in the future (allow current day)
                current_date = datetime.utcnow().date()
                if end_date > current_date:
                    raise HTTPException(
                        status_code=400,
                        detail="End date cannot be in the future"
                    )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date format: {str(e)}"
            )
        
        # Validate date range
        if start_datetime and end_datetime:
            if start_datetime > end_datetime:
                raise HTTPException(
                    status_code=400,
                    detail="Start date must be before or equal to end date"
                )
            
            # Check if date range is reasonable (not more than 2 years)
            if (end_datetime - start_datetime).days > 730:
                raise HTTPException(
                    status_code=400,
                    detail="Date range cannot exceed 2 years (730 days)"
                )
        
        # Get analytics data from CRUD function
        analytics_data = crud.inventory.get_warehouse_analytics(
            db=db,
            warehouse_id=warehouse_id,
            start_date=start_datetime,
            end_date=end_datetime,
            days=days
        )
        
        return analytics_data
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except ValueError as e:
        logger.error(f"Value error in warehouse analytics endpoint: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in warehouse analytics endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error while fetching warehouse analytics"
        )


@router.get("/warehouse/{warehouse_id}/analytics/trends", response_model=schemas.WarehouseAnalyticsTrendsResponse)
async def get_warehouse_analytics_trends(
    warehouse_id: uuid.UUID,
    period: str = Query("daily", regex="^(daily|weekly|monthly)$", description="Aggregation period: daily, weekly, or monthly"),
    days: int = Query(30, ge=1, le=365, description="Number of days to include in trends (default: 30)"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get trend data for warehouse analytics with daily, weekly, and monthly aggregation options.
    Returns time-series data for inventory values, quantities, and transaction counts.
    """
    try:
        # Validate warehouse_id format
        if not isinstance(warehouse_id, uuid.UUID):
            raise HTTPException(
                status_code=400,
                detail="Invalid warehouse ID format. Must be a valid UUID."
            )
        
        # Validate period parameter with detailed error message
        valid_periods = ["daily", "weekly", "monthly"]
        if period not in valid_periods:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid period '{period}'. Must be one of: {', '.join(valid_periods)}"
            )
        
        # Validate days parameter with detailed error message
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=400,
                detail="Days parameter must be between 1 and 365"
            )
        
        # Additional validation for period/days combination
        if period == "monthly" and days < 30:
            raise HTTPException(
                status_code=400,
                detail="For monthly period, days parameter should be at least 30 to show meaningful data"
            )
        
        if period == "weekly" and days < 7:
            raise HTTPException(
                status_code=400,
                detail="For weekly period, days parameter should be at least 7 to show meaningful data"
            )
        
        # Check if user can access this warehouse
        try:
            if not check_warehouse_access(current_user, warehouse_id, db):
                raise HTTPException(
                    status_code=403, 
                    detail="Not authorized to view analytics trends for this warehouse"
                )
        except Exception as e:
            logger.error(f"Error checking warehouse access for user {current_user.user_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error validating warehouse access permissions"
            )
        
        # Get trends data from CRUD function
        trends_data = crud.inventory.get_warehouse_analytics_trends(
            db=db,
            warehouse_id=warehouse_id,
            period=period,
            days=days
        )
        
        return trends_data
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except ValueError as e:
        logger.error(f"Value error in warehouse analytics trends endpoint: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in warehouse analytics trends endpoint: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error while fetching warehouse analytics trends"
        )


@router.get("/cache/stats")
async def get_analytics_cache_statistics(
    current_user: TokenData = Depends(require_admin)
):
    """
    Get analytics cache statistics and performance metrics.
    Only available to admin users.
    """
    try:
        cache_stats = get_analytics_cache_stats()
        return {
            "cache_statistics": cache_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting cache statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching cache statistics"
        )


# --- Cache Management Endpoints ---

@router.get("/cache/stats")
async def get_cache_statistics(
    current_user: TokenData = Depends(require_admin)
):
    """
    Get analytics cache statistics.
    Only available to admin users.
    """
    try:
        cache_stats = get_analytics_cache_stats()
        return {
            "success": True,
            "cache_statistics": cache_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error retrieving cache statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving cache statistics"
        )


@router.delete("/cache/warehouse/{warehouse_id}")
async def invalidate_warehouse_cache(
    warehouse_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Invalidate all cached analytics data for a specific warehouse.
    Useful for forcing cache refresh after data changes.
    """
    try:
        # Check if user can access this warehouse
        if current_user.role != "super_admin":
            warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
            if not warehouse or warehouse.organization_id != current_user.organization_id:
                raise HTTPException(
                    status_code=403, 
                    detail="Not authorized to manage cache for this warehouse"
                )
        
        deleted_count = invalidate_warehouse_analytics_cache(str(warehouse_id))
        
        return {
            "success": True,
            "message": f"Cache invalidated for warehouse {warehouse_id}",
            "deleted_entries": deleted_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error invalidating warehouse cache for {warehouse_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error invalidating warehouse cache"
        )


@router.post("/cache/clear-all")
async def clear_all_analytics_cache(
    current_user: TokenData = Depends(require_admin)
):
    """
    Clear all analytics cache entries.
    Only available to super admin users.
    Use with caution as this will force all analytics queries to recalculate.
    """
    try:
        if current_user.role != "super_admin":
            raise HTTPException(
                status_code=403,
                detail="Only super admin users can clear all cache entries"
            )
        
        from ..cache import cache_manager
        
        # Clear analytics and trends cache
        analytics_deleted = cache_manager.delete_pattern(f"{cache_manager.analytics_prefix}*")
        trends_deleted = cache_manager.delete_pattern(f"{cache_manager.trends_prefix}*")
        
        total_deleted = analytics_deleted + trends_deleted
        
        return {
            "success": True,
            "message": "All analytics cache entries cleared",
            "deleted_entries": {
                "analytics": analytics_deleted,
                "trends": trends_deleted,
                "total": total_deleted
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error clearing all analytics cache: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error clearing analytics cache"
        )

