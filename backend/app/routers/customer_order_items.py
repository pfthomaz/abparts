# backend/app/routers/customer_order_items.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, has_role, has_roles, TokenData # Import authentication dependencies

router = APIRouter()

# --- Customer Order Items CRUD ---
@router.get("/", response_model=List[schemas.CustomerOrderItemResponse])
async def get_customer_order_items(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    if current_user.role in ["Oraseas Admin", "Oraseas Inventory Manager"]:
        items = crud.customer_order_items.get_customer_order_items(db)
    elif current_user.role in ["Customer Admin", "Customer User"]:
        # Customers can only see order items for orders placed by their own organization
        # First, get all customer orders associated with the current user's organization
        customer_orders_ids = [str(o.id) for o in db.query(models.CustomerOrder.id).filter(models.CustomerOrder.customer_organization_id == current_user.organization_id).all()]
        if not customer_orders_ids: # If customer has no orders, no items to show
            return []
        items = db.query(models.CustomerOrderItem).filter(models.CustomerOrderItem.customer_order_id.in_(customer_orders_ids)).all()
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view customer order items")
    return items

@router.get("/{item_id}", response_model=schemas.CustomerOrderItemResponse)
async def get_customer_order_item(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    item = crud.customer_order_items.get_customer_order_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Customer order item not found")

    customer_order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == item.customer_order_id).first()
    if not customer_order:
        raise HTTPException(status_code=404, detail="Associated customer order not found for item")

    if current_user.role in ["Oraseas Admin", "Oraseas Inventory Manager"] or \
       (current_user.role in ["Customer Admin", "Customer User"] and customer_order.customer_organization_id == current_user.organization_id):
        return item
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this customer order item")

@router.post("/", response_model=schemas.CustomerOrderItemResponse, status_code=status.HTTP_201_CREATED)
async def create_customer_order_item(
    item: schemas.CustomerOrderItemCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager", "Customer Admin", "Customer User"]))
):
    order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == item.customer_order_id).first()
    part = db.query(models.Part).filter(models.Part.id == item.part_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Customer Order ID not found")
    if not part:
        raise HTTPException(status_code=400, detail="Part ID not found")

    # Authorization logic: Customers can only add items to their own orders
    if current_user.role in ["Customer Admin", "Customer User"] and order.customer_organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Customers can only add items to their own orders.")

    db_item = crud.customer_order_items.create_customer_order_item(db, item)
    if not db_item:
        raise HTTPException(status_code=400, detail="Failed to create customer order item")
    return db_item

@router.put("/{item_id}", response_model=schemas.CustomerOrderItemResponse)
async def update_customer_order_item(
    item_id: uuid.UUID,
    item_update: schemas.CustomerOrderItemUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager", "Customer Admin"]))
):
    db_item = crud.customer_order_items.get_customer_order_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Customer order item not found")

    customer_order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == db_item.customer_order_id).first()
    if not customer_order:
        raise HTTPException(status_code=404, detail="Associated customer order not found")

    # Authorization: Customers can only update items in their own orders
    if current_user.role in ["Customer Admin"] and customer_order.customer_organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Customers can only update items in their own orders.")

    # Prevent changing customer_order_id or part_id
    if item_update.customer_order_id is not None and item_update.customer_order_id != db_item.customer_order_id:
        raise HTTPException(status_code=403, detail="Cannot change customer_order_id of an order item.")
    if item_update.part_id is not None and item_update.part_id != db_item.part_id:
        raise HTTPException(status_code=403, detail="Cannot change part_id of an order item.")

    updated_item = crud.customer_order_items.update_customer_order_item(db, item_id, item_update)
    if not updated_item:
        raise HTTPException(status_code=400, detail="Failed to update customer order item")
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer_order_item(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin"]))
):
    db_item = crud.customer_order_items.get_customer_order_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Customer order item not found")

    customer_order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == db_item.customer_order_id).first()
    if not customer_order:
        raise HTTPException(status_code=404, detail="Associated customer order not found")

    # Authorization: Customers can only delete items from their own orders
    if current_user.role == "Customer Admin" and customer_order.customer_organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Customers can only delete items from their own orders.")

    result = crud.customer_order_items.delete_customer_order_item(db, item_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to delete customer order item")
    return result
