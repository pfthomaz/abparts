#!/bin/bash
echo "Checking schemas.py in container..."
docker-compose exec api grep -n "class StockAdjustmentListResponse" /app/app/schemas.py
if [ $? -eq 0 ]; then
    echo "✅ Found in container"
else
    echo "❌ NOT found in container!"
    echo ""
    echo "Checking what stock adjustment schemas exist in container:"
    docker-compose exec api grep -n "class StockAdjustment" /app/app/schemas.py
fi
