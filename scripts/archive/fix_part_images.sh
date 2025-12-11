#!/bin/bash

echo "=== Part Images Fix Script ==="
echo ""

# Check if images exist on server
echo "1. Checking server images directory..."
if [ -d "/var/www/abparts_images" ]; then
    echo "✓ Found /var/www/abparts_images/"
    echo "  Image count: $(find /var/www/abparts_images -type f | wc -l)"
    echo "  Sample files:"
    ls -lh /var/www/abparts_images | head -10
else
    echo "✗ Directory /var/www/abparts_images not found"
fi

echo ""
echo "2. Checking Docker container images directory..."
docker exec abparts_api ls -lh /app/static/images 2>/dev/null || echo "✗ Container not running or directory not accessible"

echo ""
echo "=== SOLUTION OPTIONS ==="
echo ""
echo "OPTION 1: Mount server directory into Docker (RECOMMENDED)"
echo "This will make the existing images immediately available without copying."
echo ""
echo "Add this to docker-compose.yml under the 'api' service volumes:"
echo "  - /var/www/abparts_images:/app/static/images:ro"
echo ""
echo "Then restart: docker-compose restart api"
echo ""
echo "---"
echo ""
echo "OPTION 2: Copy images to Docker volume"
echo "This will copy all images from server to the Docker volume."
echo ""
echo "Run: docker cp /var/www/abparts_images/. abparts_api:/app/static/images/"
echo ""
echo "=== CHECKING DATABASE IMAGE PATHS ==="
echo ""
echo "Checking what image paths are stored in the database..."
docker exec abparts_api python -c "
from app.database import SessionLocal
from app.models import Part
db = SessionLocal()
parts_with_images = db.query(Part).filter(Part.image_url.isnot(None)).limit(5).all()
print('Sample image URLs from database:')
for part in parts_with_images:
    print(f'  {part.part_number}: {part.image_url}')
db.close()
" 2>/dev/null || echo "Could not query database"

echo ""
echo "=== NEXT STEPS ==="
echo "1. Choose Option 1 or Option 2 above"
echo "2. If using Option 1, edit docker-compose.yml and restart"
echo "3. If using Option 2, run the docker cp command"
echo "4. Test by accessing: http://your-server/static/images/filename.jpg"
