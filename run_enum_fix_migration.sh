#!/bin/bash
set -e

echo "=== Fixing AdjustmentType Enum ==="
echo ""

echo "Step 1: Running migration..."
docker-compose exec -T api alembic upgrade head

echo ""
echo "Step 2: Verifying enum values..."
docker-compose exec -T db psql -U abparts_user -d abparts_dev -c "SELECT enumlabel FROM pg_enum WHERE enumtypid = 'adjustmenttype'::regtype ORDER BY enumsortorder;"

echo ""
echo "=== Migration Complete ==="
