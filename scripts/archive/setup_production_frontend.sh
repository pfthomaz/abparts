#!/bin/bash

echo "=== Setting up Production Frontend ==="
echo ""

# First, let's fix the database connection issue
echo "1. Restarting API to fix database connection..."
docker compose restart api
sleep 5

# Check API health
echo "2. Checking API health..."
API_HEALTH=$(curl -s http://localhost:8000/health)
echo "$API_HEALTH" | python3 -m json.tool
echo ""

# Build the React app for production
echo "3. Building React app for production..."
cd frontend

# Update the API URL in the build
export REACT_APP_API_BASE_URL=https://abparts.oraseas.com/api

echo "Installing dependencies..."
npm install

echo "Building production bundle..."
npm run build

if [ $? -eq 0 ]; then
    echo "✓ Build successful"
else
    echo "✗ Build failed"
    exit 1
fi

cd ..
echo ""

# Create backup of nginx config
echo "4. Backing up nginx config..."
sudo cp /etc/nginx/sites-available/abparts.oraseas.com /etc/nginx/sites-available/abparts.oraseas.com.backup
echo "✓ Backup created"
echo ""

# Create new nginx config
echo "5. Creating production nginx config..."
sudo tee /etc/nginx/sites-available/abparts.oraseas.com > /dev/null << 'EOF'
# ABParts - Production Configuration
# Frontend: React (built static files)
# Backend: FastAPI (Docker port 8000)

# HTTP - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name abparts.oraseas.com;

    # Allow Let's Encrypt challenges
    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    # Redirect all other HTTP traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS - Main Application
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name abparts.oraseas.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/abparts.oraseas.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/abparts.oraseas.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Client max body size (for file uploads)
    client_max_body_size 10M;

    # Backend API - Direct proxy to FastAPI
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files from backend (uploads, etc.)
    location /static/ {
        proxy_pass http://localhost:8000/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Frontend - Serve built React app
    location / {
        root /home/abparts/abparts/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Access and error logs
    access_log /var/log/nginx/abparts_access.log;
    error_log /var/log/nginx/abparts_error.log;
}
EOF

echo "✓ Nginx config created"
echo ""

# Test nginx config
echo "6. Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✓ Nginx config is valid"
    
    # Reload nginx
    echo ""
    echo "7. Reloading nginx..."
    sudo systemctl reload nginx
    echo "✓ Nginx reloaded"
else
    echo "✗ Nginx config has errors"
    echo "Restoring backup..."
    sudo cp /etc/nginx/sites-available/abparts.oraseas.com.backup /etc/nginx/sites-available/abparts.oraseas.com
    exit 1
fi

echo ""
echo "=== Production Setup Complete ==="
echo ""
echo "Testing the site..."
sleep 2
curl -I https://abparts.oraseas.com
echo ""
echo "If you see HTTP 200, the site is working!"
echo "If you see HTTP 502, check: docker compose logs api"
