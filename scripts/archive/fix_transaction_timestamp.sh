#!/bin/bash

echo "Fixing transaction timestamp to use created_at instead of midnight..."
echo ""

docker compose exec -T db psql -U abparts_user -d abparts_dev << 'EOF'
-- Update the transaction to use its created_at timestamp
UPDATE transactions
SET transaction_date = created_at
WHERE id = '55b137f4-4aa7-4c6a-99a3-8caf4f5995bd';

-- Verify
SELECT 
    id,
    transaction_type,
    transaction_date,
    created_at
FROM transactions
WHERE id = '55b137f4-4aa7-4c6a-99a3-8caf4f5995bd';
EOF

echo ""
echo "Transaction timestamp fixed!"
echo "Now the calculation should show 2 instead of 3."
