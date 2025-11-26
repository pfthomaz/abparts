# HTTPS Setup Commands for abparts.oraseas.com

## Quick Setup (Recommended)

Run these commands in order:

### 1. Make scripts executable
```bash
chmod +x cleanup_and_setup_https.sh cleanup_old_files.sh
```

### 2. Run the nginx cleanup and setup
```bash
sudo ./cleanup_and_setup_https.sh
```

This will:
- ✓ Backup old nginx configs
- ✓ Remove old abparts.oraseas.com config
- ✓ Remove aquaculture-map config
- ✓ Create new Docker-compatible nginx config
- ✓ Enable and test the configuration
- ✓ Reload nginx

### 3. (Optional) Clean up old application files
```bash
sudo ./cleanup_old_files.sh
```

This will:
- ✓ Backup old files to /root/abparts_files_backup_*
- ✓ Remove /var/www/abparts_frontend_dist
- ✓ Keep /var/www/abparts_images (backed up, but not removed)

### 4. Verify Docker containers are running
```bash
cd ~/abparts
docker-compose ps
```

Expected output:
```
NAME                IMAGE                    STATUS
abparts_api         abparts_api              Up
abparts_db          postgres:15              Up
abparts_frontend    abparts_frontend         Up
abparts_pgadmin     dpage/pgadmin4:latest    Up
abparts_redis       redis:7-alpine           Up
```

If not running:
```bash
docker-compose up -d
```

### 5. Test the HTTPS site
```bash
# Test HTTPS
curl -I https://abparts.oraseas.com

# Test HTTP redirect
curl -I http://abparts.oraseas.com

# Test API
curl https://abparts.oraseas.com/api/health
```

### 6. Check SSL certificate
```bash
sudo certbot certificates
```

Expected output should show:
```
Certificate Name: abparts.oraseas.com
  Domains: abparts.oraseas.com
  Expiry Date: [future date]
  Certificate Path: /etc/letsencrypt/live/abparts.oraseas.com/fullchain.pem
  Private Key Path: /etc/letsencrypt/live/abparts.oraseas.com/privkey.pem
```

## Troubleshooting

### If nginx fails to reload

```bash
# Check nginx error log
sudo tail -50 /var/log/nginx/error.log

# Test configuration
sudo nginx -t

# Check what's using ports
sudo lsof -i :80
sudo lsof -i :443
```

### If Docker containers aren't accessible

```bash
# Check if containers are running
docker-compose ps

# Check container logs
docker-compose logs frontend
docker-compose logs api

# Restart containers
docker-compose restart
```

### If SSL certificate is expired

```bash
# Renew certificate
sudo certbot renew

# Reload nginx
sudo systemctl reload nginx
```

### If you need to restore old configuration

```bash
# Find backup directory
ls -la /root/nginx_backup_*

# Restore from backup
sudo cp /root/nginx_backup_*/abparts.oraseas.com.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/abparts.oraseas.com.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## What Changed

### Old Setup (Non-Docker)
- Frontend served from `/var/www/abparts_frontend_dist`
- Backend running as separate process
- Complex nginx configuration with multiple server blocks

### New Setup (Docker)
- Frontend in Docker container (port 3000)
- Backend in Docker container (port 8000)
- Simple nginx reverse proxy configuration
- All services managed by docker-compose

## Nginx Configuration Details

The new configuration:
- **Port 80**: Redirects all HTTP to HTTPS
- **Port 443**: HTTPS with SSL certificate
- **Location /api/**: Proxies to backend (localhost:8000)
- **Location /static/**: Proxies to backend static files
- **Location /**: Proxies to frontend (localhost:3000)

## Security Features

✓ HTTPS enforced (HTTP redirects to HTTPS)
✓ TLS 1.2 and 1.3 only
✓ Security headers (HSTS, X-Frame-Options, etc.)
✓ 10MB file upload limit
✓ Proper proxy headers for real IP tracking

## Monitoring

### Check nginx logs
```bash
# Access log
sudo tail -f /var/log/nginx/abparts_access.log

# Error log
sudo tail -f /var/log/nginx/abparts_error.log
```

### Check Docker logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f api
```

### Check SSL certificate expiry
```bash
sudo certbot certificates
```

## Maintenance

### Renew SSL certificate (automatic)
Certbot automatically renews certificates. To test:
```bash
sudo certbot renew --dry-run
```

### Manual renewal if needed
```bash
sudo certbot renew
sudo systemctl reload nginx
```

### Update Docker containers
```bash
cd ~/abparts
docker-compose pull
docker-compose up -d
```

## Files Modified/Created

### Created
- `/etc/nginx/sites-available/abparts.oraseas.com` (new config)
- `/etc/nginx/sites-enabled/abparts.oraseas.com` (symlink)

### Removed
- `/etc/nginx/sites-available/abparts.oraseas.com.conf` (old)
- `/etc/nginx/sites-available/aquaculture-map.conf`
- `/etc/nginx/sites-enabled/abparts.oraseas.com.conf` (old symlink)
- `/etc/nginx/sites-enabled/aquaculture-map.conf` (symlink)

### Backed Up
- All old configs → `/root/nginx_backup_[timestamp]/`
- Old frontend files → `/root/abparts_files_backup_[timestamp]/`

## Success Checklist

- [ ] Old nginx configs removed
- [ ] New nginx config created and enabled
- [ ] Nginx configuration test passes
- [ ] Nginx reloaded successfully
- [ ] Docker containers running
- [ ] HTTPS site accessible
- [ ] HTTP redirects to HTTPS
- [ ] API endpoints working
- [ ] SSL certificate valid
- [ ] No errors in nginx logs
