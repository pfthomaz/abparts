#!/bin/bash

echo "Checking recent order receipts (creation transactions)..."
echo ""

docker compose exec -T db psql -U abparts_user -d abparts_dev << 'EOF'
-- Show recent creation transactions
SELECT 
    id,
    transaction_type,
    part_id,
    to_warehouse_id,
    quantity,
    transaction_date,
    created_at,
    notes
FROM transactions
WHERE transaction_type = 'creation'
ORDER BY created_at DESC
LIMIT 5;
EOF
