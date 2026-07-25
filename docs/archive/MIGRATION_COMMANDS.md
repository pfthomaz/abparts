# ABParts Migration - Command Reference

Quick reference for all commands you'll need during migration.

## Phase 1: Port Check on New Server

```bash
# Transfer port check script to new server
scp check_server_ports.sh diogo@46.62.131.135:~/

# SSH to new server
ssh diogo@46.62.131.135

# Make script executable and run it
chmod +x ~/check_server_ports.sh
~/check_server_ports.sh

# Save results to file
~/check_server_ports.sh > ~/port_check_results.txt

# View results
cat ~/port_check_results.txt

# Download results to local machine (optional)
# On your LOCAL machine:
scp diogo@46.62.131.135:~/port_check_results.txt ~/
```

## Phase 2: Backup Old Server

```bash
# SSH to OLD server
ssh abparts@<OLD_SERVER_IP>

# Navigate to abparts directory
cd ~/abparts

# Create backup directory
mkdir -p ~/backups

# Backup database
docker compose exec -T db pg_dump -U abparts_user abparts_prod > ~/backups/abparts_prod_$(date +%Y%m%d_%H%M%S).sql

# Backup static files
tar -czf ~/backups/backend_static_$(date +%Y%m%d_%H%M%S).tar.gz backend/static/

# Backup AI database (if applicable)
docker compose exec -T ai_db pg_dump -U ai_user ai_assistant > ~/backups/ai_assistant_$(date +%Y%m%d_%H%M%S).sql 2>/dev/null || echo "No AI database"

# List backups
ls -lh ~/backups/

# Exit old server
exit
```

## Phase 3: Transfer Backups to Local Machine

```bash
# On your LOCAL machine
mkdir -p ~/abparts_migration_backups

# Download backups from old server
scp abparts@<OLD_SERVER_IP>:~/backups/*.sql ~/abparts_migration_backups/
scp abparts@<OLD_SERVER_IP>:~/backups/*.tar.gz ~/abparts_migration_backups/

# Verify files
ls -lh ~/abparts_migration_backups/
```

## Phase 4: Transfer Everything to New Server

```bash
# On your LOCAL machine (in abparts directory)

# Transfer entire project
rsync -avz --progress \
  --exclude 'node_modules' \
  --exclude '__pycache__' \
  --exclude '.git' \
  --exclude '*.pyc' \
  --exclude '.env' \
  --exclude 'backups' \
  ~/abparts/ diogo@46.62.131.135:~/abparts/

# Transfer backups
scp ~/abparts_migration_backups/*.sql diogo@46.62.131.135:~/abparts/
scp ~/abparts_migration_backups/*.tar.gz diogo@46.62.131.135:~/abparts/
```

## Phase 5: Setup New Server

```bash
# SSH to new server
ssh diogo@46.62.131.135

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker (if not installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker diogo

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Install Nginx
sudo apt install nginx -y

# Install other tools
sudo apt install git htop curl wget unzip -y

# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Log out and back in for docker group to take effect
exit
ssh diogo@46.62.131.135

# Verify Docker works
docker --version
docker ps
```

## Phase 6: Configure ABParts

```bash
# On new server
cd ~/abparts

# Copy docker-compose template
cp docker-compose.prod.custom-ports.yml docker-compose.prod.yml

# Edit docker-compose to set correct ports
nano docker-compose.prod.yml
# Update port mappings based on port check results

# Create production environment file
cp .env.production.template .env.production

# Generate secrets
python3 -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(50))"
python3 -c "import secrets; print('JWT_SECRET_KEY:', secrets.token_urlsafe(50))"
openssl rand -base64 32  # Database password

# Edit environment file
nano .env.production
# Fill in all required values
```

## Phase 7: Deploy ABParts

```bash
# On new server
cd ~/abparts

# Build and start containers
docker compose -f docker-compose.prod.yml up -d --build

# Watch logs
docker compose -f docker-compose.prod.yml logs -f
# Press Ctrl+C to stop watching

# Check container status
docker compose -f docker-compose.prod.yml ps
# All should show "Up"

# Wait for database to be ready
sleep 15

# Test database connection
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "SELECT version();"
```

## Phase 8: Restore Data

```bash
# On new server
cd ~/abparts

# List backup files
ls -lh *.sql *.tar.gz

# Restore database (replace filename with yours)
docker compose -f docker-compose.prod.yml exec -T db \
  psql -U abparts_user abparts_prod < abparts_prod_YYYYMMDD_HHMMSS.sql

# Restore AI database (if applicable)
docker compose -f docker-compose.prod.yml exec -T ai_db \
  psql -U ai_user ai_assistant < ai_assistant_YYYYMMDD_HHMMSS.sql 2>/dev/null || echo "Skipping AI database"

# Extract static files (replace filename with yours)
tar -xzf backend_static_YYYYMMDD_HHMMSS.tar.gz

# Set permissions
chmod -R 755 backend/static/

# Run database migrations
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# Verify migration status
docker compose -f docker-compose.prod.yml exec api alembic current
```

## Phase 9: Configure Nginx

```bash
# On new server

# Copy Nginx configuration
sudo cp ~/abparts/nginx-abparts-custom-ports.conf /etc/nginx/sites-available/abparts

# Edit to set correct ports
sudo nano /etc/nginx/sites-available/abparts
# Update proxy_pass directives to match docker-compose ports

# Enable site
sudo ln -s /etc/nginx/sites-available/abparts /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx

# Check Nginx status
sudo systemctl status nginx
```

