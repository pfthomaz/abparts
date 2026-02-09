#!/bin/bash

# Fix Service Worker Cache Issue
# This script increments the service worker cache version to force cache invalidation

set -e

echo "=========================================="
echo "Fix Service Worker Cache Issue"
echo "=========================================="
echo ""

# Check if service worker exists
if [ ! -f "frontend/public/service-worker.js" ]; then
    echo "❌ Error: frontend/public/service-worker.js not found"
    exit 1
fi

echo "📝 Current service worker cache version:"
grep "CACHE_VERSION" frontend/public/service-worker.js | head -1

echo ""
echo "🔧 Incrementing cache version..."

# Increment cache version (v1 -> v2, v2 -> v3, etc.)
sed -i.bak "s/abparts-offline-v\([0-9]*\)/abparts-offline-v\$((\1+1))/g" frontend/public/service-worker.js

echo "✓ Updated cache version:"
grep "CACHE_VERSION" frontend/public/service-worker.js | head -1

echo ""
echo "🛑 Stopping containers..."
docker compose -f docker-compose.prod.yml down

echo ""
echo "🔨 Rebuilding web container (no cache)..."
docker compose -f docker-compose.prod.yml build --no-cache web

echo ""
echo "🚀 Starting containers..."
docker compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ Waiting for containers to be ready..."
sleep 5

echo ""
echo "📋 Container status:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "=========================================="
echo "✅ Service worker cache version updated!"
echo "=========================================="
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Open browser and go to https://abparts.oraseas.com"
echo "2. Open DevTools (F12) → Console"
echo "3. Run this JavaScript to clear browser cache:"
echo ""
echo "navigator.serviceWorker.getRegistrations().then(r => r.forEach(reg => reg.unregister()));"
echo "caches.keys().then(names => names.forEach(name => caches.delete(name)));"
echo "indexedDB.deleteDatabase('ABPartsOfflineDB');"
echo "setTimeout(() => location.reload(true), 2000);"
echo ""
echo "4. After reload, check console for:"
echo "   [OfflinePreloader] Module loaded, STORES = ..."
echo "   [OfflinePreloader] ✓ Cached X protocols"
echo ""

