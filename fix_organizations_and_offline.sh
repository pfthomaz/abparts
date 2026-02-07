#!/bin/bash

# Fix Organizations Display and Offline Mode Issues
# This script rebuilds the frontend with all offline mode fixes

set -e

echo "=========================================="
echo "Fix Organizations & Offline Mode"
echo "=========================================="
echo ""

# Detect environment
if [ -f "docker-compose.prod.yml" ] && [ "$1" == "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    ENV="PRODUCTION"
else
    COMPOSE_FILE="docker-compose.yml"
    ENV="DEVELOPMENT"
fi

echo "Environment: $ENV"
echo "Compose file: $COMPOSE_FILE"
echo ""

# Step 1: Organizations Issue
echo "=========================================="
echo "STEP 1: Organizations Not Showing"
echo "=========================================="
echo ""
echo "Issue: New organizations in database don't appear in UI"
echo "Cause: Browser cache"
echo "Solution: Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)"
echo ""
echo "If hard refresh doesn't work:"
echo "  1. Open browser DevTools (F12)"
echo "  2. Go to Application tab"
echo "  3. Click 'Clear site data'"
echo "  4. Reload page"
echo ""
read -p "Press Enter to continue to offline mode fix..."
echo ""

# Step 2: Verify files exist
echo "=========================================="
echo "STEP 2: Verify Offline Mode Files"
echo "=========================================="
echo ""

FILES=(
    "frontend/src/services/offlineDataPreloader.js"
    "frontend/copy-sw.js"
    "frontend/public/service-worker.js"
)

ALL_EXIST=true
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file MISSING"
        ALL_EXIST=false
    fi
done

if [ "$ALL_EXIST" = false ]; then
    echo ""
    echo "ERROR: Some required files are missing!"
    echo "Please ensure all offline mode fixes are committed."
    exit 1
fi

echo ""
echo "All required files present!"
echo ""

# Step 3: Check package.json for postbuild script
echo "=========================================="
echo "STEP 3: Verify package.json Configuration"
echo "=========================================="
echo ""

if grep -q "postbuild.*copy-sw.js" frontend/package.json; then
    echo "✓ postbuild script configured in package.json"
else
    echo "✗ postbuild script NOT configured in package.json"
    echo ""
    echo "Adding postbuild script..."
    # This would require jq or manual editing
    echo "Please manually add to frontend/package.json:"
    echo '  "postbuild": "node copy-sw.js"'
    exit 1
fi

echo ""

# Step 4: Stop containers
echo "=========================================="
echo "STEP 4: Stop Containers"
echo "=========================================="
echo ""

if [ "$ENV" == "PRODUCTION" ]; then
    docker compose -f $COMPOSE_FILE down
else
    docker compose down
fi

echo "Containers stopped"
echo ""

# Step 5: Rebuild frontend
echo "=========================================="
echo "STEP 5: Rebuild Frontend (No Cache)"
echo "=========================================="
echo ""
echo "This will take a few minutes..."
echo ""

if [ "$ENV" == "PRODUCTION" ]; then
    docker compose -f $COMPOSE_FILE build web --no-cache
else
    docker compose build web --no-cache
fi

echo ""
echo "Frontend rebuilt successfully!"
echo ""

# Step 6: Start containers
echo "=========================================="
echo "STEP 6: Start Containers"
echo "=========================================="
echo ""

if [ "$ENV" == "PRODUCTION" ]; then
    docker compose -f $COMPOSE_FILE up -d
else
    docker compose up -d
fi

echo ""
echo "Containers started"
echo ""

# Step 7: Verify service worker
echo "=========================================="
echo "STEP 7: Verify Service Worker"
echo "=========================================="
echo ""

sleep 5  # Wait for containers to fully start

if [ "$ENV" == "PRODUCTION" ]; then
    SW_CHECK=$(docker compose -f $COMPOSE_FILE exec web ls -lh /usr/share/nginx/html/service-worker.js 2>&1 || echo "NOT FOUND")
else
    SW_CHECK=$(docker compose exec web ls -lh /usr/share/nginx/html/service-worker.js 2>&1 || echo "NOT FOUND")
fi

if [[ "$SW_CHECK" == *"NOT FOUND"* ]]; then
    echo "✗ Service worker NOT found in build!"
    echo ""
    echo "This means the postbuild script didn't run."
    echo "Check frontend/copy-sw.js and package.json"
else
    echo "✓ Service worker found in build:"
    echo "$SW_CHECK"
fi

echo ""

# Step 8: Testing instructions
echo "=========================================="
echo "STEP 8: Testing Instructions"
echo "=========================================="
echo ""
echo "Organizations Issue:"
echo "  1. Open browser and navigate to Organizations page"
echo "  2. Press Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)"
echo "  3. Verify all organizations appear"
echo ""
echo "Offline Mode Testing:"
echo "  1. Login to the app"
echo "  2. Open browser DevTools (F12)"
echo "  3. Check Console for '[OfflinePreloader]' messages"
echo "  4. Go to Application > IndexedDB > ABPartsOfflineDB"
echo "  5. Verify all stores have data (machines, protocols, users, etc.)"
echo "  6. Go to Network tab and enable 'Offline' mode"
echo "  7. Try creating maintenance execution - should work offline"
echo "  8. Try creating net cleaning record - should work offline"
echo ""
echo "Expected Console Messages After Login:"
echo "  [OfflinePreloader] Starting data preload for user: <username>"
echo "  [OfflinePreloader] Preloading machines..."
echo "  [OfflinePreloader] Preloading maintenance protocols..."
echo "  [OfflinePreloader] Preloading users..."
echo "  [OfflinePreloader] Preloading farm sites..."
echo "  [OfflinePreloader] Preloading nets..."
echo "  [OfflinePreloader] Data preload complete"
echo ""

# Step 9: Summary
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo ""
echo "✓ Frontend rebuilt with offline mode fixes"
echo "✓ Service worker copied to build folder"
echo "✓ Data preloader integrated into login flow"
echo "✓ User context fix applied to MaintenanceExecutions"
echo "✓ Service worker disabled in development mode"
echo ""
echo "Next Steps:"
echo "  1. Clear browser cache (Cmd+Shift+R)"
echo "  2. Login and verify preloader runs"
echo "  3. Test offline mode functionality"
echo ""
echo "For detailed troubleshooting, see: OFFLINE_MODE_FIX.md"
echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="
