#!/bin/bash

# Verify Protocols Fix is Deployed

echo "=========================================="
echo "Verify Protocols Fix Deployment"
echo "=========================================="
echo ""

echo "1️⃣ Checking git commit..."
git log --oneline -1

echo ""
echo "2️⃣ Checking if fix is in offlineDataPreloader.js..."
if grep -q "await cacheData('protocols'" frontend/src/services/offlineDataPreloader.js; then
    echo "✅ Fix found: Using string literal 'protocols'"
    grep -n "await cacheData('protocols'" frontend/src/services/offlineDataPreloader.js
else
    echo "❌ Fix NOT found: Still using STORES.PROTOCOLS"
    grep -n "STORES.PROTOCOLS" frontend/src/services/offlineDataPreloader.js || echo "No STORES.PROTOCOLS found either - check file manually"
fi

echo ""
echo "3️⃣ Checking if STORES import was removed..."
if grep -q "import.*STORES.*from.*indexedDB" frontend/src/services/offlineDataPreloader.js; then
    echo "⚠️  STORES still imported (should be removed)"
    grep -n "import.*STORES" frontend/src/services/offlineDataPreloader.js
else
    echo "✅ STORES import removed"
fi

echo ""
echo "4️⃣ Checking all string literal usages..."
echo "Should see: 'protocols', 'users', 'farmSites', 'nets', 'machines'"
grep -n "await cacheData('" frontend/src/services/offlineDataPreloader.js | head -5

echo ""
echo "5️⃣ Checking container status..."
docker compose -f docker-compose.prod.yml ps

echo ""
echo "=========================================="
echo "Verification complete!"
echo "=========================================="
echo ""
echo "If all checks pass, the fix is deployed."
echo "Now clear browser cache and test!"
echo ""

