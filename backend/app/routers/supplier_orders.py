# backend/app/routers/supplier_orders.py

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud, models # Import schemas, CRUD functions, and models
from ..database import get_db # Import DB session dependency
from ..auth import get_current_user, has_role, has_roles, TokenData # Import authentication dependencies

router = APIRouter()

# --- Supplier Orders CRUD ---
@router.get("/", response_model=List[schemas.SupplierOrderResponse])
async def get_supplier_orders(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager", "Supplier User"]))
):
    if current_user.role in ["Oraseas Admin", "Oraseas Inventory Manager"]:
        orders = crud.supplier_orders.get_supplier_orders(db)
    elif current_user.role == "Supplier User":
        # Supplier users can only view orders placed by their own organization (if they are a supplier org)
        # This assumes supplier user is associated with a 'Supplier' type organization
        organization = db.query(models.Organization).filter(models.Organization.id == current_user.organization_id).first()
        if not organization or organization.type != 'Supplier':
            raise HTTPException(status_code=403, detail="Supplier user not associated with a Supplier Organization.")
        orders = db.query(models.SupplierOrder).filter(models.SupplierOrder.ordering_organization_id == current_user.organization_id).all()
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view supplier orders")
    return orders

@router.get("/{order_id}", response_model=schemas.SupplierOrderResponse)
async def get_supplier_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager", "Supplier User"]))
):
    order = crud.supplier_orders.get_supplier_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Supplier order not found")
    
    if current_user.role in ["Oraseas Admin", "Oraseas Inventory Manager"] or \
       (current_user.role == "Supplier User" and order.ordering_organization_id == current_user.organization_id):
        return order
    else:
        raise HTTPException(status_code=403, detail="Not authorized to view this supplier order")

@router.post("/", response_model=schemas.SupplierOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier_order(
    order: schemas.SupplierOrderCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager"])) # Only Oraseas roles can place supplier orders
):
    # Ensure the ordering_organization_id matches the Oraseas EE organization ID
    oraseas_org = db.query(models.Organization).filter(models.Organization.name == 'Oraseas EE').first()
    if not oraseas_org or order.ordering_organization_id != oraseas_org.id:
        raise HTTPException(status_code=403, detail="Only Oraseas EE can place supplier orders.")

    db_order = crud.supplier_orders.create_supplier_order(db, order)
    if not db_order:
        raise HTTPException(status_code=400, detail="Failed to create supplier order")
    return db_order

@router.put("/{order_id}", response_model=schemas.SupplierOrderResponse)
async def update_supplier_order(
    order_id: uuid.UUID,
    order_update: schemas.SupplierOrderUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_roles(["Oraseas Admin", "Oraseas Inventory Manager"])) # Only Oraseas roles can update
):
    db_order = crud.supplier_orders.get_supplier_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Supplier order not found")

    # Ensure the order belongs to Oraseas EE
    oraseas_org = db.query(models.Organization).filter(models.Organization.name == 'Oraseas EE').first()
    if not oraseas_org or db_order.ordering_organization_id != oraseas_org.id:
        raise HTTPException(status_code=403, detail="Cannot update supplier orders not placed by Oraseas EE.")

    # Prevent changing ordering_organization_id
    if order_update.ordering_organization_id is not None and order_update.ordering_organization_id != db_order.ordering_organization_id:
        raise HTTPException(status_code=403, detail="Cannot change ordering organization ID for a supplier order.")

    updated_order = crud.supplier_orders.update_supplier_order(db, order_id, order_update)
    if not updated_order:
        raise HTTPException(status_code=400, detail="Failed to update supplier order")
    return updated_order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(has_role("Oraseas Admin")) # Only Oraseas Admin can delete
):
    db_order = crud.supplier_orders.get_supplier_order(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Supplier order not found")

    oraseas_org = db.query(models.Organization).filter(models.Organization.name == 'Oraseas EE').first()
    if not oraseas_org or db_order.ordering_organization_id != oraseas_org.id:
        raise HTTPException(status_code=403, detail="Cannot delete supplier orders not placed by Oraseas EE.")
    
    result = crud.supplier_orders.delete_supplier_order(db, order_id)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to delete supplier order")
    return result
