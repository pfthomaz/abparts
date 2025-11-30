#!/bin/bash
set -e

echo "=== Fixing reason_code Column ==="
echo ""

echo "Making reason_code nullable..."
docker-compose exec -T db psql -U abparts_user -d abparts_dev << 'EOF'
ALTER TABLE stock_adjustments 
ALTER COLUMN reason_code DROP NOT NULL;
EOF

echo ""
echo "✅ Column fixed - reason_code is now nullable"
echo ""
echo "You can now use the stock reset feature!"
