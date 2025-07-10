# c:/abparts/backend/app/routers/supplier_orders.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload
from typing import List

from .. import models, schemas, crud
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.SupplierOrderResponse, status_code=201)
def create_supplier_order(order: schemas.SupplierOrderCreate, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    # Assuming a crud function exists to handle creation logic
    return crud.supplier_order.create(db=db, order=order)

@router.get("/", response_model=List[schemas.SupplierOrderResponse])
def read_supplier_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    """
    Retrieves a list of supplier orders, with their items and part details eagerly loaded.
    """
    orders = db.query(models.SupplierOrder).options(
        selectinload(models.SupplierOrder.items).selectinload(models.SupplierOrderItem.part)
    ).order_by(models.SupplierOrder.order_date.desc()).offset(skip).limit(limit).all()
    return orders