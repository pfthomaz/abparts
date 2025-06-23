# backend/app/routers/supplier_order_items.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, has_role, has_roles, TokenData # Import authentication dependencies

router = APIRouter()

# --- Supplier Order Items CRUD ---
@router.get("/", response_model=List[schemas.SupplierOrderItemResponse])
async def get_supplier_order_items(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager"]))
):
    # Only Oraseas Admin/Inventory Manager can list all supplier order items.
    # Supplier User access to items is handled by specific order lookup, not direct list.
    if current_user.role not in ["Oraseas Admin", "Oraseas Inventory Manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to view all supplier order items.")
    
    items = crud.supplier_order_items.get_supplier_order_items(db)
    return items

@router.get("/{item_id}", response_model=schemas.SupplierOrderItemResponse)
async def get_supplier_order_item(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager", "Supplier User"]))
):
    item = crud.supplier_order_items.get_supplier_order_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Supplier order item not found")

    # Check if the user is authorized to view this item (it belongs to an Oraseas order)
    supplier_order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == item.supplier_order_id).first()
    if not supplier_order:
        raise HTTPException(status_code=404, detail="Associated supplier order not found for item")

    oraseas_org = db.query(models.Organization).filter(models.Organization.name == 'Oraseas EE').first()

    if current_user.role in ["Oraseas Admin", "Oraseas Inventory Manager"] or \
       (current_user.role == "Supplier User" and supplier_order.ordering_organization_id == oraseas_org.id): # Simplified: Supplier can see if Oraseas ordered from them
        return item
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this supplier order item")

@router.post("/", response_model=schemas.SupplierOrderItemResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier_order_item(
    item: schemas.SupplierOrderItemCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager"]))
):
    order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == item.supplier_order_id).first()
    part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Supplier Order ID not found")
    if not part:
        raise HTTPException(status_code=400, detail="Part ID not found")
    
    # Ensure the order belongs to Oraseas EE
    oraseas_org = db.query(models.Organization).filter(models.Organization.name == 'Oraseas EE').first()
    if not oraseas_org or order.ordering_organization_id != oraseas_org.id:
        raise HTTPException(status_code=403, detail="Cannot add items to supplier orders not placed by Oraseas EE.")

    db_item = crud.supplier_order_items.create_supplier_order_item(db, item)
    if not db_item:
        raise HTTPException(status_code=400, detail="Failed to create supplier order item")
    return db_item

@router.put("/{item_id}", response_model=schemas.SupplierOrderItemResponse)
async def update_supplier_order_item(
    item_id: uuid.UUID,
    item_update: schemas.SupplierOrderItemUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager"]))
):
    db_item = crud.supplier_order_items.get_supplier_order_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Supplier order item not found")

    supplier_order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == db_item.supplier_order_id).first()
    if not supplier_order:
        raise HTTPException(status_code=404, detail="Associated supplier order not found")

    oraseas_org = db.query(models.Organization).filter(models.Organization.name == 'Oraseas EE').first()
    if not oraseas_org or supplier_order.ordering_organization_id != oraseas_org.id:
        raise HTTPException(status_code=403, detail="Cannot update supplier order items not belonging to Oraseas EE orders.")

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
async def delete_supplier_order_item(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("Oraseas Admin"))
):
    db_item = crud.supplier_order_items.get_supplier_order_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Supplier order item not found")
    
    supplier_order = db.query(models.SupplierOrder).filter(models.SupplierOrder.id == db_item.supplier_order_id).first()
    if not supplier_order:
        raise HTTPException(status_code=404, detail="Associated supplier order not found")

    oraseas_org = db.query(models.Organization).filter(models.Organization.name == 'Oraseas EE').first()
    if not oraseas_org or supplier_order.ordering_organization_id != oraseas_org.id:
        raise HTTPException(status_code=403, detail="Cannot delete supplier order items not belonging to Oraseas EE orders.")

    result = crud.supplier_order_items.delete_supplier_order_item(db, item_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to delete supplier order item")
    return result
