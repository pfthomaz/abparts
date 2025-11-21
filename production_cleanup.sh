#!/bin/bash
# Production Server Cleanup Script
# Run this on the production server to free up disk space

set -e

echo "=== Production Server Cleanup ==="
echo ""
echo "WARNING: This will remove unused Docker resources and old files."
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Check current disk usage
echo ""
echo "=== Current Disk Usage ==="
df -h
echo ""

# 1. Docker cleanup
echo "=== Step 1: Docker Cleanup ==="
echo ""

echo "Stopping all containers..."
sudo docker compose -f docker-compose.prod.yml down

echo ""
echo "Removing stopped containers..."
sudo docker container prune -f

echo ""
echo "Removing unused images..."
sudo docker image prune -a -f

echo ""
echo "Removing unused networks..."
sudo docker network prune -f

echo ""
echo "Removing build cache..."
sudo docker builder prune -a -f

echo ""
echo "WARNING: About to remove unused volumes (this is safe if you only use named volumes)"
echo "Current volumes:"
sudo docker volume ls
echo ""
echo "Press Enter to continue or Ctrl+C to skip..."
read
sudo docker volume prune -f

# 2. Docker logs cleanup
echo ""
echo "=== Step 2: Docker Logs Cleanup ==="
echo ""
echo "Checking Docker log sizes..."
sudo du -sh /var/lib/docker/containers/*/*-json.log 2>/dev/null | sort -h | tail -20 || echo "No large logs found"

echo ""
echo "Truncating all Docker container logs..."
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log 2>/dev/null || echo "No logs to truncate"

# 3. System logs cleanup
echo ""
echo "=== Step 3: System Logs Cleanup ==="
echo ""
echo "Cleaning journalctl logs older than 7 days..."
sudo journalctl --vacuum-time=7d

echo ""
echo "Limiting journalctl size to 500MB..."
sudo journalctl --vacuum-size=500M

# 4. APT cache cleanup
echo ""
echo "=== Step 4: APT Cache Cleanup ==="
echo ""
echo "Cleaning apt cache..."
sudo apt-get clean
sudo apt-get autoclean
sudo apt-get autoremove -y

# 5. Old kernels cleanup (be careful!)
echo ""
echo "=== Step 5: Old Kernels Cleanup ==="
echo ""
echo "Current kernel: $(uname -r)"
echo "Installed kernels:"
dpkg --list | grep linux-image
echo ""
echo "Do you want to remove old kernels? (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    sudo apt-get autoremove --purge -y
fi

# 6. Temporary files cleanup
echo ""
echo "=== Step 6: Temporary Files Cleanup ==="
echo ""
echo "Cleaning /tmp..."
sudo find /tmp -type f -atime +7 -delete 2>/dev/null || true

echo "Cleaning /var/tmp..."
sudo find /var/tmp -type f -atime +7 -delete 2>/dev/null || true

# 7. Application-specific cleanup
echo ""
echo "=== Step 7: Application Cleanup ==="
echo ""

# Remove old git stashes
cd ~/abparts
echo "Clearing git stash..."
git stash clear || true

# Remove Python cache
echo "Removing Python cache files..."
find ~/abparts -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find ~/abparts -type f -name "*.pyc" -delete 2>/dev/null || true

# Remove node_modules if they exist (they shouldn't in production)
if [ -d ~/abparts/frontend/node_modules ]; then
    echo "WARNING: Found node_modules in production. Removing..."
    rm -rf ~/abparts/frontend/node_modules
fi

# 8. Check for large files
echo ""
echo "=== Step 8: Large Files Check ==="
echo ""
echo "Finding files larger than 100MB..."
sudo find /home /var -type f -size +100M -exec ls -lh {} \; 2>/dev/null | head -20 || echo "No large files found"

# 9. Final disk usage
echo ""
echo "=== Final Disk Usage ==="
df -h
echo ""

# 10. Restart services
echo ""
echo "=== Step 9: Restarting Services ==="
echo ""
echo "Starting Docker containers..."
cd ~/abparts
sudo docker compose -f docker-compose.prod.yml up -d

echo ""
echo "Waiting for services to start..."
sleep 10

echo ""
echo "Checking service status..."
sudo docker ps

echo ""
echo "=== Cleanup Complete ==="
echo ""
echo "Disk space freed. Check the output above for details."
echo ""
echo "To prevent future issues, consider:"
echo "1. Setting up Docker log rotation (see below)"
echo "2. Regular cleanup cron job"
echo "3. Monitoring disk usage"
echo ""
