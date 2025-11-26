# HTTPS Setup for abparts.oraseas.com

## Step-by-Step Guide

### Step 1: Check and Clean Existing Nginx Configuration

First, let's check if there are any existing nginx configurations for this domain:

```bash
# Check nginx sites-enabled
ls -la /etc/nginx/sites-enabled/

# Check nginx sites-available
ls -la /etc/nginx/sites-available/

# Search for any references to abparts.oraseas.com
grep -r "abparts.oraseas.com" /etc/nginx/

# Check if nginx is running
systemctl status nginx
```

### Step 2: Remove Old Configuration (if exists)

If you find any old configuration for abparts.oraseas.com:

```bash
# Remove from sites-enabled
sudo rm /etc/nginx/sites-enabled/abparts.oraseas.com

# Remove from sites-available
sudo rm /etc/nginx/sites-available/abparts.oraseas.com

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Step 3: Check Old Application Files

Check if there's an old application running:

```bash
# Check for any processes using port 80 or 443
sudo lsof -i :80
sudo lsof -i :443

# Check for any systemd services related to abparts
systemctl list-units | grep abparts

# Check for any old application directories
ls -la /var/www/
ls -la /opt/
ls -la /home/*/abparts*
```

### Step 4: Install Certbot (if not already installed)

```bash
# Install certbot and nginx plugin
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

### Step 5: Create Nginx Configuration for ABParts

Create a new nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/abparts.oraseas.com
```

Add this configuration:

```nginx
# HTTP - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name abparts.oraseas.com;

    # Redirect all HTTP traffic to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS - Main Application
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name abparts.oraseas.com;

    # SSL certificates (will be added by certbot)
    # ssl_certificate /etc/letsencrypt/live/abparts.oraseas.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/abparts.oraseas.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Client max body size (for file uploads)
    client_max_body_size 10M;

    # Frontend (React app)
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
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers (if needed)
        add_header Access-Control-Allow-Origin "https://abparts.oraseas.com" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    }

    # Static files (if served directly by nginx)
    location /static {
        proxy_pass http://localhost:8000/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Access and error logs
    access_log /var/log/nginx/abparts_access.log;
    error_log /var/log/nginx/abparts_error.log;
}
```

### Step 6: Enable the Site

```bash
# Create symbolic link to sites-enabled
sudo ln -s /etc/nginx/sites-available/abparts.oraseas.com /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

### Step 7: Obtain SSL Certificate with Certbot

```bash
# Run certbot to obtain and install SSL certificate
sudo certbot --nginx -d abparts.oraseas.com

# Follow the prompts:
# - Enter your email address
# - Agree to terms of service
# - Choose whether to share email with EFF
# - Certbot will automatically configure SSL
```

### Step 8: Verify SSL Certificate

```bash
# Check certificate status
sudo certbot certificates

# Test SSL configuration
curl -I https://abparts.oraseas.com

# Check certificate expiry
sudo certbot renew --dry-run
```

### Step 9: Update Docker Compose (if needed)

If your docker-compose.yml has hardcoded URLs, update them:

```yaml
# In docker-compose.yml, update environment variables
environment:
  - FRONTEND_URL=https://abparts.oraseas.com
  - BACKEND_URL=https://abparts.oraseas.com/api
```

### Step 10: Update Frontend Environment

Update your frontend `.env` file:

```bash
# .env.production
REACT_APP_API_URL=https://abparts.oraseas.com/api
```

### Step 11: Set Up Auto-Renewal

Certbot automatically sets up a cron job or systemd timer for renewal. Verify it:

```bash
# Check certbot timer
sudo systemctl status certbot.timer

# Or check cron
sudo crontab -l | grep certbot
```

## Troubleshooting

### If Port 80/443 is Already in Use

```bash
# Find what's using the port
sudo lsof -i :80
sudo lsof -i :443

# Stop the service
sudo systemctl stop <service-name>

# Or kill the process
sudo kill <PID>
```

### If DNS is Not Resolving

```bash
# Check DNS resolution
nslookup abparts.oraseas.com
dig abparts.oraseas.com

# Verify it points to your server IP
curl -I http://abparts.oraseas.com
```

### If Certbot Fails

```bash
# Check nginx is running
sudo systemctl status nginx

# Check firewall allows ports 80 and 443
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Try manual certificate request
sudo certbot certonly --nginx -d abparts.oraseas.com
```

## Security Checklist

- [ ] SSL certificate installed and working
- [ ] HTTP redirects to HTTPS
- [ ] Security headers configured
- [ ] Firewall allows ports 80 and 443
- [ ] Auto-renewal configured
- [ ] Old application removed
- [ ] Old nginx configs removed
- [ ] CORS configured correctly
- [ ] File upload size limits set
- [ ] Access logs configured

## Maintenance

### Renew Certificate Manually

```bash
sudo certbot renew
sudo systemctl reload nginx
```

### Check Certificate Expiry

```bash
sudo certbot certificates
```

### View Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/abparts_access.log

# Error logs
sudo tail -f /var/log/nginx/abparts_error.log
```

## Quick Reference Commands

```bash
# Test nginx config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Restart nginx
sudo systemctl restart nginx

# Check SSL certificate
sudo certbot certificates

# Renew certificates
sudo certbot renew

# View nginx error log
sudo tail -f /var/log/nginx/error.log
```
