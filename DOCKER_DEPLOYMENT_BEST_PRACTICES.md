# Docker Deployment Best Practices for ABParts

## Key Lessons from Image Storage Deployment

### ✅ What Worked Well

1. **Auto-detect Docker Compose version**
   ```bash
   # Support both v1 and v2
   if command -v docker-compose &> /dev/null; then
       DOCKER_COMPOSE="docker-compose"
   elif docker compose version &> /dev/null; then
       DOCKER_COMPOSE="docker compose"
   fi
   ```

2. **Pre-deployment checks**
   - Verify database schema before deploying
   - Check configuration files exist
   - Validate prerequisites

3. **Automated deployment script**
   - Single command deployment
   - Clear progress indicators
   - Health checks after deployment

4. **Comprehensive documentation**
   - Deployment guide
   - Troubleshooting section
   - Rollback procedures

## Standard Deployment Process

### 1. Development Phase

```bash
# Local development
docker-compose up -d
docker-compose logs -f api web

# Test changes locally
# Run tests if available
```

### 2. Commit and Push

```bash
# Clear commit message
git add .
git commit -m "feat: descriptive message of what changed"
git push origin main
```

### 3. Production Deployment

```bash
# SSH to production
ssh root@abparts.oraseas.com
cd /root/abparts

# Pull latest code
git pull origin main

# Run deployment script
chmod +x deploy_script.sh
./deploy_script.sh
```

## Deployment Script Template

Every deployment should have a script that:

```bash
#!/bin/bash
set -e  # Exit on error

# 1. Detect Docker Compose version
if command -v docker-compose &> /dev/null; then
    DC="docker-compose"
elif docker compose version &> /dev/null; then
    DC="docker compose"
else
    echo "❌ Docker Compose not found"
    exit 1
fi

# 2. Pre-deployment checks
echo "📋 Running pre-deployment checks..."
# Check database, configs, etc.

# 3. Confirm deployment
read -p "Continue? (y/n) " -n 1 -r
echo
[[ ! $REPLY =~ ^[Yy]$ ]] && exit 0

# 4. Build services
echo "🔨 Building..."
$DC -f docker-compose.prod.yml build service1 service2

# 5. Deploy
echo "🚀 Deploying..."
$DC -f docker-compose.prod.yml up -d service1 service2

# 6. Wait and verify
echo "⏳ Waiting for services..."
sleep 10

# 7. Health checks
echo "🔍 Checking health..."
$DC -f docker-compose.prod.yml ps

# 8. Success message
echo "✅ Deployment complete!"
```

## Docker Compose Best Practices

### Use Specific Compose File

```bash
# ❌ Don't rely on default
docker compose up -d

# ✅ Always specify the file
docker compose -f docker-compose.prod.yml up -d
```

### Build Before Deploy

```bash
# ✅ Build first, then deploy
docker compose -f docker-compose.prod.yml build api web
docker compose -f docker-compose.prod.yml up -d api web

# This ensures new code is built before containers restart
```

### Selective Service Restart

```bash
# ❌ Don't restart everything
docker compose -f docker-compose.prod.yml restart

# ✅ Restart only what changed
docker compose -f docker-compose.prod.yml restart api web
```

### Check Logs After Deployment

```bash
# View recent logs
docker compose -f docker-compose.prod.yml logs --tail=50 api web

# Follow logs in real-time
docker compose -f docker-compose.prod.yml logs -f api

# Check for errors
docker compose -f docker-compose.prod.yml logs api | grep -i error
```

## Database Changes

### When Schema Changes Required

1. **Create migration locally**
   ```bash
   docker-compose exec api alembic revision --autogenerate -m "description"
   ```

2. **Test migration locally**
   ```bash
   docker-compose exec api alembic upgrade head
   docker-compose exec api alembic downgrade -1  # Test rollback
   docker-compose exec api alembic upgrade head
   ```

3. **Commit migration**
   ```bash
   git add backend/alembic/versions/
   git commit -m "feat: add migration for X"
   git push
   ```

4. **Deploy to production**
   ```bash
   # Pull code
   git pull origin main
   
   # Run migration
   docker compose -f docker-compose.prod.yml exec api alembic upgrade head
   
   # Deploy code
   ./deploy_script.sh
   ```

