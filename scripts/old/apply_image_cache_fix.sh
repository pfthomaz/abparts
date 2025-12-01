#!/bin/bash
echo "Restarting API to apply cache-busting fix..."
docker-compose restart api
echo "Waiting for API to start..."
sleep 3
echo "Checking API status..."
docker-compose ps api
echo ""
echo "✓ Done! Now when you upload/change a photo, the URL will include ?v=timestamp"
echo "  This forces the browser to fetch the new image instead of using cached version."
