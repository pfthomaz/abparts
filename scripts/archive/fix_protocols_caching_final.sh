#!/bin/bash

# Fix Protocols Caching - Final Solution
# This script deploys the fix that uses string literals instead of STORES constants

set -e

echo "=========================================="
echo "Fix Protocols Caching - Final Solution"
echo "=========================================="
echo ""

echo "📝 Changes made:"
echo "  - Replaced STORES.PROTOCOLS with 'protocols' string literal"
echo "  - Replaced STORES.USERS with 'users' string literal"
echo "  - Replaced STORES.FARM_SITES with 'farmSites' string literal"
echo "  - Replaced STORES.NETS with 'nets' string literal"
echo "  - Removed STORES import (not needed anymore)"
echo "  - Removed debug console.log statements"
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
echo "📝 Recent web container logs:"
docker compose -f docker-compose.prod.yml logs web | tail -30

echo ""
echo "=========================================="
echo "✅ Deployment complete!"
echo "=========================================="
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Open browser (or use a fresh browser like Safari)"
echo "2. Go to https://abparts.oraseas.com"
echo "3. Login"
echo "4. Check console for:"
echo "   [OfflinePreloader] Starting data preload for offline mode..."
echo "   [OfflinePreloader] ========== PROTOCOLS SECTION START =========="
echo "   [OfflinePreloader] DEBUG: Fetched protocols from API, count = X"
echo "   [OfflinePreloader] ✓ Cached X protocols"
echo "   [OfflinePreloader] Preload complete: 5/5 successful"
echo ""
echo "5. Verify in console:"
echo ""
echo "   // Check IndexedDB"
echo "   const request = indexedDB.open('ABPartsOfflineDB', 3);"
echo "   request.onsuccess = function(event) {"
echo "     const db = event.target.result;"
echo "     const tx = db.transaction('protocols', 'readonly');"
echo "     const store = tx.objectStore('protocols');"
echo "     const countRequest = store.count();"
echo "     countRequest.onsuccess = function() {"
echo "       console.log('Protocols in IndexedDB:', countRequest.result);"
echo "     };"
echo "   };"
echo ""
echo "If you still see errors, clear browser cache:"
echo "  - DevTools > Application > Clear storage > Clear site data"
echo "  - Close browser completely"
echo "  - Reopen and try again"
echo ""

