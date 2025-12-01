# HTTPS Setup Guide with Let's Encrypt

## Prerequisites

1. **Domain name** pointing to your server (46.62.153.166)
   - Example: `abparts.yourdomain.com`
   - DNS A record must be configured before running certbot

2. **Port 80 available** (already configured)
   - Let's Encrypt needs port 80 for verification

## Option 1: Using Certbot (Recommended)

### Step 1: Install Certbot

```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

### Step 2: Stop nginx container temporarily

```bash
cd ~/abparts
sudo docker compose -f docker-compose.prod.yml stop web
```

### Step 3: Get SSL Certificate

```bash
# Replace with your actual domain
sudo certbot certonly --standalone -d abparts.yourdomain.com

# Follow the prompts:
# - Enter your email
# - Agree to terms
# - Choose whether to share email with EFF
```

Certificates will be saved to:
- Certificate: `/etc/letsencrypt/live/abparts.yourdomain.com/fullchain.pem`
- Private Key: `/etc/letsencrypt/live/abparts.yourdomain.com/privkey.pem`

### Step 4: Update nginx Configuration

Create a new nginx config for HTTPS:

```bash
nano ~/abparts/frontend/nginx.conf
```

Replace with:

```nginx
# HTTP - Redirect to HTTPS
server {
    listen 80;
    server_name abparts.yourdomain.com;
    
    # Allow Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name abparts.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/abparts.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/abparts.yourdomain.com/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    root /usr/share/nginx/html;
    index index.html index.htm;

    # API proxy - proxy all API requests to backend
    location /api/ {
        proxy_pass http://api:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;
    }

    # Static files from backend (images, uploads)
    location /static/ {
        proxy_pass http://api:8000/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API docs
    location /docs {
        proxy_pass http://api:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /openapi.json {
        proxy_pass http://api:8000/openapi.json;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Handle client-side routing - must be last
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
}
```

### Step 5: Update docker-compose.prod.yml

```bash
nano ~/abparts/docker-compose.prod.yml
```

Update the web service to mount SSL certificates:

```yaml
  web:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
      target: production
      args:
        REACT_APP_API_BASE_URL: ${REACT_APP_API_BASE_URL:-/api}
    container_name: abparts_web_prod
    ports:
      - "80:80"
      - "443:443"  # Add HTTPS port
    volumes:
      # Mount SSL certificates
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - /var/www/certbot:/var/www/certbot
    depends_on:
      api:
        condition: service_started
    restart: unless-stopped
```

### Step 6: Update .env file

```bash
nano ~/abparts/.env
```

Update these values:

```bash
# Use HTTPS URLs
BASE_URL=https://abparts.yourdomain.com
REACT_APP_API_BASE_URL=/api

# Update CORS for HTTPS
CORS_ALLOWED_ORIGINS=https://abparts.yourdomain.com,http://localhost

# Enable HTTPS enforcement
FORCE_HTTPS=true
```

### Step 7: Rebuild and Restart

```bash
cd ~/abparts

# Rebuild frontend with new API URL
sudo docker compose -f docker-compose.prod.yml build web --no-cache

# Restart all services
sudo docker compose -f docker-compose.prod.yml down
sudo docker compose -f docker-compose.prod.yml up -d

# Check logs
sudo docker logs abparts_web_prod --tail=50
sudo docker logs abparts_api_prod --tail=20
```

### Step 8: Test HTTPS

```bash
# Test HTTP redirect
curl -I http://abparts.yourdomain.com

# Test HTTPS
curl -I https://abparts.yourdomain.com

# Check SSL certificate
openssl s_client -connect abparts.yourdomain.com:443 -servername abparts.yourdomain.com
```

### Step 9: Setup Auto-Renewal

Let's Encrypt certificates expire after 90 days. Set up auto-renewal:

```bash
# Test renewal (dry run)
sudo certbot renew --dry-run

# If successful, certbot will auto-renew via systemd timer
# Check renewal timer status
sudo systemctl status certbot.timer

# Or add a cron job
sudo crontab -e

# Add this line to renew twice daily:
0 0,12 * * * certbot renew --quiet --deploy-hook "docker compose -f /home/abparts/abparts/docker-compose.prod.yml restart web"
```

## Option 2: Using Docker with Certbot Container

If you prefer to keep everything in Docker:

### Add certbot service to docker-compose.prod.yml:

```yaml
  certbot:
    image: certbot/certbot
    container_name: abparts_certbot
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt
      - /var/www/certbot:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

## Troubleshooting

### Certificate not found
- Ensure domain DNS is pointing to your server
- Check firewall allows port 80 and 443
- Verify certbot ran successfully

### nginx fails to start
- Check certificate paths in nginx.conf
- Ensure certificates are readable by nginx container
- Check nginx logs: `sudo docker logs abparts_web_prod`

### CORS errors after HTTPS
- Update CORS_ALLOWED_ORIGINS in .env to use https://
- Restart API container to reload environment

### Mixed content warnings
- Ensure all API calls use relative paths (/api/)
- Check browser console for http:// resources

## Security Checklist

- [ ] SSL certificates installed and valid
- [ ] HTTP redirects to HTTPS
- [ ] HSTS header enabled
- [ ] CORS configured for HTTPS origin
- [ ] Auto-renewal configured
- [ ] Firewall allows ports 80 and 443
- [ ] Backend FORCE_HTTPS enabled
- [ ] Test on SSL Labs: https://www.ssllabs.com/ssltest/

## Quick Reference

```bash
# Check certificate expiry
sudo certbot certificates

# Renew certificates manually
sudo certbot renew

# Restart nginx after renewal
sudo docker compose -f docker-compose.prod.yml restart web

# View nginx SSL config
sudo docker exec abparts_web_prod cat /etc/nginx/conf.d/default.conf
```
