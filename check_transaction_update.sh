#!/bin/bash

echo "Enter the transaction ID you just edited:"
read TRANSACTION_ID

echo ""
echo "Checking transaction details..."
echo ""

docker compose exec -T db psql -U abparts_user -d abparts_dev << EOF
SELECT 
    id,
    transaction_type,
    part_id,
    quantity,
    transaction_date,
    created_at,
    notes
FROM transactions
WHERE id = '$TRANSACTION_ID';
EOF
