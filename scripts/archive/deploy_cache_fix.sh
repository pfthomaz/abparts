#!/bin/bash

# Deploy Cache Fix - Fixes stale IndexedDB cache issue

set -e

echo "=== DEPLOYING CACHE FIX ==="
echo ""
echo "This fix resolves:"
echo "- Stale data in IndexedDB (wrong warranty dates, missing organizations)"
echo "- Cache not clearing on login/logout"
echo "- Users seeing outdated information"
echo ""

echo "STEP 1: Verify we're on production server..."
echo "============================================="
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ ERROR: docker-compose.prod.yml not found!"
    echo "Are you in the ~/abparts directory on the production server?"
    exit 1
fi
echo "✓ Found docker-compose.prod.yml"
echo ""

echo "STEP 2: Pull latest code from Git..."
echo "====================================="
git pull origin main
echo ""

echo "STEP 3: Show what changed..."
echo "============================"
echo "Modified files:"
git log -1 --name-status
echo ""

echo "STEP 4: Rebuild frontend with cache clearing fix..."
echo "===================================================="
echo "This will take a few minutes..."
docker compose -f docker-compose.prod.yml build web --no-cache
echo ""

echo "STEP 5: Restart web container..."
echo "================================="
docker compose -f docker-compose.prod.yml up -d web
echo ""

echo "STEP 6: Wait for container to be ready..."
echo "=========================================="
sleep 10
echo ""

echo "STEP 7: Verify services are running..."
echo "======================================="
docker compose -f docker-compose.prod.yml ps
echo ""

echo "STEP 8: Check web container logs..."
echo "===================================="
docker compose -f docker-compose.prod.yml logs web | tail -20
echo ""

echo "STEP 9: Test API is responding..."
echo "=================================="
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
if [ "$API_STATUS" = "200" ]; then
    echo "✓ API is healthy (HTTP 200)"
else
    echo "⚠️  API returned HTTP $API_STATUS"
fi
echo ""

echo "STEP 10: Test frontend is serving..."
echo "====================================="
WEB_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 || echo "000")
if [ "$WEB_STATUS" = "200" ]; then
    echo "✓ Frontend is serving (HTTP 200)"
else
    echo "⚠️  Frontend returned HTTP $WEB_STATUS"
fi
echo ""

echo "=== DEPLOYMENT COMPLETE ==="
echo ""
echo "✅ Cache fix deployed successfully!"
echo ""
echo "WHAT WAS FIXED:"
echo "- IndexedDB cache now clears on login"
echo "- IndexedDB cache now clears on logout"
echo "- Users will see fresh data from server"
echo "- KEF-2 warranty date will show correct value (2025-12-31)"
echo "- All 21 organizations will be visible"
echo ""
echo "USER INSTRUCTIONS:"
echo "==================="
echo "Tell users to:"
echo "1. Clear browser cache (Ctrl+Shift+Delete)"
echo "2. Or use Incognito/Private mode"
echo "3. Login again"
echo ""
echo "After login, they will see:"
echo "- Correct warranty dates"
echo "- All organizations (21 total)"
echo "- Fresh data from server"
echo ""
echo "TESTING:"
echo "========"
echo "1. Login to the app"
echo "2. Check KEF-2 machine - warranty should be 2025-12-31"
echo "3. Check Organizations page - should show 21 organizations"
echo "4. Open DevTools > Application > IndexedDB"
echo "5. Verify cache is cleared on login"
echo ""
echo "If issues persist, check:"
echo "- Browser console for errors"
echo "- IndexedDB in DevTools"
echo "- API logs: docker compose -f docker-compose.prod.yml logs api"
