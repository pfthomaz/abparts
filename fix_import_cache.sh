#!/bin/bash
set -e

echo "=== Fixing Python Import Cache Issue ==="
echo ""

echo "Step 1: Clearing local Python cache..."
find backend -type d -name __pycache__ -print0 | xargs -0 rm -rf 2>/dev/null || true
find backend -type f -name "*.pyc" -print0 | xargs -0 rm -f 2>/dev/null || true
echo "✅ Local cache cleared"
echo ""

echo "Step 2: Rebuilding API container (no cache)..."
docker-compose build --no-cache api
echo "✅ Container rebuilt"
echo ""

echo "Step 3: Restarting services..."
docker-compose up -d
echo "✅ Services restarted"
echo ""

echo "Step 4: Waiting for API to be ready..."
sleep 10
echo ""

echo "Step 5: Testing import..."
docker-compose exec -T api python << 'EOF'
from app.schemas import StockAdjustmentListResponse
print("✅ StockAdjustmentListResponse imported successfully!")
print(f"   Fields: {list(StockAdjustmentListResponse.__fields__.keys())}")
EOF

echo ""
echo "=== Fix Complete ==="
