# c:/abparts/backend/app/routers/customer_orders.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, selectinload
from typing import List

from .. import models, schemas, crud
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.CustomerOrderResponse, status_code=201)
def create_customer_order(order: schemas.CustomerOrderCreate, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    # Assuming a crud function exists to handle creation logic
    return crud.customer_order.create(db=db, order=order, user_id=current_user.user_id)

@router.get("/", response_model=List[schemas.CustomerOrderResponse])
def read_customer_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    """
    Retrieves a list of customer orders, with their items, part details,
    and customer organization eagerly loaded.
    """
    orders = db.query(models.CustomerOrder).options(
        selectinload(models.CustomerOrder.items).selectinload(models.CustomerOrderItem.part),
        selectinload(models.CustomerOrder.customer_organization)
    ).order_by(models.CustomerOrder.order_date.desc()).offset(skip).limit(limit).all()
    return orders