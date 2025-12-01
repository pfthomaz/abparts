#!/bin/bash
echo "=== Checking for Database Triggers ==="
echo ""

echo "Triggers on inventory table:"
docker-compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE event_object_table IN ('inventory', 'transactions', 'stock_adjustments', 'stock_adjustment_items')
ORDER BY event_object_table, trigger_name;
"

echo ""
echo "Checking for functions that might update inventory:"
docker-compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
    proname as function_name,
    prosrc as source_code
FROM pg_proc
WHERE proname LIKE '%inventory%' OR proname LIKE '%stock%'
LIMIT 10;
"
