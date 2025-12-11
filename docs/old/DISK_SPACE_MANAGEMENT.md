# Disk Space Management Guide

## Immediate Cleanup (Run on Server)

### Quick Cleanup Commands
```bash
# Check current usage
df -h

# Quick Docker cleanup (safe)
sudo docker system prune -a -f
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log

# Check usage again
df -h
```

### Full Cleanup Script
```bash
cd ~/abparts
chmod +x production_cleanup.sh
./production_cleanup.sh
```

This script will:
1. Clean Docker (containers, images, networks, build cache)
2. Truncate Docker logs
3. Clean system logs (journalctl)
4. Clean APT cache
5. Remove old kernels (optional)
6. Clean temporary files
7. Remove Python cache and git stash
8. Show large files
9. Restart services

## Prevention (One-Time Setup)

### 1. Setup Docker Log Rotation
```bash
cd ~/abparts
chmod +x setup_log_rotation.sh
sudo ./setup_log_rotation.sh
```

This limits each container's logs to 30MB total (3 files × 10MB).

### 2. Setup Monitoring
```bash
cd ~/abparts
chmod +x setup_monitoring.sh
./setup_monitoring.sh
```

This creates a daily cron job to check disk usage.

## Regular Maintenance

### Weekly Cleanup (Recommended)
```bash
# Clean Docker
sudo docker system prune -f
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log

# Clean system logs
sudo journalctl --vacuum-time=7d
```

### Monthly Cleanup
```bash
# Full cleanup
cd ~/abparts
./production_cleanup.sh
```

## Monitoring Commands

### Check Disk Usage
```bash
# Overall disk usage
df -h

# Largest directories
sudo du -sh /* | sort -h | tail -10

# Docker disk usage
sudo docker system df

# Docker log sizes
sudo du -sh /var/lib/docker/containers/*/*-json.log | sort -h | tail -10
```

### Check What's Using Space
```bash
# Top 20 largest files
sudo find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null | head -20

# Docker images
sudo docker images

# Docker volumes
sudo docker volume ls
```

## Emergency Cleanup (When Disk is Full)

If disk is 100% full and services won't start:

```bash
# 1. Truncate logs immediately
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log

# 2. Remove all stopped containers
sudo docker container prune -f

# 3. Remove unused images
sudo docker image prune -a -f

# 4. Clean system logs
sudo journalctl --vacuum-size=100M

# 5. Clean APT cache
sudo apt-get clean

# 6. Check space
df -h

# 7. Restart services
cd ~/abparts
sudo docker compose -f docker-compose.prod.yml up -d
```

## What NOT to Delete

**DO NOT delete these:**
- `/var/lib/abparts/images/` - Your uploaded images
- Docker volumes: `abparts_db_data_prod`, `abparts_redis_data_prod`
- `/home/abparts/abparts/` - Your application code

**Safe to delete:**
- Docker logs
- Unused Docker images
- Stopped containers
- Build cache
- System logs older than 7 days
- APT cache

## Automated Cleanup Cron Job

Add to crontab for weekly cleanup:

```bash
crontab -e
```

Add this line:
```
0 2 * * 0 /home/abparts/abparts/production_cleanup.sh >> /home/abparts/cleanup.log 2>&1
```

This runs cleanup every Sunday at 2 AM.

## Disk Space Alerts

To get email alerts when disk is full, install and configure:

```bash
sudo apt-get install mailutils
```

Then add to crontab:
```bash
0 */6 * * * df -h | grep -vE '^Filesystem|tmpfs|cdrom' | awk '{ print $5 " " $1 }' | while read output; do usage=$(echo $output | awk '{ print $1}' | cut -d'%' -f1); if [ $usage -ge 80 ]; then echo "Disk usage alert: $output" | mail -s "Disk Space Alert" your@email.com; fi; done
```

## Troubleshooting

### "No space left on device" error
1. Run emergency cleanup commands above
2. Check what's using space: `sudo du -sh /* | sort -h`
3. Truncate Docker logs: `sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log`

### Services won't start after cleanup
```bash
cd ~/abparts
sudo docker compose -f docker-compose.prod.yml down
sudo docker compose -f docker-compose.prod.yml up -d
```

### Lost Docker images after cleanup
```bash
cd ~/abparts
sudo docker compose -f docker-compose.prod.yml build
sudo docker compose -f docker-compose.prod.yml up -d
```

## Best Practices

1. **Enable log rotation** - Prevents logs from growing indefinitely
2. **Regular cleanup** - Weekly Docker cleanup, monthly full cleanup
3. **Monitor disk usage** - Set up alerts before it's too late
4. **Keep backups** - Regular database backups to external storage
5. **Upgrade storage** - If consistently running out of space, consider upgrading

## Quick Reference

```bash
# Check space
df -h

# Quick cleanup
sudo docker system prune -a -f && sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log

# Full cleanup
cd ~/abparts && ./production_cleanup.sh

# Setup prevention
cd ~/abparts && sudo ./setup_log_rotation.sh && ./setup_monitoring.sh
```
