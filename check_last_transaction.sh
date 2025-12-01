#!/bin/bash

echo "Checking last consumption transaction..."
echo ""

docker compose exec -T db psql -U abparts_user -d abparts_dev << 'EOF'
SELECT 
    id,
    transaction_type,
    part_id,
    from_warehouse_id,
    machine_id,
    quantity,
    transaction_date,
    created_at
FROM transactions
WHERE transaction_type = 'consumption'
ORDER BY created_at DESC
LIMIT 1;
EOF
