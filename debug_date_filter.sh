#!/bin/bash
echo "=== Debugging Date Filter Issue ==="
echo ""

echo "Current date/time:"
date
echo ""

echo "Adjustments in database with dates:"
docker-compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
    id,
    adjustment_date,
    adjustment_date::date as date_only,
    created_at
FROM stock_adjustments
ORDER BY created_at DESC
LIMIT 5;
"

echo ""
echo "Testing date comparison:"
docker-compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
    id,
    adjustment_date,
    adjustment_date >= '2024-10-31'::timestamp as after_start,
    adjustment_date <= '2024-11-30'::timestamp as before_end
FROM stock_adjustments
ORDER BY created_at DESC
LIMIT 5;
"
