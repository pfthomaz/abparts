# backend/app/routers/inventory_reports.py

import uuid
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from .. import schemas, crud, models
from ..database import get_db
from ..auth import get_current_user, TokenData
from ..permissions import (
    ResourceType, PermissionType, require_permission, require_super_admin,
    OrganizationScopedQueries, check_organization_access, permission_checker
)

router = APIRouter()

@router.get("/movement", response_model=List[dict])
async def get_inventory_movement_report(
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    warehouse_id: Optional[uuid.UUID] = Query(None, description="Filter by warehouse ID"),
    part_id: Optional[uuid.UUID] = Query(None, description="Filter by part ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for report period"),
    end_date: Optional[datetime] = Query(None, description="End date for report period"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.READ))
):
    """Generate inventory movement report based on transactions."""
    # If organization_id is not provided, use the current user's organization
    # unless the user is a super_admin
    if not organization_id and not permission_checker.is_super_admin(current_user):
        organization_id = current_user.organization_id
    
    # Check organization access if organization_id is provided
    if organization_id and not check_organization_access(current_user, organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this organization's data")
    
    # Check warehouse access if warehouse_id is provided
    if warehouse_id:
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        if not check_organization_access(current_user, warehouse.organization_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to access this warehouse")
    
    # Set default date range if not provided (last 30 days)
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get all warehouses for the organization if organization_id is provided
    warehouse_ids = []
    if organization_id:
        warehouses = db.query(models.Warehouse).filter(models.Warehouse.organization_id == organization_id).all()
        warehouse_ids = [w.id for w in warehouses]
    
    # If specific warehouse_id is provided, use only that one
    if warehouse_id:
        warehouse_ids = [warehouse_id]
    
    # If no warehouses found or specified, return empty result
    if not warehouse_ids:
        return []
    
    # Get all parts (filtered by part_id if provided)
    parts_query = db.query(models.Part)
    if part_id:
        parts_query = parts_query.filter(models.Part.id == part_id)
    parts = parts_query.all()
    
    # Prepare result
    result = []
    
    for part in parts:
        # Get beginning balance (transactions before start_date)
        beginning_balance_query = db.query(
            func.sum(models.Transaction.quantity).label("total_quantity")
        ).filter(
            models.Transaction.part_id == part.id,
            models.Transaction.transaction_date < start_date
        )
        
        # Filter by warehouse_ids
        beginning_balance_query = beginning_balance_query.filter(
            (models.Transaction.to_warehouse_id.in_(warehouse_ids)) |
            (models.Transaction.from_warehouse_id.in_(warehouse_ids))
        )
        
        beginning_balance_result = beginning_balance_query.first()
        beginning_balance = beginning_balance_result.total_quantity or Decimal('0')
        
        # Get transactions during the period
        transactions_query = db.query(
            models.Transaction.transaction_type,
            func.sum(models.Transaction.quantity).label("total_quantity"),
            func.count(models.Transaction.id).label("transaction_count")
        ).filter(
            models.Transaction.part_id == part.id,
            models.Transaction.transaction_date >= start_date,
            models.Transaction.transaction_date <= end_date
        ).group_by(
            models.Transaction.transaction_type
        )
        
        # Filter by warehouse_ids
        transactions_query = transactions_query.filter(
            (models.Transaction.to_warehouse_id.in_(warehouse_ids)) |
            (models.Transaction.from_warehouse_id.in_(warehouse_ids))
        )
        
        transactions_result = transactions_query.all()
        
        # Calculate movement by transaction type
        received = Decimal('0')
        issued = Decimal('0')
        adjusted = Decimal('0')
        
        for transaction_type, total_quantity, transaction_count in transactions_result:
            if transaction_type == models.TransactionType.CREATION:
                received += total_quantity
            elif transaction_type == models.TransactionType.TRANSFER:
                # For transfers, we need to check if it's incoming or outgoing
                transfer_in_query = db.query(
                    func.sum(models.Transaction.quantity).label("total_in")
                ).filter(
                    models.Transaction.part_id == part.id,
                    models.Transaction.transaction_type == models.TransactionType.TRANSFER,
                    models.Transaction.to_warehouse_id.in_(warehouse_ids),
                    models.Transaction.transaction_date >= start_date,
                    models.Transaction.transaction_date <= end_date
                )
                
                transfer_out_query = db.query(
                    func.sum(models.Transaction.quantity).label("total_out")
                ).filter(
                    models.Transaction.part_id == part.id,
                    models.Transaction.transaction_type == models.TransactionType.TRANSFER,
                    models.Transaction.from_warehouse_id.in_(warehouse_ids),
                    models.Transaction.transaction_date >= start_date,
                    models.Transaction.transaction_date <= end_date
                )
                
                transfer_in_result = transfer_in_query.first()
                transfer_out_result = transfer_out_query.first()
                
                transfer_in = transfer_in_result.total_in or Decimal('0')
                transfer_out = transfer_out_result.total_out or Decimal('0')
                
                received += transfer_in
                issued += transfer_out
            elif transaction_type == models.TransactionType.CONSUMPTION:
                issued += total_quantity
            elif transaction_type == models.TransactionType.ADJUSTMENT:
                adjusted += total_quantity
        
        # Calculate ending balance
        ending_balance = beginning_balance + received - issued + adjusted
        
        # Get current inventory levels
        current_inventory_query = db.query(
            func.sum(models.Inventory.current_stock).label("total_stock")
        ).filter(
            models.Inventory.part_id == part.id,
            models.Inventory.warehouse_id.in_(warehouse_ids)
        )
        
        current_inventory_result = current_inventory_query.first()
        current_inventory = current_inventory_result.total_stock or Decimal('0')
        
        # Add to result
        result.append({
            "part_id": part.id,
            "part_number": part.part_number,
            "part_name": part.name,
            "unit_of_measure": part.unit_of_measure,
            "beginning_balance": beginning_balance,
            "received": received,
            "issued": issued,
            "adjusted": adjusted,
            "ending_balance": ending_balance,
            "current_inventory": current_inventory,
            "variance": current_inventory - ending_balance,
            "report_start_date": start_date,
            "report_end_date": end_date
        })
    
    return result

@router.get("/turnover", response_model=List[dict])
async def get_inventory_turnover_report(
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    warehouse_id: Optional[uuid.UUID] = Query(None, description="Filter by warehouse ID"),
    period_days: int = Query(90, ge=30, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.READ))
):
    """Generate inventory turnover report based on transactions."""
    # If organization_id is not provided, use the current user's organization
    # unless the user is a super_admin
    if not organization_id and not permission_checker.is_super_admin(current_user):
        organization_id = current_user.organization_id
    
    # Check organization access if organization_id is provided
    if organization_id and not check_organization_access(current_user, organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this organization's data")
    
    # Check warehouse access if warehouse_id is provided
    if warehouse_id:
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        if not check_organization_access(current_user, warehouse.organization_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to access this warehouse")
    
    # Calculate the start date for the analysis period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)
    
    # Get all warehouses for the organization if organization_id is provided
    warehouse_ids = []
    if organization_id:
        warehouses = db.query(models.Warehouse).filter(models.Warehouse.organization_id == organization_id).all()
        warehouse_ids = [w.id for w in warehouses]
    
    # If specific warehouse_id is provided, use only that one
    if warehouse_id:
        warehouse_ids = [warehouse_id]
    
    # If no warehouses found or specified, return empty result
    if not warehouse_ids:
        return []
    
    # Get all parts with inventory in the specified warehouses
    inventory_query = db.query(
        models.Inventory.part_id,
        func.sum(models.Inventory.current_stock).label("total_stock")
    ).filter(
        models.Inventory.warehouse_id.in_(warehouse_ids)
    ).group_by(
        models.Inventory.part_id
    )
    
    inventory_results = inventory_query.all()
    
    # Prepare result
    result = []
    
    for part_id, current_stock in inventory_results:
        # Get part details
        part = db.query(models.Part).filter(models.Part.id == part_id).first()
        if not part:
            continue
        
        # Get consumption transactions during the period
        consumption_query = db.query(
            func.sum(models.Transaction.quantity).label("total_consumed")
        ).filter(
            models.Transaction.part_id == part_id,
            models.Transaction.transaction_type == models.TransactionType.CONSUMPTION,
            models.Transaction.from_warehouse_id.in_(warehouse_ids),
            models.Transaction.transaction_date >= start_date,
            models.Transaction.transaction_date <= end_date
        )
        
        consumption_result = consumption_query.first()
        total_consumed = consumption_result.total_consumed or Decimal('0')
        
        # Calculate average inventory (current stock as approximation)
        average_inventory = current_stock
        
        # Calculate turnover ratio (if average inventory is zero, set to None)
        turnover_ratio = None
        if average_inventory > 0:
            # Annualize the consumption (convert from period_days to 365 days)
            annual_consumption = total_consumed * (365 / period_days)
            turnover_ratio = annual_consumption / average_inventory
        
        # Calculate days on hand (if total_consumed is zero, set to None)
        days_on_hand = None
        if total_consumed > 0:
            # Calculate daily consumption
            daily_consumption = total_consumed / period_days
            days_on_hand = current_stock / daily_consumption if daily_consumption > 0 else None
        
        # Add to result
        result.append({
            "part_id": part_id,
            "part_number": part.part_number,
            "part_name": part.name,
            "unit_of_measure": part.unit_of_measure,
            "current_stock": current_stock,
            "total_consumed": total_consumed,
            "consumption_period_days": period_days,
            "turnover_ratio": turnover_ratio,
            "days_on_hand": days_on_hand,
            "is_slow_moving": turnover_ratio < 1 if turnover_ratio is not None else None,
            "is_fast_moving": turnover_ratio > 4 if turnover_ratio is not None else None
        })
    
    # Sort by turnover ratio (descending)
    result.sort(key=lambda x: x["turnover_ratio"] if x["turnover_ratio"] is not None else -1, reverse=True)
    
    return result

@router.get("/valuation", response_model=List[dict])
async def get_inventory_valuation_report(
    organization_id: Optional[uuid.UUID] = Query(None, description="Filter by organization ID"),
    warehouse_id: Optional[uuid.UUID] = Query(None, description="Filter by warehouse ID"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.INVENTORY, PermissionType.READ))
):
    """Generate inventory valuation report based on current inventory and transaction history."""
    # If organization_id is not provided, use the current user's organization
    # unless the user is a super_admin
    if not organization_id and not permission_checker.is_super_admin(current_user):
        organization_id = current_user.organization_id
    
    # Check organization access if organization_id is provided
    if organization_id and not check_organization_access(current_user, organization_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to access this organization's data")
    
    # Check warehouse access if warehouse_id is provided
    if warehouse_id:
        warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        if not check_organization_access(current_user, warehouse.organization_id, db):
            raise HTTPException(status_code=403, detail="Not authorized to access this warehouse")
    
    # Get all warehouses for the organization if organization_id is provided
    warehouse_ids = []
    if organization_id:
        warehouses = db.query(models.Warehouse).filter(models.Warehouse.organization_id == organization_id).all()
        warehouse_ids = [w.id for w in warehouses]
    
    # If specific warehouse_id is provided, use only that one
    if warehouse_id:
        warehouse_ids = [warehouse_id]
    
    # If no warehouses found or specified, return empty result
    if not warehouse_ids:
        return []
    
    # Get all inventory items in the specified warehouses
    inventory_query = db.query(
        models.Inventory,
        models.Part,
        models.Warehouse.name.label("warehouse_name")
    ).join(
        models.Part, models.Inventory.part_id == models.Part.id
    ).join(
        models.Warehouse, models.Inventory.warehouse_id == models.Warehouse.id
    ).filter(
        models.Inventory.warehouse_id.in_(warehouse_ids)
    )
    
    inventory_results = inventory_query.all()
    
    # Prepare result
    result = []
    
    for inventory, part, warehouse_name in inventory_results:
        # Get the most recent supplier order item for this part to estimate value
        supplier_order_item = db.query(
            models.SupplierOrderItem
        ).join(
            models.SupplierOrder, models.SupplierOrderItem.supplier_order_id == models.SupplierOrder.id
        ).filter(
            models.SupplierOrderItem.part_id == part.id
        ).order_by(
            desc(models.SupplierOrder.order_date)
        ).first()
        
        # Estimate unit value
        unit_value = None
        if supplier_order_item and supplier_order_item.unit_price:
            unit_value = supplier_order_item.unit_price
        
        # Calculate total value
        total_value = None
        if unit_value is not None:
            total_value = unit_value * inventory.current_stock
        
        # Add to result
        result.append({
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
    
    return result