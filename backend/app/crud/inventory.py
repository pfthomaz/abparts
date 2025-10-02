# backend/app/crud/inventory.py

import uuid
import logging
from typing import List, Optional
from decimal import Decimal, InvalidOperation
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func, case, or_
from fastapi import HTTPException, status

from .. import models, schemas # Import models and schemas
from ..cache import cached_analytics, invalidate_warehouse_analytics_cache

logger = logging.getLogger(__name__)

def get_inventory_item(db: Session, inventory_id: uuid.UUID):
    """Retrieve a single inventory item by ID."""
    return db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()

def get_inventory_items(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of inventory items."""
    return db.query(models.Inventory).offset(skip).limit(limit).all()

def create_inventory_item(db: Session, item: schemas.InventoryCreate):
    """Create a new inventory item."""
    # Validate FKs - these checks should ideally be in the router or a service layer
    # but for direct CRUD function, they are fine here for simplicity.
    warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == item.warehouse_id).first()
    part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
    if not warehouse:
        raise HTTPException(status_code=400, detail="Warehouse ID not found")
    if not part:
        raise HTTPException(status_code=400, detail="Part ID not found")

    db_item = models.Inventory(**item.dict())
    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # Invalidate cache for the warehouse
        invalidate_warehouse_analytics_cache(str(item.warehouse_id))
        
        return db_item
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Inventory for this warehouse and part already exists")
        logger.error(f"Error creating inventory item: {e}")
        raise HTTPException(status_code=400, detail="Error creating inventory item")

def update_inventory_item(db: Session, inventory_id: uuid.UUID, item_update: schemas.InventoryUpdate):
    """Update an existing inventory item."""
    db_item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not db_item:
        return None # Indicate not found

    update_data = item_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    try:
        # Re-validate FKs if warehouse_id or part_id are updated
        if "warehouse_id" in update_data:
            warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == db_item.warehouse_id).first()
            if not warehouse: raise HTTPException(status_code=400, detail="Warehouse ID not found")
        if "part_id" in update_data:
            part = db.query(models.Part).filter(models.Part.id == db_item.part_id).first()
            if not part: raise HTTPException(status_code=400, detail="Part ID not found")

        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        # Invalidate cache for the warehouse
        invalidate_warehouse_analytics_cache(str(db_item.warehouse_id))
        
        return db_item
    except Exception as e:
        db.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=409, detail="Inventory for this warehouse and part already exists")
        logger.error(f"Error updating inventory item: {e}")
        raise HTTPException(status_code=400, detail="Error updating inventory item")

def delete_inventory_item(db: Session, inventory_id: uuid.UUID):
    """Delete an inventory item by ID."""
    db_item = db.query(models.Inventory).filter(models.Inventory.id == inventory_id).first()
    if not db_item:
        return None # Indicate not found
    warehouse_id = str(db_item.warehouse_id)  # Store before deletion
    try:
        db.delete(db_item)
        db.commit()
        
        # Invalidate cache for the warehouse
        invalidate_warehouse_analytics_cache(warehouse_id)
        
        return {"message": "Inventory item deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting inventory item: {e}")
        raise HTTPException(status_code=400, detail="Error deleting inventory item.")


def get_stocktake_worksheet_items(db: Session, organization_id: uuid.UUID) -> List[schemas.StocktakeWorksheetItemResponse]:
    """
    Retrieve inventory items for a stocktake worksheet for a given organization.
    Includes part details (number, name) and current stock across all warehouses.
    """
    # Fetch inventory items for the organization's warehouses, joining with Part and Warehouse
    results = db.query(
        models.Inventory.id, # inventory_id
        models.Part.id,      # part_id
        models.Part.part_number,
        models.Part.name,    # part_name
        models.Inventory.current_stock, # system_quantity
        models.Warehouse.name # warehouse_name
    ).join(models.Part, models.Inventory.part_id == models.Part.id)\
     .join(models.Warehouse, models.Inventory.warehouse_id == models.Warehouse.id)\
     .filter(models.Warehouse.organization_id == organization_id)\
     .order_by(models.Part.part_number, models.Warehouse.name)\
     .all()

    if not results:
        return []

    # Map results to the Pydantic schema
    worksheet_items = [
        schemas.StocktakeWorksheetItemResponse(
            inventory_id=row[0],
            part_id=row[1],
            part_number=row[2],
            part_name=row[3],
            system_quantity=row[4],
            warehouse_name=row[5]
        ) for row in results
    ]
    return worksheet_items


# --- Warehouse-specific inventory functions ---

def get_inventory_by_warehouse(db: Session, warehouse_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[dict]:
    """Get all inventory items for a specific warehouse with part details."""
    # Join with Part to get part details
    results = db.query(
        models.Inventory,
        models.Part
    ).join(
        models.Part, models.Inventory.part_id == models.Part.id
    ).filter(
        models.Inventory.warehouse_id == warehouse_id
    ).offset(skip).limit(limit).all()
    
    # Convert to response format
    inventory_items = []
    for inventory, part in results:
        item_dict = {
            "id": inventory.id,
            "warehouse_id": inventory.warehouse_id,
            "part_id": inventory.part_id,
            "current_stock": float(inventory.current_stock),
            "minimum_stock_recommendation": float(inventory.minimum_stock_recommendation),
            "unit_of_measure": inventory.unit_of_measure,
            "reorder_threshold_set_by": inventory.reorder_threshold_set_by,
            "last_recommendation_update": inventory.last_recommendation_update,
            "last_updated": inventory.last_updated,
            "created_at": inventory.created_at,
            "part_number": part.part_number,
            "part_name": part.name
        }
        inventory_items.append(item_dict)
    
    return inventory_items


def get_inventory_by_organization(db: Session, organization_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[models.Inventory]:
    """Get all inventory items for an organization across all its warehouses."""
    return db.query(models.Inventory).join(
        models.Warehouse, models.Inventory.warehouse_id == models.Warehouse.id
    ).filter(
        models.Warehouse.organization_id == organization_id
    ).offset(skip).limit(limit).all()


def get_inventory_aggregation_by_organization(db: Session, organization_id: uuid.UUID) -> List[dict]:
    """Get inventory aggregated by part across all warehouses for an organization."""
    from sqlalchemy import func
    
    results = db.query(
        models.Part.id.label('part_id'),
        models.Part.part_number,
        models.Part.name.label('part_name'),
        models.Part.unit_of_measure,
        func.sum(models.Inventory.current_stock).label('total_stock'),
        func.count(models.Inventory.id).label('warehouse_count'),
        func.sum(models.Inventory.minimum_stock_recommendation).label('total_min_stock')
    ).join(
        models.Inventory, models.Part.id == models.Inventory.part_id
    ).join(
        models.Warehouse, models.Inventory.warehouse_id == models.Warehouse.id
    ).filter(
        models.Warehouse.organization_id == organization_id
    ).group_by(
        models.Part.id, models.Part.part_number, models.Part.name, models.Part.unit_of_measure
    ).order_by(models.Part.part_number).all()
    
    return [
        {
            'part_id': str(row.part_id),
            'part_number': row.part_number,
            'part_name': row.part_name,
            'unit_of_measure': row.unit_of_measure,
            'total_stock': float(row.total_stock),
            'warehouse_count': row.warehouse_count,
            'total_minimum_stock': float(row.total_min_stock),
            'is_low_stock': float(row.total_stock) <= float(row.total_min_stock)
        }
        for row in results
    ]


def transfer_inventory_between_warehouses(db: Session, from_warehouse_id: uuid.UUID, 
                                        to_warehouse_id: uuid.UUID, part_id: uuid.UUID, 
                                        quantity: Decimal, performed_by_user_id: uuid.UUID) -> dict:
    """Transfer inventory between warehouses with enhanced error handling and type safety."""
    try:
        # Ensure quantity is Decimal type and validate
        if not isinstance(quantity, Decimal):
            try:
                quantity = Decimal(str(quantity))
            except (InvalidOperation, ValueError) as e:
                logger.error(f"Invalid quantity format: {quantity}")
                raise HTTPException(status_code=400, detail=f"Invalid quantity format: {str(e)}")
        
        # Validate quantity precision (3 decimal places max)
        if quantity.as_tuple().exponent < -3:
            raise HTTPException(status_code=400, detail="Quantity precision cannot exceed 3 decimal places")
        
        # Validate quantity is positive
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        
        # Validate warehouses exist
        from_warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == from_warehouse_id).first()
        to_warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == to_warehouse_id).first()
        
        if not from_warehouse:
            raise HTTPException(status_code=404, detail="Source warehouse not found")
        if not to_warehouse:
            raise HTTPException(status_code=404, detail="Destination warehouse not found")
        
        # Validate warehouses are different
        if from_warehouse_id == to_warehouse_id:
            raise HTTPException(status_code=400, detail="Source and destination warehouses must be different")
        
        # Get part for validation and unit of measure
        part = db.query(models.Part).filter(models.Part.id == part_id).first()
        if not part:
            raise HTTPException(status_code=404, detail="Part not found")
        
        # Get source inventory
        from_inventory = db.query(models.Inventory).filter(
            models.Inventory.warehouse_id == from_warehouse_id,
            models.Inventory.part_id == part_id
        ).first()
        
        if not from_inventory:
            raise HTTPException(status_code=400, detail="Part not found in source warehouse")
        
        # Check sufficient stock
        if from_inventory.current_stock < quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock. Available: {from_inventory.current_stock}, Requested: {quantity}"
            )
        
        # Get or create destination inventory
        to_inventory = db.query(models.Inventory).filter(
            models.Inventory.warehouse_id == to_warehouse_id,
            models.Inventory.part_id == part_id
        ).first()
        
        # Store before values for audit
        before_stock_source = from_inventory.current_stock
        before_stock_destination = to_inventory.current_stock if to_inventory else Decimal('0')
        
        # Note: Inventory updates are handled automatically by the database trigger
        # 'trigger_update_inventory_on_transaction' when the transaction is inserted.
        # We don't need to manually update inventory here to avoid double updates.
        
        # Create comprehensive transaction record (only using fields that exist in database)
        transaction = models.Transaction(
            transaction_type="transfer",  # Use string value directly
            part_id=part_id,
            from_warehouse_id=from_warehouse_id,
            to_warehouse_id=to_warehouse_id,
            quantity=quantity,
            unit_of_measure=part.unit_of_measure,
            performed_by_user_id=performed_by_user_id,
            transaction_date=datetime.now(),
            notes=f"Transfer from {from_warehouse.name} to {to_warehouse.name}",
            reference_number=None
        )
        db.add(transaction)
        
        # Commit all changes atomically (trigger will update inventory)
        db.commit()
        db.refresh(transaction)
        
        # Fetch updated inventory values after trigger execution
        updated_from_inventory = db.query(models.Inventory).filter(
            models.Inventory.warehouse_id == from_warehouse_id,
            models.Inventory.part_id == part_id
        ).first()
        
        updated_to_inventory = db.query(models.Inventory).filter(
            models.Inventory.warehouse_id == to_warehouse_id,
            models.Inventory.part_id == part_id
        ).first()
        
        # Invalidate cache for both warehouses
        invalidate_warehouse_analytics_cache(str(from_warehouse_id))
        invalidate_warehouse_analytics_cache(str(to_warehouse_id))
        
        # Return detailed transfer result
        return {
            "success": True,
            "transaction_id": str(transaction.id),
            "part_number": part.part_number,
            "part_name": part.name,
            "quantity_transferred": float(quantity),
            "unit_of_measure": part.unit_of_measure,
            "source_warehouse": {
                "id": str(from_warehouse_id),
                "name": from_warehouse.name,
                "stock_before": float(before_stock_source),
                "stock_after": float(updated_from_inventory.current_stock) if updated_from_inventory else 0.0
            },
            "destination_warehouse": {
                "id": str(to_warehouse_id),
                "name": to_warehouse.name,
                "stock_before": float(before_stock_destination),
                "stock_after": float(updated_to_inventory.current_stock) if updated_to_inventory else float(quantity)
            },
            "transfer_date": transaction.transaction_date.isoformat()
        }
        
    except HTTPException:
        db.rollback()
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error transferring inventory: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during inventory transfer")


def get_inventory_balance_calculations(db: Session, warehouse_id: uuid.UUID) -> List[dict]:
    """Calculate inventory balances based on transactions for a warehouse."""
    from sqlalchemy import func, case
    
    # Get all transactions affecting this warehouse
    results = db.query(
        models.Transaction.part_id,
        models.Part.part_number,
        models.Part.name.label('part_name'),
        models.Part.unit_of_measure,
        func.sum(
            case(
                (models.Transaction.to_warehouse_id == warehouse_id, models.Transaction.quantity),
                else_=0
            )
        ).label('total_in'),
        func.sum(
            case(
                (models.Transaction.from_warehouse_id == warehouse_id, models.Transaction.quantity),
                else_=0
            )
        ).label('total_out')
    ).join(
        models.Part, models.Transaction.part_id == models.Part.id
    ).filter(
        or_(
            models.Transaction.from_warehouse_id == warehouse_id,
            models.Transaction.to_warehouse_id == warehouse_id
        )
    ).group_by(
        models.Transaction.part_id, models.Part.part_number, 
        models.Part.name, models.Part.unit_of_measure
    ).all()
    
    return [
        {
            'part_id': str(row.part_id),
            'part_number': row.part_number,
            'part_name': row.part_name,
            'unit_of_measure': row.unit_of_measure,
            'total_in': float(row.total_in or 0),
            'total_out': float(row.total_out or 0),
            'calculated_balance': float((row.total_in or 0) - (row.total_out or 0))
        }
        for row in results
    ]


@cached_analytics(ttl=900)  # Cache for 15 minutes
def get_warehouse_analytics(db: Session, warehouse_id: uuid.UUID, start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None, days: int = 30) -> dict:
    """
    Calculate comprehensive analytics for a warehouse including inventory summary, 
    top parts by value, stock movements, and turnover metrics.
    
    Args:
        db: Database session
        warehouse_id: UUID of the warehouse
        start_date: Optional start date for analytics period
        end_date: Optional end date for analytics period  
        days: Number of days to include (default: 30)
        
    Returns:
        Dictionary with comprehensive warehouse analytics data
        
    Raises:
        HTTPException: If warehouse not found or calculation errors occur
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func, case, desc, and_
    from sqlalchemy.exc import SQLAlchemyError, DatabaseError
    
    try:
        # Validate input parameters
        if not isinstance(warehouse_id, uuid.UUID):
            raise HTTPException(
                status_code=400, 
                detail="Invalid warehouse ID format. Must be a valid UUID."
            )
        
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=400,
                detail="Days parameter must be between 1 and 365"
            )
        
        # Validate date range if provided
        if start_date and end_date:
            if start_date > end_date:
                raise HTTPException(
                    status_code=400,
                    detail="Start date must be before or equal to end date"
                )
            
            # Check if date range is reasonable (not more than 2 years)
            if (end_date - start_date).days > 730:
                raise HTTPException(
                    status_code=400,
                    detail="Date range cannot exceed 2 years (730 days)"
                )
        
        # Validate warehouse exists and get warehouse info
        try:
            warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching warehouse {warehouse_id}: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Database error occurred while validating warehouse"
            )
        
        if not warehouse:
            raise HTTPException(
                status_code=404, 
                detail=f"Warehouse with ID {warehouse_id} not found"
            )
        
        # Check if warehouse is active
        if not warehouse.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot generate analytics for inactive warehouse '{warehouse.name}'"
            )
        
        # Set date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=days)
        
        # Validate final date range
        if start_date > datetime.utcnow():
            raise HTTPException(
                status_code=400,
                detail="Start date cannot be in the future"
            )
            
        # 1. Inventory Summary with error handling
        try:
            inventory_summary_query = db.query(
                func.count(models.Inventory.id).label('total_parts'),
                func.sum(
                    case(
                        (models.Inventory.current_stock <= models.Inventory.minimum_stock_recommendation, 1),
                        else_=0
                    )
                ).label('low_stock_parts'),
                func.sum(
                    case(
                        (models.Inventory.current_stock == 0, 1),
                        else_=0
                    )
                ).label('out_of_stock_parts')
            ).filter(
                models.Inventory.warehouse_id == warehouse_id
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error calculating inventory summary for warehouse {warehouse_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while calculating inventory summary"
            )
        
        # Calculate total value using recent order prices with error handling
        try:
            total_value_query = db.query(
                func.coalesce(
                    func.sum(models.Inventory.current_stock * models.SupplierOrderItem.unit_price), 0
                ).label('total_value')
            ).join(
                models.SupplierOrderItem, models.Inventory.part_id == models.SupplierOrderItem.part_id
            ).join(
                models.SupplierOrder, models.SupplierOrderItem.supplier_order_id == models.SupplierOrder.id
            ).filter(
                models.Inventory.warehouse_id == warehouse_id,
                models.SupplierOrderItem.unit_price.isnot(None)
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error calculating total value for warehouse {warehouse_id}: {e}")
            # Continue with zero value rather than failing completely
            total_value_query = type('obj', (object,), {'total_value': 0})
        
        inventory_summary = {
            'total_parts': int(inventory_summary_query.total_parts or 0),
            'total_value': float(total_value_query.total_value or 0) if total_value_query else 0.0,
            'low_stock_parts': int(inventory_summary_query.low_stock_parts or 0),
            'out_of_stock_parts': int(inventory_summary_query.out_of_stock_parts or 0)
        }
        
        # 2. Top Parts by Value (top 10) - using recent supplier order prices with error handling
        try:
            top_parts_subquery = db.query(
                models.SupplierOrderItem.part_id,
                func.avg(models.SupplierOrderItem.unit_price).label('avg_unit_price')
            ).join(
                models.SupplierOrder, models.SupplierOrderItem.supplier_order_id == models.SupplierOrder.id
            ).filter(
                models.SupplierOrderItem.unit_price.isnot(None),
                models.SupplierOrder.order_date >= start_date - timedelta(days=365)  # Use prices from last year
            ).group_by(
                models.SupplierOrderItem.part_id
            ).subquery()
            
            top_parts_query = db.query(
                models.Part.id.label('part_id'),
                models.Part.name.label('part_name'),
                models.Inventory.current_stock.label('quantity'),
                func.coalesce(top_parts_subquery.c.avg_unit_price, 0).label('unit_price'),
                (models.Inventory.current_stock * func.coalesce(top_parts_subquery.c.avg_unit_price, 0)).label('total_value')
            ).join(
                models.Inventory, models.Part.id == models.Inventory.part_id
            ).outerjoin(
                top_parts_subquery, models.Part.id == top_parts_subquery.c.part_id
            ).filter(
                models.Inventory.warehouse_id == warehouse_id,
                models.Inventory.current_stock > 0
            ).order_by(
                desc('total_value')
            ).limit(10).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error calculating top parts for warehouse {warehouse_id}: {e}")
            # Continue with empty list rather than failing completely
            top_parts_query = []
        
        top_parts_by_value = [
            {
                'part_id': str(row.part_id),
                'part_name': row.part_name,
                'quantity': float(row.quantity),
                'unit_price': float(row.unit_price or 0),
                'total_value': float(row.total_value or 0)
            }
            for row in top_parts_query
        ]
        
        # 3. Stock Movements (within date range) with error handling
        try:
            stock_movements_query = db.query(
                func.coalesce(
                    func.sum(
                        case(
                            (models.Transaction.to_warehouse_id == warehouse_id, models.Transaction.quantity),
                            else_=0
                        )
                    ), 0
                ).label('total_inbound'),
                func.coalesce(
                    func.sum(
                        case(
                            (models.Transaction.from_warehouse_id == warehouse_id, models.Transaction.quantity),
                            else_=0
                        )
                    ), 0
                ).label('total_outbound')
            ).filter(
                or_(
                    models.Transaction.from_warehouse_id == warehouse_id,
                    models.Transaction.to_warehouse_id == warehouse_id
                ),
                models.Transaction.transaction_date >= start_date,
                models.Transaction.transaction_date <= end_date
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error calculating stock movements for warehouse {warehouse_id}: {e}")
            # Continue with zero values rather than failing completely
            stock_movements_query = type('obj', (object,), {'total_inbound': 0, 'total_outbound': 0})
        
        total_inbound = float(stock_movements_query.total_inbound or 0)
        total_outbound = float(stock_movements_query.total_outbound or 0)
        
        stock_movements = {
            'total_inbound': total_inbound,
            'total_outbound': total_outbound,
            'net_change': total_inbound - total_outbound
        }
        
        # 4. Turnover Metrics (simplified calculation) with error handling
        # Calculate average days between transactions for parts with activity
        try:
            turnover_query = db.query(
                models.Transaction.part_id,
                func.count(models.Transaction.id).label('transaction_count'),
                func.max(models.Transaction.transaction_date).label('last_transaction'),
                func.min(models.Transaction.transaction_date).label('first_transaction')
            ).filter(
                or_(
                    models.Transaction.from_warehouse_id == warehouse_id,
                    models.Transaction.to_warehouse_id == warehouse_id
                ),
                models.Transaction.transaction_date >= start_date,
                models.Transaction.transaction_date <= end_date
            ).group_by(
                models.Transaction.part_id
            ).having(
                func.count(models.Transaction.id) > 1
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error calculating turnover metrics for warehouse {warehouse_id}: {e}")
            # Continue with empty list rather than failing completely
            turnover_query = []
        
        # Calculate turnover metrics
        if turnover_query:
            total_turnover_days = 0
            valid_parts = 0
            fast_moving_parts = 0
            slow_moving_parts = 0
            
            for row in turnover_query:
                if row.last_transaction and row.first_transaction:
                    days_span = (row.last_transaction - row.first_transaction).days
                    if days_span > 0:
                        avg_days_between_transactions = days_span / (row.transaction_count - 1)
                        total_turnover_days += avg_days_between_transactions
                        valid_parts += 1
                        
                        # Classify as fast/slow moving (arbitrary thresholds)
                        if avg_days_between_transactions <= 7:  # Weekly or more frequent
                            fast_moving_parts += 1
                        elif avg_days_between_transactions >= 30:  # Monthly or less frequent
                            slow_moving_parts += 1
            
            average_turnover_days = total_turnover_days / valid_parts if valid_parts > 0 else 0
        else:
            average_turnover_days = 0
            fast_moving_parts = 0
            slow_moving_parts = 0
        
        turnover_metrics = {
            'average_turnover_days': round(average_turnover_days, 2),
            'fast_moving_parts': fast_moving_parts,
            'slow_moving_parts': slow_moving_parts
        }
        
        # Compile final analytics response
        analytics_data = {
            'warehouse_id': str(warehouse_id),
            'warehouse_name': warehouse.name,
            'analytics_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'inventory_summary': inventory_summary,
            'top_parts_by_value': top_parts_by_value,
            'stock_movements': stock_movements,
            'turnover_metrics': turnover_metrics
        }
        
        return analytics_data
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except SQLAlchemyError as e:
        logger.error(f"Database error calculating warehouse analytics for warehouse {warehouse_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Database error occurred while calculating warehouse analytics"
        )
    except ValueError as e:
        logger.error(f"Value error in warehouse analytics calculation for warehouse {warehouse_id}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid data encountered during analytics calculation: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error calculating warehouse analytics for warehouse {warehouse_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while calculating warehouse analytics"
        )


@cached_analytics(ttl=900)  # Cache for 15 minutes
def get_warehouse_analytics_trends(db: Session, warehouse_id: uuid.UUID, period: str = "daily", 
                                 days: int = 30) -> dict:
    """
    Calculate trend data for warehouse analytics with daily, weekly, and monthly aggregation options.
    
    Args:
        db: Database session
        warehouse_id: UUID of the warehouse
        period: Aggregation period ("daily", "weekly", "monthly")
        days: Number of days to include (default: 30)
        
    Returns:
        Dictionary with trend data points for the specified period
        
    Raises:
        HTTPException: If warehouse not found or calculation errors occur
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func, case, and_, or_, text
    from sqlalchemy.exc import SQLAlchemyError, DatabaseError
    
    try:
        # Validate input parameters
        if not isinstance(warehouse_id, uuid.UUID):
            raise HTTPException(
                status_code=400, 
                detail="Invalid warehouse ID format. Must be a valid UUID."
            )
        
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=400,
                detail="Days parameter must be between 1 and 365"
            )
        
        # Validate period parameter
        valid_periods = ["daily", "weekly", "monthly"]
        if period not in valid_periods:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid period '{period}'. Must be one of: {', '.join(valid_periods)}"
            )
        
        # Validate warehouse exists with error handling
        try:
            warehouse = db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching warehouse {warehouse_id}: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Database error occurred while validating warehouse"
            )
        
        if not warehouse:
            raise HTTPException(
                status_code=404, 
                detail=f"Warehouse with ID {warehouse_id} not found"
            )
        
        # Check if warehouse is active
        if not warehouse.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot generate analytics trends for inactive warehouse '{warehouse.name}'"
            )
        
        # Calculate date range with validation
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Validate date range is reasonable
        if start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="Invalid date range calculated"
            )
        
        # Define date truncation based on period with error handling
        try:
            if period == "daily":
                date_trunc = func.date_trunc('day', models.Transaction.transaction_date)
                date_format = 'YYYY-MM-DD'
            elif period == "weekly":
                date_trunc = func.date_trunc('week', models.Transaction.transaction_date)
                date_format = 'YYYY-MM-DD'
            else:  # monthly
                date_trunc = func.date_trunc('month', models.Transaction.transaction_date)
                date_format = 'YYYY-MM-DD'
        except Exception as e:
            logger.error(f"Error setting up date truncation for period {period}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error configuring date aggregation"
            )
        
        # Query for transaction trends with comprehensive error handling
        try:
            trends_query = db.query(
                date_trunc.label('period_date'),
                func.count(models.Transaction.id).label('transactions_count'),
                func.count(func.distinct(models.Transaction.part_id)).label('parts_count'),
                func.coalesce(
                    func.sum(
                        case(
                            (models.Transaction.to_warehouse_id == warehouse_id, models.Transaction.quantity),
                            else_=0
                        )
                    ), 0
                ).label('total_inbound'),
                func.coalesce(
                    func.sum(
                        case(
                            (models.Transaction.from_warehouse_id == warehouse_id, models.Transaction.quantity),
                            else_=0
                        )
                    ), 0
                ).label('total_outbound')
            ).filter(
                or_(
                    models.Transaction.from_warehouse_id == warehouse_id,
                    models.Transaction.to_warehouse_id == warehouse_id
                ),
                models.Transaction.transaction_date >= start_date,
                models.Transaction.transaction_date <= end_date
            ).group_by(
                date_trunc
            ).order_by(
                date_trunc
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error executing trends query for warehouse {warehouse_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Database error occurred while calculating trends data"
            )
        
        # Query for inventory value trends (using recent supplier order prices) with error handling
        # Create subquery for average part prices
        try:
            price_subquery = db.query(
                models.SupplierOrderItem.part_id,
                func.avg(models.SupplierOrderItem.unit_price).label('avg_unit_price')
            ).join(
                models.SupplierOrder, models.SupplierOrderItem.supplier_order_id == models.SupplierOrder.id
            ).filter(
                models.SupplierOrderItem.unit_price.isnot(None),
                models.SupplierOrder.order_date >= start_date - timedelta(days=365)  # Use prices from last year
            ).group_by(
                models.SupplierOrderItem.part_id
            ).subquery()
        except SQLAlchemyError as e:
            logger.error(f"Database error creating price subquery for warehouse {warehouse_id}: {e}")
            # Continue without price data rather than failing completely
            price_subquery = None
        
        # Generate complete date range for the period
        trends_data = []
        current_date = start_date
        
        # Create a dictionary for quick lookup of actual data
        trends_dict = {}
        for row in trends_query:
            period_key = row.period_date.date()
            trends_dict[period_key] = {
                'transactions_count': int(row.transactions_count),
                'parts_count': int(row.parts_count),
                'total_inbound': float(row.total_inbound),
                'total_outbound': float(row.total_outbound),
                'net_change': float(row.total_inbound - row.total_outbound)
            }
        
        # Generate data points for each period in the range
        while current_date <= end_date:
            if period == "daily":
                period_key = current_date.date()
                next_date = current_date + timedelta(days=1)
            elif period == "weekly":
                # Start of week (Monday)
                days_since_monday = current_date.weekday()
                period_start = current_date - timedelta(days=days_since_monday)
                period_key = period_start.date()
                next_date = current_date + timedelta(days=7)
            else:  # monthly
                # Start of month
                period_start = current_date.replace(day=1)
                period_key = period_start.date()
                # Next month
                if current_date.month == 12:
                    next_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    next_date = current_date.replace(month=current_date.month + 1)
            
            # Get data for this period or use defaults
            period_data = trends_dict.get(period_key, {
                'transactions_count': 0,
                'parts_count': 0,
                'total_inbound': 0.0,
                'total_outbound': 0.0,
                'net_change': 0.0
            })
            
            # Calculate inventory value for this period (simplified - current inventory value) with error handling
            if period_key == current_date.date() or len(trends_data) == 0:
                # For the current period or first data point, calculate current inventory value
                try:
                    if price_subquery is not None:
                        inventory_value_query = db.query(
                            func.coalesce(
                                func.sum(models.Inventory.current_stock * func.coalesce(price_subquery.c.avg_unit_price, 0)), 0
                            ).label('total_value'),
                            func.coalesce(
                                func.sum(models.Inventory.current_stock), 0
                            ).label('total_quantity')
                        ).outerjoin(
                            price_subquery, models.Inventory.part_id == price_subquery.c.part_id
                        ).filter(
                            models.Inventory.warehouse_id == warehouse_id
                        ).first()
                    else:
                        # Fallback query without price data
                        inventory_value_query = db.query(
                            func.coalesce(func.sum(models.Inventory.current_stock), 0).label('total_quantity')
                        ).filter(
                            models.Inventory.warehouse_id == warehouse_id
                        ).first()
                        inventory_value_query.total_value = 0
                    
                    total_value = float(inventory_value_query.total_value or 0)
                    total_quantity = float(inventory_value_query.total_quantity or 0)
                except SQLAlchemyError as e:
                    logger.error(f"Database error calculating inventory value for warehouse {warehouse_id}: {e}")
                    # Continue with zero values rather than failing
                    total_value = 0.0
                    total_quantity = 0.0
                except (ValueError, TypeError) as e:
                    logger.error(f"Data conversion error in inventory value calculation: {e}")
                    total_value = 0.0
                    total_quantity = 0.0
            else:
                # For historical periods, use the previous value (simplified approach)
                # In a real implementation, you might want to calculate historical inventory levels
                total_value = trends_data[-1]['total_value'] if trends_data else 0.0
                total_quantity = trends_data[-1]['total_quantity'] if trends_data else 0.0
            
            trend_point = {
                'date': period_key.isoformat(),
                'total_value': total_value,
                'total_quantity': total_quantity,
                'parts_count': period_data['parts_count'],
                'transactions_count': period_data['transactions_count'],
                'total_inbound': period_data['total_inbound'],
                'total_outbound': period_data['total_outbound'],
                'net_change': period_data['net_change']
            }
            
            trends_data.append(trend_point)
            current_date = next_date
            
            # Break if we've exceeded the end date
            if current_date > end_date:
                break
        
        # Compile final trends response
        trends_response = {
            'warehouse_id': str(warehouse_id),
            'period': period,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'trends': trends_data
        }
        
        return trends_response
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except SQLAlchemyError as e:
        logger.error(f"Database error calculating warehouse analytics trends for warehouse {warehouse_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Database error occurred while calculating warehouse analytics trends"
        )
    except ValueError as e:
        logger.error(f"Value error in warehouse analytics trends calculation for warehouse {warehouse_id}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid data encountered during trends calculation: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error calculating warehouse analytics trends for warehouse {warehouse_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while calculating warehouse analytics trends"
        )