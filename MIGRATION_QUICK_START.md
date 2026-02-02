# ABParts Migration Quick Start Guide

## Overview
This guide will help you migrate ABParts to your new Hetzner server (46.62.131.135) while avoiding port conflicts with your existing aquaculture-app.

## Prerequisites
- New server: 46.62.131.135
- SSH access as user: `diogo` (with sudo)
- Existing aquaculture-app running on the server

## Step-by-Step Migration

### Step 1: Check Port Availability on New Server

First, we need to see what ports are already in use by the aquaculture-app.

```bash
# On your LOCAL machine, transfer the port check script
scp check_server_ports.sh diogo@46.62.131.135:~/

# SSH to the new server
ssh diogo@46.62.131.135

# Make the script executable
chmod +x ~/check_server_ports.sh

# Run the port check
~/check_server_ports.sh

# Save the output to a file for reference
~/check_server_ports.sh > ~/port_check_results.txt
```

**Review the output carefully!** Look for:
- Which ports are IN USE (marked with ❌)
- Which ports are AVAILABLE (marked with ✅)
- What Docker containers are running
- What Nginx configurations exist

### Step 2: Share Results

```bash
# On the new server, view the results
cat ~/port_check_results.txt

# Copy the output and share it with me so I can help configure the exact ports
```

**Common Scenarios:**

**Scenario A: Aquaculture-app uses ports 3000 and 8000**
- ABParts will use: 3001 (frontend), 8002 (API), 8003 (AI)

**Scenario B: Aquaculture-app uses ports 80 and 443 only**
- ABParts can use default ports: 3000 (frontend), 8000 (API), 8001 (AI)
- Nginx will route both apps

**Scenario C: Custom configuration needed**
- We'll adjust based on your specific port availability

### Step 3: Prepare Configuration Files

Based on the port check results, you'll need to update these files:

1. **docker-compose.prod.yml** - Set the correct host ports
2. **nginx-abparts-custom-ports.conf** - Configure Nginx to proxy to those ports
3. **.env.production** - Set environment variables

I've created templates for you:
- `docker-compose.prod.custom-ports.yml` - Template with port configuration instructions
- `nginx-abparts-custom-ports.conf` - Nginx template with port placeholders
- `.env.production.template` - Environment variables template

### Step 4: Transfer Files to New Server

```bash
# On your LOCAL machine (in the abparts directory)

# Transfer the entire project (excluding unnecessary files)
rsync -avz --progress \
  --exclude 'node_modules' \
  --exclude '__pycache__' \
  --exclude '.git' \
  --exclude '*.pyc' \
  --exclude '.env' \
  --exclude 'backups' \
  ~/abparts/ diogo@46.62.131.135:~/abparts/

# Transfer your backup files
scp ~/abparts_migration_backups/*.sql diogo@46.62.131.135:~/abparts/
scp ~/abparts_migration_backups/*.tar.gz diogo@46.62.131.135:~/abparts/
```

### Step 5: Configure ABParts on New Server

```bash
# SSH to new server
ssh diogo@46.62.131.135

# Navigate to abparts directory
cd ~/abparts

# Copy and customize docker-compose file
cp docker-compose.prod.custom-ports.yml docker-compose.prod.yml

# Edit to set the correct ports (based on Step 1 results)
nano docker-compose.prod.yml
# Update the port mappings in the 'ports' sections

# Create production environment file
cp .env.production.template .env.production

# Edit environment variables
nano .env.production
# Set database passwords, secret keys, API keys, etc.
```

**Generate secure secrets:**
```bash
# Generate SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Generate database password
openssl rand -base64 32

# Copy these values into .env.production
```

### Step 6: Install Docker (if not already installed)

```bash
# Check if Docker is installed
docker --version

# If not installed:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker diogo

# Log out and back in for group changes to take effect
exit
ssh diogo@46.62.131.135

# Verify Docker works without sudo
docker --version
docker ps
```

### Step 7: Deploy ABParts

```bash
cd ~/abparts

# Build and start containers
docker compose -f docker-compose.prod.yml up -d --build

# Watch logs to ensure everything starts
docker compose -f docker-compose.prod.yml logs -f
# Press Ctrl+C when you see services are running

# Check container status
docker compose -f docker-compose.prod.yml ps
# All containers should show "Up" status
```

### Step 8: Restore Database