## Phase 10: Test Application

```bash
# On new server

# Test API directly
curl http://localhost:8000/api/health

# Test AI Assistant directly (if using)
curl http://localhost:8001/health

# Test through Nginx
curl http://46.62.131.135/api/health
curl http://46.62.131.135/

# Check logs
docker compose -f docker-compose.prod.yml logs api
docker compose -f docker-compose.prod.yml logs web

# Check Nginx logs
sudo tail -f /var/log/nginx/abparts_error.log
```

## Phase 11: Setup SSL (Optional)

```bash
# On new server (if you have a domain)

# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Useful Management Commands

### Docker Commands
```bash
# Start ABParts
cd ~/abparts && docker compose -f docker-compose.prod.yml up -d

# Stop ABParts
cd ~/abparts && docker compose -f docker-compose.prod.yml down

# Restart ABParts
cd ~/abparts && docker compose -f docker-compose.prod.yml restart

# Restart specific service
cd ~/abparts && docker compose -f docker-compose.prod.yml restart api

# View logs (all services)
cd ~/abparts && docker compose -f docker-compose.prod.yml logs -f

# View logs (specific service)
cd ~/abparts && docker compose -f docker-compose.prod.yml logs -f api

# Check status
cd ~/abparts && docker compose -f docker-compose.prod.yml ps

# Rebuild containers
cd ~/abparts && docker compose -f docker-compose.prod.yml up -d --build

# Remove everything and start fresh
cd ~/abparts && docker compose -f docker-compose.prod.yml down -v
cd ~/abparts && docker compose -f docker-compose.prod.yml up -d --build
```

### Nginx Commands
```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx

# View error logs
sudo tail -f /var/log/nginx/error.log

# View access logs
sudo tail -f /var/log/nginx/access.log

# View ABParts specific logs
sudo tail -f /var/log/nginx/abparts_error.log
sudo tail -f /var/log/nginx/abparts_access.log
```

### Database Commands
```bash
# Connect to database
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user abparts_prod

# Backup database
docker compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U abparts_user abparts_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
docker compose -f docker-compose.prod.yml exec -T db \
  psql -U abparts_user abparts_prod < backup_file.sql

# Check database size
docker compose -f docker-compose.prod.yml exec db \
  psql -U abparts_user abparts_prod -c "SELECT pg_size_pretty(pg_database_size('abparts_prod'));"
```

### System Monitoring
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check CPU and memory per container
docker stats

# Check running processes
htop

# Check port usage
sudo netstat -tulpn | grep LISTEN
sudo ss -tulpn | grep LISTEN

# Check specific port
sudo lsof -i :8000
```

### Troubleshooting Commands
```bash
# Check if port is in use
sudo lsof -i :PORT_NUMBER

# Kill process on port
sudo kill -9 $(sudo lsof -t -i:PORT_NUMBER)

# Check Docker network
docker network ls
docker network inspect abparts_abparts_network

# Check Docker volumes
docker volume ls
docker volume inspect abparts_db_data_prod

# Remove unused Docker resources
docker system prune -a

# Check container resource usage
docker stats --no-stream

# Inspect container
docker inspect abparts_api_prod

# Execute command in container
docker compose -f docker-compose.prod.yml exec api bash
docker compose -f docker-compose.prod.yml exec db bash
```

## Emergency Rollback

```bash
# If migration fails and you need to rollback:

# On new server - stop ABParts
cd ~/abparts
docker compose -f docker-compose.prod.yml down

# On old server - ensure ABParts is still running
ssh abparts@<OLD_SERVER_IP>
cd ~/abparts
docker compose ps
# If not running: docker compose up -d

# Update DNS back to old server (if changed)
# Point A record back to old server IP
```

## Quick Health Check

```bash
# Run this to check if everything is working
cd ~/abparts

echo "=== Container Status ==="
docker compose -f docker-compose.prod.yml ps

echo -e "\n=== API Health ==="
curl -s http://localhost:8000/api/health | jq .

echo -e "\n=== AI Health ==="
curl -s http://localhost:8001/health | jq .

echo -e "\n=== Nginx Status ==="
sudo systemctl status nginx --no-pager

echo -e "\n=== Disk Space ==="
df -h | grep -E "Filesystem|/$"

echo -e "\n=== Memory ==="
free -h
```

## File Locations Reference

```
New Server File Locations:
├── /home/diogo/abparts/                    # Main application directory
├── /home/diogo/abparts/backend/static/     # Static files (images)
├── /var/www/abparts_images/                # Alternative static location
├── /etc/nginx/sites-available/abparts      # Nginx config
├── /etc/nginx/sites-enabled/abparts        # Nginx enabled site
├── /var/log/nginx/abparts_access.log       # Nginx access logs
├── /var/log/nginx/abparts_error.log        # Nginx error logs
└── /home/diogo/abparts/.env.production     # Environment variables
```

## Support

If you encounter issues:
1. Check container logs: `docker compose logs`
2. Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Run port check: `~/check_server_ports.sh`
4. Check disk space: `df -h`
5. Check memory: `free -h`

---

**Pro Tip:** Save this file on the new server for quick reference!

```bash
# On new server
cd ~/abparts
cat MIGRATION_COMMANDS.md
```
