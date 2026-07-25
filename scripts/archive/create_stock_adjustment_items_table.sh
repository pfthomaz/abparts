#!/bin/bash

echo "=== Creating stock_adjustment_items table in production ==="
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod << 'EOF'
BEGIN;

-- Create stock_adjustment_items table
CREATE TABLE IF NOT EXISTS stock_adjustment_items (
    id UUID PRIMARY KEY,
    stock_adjustment_id UUID NOT NULL REFERENCES stock_adjustments(id) ON DELETE CASCADE,
    part_id UUID NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    quantity_before NUMERIC(10, 3) NOT NULL,
    quantity_after NUMERIC(10, 3) NOT NULL,
    quantity_change NUMERIC(10, 3) NOT NULL,
    reason TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_stock_adjustment_items_stock_adjustment_id ON stock_adjustment_items(stock_adjustment_id);
CREATE INDEX IF NOT EXISTS idx_stock_adjustment_items_part_id ON stock_adjustment_items(part_id);

-- Verify
SELECT 
    tablename,
    schemaname
FROM pg_tables 
WHERE tablename = 'stock_adjustment_items';

COMMIT;

SELECT 'Table created successfully!' as status;
EOF

echo ""
echo "Restarting API..."
docker compose -f docker-compose.prod.yml restart api

echo ""
echo "✓ stock_adjustment_items table created"
echo "✓ Indexes created"
echo "✓ API restarted"
echo ""
echo "Stock adjustments should now work!"
