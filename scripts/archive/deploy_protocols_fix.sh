#!/bin/bash

# Deploy Protocols Caching Fix
# This script pulls latest code and rebuilds frontend with cache busting

set -e  # Exit on error

echo "=========================================="
echo "Deploying Protocols Caching Fix"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: docker-compose.prod.yml not found"
    echo "Please run this script from the abparts root directory"
    exit 1
fi

echo "Step 1: Pulling latest code from GitHub..."
git pull origin main
echo "✓ Code updated"
echo ""

echo "Step 2: Stopping containers..."
docker compose -f docker-compose.prod.yml down
echo "✓ Containers stopped"
echo ""

echo "Step 3: Removing old frontend image..."
docker rmi abparts-web:latest 2>/dev/null || echo "  (No old image to remove)"
echo "✓ Old image removed"
echo ""

echo "Step 4: Rebuilding frontend with --no-cache..."
docker compose -f docker-compose.prod.yml build --no-cache web
echo "✓ Frontend rebuilt"
echo ""

echo "Step 5: Starting containers..."
docker compose -f docker-compose.prod.yml up -d
echo "✓ Containers started"
echo ""

echo "=========================================="
echo "✓ Deployment Complete!"
echo "=========================================="
echo ""
echo "⚠️  IMPORTANT: You MUST clear your browser cache now!"
echo ""
echo "In Safari:"
echo "  1. Safari → Preferences → Privacy → Manage Website Data"
echo "  2. Search for 'abparts' or 'oraseas'"
echo "  3. Click 'Remove All'"
echo "  4. Close and reopen Safari"
echo ""
echo "OR use hard refresh:"
echo "  1. Open https://abparts.oraseas.com"
echo "  2. Press Cmd + Option + E (empty caches)"
echo "  3. Press Cmd + Shift + R (hard reload)"
echo ""
echo "After clearing cache, login and check console for:"
echo "  [OfflinePreloader] ✓ Cached X protocols"
echo ""
