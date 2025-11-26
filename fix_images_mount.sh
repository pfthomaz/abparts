#!/bin/bash

echo "=== Fixing Part Images Access ==="
echo ""
echo "This script will configure Docker to use the server's image directory"
echo ""

# Backup docker-compose.yml
echo "1. Creating backup of docker-compose.yml..."
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)
echo "✓ Backup created"

echo ""
echo "2. Updating docker-compose.yml to mount /var/www/abparts_images..."

# Update the api service volumes section
# Replace the api_static_images volume with the server directory mount
sed -i.bak '/api_static_images:\/app\/static\/images/c\      - /var/www/abparts_images:/app/static/images:ro # Mount server images directory (read-only)' docker-compose.yml

echo "✓ Updated docker-compose.yml"

echo ""
echo "3. Restarting API container to apply changes..."
docker-compose restart api

echo ""
echo "4. Waiting for API to be ready..."
sleep 5

echo ""
echo "5. Testing image access..."
echo ""
echo "Checking if images are accessible in container:"
docker exec abparts_api ls -lh /app/static/images | head -10

echo ""
echo "=== VERIFICATION ==="
echo ""
echo "To verify images are working:"
echo "1. Visit your app and check if part images display"
echo "2. Or test directly: curl http://your-server/static/images/filename.jpg"
echo ""
echo "If images still don't show, check:"
echo "- Image filenames in database match files in /var/www/abparts_images/"
echo "- Nginx is properly proxying /static/images/ to backend"
echo "- File permissions allow Docker to read the images"
echo ""
echo "To check database image paths:"
echo "docker exec abparts_api python -c \"
from app.database import SessionLocal
from app.models import Part
db = SessionLocal()
parts = db.query(Part).filter(Part.image_url.isnot(None)).limit(5).all()
for p in parts:
    print(f'{p.part_number}: {p.image_url}')
db.close()
\""
