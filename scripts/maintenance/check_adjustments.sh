#!/bin/bash
echo "=== Checking Stock Adjustments Data ==="
echo ""

echo "Stock Adjustments in database:"
docker-compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
    sa.id,
    w.name as warehouse,
    sa.adjustment_type,
    u.username,
    sa.total_items_adjusted,
    sa.adjustment_date
FROM stock_adjustments sa
JOIN warehouses w ON sa.warehouse_id = w.id
JOIN users u ON sa.user_id = u.id
ORDER BY sa.created_at DESC
LIMIT 5;
"

echo ""
echo "Stock Adjustment Items:"
docker-compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
    sai.id,
    p.part_number,
    sai.quantity_before,
    sai.quantity_after,
    sai.quantity_change
FROM stock_adjustment_items sai
JOIN parts p ON sai.part_id = p.id
ORDER BY sai.created_at DESC
LIMIT 5;
"
