#!/bin/bash

echo "Checking for database triggers on inventory table..."
echo ""

docker compose exec -T db psql -U abparts_user -d abparts_dev << 'EOF'
-- Check for triggers on inventory table
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement,
    action_timing
FROM information_schema.triggers
WHERE event_object_table = 'inventory'
ORDER BY trigger_name;

-- Check for triggers on transactions table
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement,
    action_timing
FROM information_schema.triggers
WHERE event_object_table = 'transactions'
ORDER BY trigger_name;
EOF
