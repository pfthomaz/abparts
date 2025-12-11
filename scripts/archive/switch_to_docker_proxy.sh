#!/bin/bash

echo "=== Switching to Full Docker Setup ==="
echo ""
echo "This will configure host nginx to proxy everything to Docker containers"
echo "instead of serving files from the filesystem."
echo ""

# Backup current config
echo "1. Backing up current nginx config..."
sudo cp /etc/nginx/sites-enabled/abparts.oraseas.com /etc/nginx/sites-enabled/abparts.oraseas.com.backup.$(date +%Y%m%d_%H%M%S)

# Copy new config
echo ""
echo "2. Installing new nginx config..."
sudo cp nginx-docker-proxy.conf /etc/nginx/sites-enabled/abparts.oraseas.com

# Test nginx config
echo ""
echo "3. Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "   ✅ Nginx config is valid"
    
    echo ""
    echo "4. Reloading nginx..."
    sudo systemctl reload nginx
    
    echo ""
    echo "5. Verifying Docker containers are running..."
    sudo docker ps | grep -E "abparts_(web|api)_prod"
    
    echo ""
    echo "=== Done ==="
    echo ""
    echo "Your setup is now:"
    echo "  - Host nginx (port 443) → SSL termination only"
    echo "  - Docker web container (port 3001) → Serves React frontend"
    echo "  - Docker API container (port 8000) → Serves backend API"
    echo ""
    echo "To update frontend in the future:"
    echo "  1. Make code changes"
    echo "  2. git push"
    echo "  3. On server: git pull"
    echo "  4. sudo docker compose -f docker-compose.prod.yml build web"
    echo "  5. sudo docker compose -f docker-compose.prod.yml up -d web"
    echo ""
    echo "Test at: https://abparts.oraseas.com"
else
    echo "   ❌ Nginx config has errors!"
    echo "   Restoring backup..."
    sudo cp /etc/nginx/sites-enabled/abparts.oraseas.com.backup.* /etc/nginx/sites-enabled/abparts.oraseas.com
    echo "   Original config restored."
    exit 1
fi
