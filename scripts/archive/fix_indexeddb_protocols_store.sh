#!/bin/bash
# Fix IndexedDB Protocols Store Issue
# This increments the database version to force schema upgrade

set -e

echo "=========================================="
echo "Fixing IndexedDB Protocols Store"
echo "=========================================="
echo ""

echo "PROBLEM:"
echo "The 'protocols' store doesn't exist in your browser's IndexedDB."
echo "This happens when the database was created with an older version."
echo ""

echo "SOLUTION:"
echo "1. Increment DB_VERSION to force schema upgrade"
echo "2. Delete old database in browser"
echo "3. Rebuild and deploy"
echo ""

# Check if we're in the right directory
if [ ! -f "frontend/src/db/indexedDB.js" ]; then
  echo "ERROR: Must run from abparts root directory"
  exit 1
fi

echo "Step 1: Database version incremented (already done)"
echo "✓ DB_VERSION changed from 2 to 3"
echo ""

echo "Step 2: Committing changes..."
git add frontend/src/db/indexedDB.js
git commit -m "Fix: Increment IndexedDB version to ensure protocols store exists"
echo "✓ Changes committed"
echo ""

echo "Step 3: Pushing to repository..."
git push origin main
echo "✓ Changes pushed"
echo ""

echo "=========================================="
echo "Next: Deploy to Production"
echo "=========================================="
echo ""
echo "Run on production server:"
echo "  cd ~/abparts"
echo "  git pull origin main"
echo "  docker compose -f docker-compose.prod.yml build --no-cache web"
echo "  docker compose -f docker-compose.prod.yml up -d web"
echo ""
echo "Then in browser:"
echo "  1. F12 > Application > Storage > IndexedDB"
echo "  2. Right-click 'ABPartsOfflineDB' > Delete database"
echo "  3. Cmd+Shift+R (hard refresh)"
echo "  4. Login"
echo "  5. Check console for: [OfflinePreloader] ✓ Cached X protocols"
echo ""
