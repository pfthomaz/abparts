#!/bin/bash

echo "=== Part Images Diagnostic ==="
echo ""

echo "1. Server images directory:"
echo "   Location: /var/www/abparts_images/"
if [ -d "/var/www/abparts_images" ]; then
    echo "   Status: ✓ EXISTS"
    echo "   Files: $(find /var/www/abparts_images -type f 2>/dev/null | wc -l)"
    echo "   Size: $(du -sh /var/www/abparts_images 2>/dev/null | cut -f1)"
    echo ""
    echo "   Sample files:"
    ls -lh /var/www/abparts_images 2>/dev/null | head -5
else
    echo "   Status: ✗ NOT FOUND"
fi

echo ""
echo "2. Docker container images directory:"
echo "   Location: /app/static/images (inside container)"
if docker exec abparts_api test -d /app/static/images 2>/dev/null; then
    echo "   Status: ✓ EXISTS"
    echo "   Files: $(docker exec abparts_api find /app/static/images -type f 2>/dev/null | wc -l)"
    echo ""
    echo "   Sample files:"
    docker exec abparts_api ls -lh /app/static/images 2>/dev/null | head -5
else
    echo "   Status: ✗ NOT ACCESSIBLE"
fi

echo ""
echo "3. Database image paths:"
docker exec abparts_api python -c "
from app.database import SessionLocal
from app.models import Part
db = SessionLocal()
parts = db.query(Part).filter(Part.image_url.isnot(None)).limit(5).all()
if parts:
    print('   Sample image URLs:')
    for p in parts:
        print(f'   - {p.part_number}: {p.image_url}')
else:
    print('   No parts with images found in database')
db.close()
" 2>/dev/null || echo "   ✗ Could not query database"

echo ""
echo "4. Current docker-compose.yml volume configuration:"
echo "   API volumes:"
grep -A 2 "api_static_images\|/var/www/abparts_images" docker-compose.yml | head -5

echo ""
echo "=== DIAGNOSIS ==="
echo ""

# Check if using volume or mount
if grep -q "/var/www/abparts_images:/app/static/images" docker-compose.yml; then
    echo "✓ Docker is configured to mount server directory"
    echo "  Images should be accessible"
elif grep -q "api_static_images:/app/static/images" docker-compose.yml; then
    echo "✗ Docker is using a volume instead of mounting server directory"
    echo "  This is why images are not showing!"
    echo ""
    echo "  FIX: Run ./fix_images_mount.sh"
else
    echo "? Could not determine volume configuration"
fi

echo ""
echo "=== RECOMMENDATIONS ==="
echo ""
echo "If images are not showing:"
echo "1. Run: ./fix_images_mount.sh"
echo "2. Or manually follow: PART_IMAGES_FIX_GUIDE.md"
echo "3. Then test: curl -I http://your-server/static/images/test.jpg"
