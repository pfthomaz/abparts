#!/bin/bash

echo "Enter the TO warehouse ID:"
read TO_WAREHOUSE_ID

echo "Enter the part ID:"
read PART_ID

echo ""
echo "Checking transfer for part $PART_ID in warehouse $TO_WAREHOUSE_ID..."
echo ""

docker compose exec -T api python << EOF
import sys
sys.path.insert(0, '/app')

from app.database import SessionLocal
from app import models
from app.crud.inventory_calculator import calculate_current_stock
import uuid

db = SessionLocal()
try:
    warehouse_id = uuid.UUID('$TO_WAREHOUSE_ID')
    part_id = uuid.UUID('$PART_ID')
    
    # Check if inventory record exists
    inventory = db.query(models.Inventory).filter(
        models.Inventory.warehouse_id == warehouse_id,
        models.Inventory.part_id == part_id
    ).first()
    
    if inventory:
        print(f"✓ Inventory record EXISTS")
        print(f"  Cached stock: {inventory.current_stock}")
    else:
        print(f"✗ Inventory record DOES NOT EXIST")
        print(f"  This is the problem - record wasn't created")
    
    # Calculate stock
    calculated = calculate_current_stock(db, warehouse_id, part_id)
    print(f"  Calculated stock: {calculated}")
    
    # Check for transfer transactions
    print(f"\nTransfer transactions TO this warehouse:")
    transfers = db.query(models.Transaction).filter(
        models.Transaction.to_warehouse_id == warehouse_id,
        models.Transaction.part_id == part_id,
        models.Transaction.transaction_type == 'transfer'
    ).all()
    
    for txn in transfers:
        print(f"  {txn.transaction_date} | Quantity: {txn.quantity}")
    
    if not transfers:
        print(f"  No transfer transactions found")
        
finally:
    db.close()
EOF
