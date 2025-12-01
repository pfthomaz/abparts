#!/bin/bash

echo "Fixing all transactions with midnight timestamps..."
echo ""
echo "This will update transaction_date to match created_at for all transactions"
echo "where the time is exactly midnight (00:00:00)."
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

docker compose exec -T db psql -U abparts_user -d abparts_dev << 'EOF'
BEGIN;

-- Update all transactions where transaction_date is at midnight
-- to use their created_at timestamp instead
UPDATE transactions
SET transaction_date = created_at
WHERE EXTRACT(HOUR FROM transaction_date) = 0
  AND EXTRACT(MINUTE FROM transaction_date) = 0
  AND EXTRACT(SECOND FROM transaction_date) = 0;

-- Show how many were updated
SELECT 
    COUNT(*) as updated_count,
    transaction_type
FROM transactions
WHERE transaction_date = created_at
GROUP BY transaction_type;

COMMIT;

SELECT 'All midnight timestamps fixed!' as status;
EOF

echo ""
echo "✓ Transaction timestamps updated"
echo "✓ Inventory calculations should now be correct"
echo ""
echo "Restart the API and refresh your browser to see updated inventory."
