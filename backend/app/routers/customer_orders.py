# backend/app/routers/customer_orders.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, has_role, has_roles, TokenData # Import authentication dependencies

router = APIRouter()

# --- Customer Orders CRUD ---
@router.get("/", response_model=List[schemas.CustomerOrderResponse])
async def get_customer_orders(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    if current_user.role == "Oraseas Admin" or current_user.role == "Oraseas Inventory Manager":
        orders = crud.customer_orders.get_customer_orders(db)
    elif current_user.role in ["Customer Admin", "Customer User"]:
        orders = db.query(models.CustomerOrder).filter(models.CustomerOrder.customer_organization_id == current_user.organization_id).all()
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view customer orders")
    return orders

@router.get("/{order_id}", response_model=schemas.CustomerOrderResponse)
async def get_customer_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    order = crud.customer_orders.get_customer_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Customer order not found")

    if current_user.role in ["Oraseas Admin", "Oraseas Inventory Manager"] or \
       (current_user.role in ["Customer Admin", "Customer User"] and order.customer_organization_id == current_user.organization_id):
        return order
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this customer order")

@router.post("/", response_model=schemas.CustomerOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_customer_order(
    order: schemas.CustomerOrderCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager", "Customer Admin", "Customer User"]))
):
    # Validate FKs
    customer_org = db.query(models.Organization).filter(models.Organization.id == order.customer_organization_id).first()
    oraseas_org = db.query(models.Organization).filter(models.Organization.id == order.oraseas_organization_id).first()
    if not customer_org or not oraseas_org:
        raise HTTPException(status_code=400, detail="Customer or Oraseas Organization ID not found")
    if order.ordered_by_user_id:
        user = db.query(models.User).filter(models.User.id == order.ordered_by_user_id).first()
        if not user: raise HTTPException(status_code=400, detail="Ordered by User ID not found")
    
    # Authorization logic for creating customer orders:
    # Oraseas roles can create orders from any customer.
    # Customer roles can only create orders for their own organization.
    if current_user.role in ["Customer Admin", "Customer User"] and order.customer_organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Customers can only create orders for their own organization.")
    
    # If ordered_by_user_id is provided by a customer, ensure it's their own user ID
    if current_user.role in ["Customer Admin", "Customer User"] and order.ordered_by_user_id and order.ordered_by_user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Customers can only place orders as themselves.")
    
    # Ensure oraseas_organization_id is indeed Oraseas EE's ID
    if oraseas_org.name != 'Oraseas EE':
        raise HTTPException(status_code=400, detail="Orders must be placed with 'Oraseas EE' as the receiving organization.")

    db_order = crud.customer_orders.create_customer_order(db, order)
    if not db_order:
        raise HTTPException(status_code=400, detail="Failed to create customer order")
    return db_order

@router.put("/{order_id}", response_model=schemas.CustomerOrderResponse)
async def update_customer_order(
    order_id: uuid.UUID,
    order_update: schemas.CustomerOrderUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager", "Customer Admin", "Customer User"]))
):
    db_order = crud.customer_orders.get_customer_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Customer order not found")

    # Authorization logic for updating customer orders:
    # Oraseas roles can update any customer order.
    # Customer roles can only update their own organization's orders.
    if current_user.role in ["Oraseas Admin", "Oraseas Inventory Manager"] or \
       (current_user.role in ["Customer Admin", "Customer User"] and db_order.customer_organization_id == current_user.organization_id):
        
        # Prevent customers from changing key IDs or the Oraseas organization
        if current_user.role in ["Customer Admin", "Customer User"]:
            if order_update.customer_organization_id is not None and order_update.customer_organization_id != db_order.customer_organization_id:
                raise HTTPException(status_code=403, detail="Cannot change customer organization ID for an existing order.")
            if order_update.oraseas_organization_id is not None and order_update.oraseas_organization_id != db_order.oraseas_organization_id:
                raise HTTPException(status_code=403, detail="Cannot change Oraseas organization ID for an existing order.")
            if order_update.ordered_by_user_id is not None and order_update.ordered_by_user_id != db_order.ordered_by_user_id:
                 raise HTTPException(status_code=403, detail="Cannot change ordered by user for an existing order.")

        updated_order = crud.customer_orders.update_customer_order(db, order_id, order_update)
        if not updated_order:
            raise HTTPException(status_code=400, detail="Failed to update customer order")
        return updated_order
    else:
        raise HTTPException(status_code=403, detail="Not authorized to update this customer order")

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Customer Admin"])) # Only Admins can delete customer orders
):
    db_order = crud.customer_orders.get_customer_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Customer order not found")

    # Authorization for deletion:
    # Oraseas Admin can delete any customer order.
    # Customer Admin can only delete orders from their own organization.
    if current_user.role == "Oraseas Admin" or \
       (current_user.role == "Customer Admin" and db_order.customer_organization_id == current_user.organization_id):
        result = crud.customer_orders.delete_customer_order(db, order_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to delete customer order")
        return result
    else:
        raise HTTPException(status_code=403, detail="Not authorized to delete this customer order.")
