# ABParts Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying ABParts to a production server using the provided configuration templates.

## Prerequisites

- Ubuntu/Debian server with sudo access
- Domain name pointing to your server
- SSL certificate (Let's Encrypt recommended)
- Docker and Docker Compose installed
- Nginx installed
- PostgreSQL and Redis (via Docker)

## Configuration Templates

The repository includes production-ready templates:

- **`.env.production.template`** - Environment variables template
- **`nginx-production.template`** - Nginx configuration template
- **`docker-compose.prod.yml`** - Production Docker Compose configuration

## Step-by-Step Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y nginx certbot python3-certbot-nginx git

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone Repository

```bash
# Create application user (recommended)
sudo useradd -m -s /bin/bash abparts
sudo usermod -aG docker abparts
sudo su - abparts

# Clone repository
git clone https://github.com/your-org/abparts.git
cd abparts
```

### 3. Environment Configuration

```bash
# Copy and customize environment file
cp .env.production.template .env

# Edit the .env file with your actual values
nano .env
```

**Required customizations in `.env`:**
- `POSTGRES_PASSWORD` - Strong database password
- `PGADMIN_DEFAULT_EMAIL` - Your admin email
- `PGADMIN_DEFAULT_PASSWORD` - PgAdmin password
- `SMTP_*` - Email configuration for notifications
- `BASE_URL` - Your domain (https://yourdomain.com)
- `CORS_ALLOWED_ORIGINS` - Your domain
- `SECRET_KEY` - Generate with `openssl rand -hex 32`
- `JWT_SECRET_KEY` - Generate with `openssl rand -hex 32`
- `OPENAI_API_KEY` - Your OpenAI API key for AI Assistant

### 4. SSL Certificate Setup

```bash
# Exit to main user for SSL setup
exit

# Obtain SSL certificate
sudo certbot certonly --nginx -d yourdomain.com

# Verify certificate
sudo certbot certificates
```

### 5. Nginx Configuration

```bash
# Copy and customize nginx template
sudo cp /home/abparts/abparts/nginx-production.template /etc/nginx/sites-available/abparts

# Edit nginx configuration
sudo nano /etc/nginx/sites-available/abparts
```

**Required customizations in nginx config:**
- Replace `YOUR_DOMAIN_HERE` with your actual domain
- Replace `YOUR_USER` with `abparts` (or your chosen user)
- Verify SSL certificate paths match your domain

```bash
# Enable site and test configuration
sudo ln -s /etc/nginx/sites-available/abparts /etc/nginx/sites-enabled/
sudo nginx -t

# Remove default site if present
sudo rm -f /etc/nginx/sites-enabled/default

# Restart nginx
sudo systemctl restart nginx
```

### 6. Database and Services Setup

```bash
# Switch back to application user
sudo su - abparts
cd ~/abparts

# Start database and Redis services
docker compose -f docker-compose.prod.yml up -d db redis

# Wait for database to be ready
sleep 10

# Run database migrations
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# Create initial admin user (optional)
docker compose -f docker-compose.prod.yml exec api python -c "
from app.database import get_db
from app.crud.users import create_user
from app.schemas import UserCreate
from app.auth import get_password_hash
import uuid

# Create admin user
user_data = UserCreate(
    email='admin@yourdomain.com',
    password='your-secure-password',
    full_name='System Administrator',
    role='super_admin'
)
# Add user creation logic here
"
```

### 7. Build and Deploy Application

```bash
# Build frontend
cd frontend
npm install
npm run build
cd ..

# Start all services
docker compose -f docker-compose.prod.yml up -d

# Verify services are running
docker compose -f docker-compose.prod.yml ps
```

### 8. Verify Deployment

```bash
# Check service logs
docker compose -f docker-compose.prod.yml logs api
docker compose -f docker-compose.prod.yml logs ai_assistant

# Test API endpoints
curl https://yourdomain.com/api/health
curl https://yourdomain.com/ai/health

# Check database connection
docker compose -f docker-compose.prod.yml exec api alembic current
```

## Post-Deployment Configuration

### 1. Firewall Setup

```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. SSL Auto-Renewal

```bash
# Test SSL renewal
sudo certbot renew --dry-run

# SSL will auto-renew via systemd timer
sudo systemctl status certbot.timer
```

### 3. Monitoring Setup

```bash
# Set up log rotation
sudo nano /etc/logrotate.d/abparts

# Add monitoring for services
sudo systemctl enable docker
```

### 4. Backup Configuration

```bash
# Create backup script
nano ~/backup_abparts.sh

#!/bin/bash
# Backup database
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U abparts_user abparts_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup uploaded files
tar -czf static_backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/static/

chmod +x ~/backup_abparts.sh

# Add to crontab for daily backups
crontab -e
# Add: 0 2 * * * /home/abparts/backup_abparts.sh
```

## Maintenance Commands

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart services
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

# Run any new migrations
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# Rebuild frontend if needed
cd frontend && npm run build && cd ..
```

### View Logs

```bash
# Application logs
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f ai_assistant

# Nginx logs
sudo tail -f /var/log/nginx/abparts_access.log
sudo tail -f /var/log/nginx/abparts_error.log
```

### Database Operations

```bash
# Connect to database
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod

# Create database backup
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U abparts_user abparts_prod > backup.sql

# Restore from backup
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod < backup.sql
```

## Troubleshooting

### Common Issues

1. **Services won't start**
   ```bash
   # Check logs
   docker compose -f docker-compose.prod.yml logs
   
   # Check disk space
   df -h
   
   # Check memory
   free -h
   ```

2. **Database connection errors**
   ```bash
   # Verify database is running
   docker compose -f docker-compose.prod.yml ps db
   
   # Check database logs
   docker compose -f docker-compose.prod.yml logs db
   ```

3. **SSL certificate issues**
   ```bash
   # Check certificate status
   sudo certbot certificates
   
   # Renew certificate
   sudo certbot renew
   ```

4. **Nginx configuration errors**
   ```bash
   # Test nginx config
   sudo nginx -t
   
   # Check nginx status
   sudo systemctl status nginx
   ```

## Security Considerations

### 1. Environment Variables
- Never commit `.env` files to version control
- Use strong, unique passwords for all services
- Rotate secrets regularly

### 2. Database Security
- Use strong database passwords
- Limit database access to application services only
- Regular security updates

### 3. SSL/TLS
- Use strong SSL configurations
- Enable HSTS headers
- Regular certificate renewal

### 4. Application Security
- Keep Docker images updated
- Regular security patches
- Monitor application logs for suspicious activity

## Performance Optimization

### 1. Database
- Regular VACUUM and ANALYZE operations
- Monitor query performance
- Optimize indexes as needed

### 2. Frontend
- Enable gzip compression in nginx
- Optimize static asset caching
- Use CDN for static assets if needed

### 3. Backend
- Monitor API response times
- Optimize database queries
- Scale services horizontally if needed

## Support and Maintenance

### Regular Tasks
- [ ] Weekly: Check service logs for errors
- [ ] Weekly: Verify backups are working
- [ ] Monthly: Update system packages
- [ ] Monthly: Review SSL certificate expiration
- [ ] Quarterly: Security audit and updates

### Emergency Contacts
- System Administrator: [Your contact info]
- Database Administrator: [Your contact info]
- Application Developer: [Your contact info]

---

## Quick Reference

### Service Management
```bash
# Start all services
docker compose -f docker-compose.prod.yml up -d

# Stop all services
docker compose -f docker-compose.prod.yml down

# Restart specific service
docker compose -f docker-compose.prod.yml restart api

# View service status
docker compose -f docker-compose.prod.yml ps
```

### Database Management
```bash
# Run migrations
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# Check migration status
docker compose -f docker-compose.prod.yml exec api alembic current

# Create backup
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U abparts_user abparts_prod > backup.sql
```

### Log Management
```bash
# API logs
docker compose -f docker-compose.prod.yml logs -f api

# Database logs
docker compose -f docker-compose.prod.yml logs -f db

# Nginx logs
sudo tail -f /var/log/nginx/abparts_error.log
```

This deployment guide ensures a secure, scalable, and maintainable production deployment of ABParts.