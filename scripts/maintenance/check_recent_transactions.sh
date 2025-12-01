#!/bin/bash

echo "Checking recent consumption transactions..."
echo ""

docker compose exec -T db psql -U abparts_user -d abparts_dev << 'EOF'
-- Show last 10 consumption transactions
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
LIMIT 10;

-- Check for duplicate transactions (same part, machine, quantity, within 1 second)
SELECT 
    part_id,
    machine_id,
    quantity,
    COUNT(*) as count,
    array_agg(id) as transaction_ids,
    MIN(created_at) as first_created,
    MAX(created_at) as last_created
FROM transactions
WHERE transaction_type = 'consumption'
    AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY part_id, machine_id, quantity, DATE_TRUNC('second', created_at)
HAVING COUNT(*) > 1;
EOF
