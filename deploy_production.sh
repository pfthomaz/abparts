#!/bin/bash

echo "=== ABParts Production Deployment ==="
echo ""

# Check if running on server
if [ ! -f "/etc/nginx/sites-available/abparts.oraseas.com" ]; then
    echo "⚠️  This script should be run on the production server"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Step 1: Pulling latest code..."
git pull

echo ""
echo "Step 2: Updating host nginx configuration..."
sudo cp nginx-production.conf /etc/nginx/sites-available/abparts.oraseas.com
sudo nginx -t

echo ""
echo "Step 3: Rebuilding Docker containers..."
sudo docker compose -f docker-compose.prod.yml build --no-cache web api

echo ""
echo "Step 4: Restarting services..."
sudo docker compose -f docker-compose.prod.yml up -d

echo ""
echo "Step 5: Restarting host nginx..."
sudo systemctl restart nginx

echo ""
echo "Step 6: Waiting for services to be ready..."
sleep 10

echo ""
echo "Step 7: Checking service status..."
sudo docker compose -f docker-compose.prod.yml ps

echo ""
echo "Step 8: Testing endpoints..."
echo "  - Frontend: https://abparts.oraseas.com"
curl -I https://abparts.oraseas.com 2>/dev/null | head -3

echo "  - API health: https://abparts.oraseas.com/api/health"
curl -s https://abparts.oraseas.com/api/health | head -3

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "✅ Frontend: https://abparts.oraseas.com"
echo "✅ API Docs: https://abparts.oraseas.com/api/docs"
echo ""
echo "Check logs:"
echo "  sudo docker compose -f docker-compose.prod.yml logs -f web"
echo "  sudo docker compose -f docker-compose.prod.yml logs -f api"
