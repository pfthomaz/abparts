# ABParts Migration to New Hetzner Server (46.62.131.135)

## Your Setup
- **New Server IP**: 46.62.131.135
- **SSH User**: diogo (with sudo privileges)
- **Goal**: Make this the production server and decommission the old one
- **Installation Path**: `/home/diogo/abparts`

## Phase 1: Prepare New Hetzner Server

### 1.1 Connect to New Server
```bash
ssh diogo@46.62.131.135
```

### 1.2 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3 Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (so you don't need sudo for docker commands)
sudo usermod -aG docker diogo

# Log out and back in for group changes to take effect
exit
ssh diogo@46.62.131.135

# Verify Docker works without sudo
docker --version
```

### 1.4 Install Docker Compose
```bash
# Install Docker Compose plugin
sudo apt install docker-compose-plugin -y

# Verify installation
docker compose version
```

### 1.5 Install Additional Tools
```bash
# Install Git
sudo apt install git -y

# Install Nginx (for reverse proxy)
sudo apt install nginx -y

# Install Certbot (for SSL certificates)
sudo apt install certbot python3-certbot-nginx -y

# Install useful utilities
sudo apt install htop curl wget unzip -y
```

### 1.6 Configure Firewall
```bash
# Enable UFW firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Check status
sudo ufw status
```

## Phase 2: Backup Data from Old Server

### 2.1 Connect to Old Server and Create Backups
```bash
# SSH to old server
ssh abparts@<OLD_SERVER_IP>

# Navigate to abparts directory
cd ~/abparts

# Create backup directory
mkdir -p ~/backups

# Backup production database
docker compose exec -T db pg_dump -U abparts_user abparts_prod > ~/backups/abparts_prod_$(date +%Y%m%d_%H%M%S).sql

# Backup static files (images, uploads)
tar -czf ~/backups/backend_static_$(date +%Y%m%d_%H%M%S).tar.gz backend/static/

# Backup AI assistant database (if you're using it)
docker compose exec -T ai_db pg_dump -U ai_user ai_assistant > ~/backups/ai_assistant_$(date +%Y%m%d_%H%M%S).sql 2>/dev/null || echo "No AI database found"

# Backup AI data files (if applicable)
tar -czf ~/backups/ai_data_$(date +%Y%m%d_%H%M%S).tar.gz ai_assistant/data/ 2>/dev/null || echo "No AI data found"

# List backups
ls -lh ~/backups/
```

### 2.2 Transfer Backups to Your Local Machine
```bash
# On your LOCAL machine (Mac)
# Create local backup directory
mkdir -p ~/abparts_migration_backups

