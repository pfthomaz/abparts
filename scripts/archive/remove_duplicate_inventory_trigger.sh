#!/bin/bash

echo "=== Removing duplicate inventory update trigger ==="
echo ""
echo "This trigger is causing double inventory updates because"
echo "the Python code already handles inventory updates."
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

docker compose exec -T db psql -U abparts_user -d abparts_dev << 'EOF'
BEGIN;

-- Drop the trigger
DROP TRIGGER IF EXISTS trigger_update_inventory_on_transaction ON transactions;

-- Drop the function
DROP FUNCTION IF EXISTS update_inventory_on_transaction();

-- Verify triggers are removed
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table
FROM information_schema.triggers
WHERE event_object_table = 'transactions';

COMMIT;

SELECT 'Trigger removed successfully!' as status;
EOF

echo ""
echo "✓ Duplicate trigger removed"
echo "✓ Inventory updates now handled only by Python code"
echo ""
echo "Test part usage recording again - it should now update correctly."
