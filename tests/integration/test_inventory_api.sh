#!/bin/bash

echo "Testing inventory API response..."
echo ""
echo "Enter warehouse ID:"
read WAREHOUSE_ID

echo ""
echo "Fetching inventory for warehouse $WAREHOUSE_ID..."
echo ""

docker compose exec -T api python << EOF
import sys
sys.path.insert(0, '/app')

from app.database import SessionLocal
from app.crud.inventory import get_inventory_by_warehouse
import uuid

db = SessionLocal()
try:
    warehouse_id = uuid.UUID('$WAREHOUSE_ID')
    inventory = get_inventory_by_warehouse(db, warehouse_id)
    
    print(f"Found {len(inventory)} inventory items:")
    print("")
    for item in inventory[:5]:  # Show first 5
        print(f"Part: {item['part_number']} - {item['part_name']}")
        print(f"  Current Stock: {item['current_stock']}")
        print(f"  Part ID: {item['part_id']}")
        print("")
finally:
    db.close()
EOF
