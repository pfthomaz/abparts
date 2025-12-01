#!/bin/bash
# Pre-Deployment Verification Script for Stock Adjustments
# Run this in DEVELOPMENT before deploying to production

set -e

echo "========================================="
echo "Stock Adjustments Pre-Deployment Check"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Verify migration file revision ID length
echo "1. Checking migration revision ID length..."
REVISION_LINE=$(grep "^revision = " backend/alembic/versions/20241130_redesign_stock_adjustments.py)
REVISION_ID=$(echo "$REVISION_LINE" | grep -oP "'\K[^']+")
REVISION_LENGTH=${#REVISION_ID}

if [ $REVISION_LENGTH -le 32 ]; then
    echo -e "${GREEN}✅ Revision ID length: $REVISION_LENGTH chars (OK)${NC}"
    echo "   Revision ID: $REVISION_ID"
else
    echo -e "${RED}❌ Revision ID length: $REVISION_LENGTH chars (TOO LONG!)${NC}"
    echo "   Revision ID: $REVISION_ID"
    echo "   Maximum allowed: 32 characters"
    exit 1
fi
echo ""

# Check 2: Verify down_revision is set
echo "2. Checking down_revision..."
DOWN_REVISION=$(grep "^down_revision = " backend/alembic/versions/20241130_redesign_stock_adjustments.py | grep -oP "'\K[^']+")
if [ -n "$DOWN_REVISION" ]; then
    echo -e "${GREEN}✅ Down revision set: $DOWN_REVISION${NC}"
else
    echo -e "${RED}❌ Down revision not set!${NC}"
    exit 1
fi
echo ""

# Check 3: Check current migration status
echo "3. Checking current migration status..."
CURRENT_MIGRATION=$(docker-compose exec -T api alembic current 2>/dev/null | grep -oP '[a-f0-9_]+' | head -1 || echo "unknown")
echo "   Current migration: $CURRENT_MIGRATION"
echo ""

# Check 4: Check for multiple heads
echo "4. Checking for multiple heads..."
HEAD_COUNT=$(docker-compose exec -T api alembic heads 2>/dev/null | grep -c "^[a-f0-9]" || echo "0")
if [ "$HEAD_COUNT" -eq 1 ]; then
    echo -e "${GREEN}✅ Single head detected (OK)${NC}"
elif [ "$HEAD_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Could not determine head count${NC}"
else
    echo -e "${RED}❌ Multiple heads detected: $HEAD_COUNT${NC}"
    echo "   You need to create a merge migration first!"
    docker-compose exec -T api alembic heads
    exit 1
fi
echo ""

# Check 5: Test migration locally
echo "5. Testing migration locally..."
echo "   This will downgrade and upgrade to test the migration..."
read -p "   Continue? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   Downgrading..."
    docker-compose exec -T api alembic downgrade -1
    
    echo "   Upgrading..."
    docker-compose exec -T api alembic upgrade head
    
    NEW_CURRENT=$(docker-compose exec -T api alembic current 2>/dev/null | grep -oP '[a-f0-9_]+' | head -1)
    if [ "$NEW_CURRENT" == "$REVISION_ID" ]; then
        echo -e "${GREEN}✅ Migration test successful!${NC}"
        echo "   Current migration: $NEW_CURRENT"
    else
        echo -e "${RED}❌ Migration test failed!${NC}"
        echo "   Expected: $REVISION_ID"
        echo "   Got: $NEW_CURRENT"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Skipped migration test${NC}"
fi
echo ""

# Check 6: Verify database structure
echo "6. Verifying database structure..."
echo "   Checking stock_adjustments table..."
docker-compose exec -T db psql -U abparts_user -d abparts_dev -c "\d stock_adjustments" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ stock_adjustments table exists${NC}"
else
    echo -e "${RED}❌ stock_adjustments table not found${NC}"
    exit 1
fi

echo "   Checking stock_adjustment_items table..."
docker-compose exec -T db psql -U abparts_user -d abparts_dev -c "\d stock_adjustment_items" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ stock_adjustment_items table exists${NC}"
else
    echo -e "${RED}❌ stock_adjustment_items table not found${NC}"
    exit 1
fi

echo "   Checking adjustmenttype enum..."
docker-compose exec -T db psql -U abparts_user -d abparts_dev -c "\dT+ adjustmenttype" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ adjustmenttype enum exists${NC}"
else
    echo -e "${RED}❌ adjustmenttype enum not found${NC}"
    exit 1
fi
echo ""

# Check 7: Test API endpoint
echo "7. Testing API endpoint..."
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/stock-adjustments/ 2>/dev/null || echo "000")
if [ "$API_RESPONSE" == "401" ] || [ "$API_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✅ API endpoint responding (HTTP $API_RESPONSE)${NC}"
else
    echo -e "${YELLOW}⚠️  API endpoint returned HTTP $API_RESPONSE${NC}"
fi
echo ""

# Check 8: Verify all required files exist
echo "8. Checking required files..."
REQUIRED_FILES=(
    "backend/app/routers/stock_adjustments.py"
    "backend/app/crud/stock_adjustments.py"
    "backend/app/schemas/stock_adjustment.py"
    "frontend/src/pages/StockAdjustments.js"
    "frontend/src/components/StockAdjustmentsList.js"
    "frontend/src/components/CreateStockAdjustmentModal.js"
    "frontend/src/components/StockAdjustmentDetailsModal.js"
    "frontend/src/services/stockAdjustmentsService.js"
)

ALL_FILES_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✅${NC} $file"
    else
        echo -e "   ${RED}❌${NC} $file (MISSING)"
        ALL_FILES_EXIST=false
    fi
done

if [ "$ALL_FILES_EXIST" = false ]; then
    echo -e "${RED}❌ Some required files are missing!${NC}"
    exit 1
fi
echo ""

# Summary
echo "========================================="
echo "Pre-Deployment Check Summary"
echo "========================================="
echo -e "${GREEN}✅ All checks passed!${NC}"
echo ""
echo "Next steps:"
echo "1. Commit and push changes to git"
echo "2. SSH to production server"
echo "3. Follow DEPLOY_STOCK_ADJUSTMENTS_TO_PRODUCTION.md"
echo ""
echo "Production checklist:"
echo "  □ Backup production database"
echo "  □ Verify down_revision matches production"
echo "  □ Pull latest code"
echo "  □ Run migration"
echo "  □ Rebuild services"
echo "  □ Test functionality"
echo ""
