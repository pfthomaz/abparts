#!/bin/bash

echo "🚀 Applying stocktake migration to production..."

# Check if stocktake tables already exist
echo "🔍 Checking current state..."
STOCKTAKE_EXISTS=$(docker compose exec -T db psql -U ${POSTGRES_USER:-abparts_user} -d ${POSTGRES_DB:-abparts_prod} -c "\dt stocktakes" 2>/dev/null | grep -c "stocktakes" || echo "0")

if [ "$STOCKTAKE_EXISTS" -gt 0 ]; then
    echo "✅ Stocktake tables already exist - no migration needed"
    exit 0
fi

echo "📦 Creating database backup before applying stocktake migration..."
BACKUP_FILE="backup_stocktake_$(date +%Y%m%d_%H%M%S).sql"
docker compose exec -T db pg_dump -U ${POSTGRES_USER:-abparts_user} -d ${POSTGRES_DB:-abparts_prod} > $BACKUP_FILE
echo "✅ Database backed up to: $BACKUP_FILE"

echo "🔄 Attempting to apply inventory_workflow_001 migration..."

# Try to apply the specific migration
if docker compose exec -T api alembic upgrade inventory_workflow_001; then
    echo "✅ inventory_workflow_001 migration applied successfully"
else
    echo "❌ Failed to apply inventory_workflow_001 migration"
    echo "🔄 Trying alternative approach - upgrading to merge point..."
    
    # Try upgrading to the merge point that includes inventory_workflow_001
    if docker compose exec -T api alembic upgrade b102b96926f9; then
        echo "✅ Upgraded to merge point b102b96926f9"
    else
        echo "❌ Failed to upgrade to merge point"
        echo "⚠️  Manual intervention may be required"
        exit 1
    fi
fi

echo "🔄 Now upgrading to head to get latest migrations..."
docker compose exec -T api alembic upgrade head

echo "🔍 Verifying stocktake tables were created..."
docker compose exec -T db psql -U ${POSTGRES_USER:-abparts_user} -d ${POSTGRES_DB:-abparts_prod} -c "\dt stocktake*"

echo "🔄 Restarting API service..."
docker compose restart api

echo "🎉 Stocktake migration completed!"
echo "📋 Next steps:"
echo "   1. Test the stocktake functionality at /stocktake"
echo "   2. Verify existing inventory management still works at /inventory"