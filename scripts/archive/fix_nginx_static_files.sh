#!/bin/bash

echo "=== Fixing Nginx Static Files Configuration ==="
echo ""

# Backup current config
echo "1. Backing up current nginx config..."
sudo cp /etc/nginx/sites-available/abparts.oraseas.com /etc/nginx/sites-available/abparts.oraseas.com.backup.$(date +%Y%m%d_%H%M%S)
echo "✓ Backup created"
echo ""

# Create new config with correct static file handling
echo "2. Creating corrected nginx configuration..."
sudo tee /etc/nginx/sites-available/abparts.oraseas.com > /dev/null << 'EOF'
# ABParts - Production Configuration
server {
    listen 80;
    listen [::]:80;
    server_name abparts.oraseas.com;

    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name abparts.oraseas.com;

    ssl_certificate /etc/letsencrypt/live/abparts.oraseas.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/abparts.oraseas.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    client_max_body_size 10M;

    # Root directory for frontend
    root /home/abparts/abparts/frontend/build;
    index index.html;

    # API endpoints - proxy to backend
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Backend static files (uploads, images from API)
    location /api/static/ {
        proxy_pass http://localhost:8000/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Frontend static files (CSS, JS, images from React build)
    location /static/ {
        alias /home/abparts/abparts/frontend/build/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # Ensure correct MIME types
        types {
            text/css css;
            application/javascript js;
            image/png png;
            image/jpeg jpg jpeg;
            image/gif gif;
            image/svg+xml svg;
            font/woff woff;
            font/woff2 woff2;
        }
    }

    # Frontend - serve React app
    location / {
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    access_log /var/log/nginx/abparts_access.log;
    error_log /var/log/nginx/abparts_error.log;
}
EOF

echo "✓ Nginx config created"
echo ""

# Fix permissions on build directory
echo "3. Fixing permissions on build directory..."
sudo chmod 755 /home/abparts
sudo chmod 755 /home/abparts/abparts
sudo chmod 755 /home/abparts/abparts/frontend
sudo chmod -R 755 /home/abparts/abparts/frontend/build
echo "✓ Permissions fixed"
echo ""

# Test nginx config
echo "4. Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✓ Nginx config is valid"
    
    # Reload nginx
    echo ""
    echo "5. Reloading nginx..."
    sudo systemctl reload nginx
    echo "✓ Nginx reloaded"
else
    echo "✗ Nginx config has errors"
    echo "Restoring backup..."
    sudo cp /etc/nginx/sites-available/abparts.oraseas.com.backup.* /etc/nginx/sites-available/abparts.oraseas.com
    exit 1
fi

echo ""
echo "6. Testing the website..."
sleep 2

# Test if static files are accessible
echo "Testing CSS file:"
curl -I https://abparts.oraseas.com/static/css/main.0a281fb4.css 2>&1 | head -5

echo ""
echo "Testing JS file:"
curl -I https://abparts.oraseas.com/static/js/main.01434edc.js 2>&1 | head -5

echo ""
echo "Testing main page:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://abparts.oraseas.com)
echo "Main page HTTP status: $HTTP_CODE"

echo ""
echo "=== Fix Complete ==="
echo ""
echo "Visit: https://abparts.oraseas.com"
echo "The page should now load with CSS and JavaScript working!"
