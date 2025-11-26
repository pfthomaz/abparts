#!/bin/bash

echo "=== Checking nginx configuration ==="
echo ""

# Check nginx config for abparts
echo "1. Nginx site configuration:"
if [ -f /etc/nginx/sites-available/abparts.oraseas.com ]; then
    cat /etc/nginx/sites-available/abparts.oraseas.com
elif [ -f /etc/nginx/sites-available/abparts ]; then
    cat /etc/nginx/sites-available/abparts
else
    echo "⚠ No abparts nginx config found"
    echo "Checking all available sites:"
    ls -la /etc/nginx/sites-available/
fi
echo ""

# Check if site is enabled
echo "2. Enabled sites:"
ls -la /etc/nginx/sites-enabled/
echo ""

# Check nginx status
echo "3. Nginx status:"
sudo systemctl status nginx --no-pager | head -20
echo ""

# Test nginx config
echo "4. Testing nginx configuration:"
sudo nginx -t
echo ""

# Check what's listening on port 80 and 443
echo "5. Ports 80 and 443:"
sudo netstat -tulpn | grep -E ':80|:443'
echo ""

# Check if API is accessible locally
echo "6. Testing API locally:"
curl -s http://localhost:8000/health | python3 -m json.tool || echo "✗ API not responding on localhost:8000"
echo ""

# Check docker containers
echo "7. Docker containers:"
docker compose ps
echo ""

echo "=== Done ==="
