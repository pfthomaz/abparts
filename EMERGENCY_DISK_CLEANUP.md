# Emergency Disk Cleanup - Production Server

## Critical Issue
Both Redis and PostgreSQL are failing with "No space left on device" error.

## Immediate Actions Required

### 1. Check Disk Usage
```bash
df -h
du -sh /var/lib/docker/* | sort -h
```

### 2. Clean Docker System (SAFE - removes unused data)
```bash
# Remove stopped containers
sudo docker container prune -f

# Remove unused images
sudo docker image prune -a -f

# Remove unused volumes (BE CAREFUL - check first)
sudo docker volume ls
# Only remove volumes you don't need

# Remove build cache
sudo docker builder prune -a -f

# All-in-one cleanup (excludes volumes)
sudo docker system prune -a -f
```

### 3. Check Docker Logs (they can grow huge)
```bash
# Check log sizes
sudo du -sh /var/lib/docker/containers/*/*-json.log | sort -h | tail -20

# Truncate large log files
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log
```

### 4. Check Application Logs
```bash
# Check if any application logs are huge
du -sh ~/abparts/backend/logs/* 2>/dev/null
du -sh ~/abparts/frontend/logs/* 2>/dev/null

# Clean if needed
rm -rf ~/abparts/backend/logs/*
rm -rf ~/abparts/frontend/logs/*
```

### 5. Clean System Logs
```bash
# Check system logs
sudo du -sh /var/log/* | sort -h | tail -10

# Clean old logs (if needed)
sudo journalctl --vacuum-time=7d
sudo journalctl --vacuum-size=500M
```

### 6. Remove Old Docker Volumes (if safe)
```bash
# List volumes
sudo docker volume ls

# Remove development volumes (NOT production ones!)
sudo docker volume rm abparts_db_data
sudo docker volume rm abparts_redis_data
sudo docker volume rm abparts_pgadmin_data
sudo docker volume rm abparts_api_static_images
```

## After Cleanup

### Restart Services
```bash
cd ~/abparts
sudo docker-compose -f docker-compose.prod.yml down
sudo docker-compose -f docker-compose.prod.yml up -d
```

### Verify Services
```bash
sudo docker ps
sudo docker logs abparts_db_prod --tail=20
sudo docker logs abparts_redis_prod --tail=20
sudo docker logs abparts_api_prod --tail=20
```

## Prevention

### Set Log Rotation for Docker
Create `/etc/docker/daemon.json`:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Then restart Docker:
```bash
sudo systemctl restart docker
```

### Monitor Disk Usage
```bash
# Add to crontab for daily monitoring
0 9 * * * df -h | mail -s "Disk Usage Report" your@email.com
```

## Quick Reference Commands

```bash
# Check what's using space
df -h
du -sh /var/lib/docker/* | sort -h
du -sh ~/abparts/* | sort -h

# Quick cleanup
sudo docker system prune -a -f
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log

# Restart production
cd ~/abparts
sudo docker-compose -f docker-compose.prod.yml restart
```
