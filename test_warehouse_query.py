#!/usr/bin/env python3
"""Direct test of warehouse query"""

import sys
import os
sys.path.insert(0, 'backend')
os.environ['DATABASE_URL'] = 'postgresql://abparts_user:abparts_password@localhost:5432/abparts_dev'

from app.database import SessionLocal
from app import models

db = SessionLocal()

# Test order ID
order_id = "f732cf73-48e3-449c-9107-e1e00d623cd8"

# Get the order
order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()

if order:
    print(f"Order ID: {order.id}")
    print(f"Status: {order.status}")
    
    # Query for transaction
    txn = db.query(models.Transaction).filter(
        models.Transaction.customer_order_id == order.id,
        models.Transaction.to_warehouse_id.isnot(None)
    ).first()
    
    if txn:
        print(f"\nTransaction found:")
        print(f"  ID: {txn.id}")
        print(f"  To Warehouse ID: {txn.to_warehouse_id}")
        
        # Get warehouse
        warehouse = db.query(models.Warehouse).filter(
            models.Warehouse.id == txn.to_warehouse_id
        ).first()
        
        if warehouse:
            print(f"\nWarehouse found:")
            print(f"  ID: {warehouse.id}")
            print(f"  Name: {warehouse.name}")
        else:
            print("\nWarehouse NOT found")
    else:
        print("\nTransaction NOT found")
        print("Checking all transactions for this order:")
        all_txns = db.query(models.Transaction).filter(
            models.Transaction.customer_order_id == order.id
        ).all()
        print(f"Found {len(all_txns)} transactions")
        for t in all_txns:
            print(f"  - {t.id}: to_warehouse_id={t.to_warehouse_id}")
else:
    print("Order not found")

db.close()