```bash
cd ~/abparts

# Wait for database to be ready
sleep 15

# List your backup files
ls -lh *.sql

# Restore database (replace with your actual filename)
docker compose -f docker-compose.prod.yml exec -T db \
  psql -U abparts_user abparts_prod < abparts_prod_YYYYMMDD_HHMMSS.sql

# Restore static files
tar -xzf backend_static_YYYYMMDD_HHMMSS.tar.gz

# Set permissions
chmod -R 755 backend/static/
```

### Step 9: Configure Nginx

```bash
# Copy the Nginx configuration template
sudo cp ~/abparts/nginx-abparts-custom-ports.conf /etc/nginx/sites-available/abparts

# Edit to set correct ports (based on your docker-compose.prod.yml)
sudo nano /etc/nginx/sites-available/abparts
# Update proxy_pass directives to match your container ports

# Enable the site
sudo ln -s /etc/nginx/sites-available/abparts /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
```

### Step 10: Test the Application

```bash
# Test API health
curl http://localhost:8000/api/health
# Should return: {"status":"healthy"}

# Test AI Assistant health (if using)
curl http://localhost:8001/health
# Should return health status

# Test through Nginx
curl http://46.62.131.135/api/health

# Test frontend
curl http://46.62.131.135/
# Should return HTML
```

**Test in Browser:**
1. Open: `http://46.62.131.135`
2. Login with your credentials
3. Verify all features work

### Step 11: Configure Both Apps in Nginx (Optional)

If you want both aquaculture-app and ABParts accessible from the same server, you have two options:

**Option A: Path-based routing**
- Aquaculture: `http://46.62.131.135/aquaculture/`
- ABParts: `http://46.62.131.135/abparts/`

**Option B: Subdomain routing (recommended)**
- Aquaculture: `http://aquaculture.yourdomain.com`
- ABParts: `http://abparts.yourdomain.com`

Let me know which approach you prefer, and I'll help configure it.

## Troubleshooting

### Containers won't start
```bash
# Check logs
docker compose -f docker-compose.prod.yml logs

# Check specific container
docker compose -f docker-compose.prod.yml logs api

# Rebuild
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
```

### Port conflicts
```bash
# Check what's using a port
sudo lsof -i :8000

# Kill process if needed
sudo kill -9 <PID>

# Or change ABParts to use different port in docker-compose.prod.yml
```

### Database connection issues
```bash
# Check database is running
docker compose -f docker-compose.prod.yml ps db

# Check database logs
docker compose -f docker-compose.prod.yml logs db

# Test connection
docker compose -f docker-compose.prod.yml exec db \
  psql -U abparts_user -d abparts_prod -c "SELECT version();"
```

### Nginx issues
```bash
# Check Nginx status
sudo systemctl status nginx

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## Quick Commands Reference

```bash
# Start ABParts
cd ~/abparts && docker compose -f docker-compose.prod.yml up -d

# Stop ABParts
cd ~/abparts && docker compose -f docker-compose.prod.yml down

# View logs
cd ~/abparts && docker compose -f docker-compose.prod.yml logs -f

# Restart specific service
cd ~/abparts && docker compose -f docker-compose.prod.yml restart api

# Check status
cd ~/abparts && docker compose -f docker-compose.prod.yml ps

# Check ports
~/check_server_ports.sh
```

## Next Steps After Migration

1. **Setup SSL Certificate** (if you have a domain)
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

2. **Configure Auto-start on Boot**
   - Follow Phase 8 in HETZNER_NEW_SERVER_MIGRATION.md

3. **Setup Automated Backups**
   - Follow Phase 9 in HETZNER_NEW_SERVER_MIGRATION.md

4. **Decommission Old Server**
   - Follow Phase 10 in HETZNER_NEW_SERVER_MIGRATION.md

## Files You'll Need

- ✅ `check_server_ports.sh` - Port conflict detection
- ✅ `docker-compose.prod.custom-ports.yml` - Docker configuration template
- ✅ `nginx-abparts-custom-ports.conf` - Nginx configuration template
- ✅ `.env.production.template` - Environment variables template
- ✅ `HETZNER_NEW_SERVER_MIGRATION.md` - Detailed migration guide
- ✅ `PORT_CONFLICT_RESOLUTION.md` - Port conflict strategies

## Support

If you encounter any issues:
1. Run `~/check_server_ports.sh` to verify port status
2. Check Docker logs: `docker compose logs`
3. Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
4. Share the output with me for assistance

---

**Ready to start?** Begin with Step 1 - run the port check script on your new server and share the results!
