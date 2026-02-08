#!/bin/bash
# Fix Offline Protocols Loading and Environment Configuration

echo "=== Fixing Offline Protocols and Environment Configuration ==="
echo ""

# Step 1: Update production .env file
echo "Step 1: Updating production .env file for correct API URL..."
sed -i 's|REACT_APP_API_BASE_URL=http://localhost:8000|REACT_APP_API_BASE_URL=/api|g' .env

# Verify the change
echo "Verifying .env change..."
grep "REACT_APP_API_BASE_URL" .env

echo ""
echo "Step 2: Rebuilding web container with fixed offline preloader..."
docker compose -f docker-compose.prod.yml build --no-cache web

echo ""
echo "Step 3: Restarting web container..."
docker compose -f docker-compose.prod.yml up -d web

echo ""
echo "=== Fix Complete! ==="
echo ""
echo "Changes applied:"
echo "1. ✅ Fixed STORES.MAINTENANCE_PROTOCOLS → STORES.PROTOCOLS in offlineDataPreloader.js"
echo "2. ✅ Updated production .env to use /api instead of http://localhost:8000"
echo "3. ✅ Rebuilt and restarted web container"
echo ""
echo "Next steps:"
echo "1. Clear browser cache and IndexedDB"
echo "2. Login to production app"
echo "3. Check IndexedDB > protocols store - should now have data"
echo "4. Test offline mode by going offline and accessing maintenance protocols"
echo ""
echo "For local development:"
echo "- Keep .env with REACT_APP_API_BASE_URL=http://localhost:8000"
echo "- Use docker-compose.yml (not docker-compose.prod.yml)"
