#!/bin/bash

# Offline Mode Diagnostic Script
# Checks if offline mode is properly configured

echo "=========================================="
echo "ABParts Offline Mode Diagnostic"
echo "=========================================="
echo ""

echo "1. Checking service worker file..."
if [ -f "frontend/public/service-worker.js" ]; then
    echo "   ✓ Service worker file exists"
    echo "   Size: $(wc -c < frontend/public/service-worker.js) bytes"
else
    echo "   ✗ Service worker file NOT found"
fi
echo ""

echo "2. Checking if service worker is registered in index.js..."
if grep -q "serviceWorkerRegistration.register" frontend/src/index.js; then
    echo "   ✓ Service worker registration found"
else
    echo "   ✗ Service worker registration NOT found"
fi
echo ""

echo "3. Checking if OfflineProvider is in App.js..."
if grep -q "OfflineProvider" frontend/src/App.js; then
    echo "   ✓ OfflineProvider found in App.js"
else
    echo "   ✗ OfflineProvider NOT found in App.js"
fi
echo ""

echo "4. Checking if OfflineIndicator component exists..."
if [ -f "frontend/src/components/OfflineIndicator.js" ]; then
    echo "   ✓ OfflineIndicator component exists"
else
    echo "   ✗ OfflineIndicator component NOT found"
fi
echo ""

echo "5. Checking if IndexedDB utilities exist..."
if [ -f "frontend/src/db/indexedDB.js" ]; then
    echo "   ✓ IndexedDB utilities exist"
else
    echo "   ✗ IndexedDB utilities NOT found"
fi
echo ""

echo "6. Checking browser console for errors..."
echo "   Open browser DevTools (F12) and check:"
echo "   - Console tab for errors"
echo "   - Application tab > Service Workers"
echo "   - Application tab > IndexedDB"
echo ""

echo "7. Testing service worker in browser..."
echo "   Run this in browser console:"
echo "   navigator.serviceWorker.getRegistrations().then(r => console.log('SW:', r))"
echo ""

echo "8. Testing IndexedDB in browser..."
echo "   Run this in browser console:"
echo "   indexedDB.databases().then(dbs => console.log('DBs:', dbs))"
echo ""

echo "=========================================="
echo "Common Issues:"
echo "=========================================="
echo ""
echo "Issue 1: Service Worker not registering"
echo "  - Check if HTTPS is enabled (required for SW except localhost)"
echo "  - Check browser console for SW registration errors"
echo "  - Try hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)"
echo ""
echo "Issue 2: Offline indicator not showing"
echo "  - Simulate offline: DevTools > Network tab > Throttling > Offline"
echo "  - Check if OfflineIndicator is rendered in Layout component"
echo ""
echo "Issue 3: Data not saving offline"
echo "  - Check IndexedDB in DevTools > Application tab"
echo "  - Check browser console for IndexedDB errors"
echo "  - Verify browser supports IndexedDB"
echo ""
echo "Issue 4: Production build issues"
echo "  - Service worker might not be copied to build folder"
echo "  - Check if service-worker.js exists in build/public/"
echo "  - Rebuild frontend: docker compose exec web npm run build"
echo ""

