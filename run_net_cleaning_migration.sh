#!/bin/bash
# Complete script to run net cleaning migration

set -e  # Exit on error

echo "=========================================="
echo "Net Cleaning Migration Deployment"
echo "=========================================="
echo ""

# Step 1: Clear Python cache
echo "Step 1: Clearing Python cache..."
docker compose exec api rm -rf /app/alembic/versions/__pycache__ || true
echo "✓ Cache cleared"
echo ""

# Step 2: Restart API
echo "Step 2: Restarting API container..."
docker compose restart api
echo "✓ API restarted"
echo ""

# Step 3: Wait for API to be ready
echo "Step 3: Waiting for API to start..."
sleep 8
echo "✓ API ready"
echo ""

# Step 4: Show current status
echo "Step 4: Current migration status..."
docker compose exec api alembic current
echo ""

# Step 5: Show available migrations
echo "Step 5: Available migrations..."
docker compose exec api alembic history | tail -10
echo ""

# Step 6: Run migration
echo "Step 6: Running migration..."
docker compose exec api alembic upgrade head
echo "✓ Migration complete"
echo ""

# Step 7: Verify tables created
echo "Step 7: Verifying tables..."
echo "Farm Sites table:"
docker compose exec db psql -U abparts_user -d abparts_prod -c "\d farm_sites" | head -20
echo ""
echo "Nets table:"
docker compose exec db psql -U abparts_user -d abparts_prod -c "\d nets" | head -20
echo ""
echo "Net Cleaning Records table:"
docker compose exec db psql -U abparts_user -d abparts_prod -c "\d net_cleaning_records" | head -20
echo ""

# Step 8: Check final migration status
echo "Step 8: Final migration status..."
docker compose exec api alembic current
echo ""

# Step 9: Fix existing data
echo "Step 9: Fixing existing data status..."
docker compose exec api python /app/fix_net_cleaning_status.py || echo "No existing data to fix"
echo ""

# Step 10: Rebuild frontend
echo "Step 10: Rebuilding frontend..."
docker compose build --no-cache web
echo "✓ Frontend rebuilt"
echo ""

# Step 11: Restart all services
echo "Step 11: Restarting all services..."
docker compose restart
echo "✓ Services restarted"
echo ""

echo "=========================================="
echo "✓ DEPLOYMENT COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test creating a farm site"
echo "2. Test creating a net"
echo "3. Test creating a cleaning record"
echo "4. Test saving without end_time (In Progress)"
echo "5. Test editing to add end_time (should remove In Progress)"
