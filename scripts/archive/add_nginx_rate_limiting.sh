#!/bin/bash

# Add rate limiting to nginx to prevent brute force attacks

set -e

echo "=========================================="
echo "Adding Nginx Rate Limiting"
echo "=========================================="
echo ""

# Backup current config
sudo cp /etc/nginx/sites-available/abparts.oraseas.com /etc/nginx/sites-available/abparts.oraseas.com.backup.$(date +%Y%m%d_%H%M%S)

# Create rate limiting configuration
sudo tee /etc/nginx/conf.d/rate-limit.conf > /dev/null << 'EOF'
# Rate limiting zones
# Limit login attempts to prevent brute force
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;

# Limit API requests per IP
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;

# Limit general requests per IP
limit_req_zone $binary_remote_addr zone=general_limit:10m rate=200r/m;

# Connection limiting
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
EOF

echo "Rate limiting zones created"
echo ""
echo "Now update your nginx site configuration to use these limits."
echo "Add these lines to specific locations in /etc/nginx/sites-available/abparts.oraseas.com:"
echo ""
echo "For /api/token (login endpoint):"
echo "  limit_req zone=login_limit burst=3 nodelay;"
echo ""
echo "For /api/ (all API endpoints):"
echo "  limit_req zone=api_limit burst=20 nodelay;"
echo ""
echo "For / (general traffic):"
echo "  limit_req zone=general_limit burst=50 nodelay;"
echo "  limit_conn conn_limit 10;"
echo ""

# Test nginx configuration
sudo nginx -t

if [ $? -eq 0 ]; then
    echo ""
    echo "Nginx configuration test passed!"
    echo "Reload nginx to apply changes:"
    echo "  sudo systemctl reload nginx"
else
    echo ""
    echo "ERROR: Nginx configuration test failed!"
    echo "Restoring backup..."
    sudo cp /etc/nginx/sites-available/abparts.oraseas.com.backup.* /etc/nginx/sites-available/abparts.oraseas.com
fi

echo ""
echo "Rate Limiting Configuration:"
echo "  - Login attempts: 5 per minute (burst 3)"
echo "  - API requests: 100 per minute (burst 20)"
echo "  - General requests: 200 per minute (burst 50)"
echo "  - Max connections per IP: 10"
echo ""
