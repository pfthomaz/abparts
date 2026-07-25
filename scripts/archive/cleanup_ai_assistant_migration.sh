#!/bin/bash

# Cleanup AI Assistant Migration
# This script removes the AI Assistant migration and updates Alembic to skip it

echo "🧹 Cleaning up AI Assistant Alembic Migration"
echo "============================================="

# Step 1: Remove the AI Assistant migration file
echo "1. Removing AI Assistant migration file..."
if [ -f "backend/alembic/versions/add_ai_assistant_knowledge_base_tables.py" ]; then
    rm "backend/alembic/versions/add_ai_assistant_knowledge_base_tables.py"
    echo "✅ Removed add_ai_assistant_knowledge_base_tables.py"
else
    echo "⚠️  Migration file not found (already removed?)"
fi

# Step 2: Update Alembic version in development database
echo ""
echo "2. Updating Alembic version in development database..."
docker-compose exec db psql -U abparts_user -d abparts_dev -c "
UPDATE alembic_version SET version_num = 'a78bd1ac6e99' WHERE version_num = 'add_ai_knowledge_base';
"

if [ $? -eq 0 ]; then
    echo "✅ Updated development Alembic version"
else
    echo "❌ Failed to update development Alembic version"
fi

# Step 3: Update Alembic version in production database
echo ""
echo "3. Updating Alembic version in production database..."
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
UPDATE alembic_version SET version_num = 'a78bd1ac6e99' WHERE version_num = 'add_ai_knowledge_base';
"

if [ $? -eq 0 ]; then
    echo "✅ Updated production Alembic version"
else
    echo "❌ Failed to update production Alembic version"
fi

# Step 4: Verify Alembic status
echo ""
echo "4. Verifying Alembic status..."
echo "Development:"
docker-compose exec api alembic current 2>/dev/null || echo "  ⚠️  Could not check development Alembic status"

echo "Production:"
docker compose -f docker-compose.prod.yml exec api alembic current 2>/dev/null || echo "  ⚠️  Could not check production Alembic status"

# Step 5: Test that migrations work
echo ""
echo "5. Testing Alembic migrations..."
echo "Development:"
docker-compose exec api alembic upgrade head 2>/dev/null && echo "  ✅ Development migrations OK" || echo "  ❌ Development migrations failed"

echo ""
echo "🎉 AI Assistant migration cleanup complete!"
echo ""
echo "📝 Summary:"
echo "- Removed AI Assistant migration file"
echo "- Reset Alembic version to baseline (a78bd1ac6e99)"
echo "- AI Assistant tables are now managed outside of Alembic"
echo "- Future deployments will use direct schema management"
echo ""
echo "⚠️  Important:"
echo "- AI Assistant schema is now standardized across environments"
echo "- No more Alembic migrations needed for AI Assistant tables"
echo "- Use standardize_ai_assistant_schema.py for future schema changes"