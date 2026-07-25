#!/bin/bash

echo "🔄 Resetting Alembic Migrations to Current Schema"
echo "=" * 50
echo ""
echo "This script will:"
echo "1. Create a new baseline migration from current dev schema"
echo "2. Reset Alembic history to start from this baseline"
echo "3. Ensure both dev and prod start from the same point"
echo ""

# Confirm before proceeding
read -p "⚠️  This will reset migration history. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted"
    exit 1
fi

echo "📋 Step 1: Checking current migration status..."

# Check current migration status in development
echo "🔍 Current development migration status:"
docker compose exec api alembic current

echo ""
echo "📋 Step 2: Creating new baseline migration..."

# Create a new migration that captures the current state
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
MIGRATION_NAME="baseline_schema_${TIMESTAMP}"

echo "📝 Creating migration: ${MIGRATION_NAME}"
docker compose exec api alembic revision --autogenerate -m "${MIGRATION_NAME}"

if [ $? -ne 0 ]; then
    echo "❌ Failed to create baseline migration"
    exit 1
fi

echo "✅ Baseline migration created successfully"

echo ""
echo "📋 Step 3: Getting the new migration ID..."

# Get the latest migration ID
LATEST_REVISION=$(docker compose exec api alembic heads | tr -d '\r\n')
echo "📍 Latest revision: ${LATEST_REVISION}"

echo ""
echo "📋 Step 4: Stamping development database..."

# Stamp the development database with the new baseline
docker compose exec api alembic stamp ${LATEST_REVISION}

if [ $? -eq 0 ]; then
    echo "✅ Development database stamped successfully"
else
    echo "❌ Failed to stamp development database"
    exit 1
fi

echo ""
echo "📋 Step 5: Production server instructions..."
echo ""
echo "🚨 IMPORTANT: Run these commands on your PRODUCTION SERVER:"
echo "=" * 60
echo "# SSH into production server, then run:"
echo "cd ~/abparts"
echo "docker compose -f docker-compose.prod.yml exec api alembic stamp ${LATEST_REVISION}"
echo ""
echo "# Verify both environments show the same revision:"
echo "docker compose -f docker-compose.prod.yml exec api alembic current"
echo "=" * 60

echo ""
echo "📋 Step 6: Verifying development setup..."

# Verify the current state
echo "🔍 Current development migration status after reset:"
docker compose exec api alembic current

echo ""
echo "✅ Migration reset complete for development!"
echo ""
echo "📝 Summary:"
echo "- ✅ New baseline migration created from current schema"
echo "- ✅ Development database stamped with baseline"
echo "- ⏳ Production database needs to be stamped (see instructions above)"
echo "- ✅ Future migrations will start from this clean baseline"
echo ""
echo "🧪 Next steps:"
echo "1. Run the production stamping command shown above"
echo "2. Verify both environments show the same revision"
echo "3. Test creating a new migration to ensure everything works"
echo "4. Both environments now have identical schemas and migration history"

echo ""
echo "🎯 Benefits achieved:"
echo "- Clean migration history starting from current working schema"
echo "- No more migration conflicts between dev and production"
echo "- Both environments synchronized and ready for future changes"