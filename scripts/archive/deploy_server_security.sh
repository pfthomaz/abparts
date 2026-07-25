#!/bin/bash

# Complete Server Security Deployment
# This script will set up Fail2ban, UFW, and Nginx rate limiting

set -e

echo "=========================================="
echo "ABParts Server Security Deployment"
echo "=========================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: This script must be run with sudo"
    echo "Usage: sudo ./deploy_server_security.sh"
    exit 1
fi

# Get the actual user (not root when using sudo)
ACTUAL_USER="${SUDO_USER:-$USER}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Running as: $ACTUAL_USER"
echo "Script directory: $SCRIPT_DIR"
echo ""

# Step 1: Install and configure Fail2ban and UFW
echo "=========================================="
echo "Step 1: Installing Fail2ban and UFW"
echo "=========================================="
apt-get update
apt-get install -y fail2ban ufw unattended-upgrades

# Step 2: Configure Fail2ban
echo ""
echo "=========================================="
echo "Step 2: Configuring Fail2ban"
echo "=========================================="

cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
# Ban for 1 hour (3600 seconds)
bantime = 3600

# Check for attacks in last 10 minutes
findtime = 600

# Ban after 5 failed attempts
maxretry = 5

# Ignore local IPs
ignoreip = 127.0.0.1/8 ::1

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
bantime = 7200

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-noscript]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2

[nginx-noproxy]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
findtime = 60
bantime = 3600
EOF

echo "✓ Fail2ban configured"

# Step 3: Configure UFW Firewall
echo ""
echo "=========================================="
echo "Step 3: Configuring UFW Firewall"
echo "=========================================="

# Reset UFW to default state
ufw --force reset

# Set default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (CRITICAL - don't lock yourself out!)
ufw allow ssh
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable UFW
echo "y" | ufw enable

echo "✓ UFW firewall configured and enabled"

# Step 4: Configure Nginx Rate Limiting
echo ""
echo "=========================================="
echo "Step 4: Configuring Nginx Rate Limiting"
echo "=========================================="

# Backup current nginx config
if [ -f /etc/nginx/sites-available/abparts.oraseas.com ]; then
    cp /etc/nginx/sites-available/abparts.oraseas.com \
       /etc/nginx/sites-available/abparts.oraseas.com.backup.$(date +%Y%m%d_%H%M%S)
    echo "✓ Nginx config backed up"
fi

# Create rate limiting configuration
cat > /etc/nginx/conf.d/rate-limit.conf << 'EOF'
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

echo "✓ Rate limiting zones created"

# Step 5: Update nginx site configuration with rate limits
echo ""
echo "=========================================="
echo "Step 5: Applying Rate Limits to Nginx"
echo "=========================================="

# Create updated nginx configuration with rate limits
cat > /etc/nginx/sites-available/abparts.oraseas.com << 'EOF'
# ABParts Production - Host Nginx Configuration with Rate Limiting

