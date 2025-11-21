#!/bin/bash
# Fix static image paths for production

echo "=== Fixing Static Image Paths ==="
echo ""

echo "Step 1: Committing changes..."
git add frontend/src/components/Layout.js
git add frontend/src/components/PartPhotoGallery.js
git commit -m "Fix static image paths for production nginx proxy

- Remove API_BASE_URL prefix from static file paths
- Static files are now accessed directly at /static/ via nginx
- Fixes 404 errors for profile photos, org logos, and part images"

echo ""
echo "Step 2: Pushing to repository..."
git push

echo ""
echo "=== Changes committed and pushed ==="
echo ""
echo "On production server, run:"
echo "  cd ~/abparts"
echo "  git pull"
echo "  sudo docker compose -f docker-compose.prod.yml build web --no-cache"
echo "  sudo docker compose -f docker-compose.prod.yml up -d web"
echo ""
