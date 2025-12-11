#!/bin/bash

echo "=== Fixing Nginx Caching Issue ==="
echo ""

echo "1. Copying updated nginx.conf to server..."
scp frontend/nginx.conf diogo@46.62.153.166:/tmp/

echo ""
echo "2. Deploying on server..."
ssh diogo@46.62.153.166 << 'ENDSSH'

# Move file to correct location
sudo mv /tmp/nginx.conf /root/abparts/frontend/

cd /root/abparts

echo "Rebuilding web container with new nginx config..."
sudo docker compose -f docker-compose.prod.yml build --no-cache web

echo ""
echo "Restarting web container..."
sudo docker compose -f docker-compose.prod.yml up -d web

echo ""
echo "Waiting for container to start..."
sleep 5

echo ""
echo "Verifying nginx config..."
sudo docker exec abparts_web_prod nginx -t

echo ""
echo "Checking Cache-Control headers..."
curl -I https://abparts.oraseas.com/ 2>&1 | grep -i cache

echo ""
echo "=== Done ==="
echo ""
echo "Now clear your browser cache or use Ctrl+Shift+R to hard refresh"
echo "The index.html will no longer be cached, so you'll always get the latest version"

ENDSSH
