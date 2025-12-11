# backend/app/routers/supplier_order_items.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, TokenData # Import authentication dependencies
from ..permissions import (
    ResourceType, PermissionType, require_permission,
    OrganizationScopedQueries, check_organization_access, permission_checker
)

router = APIRouter()

# --- Supplier Order Items CRUD ---
@router.get("/", response_model=List[schemas.SupplierOrderItemResponse])
def get_supplier_order_items(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.READ))
):
    items = crud.supplier_order_items.get_supplier_order_items(db)
    
    # Filter based on user permissions
    if not permission_checker.is_super_admin(current_user):
        # Users can only see items from orders placed by their organization
        filtered_items = []
        for item in items:
            supplier_order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == item.supplier_order_id).first()
            if supplier_order and supplier_order.ordering_organization_id == current_user.organization_id:
                filtered_items.append(item)
        return filtered_items
    
    return items

@router.get("/{item_id}", response_model=schemas.SupplierOrderItemResponse)
def get_supplier_order_item(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.READ))
):
    item = crud.supplier_order_items.get_supplier_order_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Supplier order item not found")

    # Check permissions
    supplier_order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == item.supplier_order_id).first()
    if not supplier_order:
        raise HTTPException(status_code=404, detail="Associated supplier order not found for item")

    if not permission_checker.is_super_admin(current_user):
        if supplier_order.ordering_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied to this order item")

    return item

@router.post("/", response_model=schemas.SupplierOrderItemResponse, status_code=status.HTTP_201_CREATED)
def create_supplier_order_item(
    item: schemas.SupplierOrderItemCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.WRITE))
):
    order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == item.supplier_order_id).first()
    part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Supplier Order ID not found")
    if not part:
        raise HTTPException(status_code=400, detail="Part ID not found")
    
    # Check permissions - users can only add items to orders from their organization
    if not permission_checker.is_super_admin(current_user):
        if order.ordering_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Cannot add items to orders from other organizations")

    db_item = crud.supplier_order_items.create_supplier_order_item(db, item)
    if not db_item:
        raise HTTPException(status_code=400, detail="Failed to create supplier order item")
    return db_item

@router.put("/{item_id}", response_model=schemas.SupplierOrderItemResponse)
def update_supplier_order_item(
    item_id: uuid.UUID,
    item_update: schemas.SupplierOrderItemUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.WRITE))
):
    db_item = crud.supplier_order_items.get_supplier_order_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Supplier order item not found")

    supplier_order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == db_item.supplier_order_id).first()
    if not supplier_order:
        raise HTTPException(status_code=404, detail="Associated supplier order not found")

    # Check permissions
    if not permission_checker.is_super_admin(current_user):
        if supplier_order.ordering_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Cannot update order items from other organizations")

    # Prevent changing supplier_order_id or part_id
    if item_update.supplier_order_id is not None and item_update.supplier_order_id != db_item.supplier_order_id:
        raise HTTPException(status_code=403, detail="Cannot change supplier_order_id of an order item.")
    if item_update.part_id is not None and item_update.part_id != db_item.part_id:
        raise HTTPException(status_code=403, detail="Cannot change part_id of an order item.")

    updated_item = crud.supplier_order_items.update_supplier_order_item(db, item_id, item_update)
    if not updated_item:
        raise HTTPException(status_code=400, detail="Failed to update supplier order item")
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier_order_item(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission(ResourceType.ORDER, PermissionType.DELETE))
):
    db_item = crud.supplier_order_items.get_supplier_order_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Supplier order item not found")
    
    supplier_order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == db_item.supplier_order_id).first()
    if not supplier_order:
        raise HTTPException(status_code=404, detail="Associated supplier order not found")

    # Check permissions
    if not permission_checker.is_super_admin(current_user):
        if supplier_order.ordering_organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Cannot delete order items from other organizations")

    result = crud.supplier_order_items.delete_supplier_order_item(db, item_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to delete supplier order item")
    return result