### When No Schema Changes

Like the image storage deployment:
- Use existing columns
- No migration needed
- Just deploy code changes

## Configuration Changes

### Nginx Configuration

```bash
# After changing nginx.conf
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d web

# Verify nginx is running
docker compose -f docker-compose.prod.yml exec web nginx -t
```

### Environment Variables

```bash
# After changing .env
docker compose -f docker-compose.prod.yml up -d api

# Verify variables loaded
docker compose -f docker-compose.prod.yml exec api env | grep VARIABLE_NAME
```

## Rollback Procedures

### Quick Rollback

```bash
# Stop services
docker compose -f docker-compose.prod.yml down

# Checkout previous commit
git log --oneline -5
git checkout <previous-commit>

# Rebuild and restart
docker compose -f docker-compose.prod.yml build api web
docker compose -f docker-compose.prod.yml up -d
```

### Database Rollback

```bash
# Rollback one migration
docker compose -f docker-compose.prod.yml exec api alembic downgrade -1

# Rollback to specific version
docker compose -f docker-compose.prod.yml exec api alembic downgrade <revision>
```

## Monitoring After Deployment

### Essential Checks

```bash
# 1. Services running
docker compose -f docker-compose.prod.yml ps

# 2. No errors in logs
docker compose -f docker-compose.prod.yml logs --tail=100 api | grep -i error

# 3. API responding
curl -I https://abparts.oraseas.com/api/health

# 4. Frontend loading
curl -I https://abparts.oraseas.com

# 5. Database connections
docker compose -f docker-compose.prod.yml exec api python -c "from app.database import engine; engine.connect()"
```

### Performance Monitoring

```bash
# Container resource usage
docker stats --no-stream

# Disk space
df -h

# Database size
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "SELECT pg_size_pretty(pg_database_size('abparts_prod'));"
```

## Common Issues and Solutions

### Issue: Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000

# Stop conflicting container
docker compose -f docker-compose.prod.yml stop api
docker compose -f docker-compose.prod.yml up -d api
```

### Issue: Container Won't Start

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs api

# Check container status
docker compose -f docker-compose.prod.yml ps api

# Rebuild from scratch
docker compose -f docker-compose.prod.yml build --no-cache api
docker compose -f docker-compose.prod.yml up -d api
```

### Issue: Database Connection Failed

```bash
# Check database is running
docker compose -f docker-compose.prod.yml ps db

# Check database logs
docker compose -f docker-compose.prod.yml logs db

# Test connection
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "SELECT 1;"
```

## Security Best Practices

### 1. Don't Commit Secrets

```bash
# ❌ Never commit
.env
*.key
*.pem

# ✅ Use .gitignore
echo ".env" >> .gitignore
```

### 2. Use Environment Variables

```bash
# ✅ In docker-compose.prod.yml
environment:
  - DATABASE_URL=${DATABASE_URL}
  - SECRET_KEY=${SECRET_KEY}
```

### 3. Limit Container Permissions

```bash
# ✅ Run as non-root user in Dockerfile
USER appuser
```

### 4. Keep Images Updated

```bash
# Regularly update base images
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

## Documentation Requirements

Every deployment should have:

1. **Deployment guide** - Step-by-step instructions
2. **Deployment script** - Automated deployment
3. **Rollback procedure** - How to undo changes
4. **Testing checklist** - What to verify after deployment
5. **Troubleshooting guide** - Common issues and solutions

## Checklist for Future Deployments

- [ ] Changes tested locally
- [ ] Database migrations tested (if applicable)
- [ ] Deployment script created
- [ ] Documentation written
- [ ] Rollback procedure documented
- [ ] Code committed and pushed
- [ ] Production backup taken
- [ ] Deployment script tested
- [ ] Services verified after deployment
- [ ] Logs checked for errors
- [ ] Feature tested in production
- [ ] Team notified of deployment

---

**Remember:** Fast deployments come from good preparation, not rushing. Take time to:
- Write clear documentation
- Create automated scripts
- Test thoroughly locally
- Have rollback plans ready

This makes production deployments smooth and stress-free! 🚀
