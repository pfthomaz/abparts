#!/bin/bash

# Diagnose Current State - Organizations & Offline Mode
# This script checks the current state of the system

echo "=========================================="
echo "System Diagnostics"
echo "=========================================="
echo ""

# Check if we're in production or development
if [ -f "docker-compose.prod.yml" ] && docker compose -f docker-compose.prod.yml ps >/dev/null 2>&1; then
    COMPOSE_FILE="docker-compose.prod.yml"
    ENV="PRODUCTION"
elif docker compose ps >/dev/null 2>&1; then
    COMPOSE_FILE="docker-compose.yml"
    ENV="DEVELOPMENT"
else
    echo "ERROR: No running Docker containers found"
    exit 1
fi

echo "Environment: $ENV"
echo "Compose file: $COMPOSE_FILE"
echo ""

# Check container status
echo "=========================================="
echo "Container Status"
echo "=========================================="
echo ""

if [ "$ENV" == "PRODUCTION" ]; then
    docker compose -f $COMPOSE_FILE ps
else
    docker compose ps
fi

echo ""

# Check if required files exist
echo "=========================================="
echo "Required Files Check"
echo "=========================================="
echo ""

FILES=(
    "frontend/src/services/offlineDataPreloader.js"
    "frontend/copy-sw.js"
    "frontend/public/service-worker.js"
    "frontend/src/AuthContext.js"
    "frontend/src/pages/MaintenanceExecutions.js"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file MISSING"
    fi
done

echo ""

# Check package.json for postbuild script
echo "=========================================="
echo "package.json Configuration"
echo "=========================================="
echo ""

if grep -q "copy-sw.js" frontend/package.json; then
    echo "✓ Service worker copy script configured:"
    grep "build.*copy-sw.js" frontend/package.json
else
    echo "✗ Service worker copy script NOT configured"
fi

echo ""

# Check if service worker exists in build
echo "=========================================="
echo "Service Worker in Build"
echo "=========================================="
echo ""

if [ "$ENV" == "PRODUCTION" ]; then
    SW_CHECK=$(docker compose -f $COMPOSE_FILE exec web ls -lh /usr/share/nginx/html/service-worker.js 2>&1 || echo "NOT FOUND")
else
    SW_CHECK=$(docker compose exec web ls -lh /usr/share/nginx/html/service-worker.js 2>&1 || echo "NOT FOUND")
fi

if [[ "$SW_CHECK" == *"NOT FOUND"* ]]; then
    echo "✗ Service worker NOT found in build"
    echo "   This means offline mode won't work"
    echo "   Run: ./fix_organizations_and_offline.sh"
else
    echo "✓ Service worker found:"
    echo "$SW_CHECK"
fi

echo ""

# Check AuthContext for preloader integration
echo "=========================================="
echo "Preloader Integration"
echo "=========================================="
echo ""

if grep -q "offlineDataPreloader" frontend/src/AuthContext.js; then
    echo "✓ Preloader imported in AuthContext.js"
    if grep -q "preloadOfflineData" frontend/src/AuthContext.js; then
        echo "✓ Preloader called in AuthContext.js"
    else
        echo "✗ Preloader NOT called in AuthContext.js"
    fi
else
    echo "✗ Preloader NOT imported in AuthContext.js"
fi

echo ""

# Check MaintenanceExecutions for user context fix
echo "=========================================="
echo "User Context Fix"
echo "=========================================="
echo ""

if grep -q "getMachines.*userContext" frontend/src/pages/MaintenanceExecutions.js; then
    echo "✓ User context passed to getMachines()"
else
    echo "✗ User context NOT passed to getMachines()"
    echo "   This will cause 'Cannot fetch machines offline without user context' error"
fi

echo ""

# Check index.js for service worker conditional
echo "=========================================="
echo "Service Worker Registration"
echo "=========================================="
echo ""

if grep -q "NODE_ENV.*production" frontend/src/index.js; then
    echo "✓ Service worker conditionally registered (production only)"
else
    echo "⚠ Service worker registration not conditional"
    echo "   This may cause console spam in development"
fi

echo ""

# Summary
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""

# Count issues
ISSUES=0

if [[ "$SW_CHECK" == *"NOT FOUND"* ]]; then
    echo "✗ Service worker missing in build"
    ISSUES=$((ISSUES + 1))
fi

if ! grep -q "offlineDataPreloader" frontend/src/AuthContext.js; then
    echo "✗ Preloader not integrated"
    ISSUES=$((ISSUES + 1))
fi

if ! grep -q "getMachines.*userContext" frontend/src/pages/MaintenanceExecutions.js; then
    echo "✗ User context fix not applied"
    ISSUES=$((ISSUES + 1))
fi

if ! grep -q "copy-sw.js" frontend/package.json; then
    echo "✗ Service worker copy script not configured"
    ISSUES=$((ISSUES + 1))
fi

echo ""

if [ $ISSUES -eq 0 ]; then
    echo "✓ All checks passed!"
    echo ""
    echo "If organizations still not showing:"
    echo "  - Clear browser cache (Cmd+Shift+R or Ctrl+Shift+R)"
    echo "  - Or clear all site data in DevTools"
    echo ""
    echo "If offline mode still not working:"
    echo "  - Rebuild frontend: ./fix_organizations_and_offline.sh"
    echo "  - Check browser console for errors"
    echo "  - Verify IndexedDB has data after login"
else
    echo "Found $ISSUES issue(s)"
    echo ""
    echo "To fix all issues, run:"
    echo "  ./fix_organizations_and_offline.sh"
fi

echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="
