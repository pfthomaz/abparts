#!/bin/bash
# Clear Python bytecode cache to force reimport

echo "Clearing Python cache in backend directory..."
find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find backend -type f -name "*.pyc" -delete 2>/dev/null || true

echo "Restarting API container..."
docker-compose restart api

echo "Waiting for API to be ready..."
sleep 5

echo "Testing import..."
docker-compose exec -T api python -c "from app.schemas import StockAdjustmentListResponse; print('✅ Import successful')"

echo "Done!"
