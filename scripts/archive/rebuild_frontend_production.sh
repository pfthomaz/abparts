#!/bin/bash

# Simple script to rebuild frontend in production
# This fixes the offline mode issue

set -e

echo "=========================================="
echo "Rebuild Frontend - Production"
echo "=========================================="
echo ""
echo "This will:"
echo "  1. Rebuild the frontend container"
echo "  2. Copy service worker to build folder"
echo "  3. Restart the web container"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

# Rebuild frontend
echo "Rebuilding frontend (this takes 2-3 minutes)..."
docker compose -f docker-compose.prod.yml build web --no-cache

echo ""
echo "✓ Frontend rebuilt"
echo ""

# Restart web container
echo "Restarting web container..."
docker compose -f docker-compose.prod.yml up -d web

echo ""
echo "✓ Web container restarted"
echo ""

# Wait for container to start
echo "Waiting for container to start..."
sleep 5

# Verify service worker
echo "Verifying service worker..."
SW_CHECK=$(docker compose -f docker-compose.prod.yml exec web ls -lh /usr/share/nginx/html/service-worker.js 2>&1 || echo "NOT FOUND")

if [[ "$SW_CHECK" == *"NOT FOUND"* ]]; then
    echo ""
    echo "✗ ERROR: Service worker not found!"
    echo ""
    echo "This shouldn't happen. Please check:"
    echo "  1. frontend/copy-sw.js exists"
    echo "  2. frontend/public/service-worker.js exists"
    echo "  3. frontend/package.json has 'copy-sw.js' in build script"
    echo ""
    exit 1
else
    echo ""
    echo "✓ Service worker found:"
    echo "$SW_CHECK"
    echo ""
fi

# Success message
echo "=========================================="
echo "SUCCESS!"
echo "=========================================="
echo ""
echo "Frontend rebuilt successfully with offline mode support!"
echo ""
echo "Next steps:"
echo "  1. Clear browser cache (Cmd+Shift+R or Ctrl+Shift+R)"
echo "  2. Login to the app"
echo "  3. Check console for '[OfflinePreloader]' messages"
echo "  4. Test offline mode (DevTools > Network > Offline)"
echo ""
echo "For detailed testing instructions, see:"
echo "  QUICK_FIX_SUMMARY.md"
echo ""
echo "=========================================="
