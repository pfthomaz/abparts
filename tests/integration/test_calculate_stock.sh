#!/bin/bash

echo "Testing stock calculation for the part you just used..."
echo ""

docker compose exec -T api python << 'EOF'
import sys
sys.path.insert(0, '/app')

from app.database import SessionLocal
from app.crud.inventory_calculator import calculate_current_stock
import uuid

db = SessionLocal()
try:
    warehouse_id = uuid.UUID('1e019a80-2852-4269-b3d3-2c5a46ded47f')
    part_id = uuid.UUID('e1457957-9441-48d9-a161-75faff16bd5d')
    
    print(f"Calculating stock for:")
    print(f"  Warehouse: {warehouse_id}")
    print(f"  Part: {part_id}")
    print("")
    
    calculated_stock = calculate_current_stock(db, warehouse_id, part_id)
    
    print(f"Calculated Stock: {calculated_stock}")
    print("")
    
    # Also check what's in the database
    from app import models
    inventory = db.query(models.Inventory).filter(
        models.Inventory.warehouse_id == warehouse_id,
        models.Inventory.part_id == part_id
    ).first()
    
    if inventory:
        print(f"Cached Stock (in DB): {inventory.current_stock}")
    else:
        print("No inventory record found")
        
finally:
    db.close()
EOF
