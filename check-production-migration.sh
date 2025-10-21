#!/bin/bash

echo "🔍 Checking production migration status..."

echo "📋 Current migration:"
docker compose exec -T api alembic current

echo ""
echo "📋 Available migrations:"
docker compose exec -T api alembic branches

echo ""
echo "📋 Checking if stocktake tables exist:"
docker compose exec -T db psql -U ${POSTGRES_USER:-abparts_user} -d ${POSTGRES_DB:-abparts_dev} -c "\dt stocktake*" || echo "❌ No stocktake tables found"

echo ""
echo "📋 Checking if inventory_workflow_001 migration exists:"
docker compose exec -T api alembic show inventory_workflow_001 || echo "❌ inventory_workflow_001 migration not found"

echo ""
echo "📋 Migration history (last 10):"
docker compose exec -T api alembic history --verbose | head -20