# HTTP - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name abparts.oraseas.com;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS - Proxy to Docker containers
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name abparts.oraseas.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/abparts.oraseas.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/abparts.oraseas.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    client_max_body_size 10M;

    # AI Assistant admin and other root endpoints (strip /ai/ prefix)
    location ~ ^/ai/(admin|analytics|health|info)$ {
        # Rate limiting for AI endpoints
        limit_req zone=api_limit burst=20 nodelay;
        limit_conn conn_limit 10;
        
        rewrite ^/ai/(.*)$ /$1 break;
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # AI Assistant API endpoints (strip /ai/ prefix and forward)
    location /ai/ {
        # Rate limiting for AI endpoints
        limit_req zone=api_limit burst=20 nodelay;
        limit_conn conn_limit 10;
        
        proxy_pass http://localhost:8001/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Login endpoint - strict rate limiting to prevent brute force
    location /api/token {
        # STRICT: Only 5 login attempts per minute
        limit_req zone=login_limit burst=3 nodelay;
        limit_conn conn_limit 5;
        
        proxy_pass http://localhost:8000/token;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        
        # Prevent browser caching
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0" always;
        add_header Pragma "no-cache" always;
    }

    # Proxy to Backend API
    location /api/ {
        # Rate limiting for API endpoints
        limit_req zone=api_limit burst=20 nodelay;
        limit_conn conn_limit 10;
        
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        
        # Prevent browser caching of API responses
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0" always;
        add_header Pragma "no-cache" always;
    }

    # Backend endpoints (without /api prefix for backward compatibility)
    location ~ ^/(token|health|warehouses|parts|inventory|machines|organizations|users|customer_orders|supplier_orders|stock_adjustments|transactions|dashboard|uploads|images|maintenance_protocols|maintenance_executions|protocol_translations) {
        # Rate limiting for backend endpoints
        limit_req zone=api_limit burst=20 nodelay;
        limit_conn conn_limit 10;
        
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Proxy to Docker web container (React app + static files)
    location / {
        # Rate limiting for general traffic
        limit_req zone=general_limit burst=50 nodelay;
        limit_conn conn_limit 10;
        
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;
        
        # Prevent caching of HTML
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    access_log /var/log/nginx/abparts_access.log;
    error_log /var/log/nginx/abparts_error.log;
}
EOF

echo "✓ Nginx configuration updated with rate limits"

# Step 6: Test nginx configuration
echo ""
echo "=========================================="
echo "Step 6: Testing Nginx Configuration"
echo "=========================================="

nginx -t

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Nginx configuration test failed!"
    echo "Restoring backup..."
    cp /etc/nginx/sites-available/abparts.oraseas.com.backup.* \
       /etc/nginx/sites-available/abparts.oraseas.com
    exit 1
fi

echo "✓ Nginx configuration test passed"

# Step 7: Enable automatic security updates
echo ""
echo "=========================================="
echo "Step 7: Enabling Automatic Security Updates"
echo "=========================================="

dpkg-reconfigure -plow unattended-upgrades
echo "✓ Automatic security updates enabled"

# Step 8: Restart services
echo ""
echo "=========================================="
echo "Step 8: Restarting Services"
echo "=========================================="

systemctl restart fail2ban
systemctl enable fail2ban
echo "✓ Fail2ban restarted and enabled"

systemctl reload nginx
echo "✓ Nginx reloaded"

# Step 9: Display status
echo ""
echo "=========================================="
echo "✓ SECURITY DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "Security Configuration Summary:"
echo ""
echo "1. FAIL2BAN (Auto-ban attackers)"
echo "   - Ban time: 1 hour (3600 seconds)"
echo "   - Find time: 10 minutes (600 seconds)"
echo "   - Max retries: 5 attempts"
echo "   - SSH max retries: 3 attempts (2 hour ban)"
echo ""
echo "2. UFW FIREWALL"
echo "   - Default: Deny incoming, Allow outgoing"
echo "   - Allowed ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)"
echo ""
echo "3. NGINX RATE LIMITING"
echo "   - Login attempts: 5 per minute (burst 3)"
echo "   - API requests: 100 per minute (burst 20)"
echo "   - General requests: 200 per minute (burst 50)"
echo "   - Max connections per IP: 10"
echo ""
echo "4. AUTOMATIC SECURITY UPDATES"
echo "   - Enabled for critical security patches"
echo ""
echo "=========================================="
echo "Current Status:"
echo "=========================================="
echo ""
echo "UFW Firewall Status:"
ufw status verbose
echo ""
echo "Fail2ban Status:"
fail2ban-client status
echo ""
echo "=========================================="
echo "Useful Commands:"
echo "=========================================="
echo ""
echo "Monitor banned IPs:"
echo "  sudo fail2ban-client status"
echo "  sudo fail2ban-client status sshd"
echo "  sudo fail2ban-client status nginx-limit-req"
echo ""
echo "Unban an IP:"
echo "  sudo fail2ban-client set sshd unbanip <IP_ADDRESS>"
echo ""
echo "View logs:"
echo "  sudo tail -f /var/log/fail2ban.log"
echo "  sudo tail -f /var/log/nginx/error.log"
echo "  sudo tail -f /var/log/nginx/access.log"
echo ""
echo "Check firewall:"
echo "  sudo ufw status verbose"
echo ""
echo "Test rate limiting:"
echo "  # Try multiple rapid requests to see rate limiting in action"
echo "  for i in {1..10}; do curl -I https://abparts.oraseas.com/api/health; done"
echo ""
echo "=========================================="
echo ""

