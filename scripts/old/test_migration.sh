#!/bin/bash
# Test Migration - Run this AFTER creating a migration to test it

echo "=========================================="
echo "  Testing Migration"
echo "=========================================="
echo ""

# Get the latest migration file
LATEST_FILE=$(ls -t backend/alembic/versions/*.py 2>/dev/null | grep -v __pycache__ | head -1)

if [ -z "$LATEST_FILE" ]; then
    echo "❌ No migration files found!"
    exit 1
fi

echo "📄 Testing migration: $(basename $LATEST_FILE)"
echo ""

# Check revision ID length
REVISION=$(grep "^revision = " "$LATEST_FILE" | cut -d"'" -f2)
REVISION_LENGTH=${#REVISION}

echo "🔍 Checking revision ID..."
echo "   Revision: $REVISION"
echo "   Length: $REVISION_LENGTH characters"

if [ $REVISION_LENGTH -gt 32 ]; then
    echo "   ❌ ERROR: Revision ID is too long! (max 32 characters)"
    echo "   Please shorten it in the migration file."
    exit 1
else
    echo "   ✅ Revision ID length OK"
fi
echo ""

# Check down_revision exists
DOWN_REV=$(grep "^down_revision = " "$LATEST_FILE" | cut -d"'" -f2)
echo "🔍 Checking down_revision..."
echo "   Down revision: $DOWN_REV"

if [ -z "$DOWN_REV" ] || [ "$DOWN_REV" = "None" ]; then
    echo "   ⚠️  WARNING: No down_revision set (this might be intentional for first migration)"
else
    echo "   ✅ Down revision set"
fi
echo ""

# Run the migration
echo "🔄 Running migration..."
docker-compose exec api alembic upgrade head

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration completed successfully!"
    echo ""
    
    # Verify current state
    echo "📊 Current migration status:"
    docker-compose exec api alembic current
    echo ""
    
    # Test downgrade
    echo "🔙 Testing downgrade..."
    docker-compose exec api alembic downgrade -1
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Downgrade successful!"
        echo ""
        
        # Upgrade again
        echo "🔄 Re-applying migration..."
        docker-compose exec api alembic upgrade head
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "=========================================="
            echo "  ✅ Migration Test PASSED!"
            echo "=========================================="
            echo ""
            echo "Next steps:"
            echo "1. Verify database changes manually"
            echo "2. Test application functionality"
            echo "3. Commit the migration file"
            echo ""
        else
            echo ""
            echo "❌ Re-upgrade failed!"
            exit 1
        fi
    else
        echo ""
        echo "❌ Downgrade failed!"
        echo "   Fix the downgrade() function in your migration"
        exit 1
    fi
else
    echo ""
    echo "=========================================="
    echo "  ❌ Migration Test FAILED!"
    echo "=========================================="
    echo ""
    echo "Check the error above and fix the migration file."
    echo ""
    echo "Common issues:"
    echo "- Revision ID too long (>32 chars)"
    echo "- Wrong down_revision reference"
    echo "- SQL syntax error"
    echo "- Table/column already exists"
    echo ""
    exit 1
fi
