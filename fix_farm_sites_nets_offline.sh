#!/bin/bash

# Fix farmSitesService and netsService for offline mode
# Replace STORES constants with string literals and add userContext support

echo "Fixing farmSitesService and netsService for offline mode..."

# Fix farmSitesService.js
echo "Updating farmSitesService.js..."
sed -i '' 's/STORES\.FARM_SITES/'"'"'farmSites'"'"'/g' frontend/src/services/farmSitesService.js
sed -i '' 's/getCachedData('"'"'farmSites'"'"')/getCachedData('"'"'farmSites'"'"', userContext)/g' frontend/src/services/farmSitesService.js
sed -i '' 's/isCacheStale('"'"'farmSites'"'"'/isCacheStale('"'"'farmSites'"'"', userContext/g' frontend/src/services/farmSitesService.js
sed -i '' 's/cacheData('"'"'farmSites'"'"'/cacheData('"'"'farmSites'"'"', /g' frontend/src/services/farmSitesService.js

# Fix netsService.js  
echo "Updating netsService.js..."
sed -i '' 's/STORES\.NETS/'"'"'nets'"'"'/g' frontend/src/services/netsService.js
sed -i '' 's/getCachedData('"'"'nets'"'"')/getCachedData('"'"'nets'"'"', userContext)/g' frontend/src/services/netsService.js
sed -i '' 's/isCacheStale('"'"'nets'"'"'/isCacheStale('"'"'nets'"'"', userContext/g' frontend/src/services/netsService.js
sed -i '' 's/cacheData('"'"'nets'"'"'/cacheData('"'"'nets'"'"', /g' frontend/src/services/netsService.js

echo "✓ Services updated with string literals"
echo ""
echo "Note: You still need to:"
echo "1. Add userContext parameter to function signatures"
echo "2. Update NetCleaningRecords page to pass userContext"
echo "3. Test offline functionality"
