#!/bin/bash

echo "=== Fixing Production Part Images ==="
echo ""
echo "This will update the production Docker configuration to use /var/www/abparts_images/"
echo ""

# Check if we're on the production server
if [ ! -d "/var/www/abparts_images" ]; then
    echo "⚠️  WARNING: /var/www/abparts_images/ not found"
    echo "   Are you running this on the production server?"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "1. Checking current configuration..."
grep "/app/static/images" docker-compose.prod.yml

echo ""
echo "2. The configuration has been updated in docker-compose.prod.yml"
echo "   Old: /var/lib/abparts/images:/app/static/images"
echo "   New: /var/www/abparts_images:/app/static/images:ro"

echo ""
echo "3. Restarting API container to apply changes..."
sudo docker compose -f docker-compose.prod.yml restart api

echo ""
echo "4. Waiting for API to be ready..."
sleep 5

echo ""
echo "5. Verifying images are accessible in container..."
sudo docker exec abparts_api_prod ls -lh /app/static/images | head -10

echo ""
echo "=== VERIFICATION STEPS ==="
echo ""
echo "1. Check if images are accessible:"
echo "   sudo docker exec abparts_api_prod ls /app/static/images | head -20"
echo ""
echo "2. Test image access from browser:"
echo "   http://your-server/static/images/filename.jpg"
echo ""
echo "3. Check API logs for any errors:"
echo "   sudo docker compose -f docker-compose.prod.yml logs api --tail=50"
echo ""
echo "4. Verify database image paths are correct:"
echo "   sudo docker exec abparts_api_prod python -c \\"
echo "   from app.database import SessionLocal"
echo "   from app.models import Part"
echo "   db = SessionLocal()"
echo "   parts = db.query(Part).filter(Part.image_url.isnot(None)).limit(5).all()"
echo "   for p in parts:"
echo "       print(f'{p.part_number}: {p.image_url}')"
echo "   db.close()"
echo "   \\""
echo ""
echo "✅ Done! Check your app to see if images are now displaying."
