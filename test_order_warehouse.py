#!/usr/bin/env python3
"""Test script to check if order transactions are loaded"""

import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from app import models
from sqlalchemy.orm import selectinload

db = SessionLocal()

# Get the order
order_id = "f732cf73-48e3-449c-9107-e1e00d623cd8"

order = db.query(models.CustomerOrder).options(
    selectinload(models.CustomerOrder.transactions).selectinload(models.Transaction.to_warehouse)
).filter(models.CustomerOrder.id == order_id).first()

if order:
    print(f"Order ID: {order.id}")
    print(f"Status: {order.status}")
    print(f"Transactions count: {len(order.transactions)}")
    
    for txn in order.transactions:
        print(f"\nTransaction ID: {txn.id}")
        print(f"  Type: {txn.transaction_type}")
        print(f"  Customer Order ID: {txn.customer_order_id}")
        print(f"  To Warehouse ID: {txn.to_warehouse_id}")
        print(f"  To Warehouse: {txn.to_warehouse}")
        if txn.to_warehouse:
            print(f"  Warehouse Name: {txn.to_warehouse.name}")
else:
    print("Order not found")

db.close()