# Download backups from old server
scp abparts@<OLD_SERVER_IP>:~/backups/*.sql ~/abparts_migration_backups/
scp abparts@<OLD_SERVER_IP>:~/backups/*.tar.gz ~/abparts_migration_backups/

# Verify files
ls -lh ~/abparts_migration_backups/
```

## Phase 3: Setup ABParts on New Server

### 3.1 Clone Repository to New Server
```bash
# On NEW server (as diogo)
cd ~
git clone https://github.com/YOUR_USERNAME/abparts.git

# Or if you don't have it in Git, transfer from local machine:
# On your LOCAL machine:
# rsync -avz --exclude 'node_modules' --exclude '__pycache__' --exclude '.git' \
#   ~/abparts/ diogo@46.62.131.135:~/abparts/
```

### 3.2 Transfer Backups to New Server
```bash
# On your LOCAL machine
scp ~/abparts_migration_backups/*.sql diogo@46.62.131.135:~/abparts/
scp ~/abparts_migration_backups/*.tar.gz diogo@46.62.131.135:~/abparts/
```

### 3.3 Create Production Environment File
```bash
# On NEW server
cd ~/abparts

# Copy template
cp .env.production.template .env.production

# Edit with production values
nano .env.production
```

**Critical Environment Variables to Set:**
```bash
# Database Configuration
POSTGRES_DB=abparts_prod
POSTGRES_USER=abparts_user
POSTGRES_PASSWORD=<GENERATE_STRONG_PASSWORD>
DATABASE_URL=postgresql://abparts_user:<PASSWORD>@db:5432/abparts_prod

# Security - IMPORTANT!
SECRET_KEY=<GENERATE_STRONG_SECRET>
ALLOWED_HOSTS=46.62.131.135,yourdomain.com

# Email Configuration (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=<YOUR_APP_PASSWORD>
SMTP_FROM=your-email@gmail.com

# AI Assistant (if using)
OPENAI_API_KEY=<YOUR_OPENAI_KEY>
AI_DATABASE_URL=postgresql://ai_user:<AI_PASSWORD>@ai_db:5432/ai_assistant

# Production Settings
ENVIRONMENT=production
DEBUG=false
```

### 3.4 Generate Strong Secrets
```bash
# Generate SECRET_KEY (copy this to .env.production)
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Generate database password (copy this to .env.production)
openssl rand -base64 32

# Generate AI database password (if using AI assistant)
openssl rand -base64 32
```

## Phase 4: Deploy Application

### 4.1 Build and Start Containers
```bash
cd ~/abparts

# Build and start in production mode
docker compose -f docker-compose.prod.yml up -d --build

# Check container status
docker compose -f docker-compose.prod.yml ps

# Watch logs to ensure everything starts correctly
docker compose -f docker-compose.prod.yml logs -f
# Press Ctrl+C to stop watching logs
```

### 4.2 Wait for Database to Initialize
```bash
# Wait 15 seconds for database to be ready
sleep 15

# Check database is running
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "SELECT version();"
```

### 4.3 Restore Database
```bash
# Find your backup file
ls -lh *.sql

# Restore main database (replace with your actual filename)
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user abparts_prod < abparts_prod_YYYYMMDD_HHMMSS.sql

# If you have AI assistant database
docker compose -f docker-compose.prod.yml exec -T ai_db psql -U ai_user ai_assistant < ai_assistant_YYYYMMDD_HHMMSS.sql 2>/dev/null || echo "Skipping AI database"
```

### 4.4 Restore Static Files
```bash
# Find your backup file
ls -lh *.tar.gz

# Extract static files (replace with your actual filename)
tar -xzf backend_static_YYYYMMDD_HHMMSS.tar.gz

# Extract AI data if applicable
tar -xzf ai_data_YYYYMMDD_HHMMSS.tar.gz 2>/dev/null || echo "No AI data to restore"

# Set proper permissions
chmod -R 755 backend/static/
```

### 4.5 Run Database Migrations
```bash
# Run any pending migrations
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# Verify migration status
docker compose -f docker-compose.prod.yml exec api alembic current
```

## Phase 5: Configure Nginx Reverse Proxy

### 5.1 Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/abparts
```

**Paste this configuration:**
```nginx
server {
    listen 80;
    server_name 46.62.131.135;

    client_max_body_size 100M;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # AI Assistant API (if using)
    location /api/ai/ {
        proxy_pass http://localhost:8001/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    # Static files
    location /static/ {
        alias /home/diogo/abparts/backend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 5.2 Enable Site and Restart Nginx
```bash
# Create symlink to enable site
sudo ln -s /etc/nginx/sites-available/abparts /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# If test passes, restart Nginx
sudo systemctl restart nginx

# Check Nginx status
sudo systemctl status nginx
```

## Phase 6: Test the Application

### 6.1 Check All Services
```bash
# Check Docker containers
docker compose -f docker-compose.prod.yml ps

# All containers should show "Up" status
```

### 6.2 Test API
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test through Nginx
curl http://46.62.131.135/api/health
```

### 6.3 Test Frontend
```bash
# Test frontend
curl http://46.62.131.135/

# Should return HTML
```

### 6.4 Access from Browser
Open your browser and go to:
```
http://46.62.131.135
```

Login with your credentials and verify:
- ✅ Can login
- ✅ Dashboard loads
- ✅ Data is present (users, organizations, parts, etc.)
- ✅ Images/uploads are visible
- ✅ All features work

## Phase 7: Setup SSL Certificate (Recommended)

### 7.1 If You Have a Domain Name
```bash
# Update Nginx config to include your domain
sudo nano /etc/nginx/sites-available/abparts
# Change: server_name 46.62.131.135;
# To: server_name 46.62.131.135 yourdomain.com www.yourdomain.com;

# Test and reload
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# 1. Enter email address
# 2. Agree to terms
# 3. Choose to redirect HTTP to HTTPS (recommended)
```

### 7.2 Test Auto-Renewal
```bash
# Test certificate renewal
sudo certbot renew --dry-run

# Certbot automatically sets up a cron job for renewal
```

## Phase 8: Setup Auto-Start on Boot

### 8.1 Create Systemd Service
```bash
sudo nano /etc/systemd/system/abparts.service
```

**Paste this:**
```ini
[Unit]
Description=ABParts Application
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
User=diogo
Group=diogo
WorkingDirectory=/home/diogo/abparts
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
```

### 8.2 Enable and Start Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable abparts.service

# Start service now
sudo systemctl start abparts.service

# Check status
sudo systemctl status abparts.service
```

## Phase 9: Setup Automated Backups

### 9.1 Create Backup Script
```bash
nano ~/abparts/backup.sh
```

**Paste this:**
```bash
#!/bin/bash
BACKUP_DIR="/home/diogo/abparts/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker compose -f /home/diogo/abparts/docker-compose.prod.yml exec -T db \
  pg_dump -U abparts_user abparts_prod > $BACKUP_DIR/db_$DATE.sql

# Backup static files
tar -czf $BACKUP_DIR/static_$DATE.tar.gz /home/diogo/abparts/backend/static/

# Backup AI database (if applicable)
docker compose -f /home/diogo/abparts/docker-compose.prod.yml exec -T ai_db \
  pg_dump -U ai_user ai_assistant > $BACKUP_DIR/ai_$DATE.sql 2>/dev/null || true

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

### 9.2 Make Executable and Schedule
```bash
# Make executable
chmod +x ~/abparts/backup.sh

# Test it
~/abparts/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e

# Add this line:
0 2 * * * /home/diogo/abparts/backup.sh >> /home/diogo/abparts/backup.log 2>&1
```

## Phase 10: Decommission Old Server

### 10.1 Verify New Server is Working
Before decommissioning, verify:
- [ ] Application is accessible at http://46.62.131.135
- [ ] All data is present and correct
- [ ] All features work properly
- [ ] Backups are running automatically
- [ ] SSL is configured (if using domain)

### 10.2 Update DNS (if using domain)
```bash
# Point your domain's A record to new server:
# yourdomain.com -> 46.62.131.135
```

### 10.3 Stop Old Server
```bash
# SSH to old server
ssh abparts@<OLD_SERVER_IP>

# Stop containers
cd ~/abparts
docker compose down

# Verify containers are stopped
docker ps
```

### 10.4 Final Backup from Old Server
```bash
# On old server - create final backup
cd ~/abparts
docker compose -f docker-compose.prod.yml up -d db
sleep 5
docker compose exec -T db pg_dump -U abparts_user abparts_prod > ~/final_backup_$(date +%Y%m%d).sql
docker compose down

# Download to your local machine
# On your LOCAL machine:
scp abparts@<OLD_SERVER_IP>:~/final_backup_*.sql ~/abparts_migration_backups/
```

### 10.5 Remove ABParts User from Old Server (Optional)
```bash
# SSH to old server as root or sudo user
ssh <your-admin-user>@<OLD_SERVER_IP>

# Stop and remove all Docker containers
sudo docker stop $(sudo docker ps -aq)
sudo docker rm $(sudo docker ps -aq)

# Remove abparts user and home directory
sudo userdel -r abparts

# Verify user is removed
cat /etc/passwd | grep abparts
# Should return nothing
```

## Troubleshooting

### Containers Won't Start
```bash
# Check logs
docker compose -f docker-compose.prod.yml logs

# Check specific container
docker compose -f docker-compose.prod.yml logs api
docker compose -f docker-compose.prod.yml logs db

# Rebuild
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
```

### Database Connection Issues
```bash
# Check database is running
docker compose -f docker-compose.prod.yml ps db

# Check database logs
docker compose -f docker-compose.prod.yml logs db

# Verify credentials in .env.production
cat .env.production | grep POSTGRES
```

### Permission Issues
```bash
# Fix ownership
sudo chown -R diogo:diogo ~/abparts

# Fix static files
chmod -R 755 ~/abparts/backend/static
```

### Nginx Issues
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

## Quick Reference Commands

```bash
# Start application
cd ~/abparts
docker compose -f docker-compose.prod.yml up -d

# Stop application
docker compose -f docker-compose.prod.yml down

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Restart specific service
docker compose -f docker-compose.prod.yml restart api

# Check status
docker compose -f docker-compose.prod.yml ps

# Run backup
~/abparts/backup.sh

# Check disk space
df -h

# Check memory usage
free -h

# Monitor containers
docker stats
```

## Success Checklist

- [ ] New server accessible via SSH
- [ ] Docker and Docker Compose installed
- [ ] Application code deployed
- [ ] Database restored successfully
- [ ] Static files restored
- [ ] Application accessible via browser
- [ ] All features tested and working
- [ ] Nginx configured and running
- [ ] SSL certificate installed (if using domain)
- [ ] Auto-start on boot configured
- [ ] Automated backups scheduled
- [ ] Old server data backed up
- [ ] Old server decommissioned
- [ ] DNS updated (if using domain)

## Support

If you encounter issues during migration:
1. Check container logs: `docker compose -f docker-compose.prod.yml logs`
2. Verify environment variables in `.env.production`
3. Check firewall rules: `sudo ufw status`
4. Verify Nginx configuration: `sudo nginx -t`
5. Check disk space: `df -h`

Good luck with your migration! 🚀
