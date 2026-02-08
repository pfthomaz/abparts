#!/bin/bash
# Deploy Offline Protocols Caching Fix to Production
# This script pulls the latest code and rebuilds the frontend with the protocols caching fix

set -e

echo "=========================================="
echo "Deploying Offline Protocols Caching Fix"
echo "=========================================="
echo ""

# Step 1: Pull latest code
echo "Step 1: Pulling latest code from repository..."
cd ~/abparts
git pull origin main
echo "✓ Code updated"
echo ""

# Step 2: Rebuild web container (no cache to ensure fresh build)
echo "Step 2: Rebuilding web container with latest code..."
docker compose -f docker-compose.prod.yml build --no-cache web
echo "✓ Web container rebuilt"
echo ""

# Step 3: Restart web container
echo "Step 3: Restarting web container..."
docker compose -f docker-compose.prod.yml up -d web
echo "✓ Web container restarted"
echo ""

# Step 4: Wait for container to be healthy
echo "Step 4: Waiting for container to start..."
sleep 5
echo "✓ Container should be ready"
echo ""

echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "NEXT STEPS:"
echo "1. Open browser and go to https://abparts.oraseas.com"
echo "2. Open DevTools (F12) > Application > Storage > IndexedDB"
echo "3. Delete the 'ABPartsOfflineDB' database"
echo "4. Refresh the page (Cmd+Shift+R)"
echo "5. Login with your credentials"
echo "6. Check DevTools Console for '[OfflinePreloader]' messages"
echo "7. Verify protocols are cached in IndexedDB > ABPartsOfflineDB > protocols"
echo ""
echo "Expected console output:"
echo "  [OfflinePreloader] Starting data preload for offline mode..."
echo "  [OfflinePreloader] ✓ Cached 18 machines"
echo "  [OfflinePreloader] ✓ Cached X protocols  <-- Should see this!"
echo "  [OfflinePreloader] ✓ Cached 24 users"
echo "  [OfflinePreloader] ✓ Cached X farm sites"
echo "  [OfflinePreloader] ✓ Cached X nets"
echo "  [OfflinePreloader] Preload complete: 5/5 successful"
echo ""
