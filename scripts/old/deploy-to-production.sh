#!/bin/bash

# Production Deployment Script for Stocktake Database Changes
# Run this script in your production environment

set -e  # Exit on any error

echo "🚀 Starting production deployment for stocktake functionality..."

# Step 1: Backup database
echo "📦 Creating database backup..."
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
docker-compose exec -T db pg_dump -U $POSTGRES_USER -d $POSTGRES_DB > $BACKUP_FILE
echo "✅ Database backed up to: $BACKUP_FILE"

# Step 2: Check current migration status
echo "🔍 Checking current migration status..."
docker-compose exec -T api alembic current

# Step 3: Apply migrations
echo "🔄 Applying database migrations..."
docker-compose exec -T api alembic upgrade head

# Step 4: Verify migration was applied
echo "✅ Verifying migration status..."
docker-compose exec -T api alembic current

# Step 5: Check database schema
echo "🔍 Verifying database schema..."
echo "Checking for stocktake tables..."
docker-compose exec -T db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "\dt stocktake*" || echo "⚠️  Stocktake tables not found - check migration"
echo "Checking stocktake_items table structure..."
docker-compose exec -T db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "\d stocktake_items" | grep -E "(counted_at|counted_by_user_id|expected_quantity|actual_quantity)" || echo "⚠️  Expected columns not found - check migration"

# Step 6: Restart API to ensure new code is loaded
echo "🔄 Restarting API service..."
docker-compose restart api

# Step 7: Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
sleep 10

# Step 8: Test API health
echo "🏥 Testing API health..."
curl -f http://localhost:8000/health || echo "⚠️  API health check failed"

echo "🎉 Deployment completed successfully!"
echo "📋 Next steps:"
echo "   1. Test the stocktake functionality in the web interface"
echo "   2. Monitor logs for any errors: docker-compose logs api --tail=50"
echo "   3. If issues occur, rollback with: docker-compose exec -T api alembic downgrade add_parts_perf_idx"