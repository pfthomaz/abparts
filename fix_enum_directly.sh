#!/bin/bash
set -e

echo "=== Fixing AdjustmentType Enum Directly ==="
echo ""

echo "Step 1: Checking if stock_adjustments table has any data..."
COUNT=$(docker-compose exec -T db psql -U abparts_user -d abparts_dev -t -c "SELECT COUNT(*) FROM stock_adjustments;")
echo "Records in stock_adjustments: $COUNT"

if [ "$COUNT" -gt 0 ]; then
  echo "⚠️  Warning: Table has data. Manual intervention may be needed."
  exit 1
fi

echo ""
echo "Step 2: Dropping and recreating the enum type..."
docker-compose exec -T db psql -U abparts_user -d abparts_dev << 'EOF'
-- Drop the constraint and column temporarily
ALTER TABLE stock_adjustments DROP COLUMN adjustment_type;

-- Drop and recreate the enum
DROP TYPE IF EXISTS adjustmenttype CASCADE;

CREATE TYPE adjustmenttype AS ENUM (
    'stock_take',
    'damage',
    'loss',
    'found',
    'correction',
    'return',
    'other'
);

-- Add the column back with the new enum
ALTER TABLE stock_adjustments 
ADD COLUMN adjustment_type adjustmenttype NOT NULL;

EOF

echo ""
echo "Step 3: Verifying enum values..."
docker-compose exec -T db psql -U abparts_user -d abparts_dev -c "SELECT enumlabel FROM pg_enum WHERE enumtypid = 'adjustmenttype'::regtype ORDER BY enumsortorder;"

echo ""
echo "=== Enum Fixed Successfully ==="
echo ""
echo "You can now use the stock reset feature!"
