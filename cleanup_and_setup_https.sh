#!/bin/bash

# Cleanup and HTTPS Setup Script for ABParts
# This script will:
# 1. Remove old ABParts and aquaculture-map configurations
# 2. Remove old application files
# 3. Create new nginx configuration for Docker-based ABParts
# 4. Test and reload nginx

set -e  # Exit on error

echo "========================================="
echo "ABParts HTTPS Setup - Cleanup & Configure"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "Step 1: Backing up old configurations..."
BACKUP_DIR="/root/nginx_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup old configs
if [ -f /etc/nginx/sites-available/abparts.oraseas.com.conf ]; then
    cp /etc/nginx/sites-available/abparts.oraseas.com.conf "$BACKUP_DIR/"
    echo "✓ Backed up old abparts config"
fi

if [ -f /etc/nginx/sites-available/aquaculture-map.conf ]; then
    cp /etc/nginx/sites-available/aquaculture-map.conf "$BACKUP_DIR/"
    echo "✓ Backed up aquaculture-map config"
fi

echo "Backups saved to: $BACKUP_DIR"
echo ""

echo "Step 2: Removing old nginx configurations..."

# Remove symlinks from sites-enabled
rm -f /etc/nginx/sites-enabled/abparts.oraseas.com.conf
rm -f /etc/nginx/sites-enabled/aquaculture-map.conf
echo "✓ Removed old symlinks from sites-enabled"

# Remove old config files
rm -f /etc/nginx/sites-available/abparts.oraseas.com.conf
rm -f /etc/nginx/sites-available/abparts.oraseas.com.conf.bak.*
rm -f /etc/nginx/sites-available/aquaculture-map.conf
echo "✓ Removed old config files from sites-available"
echo ""

echo "Step 3: Creating new nginx configuration for Docker-based ABParts..."

cat > /etc/nginx/sites-available/abparts.oraseas.com << 'EOF'
# ABParts - Docker-based Application
# Frontend: React (port 3000)
# Backend: FastAPI (port 8000)

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

    # SSL certificates (already exist from previous setup)
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

    # Static files from backend
    location /static/ {
        proxy_pass http://localhost:8000/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Frontend (React app) - Everything else
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Access and error logs
    access_log /var/log/nginx/abparts_access.log;
    error_log /var/log/nginx/abparts_error.log;
}
EOF

echo "✓ Created new nginx configuration"
echo ""

echo "Step 4: Enabling the new configuration..."
ln -s /etc/nginx/sites-available/abparts.oraseas.com /etc/nginx/sites-enabled/
echo "✓ Enabled new configuration"
echo ""

echo "Step 5: Testing nginx configuration..."
if nginx -t; then
    echo "✓ Nginx configuration is valid"
else
    echo "✗ Nginx configuration test failed!"
    echo "Restoring backup..."
    cp "$BACKUP_DIR/abparts.oraseas.com.conf" /etc/nginx/sites-available/
    ln -s /etc/nginx/sites-available/abparts.oraseas.com.conf /etc/nginx/sites-enabled/
    exit 1
fi
echo ""

echo "Step 6: Reloading nginx..."
systemctl reload nginx
echo "✓ Nginx reloaded successfully"
echo ""

echo "========================================="
echo "✓ Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Make sure Docker containers are running:"
echo "   cd ~/abparts && docker-compose ps"
echo ""
echo "2. Test the site:"
echo "   curl -I https://abparts.oraseas.com"
echo ""
echo "3. Check nginx logs if needed:"
echo "   sudo tail -f /var/log/nginx/abparts_error.log"
echo ""
echo "Old configurations backed up to: $BACKUP_DIR"
echo ""
