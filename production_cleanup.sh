#!/bin/bash

echo "========================================="
echo "Production Server Cleanup"
echo "========================================="
echo ""

# Check if running as root for some commands
if [ "$EUID" -ne 0 ]; then 
    echo "Note: Some cleanup tasks require sudo. You may be prompted for password."
    echo ""
fi

# Show current disk usage
echo "Current disk usage:"
df -h /
echo ""

read -p "Continue with cleanup? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi
echo ""

# 1. Docker cleanup
echo "1. Cleaning Docker..."
echo "   - Removing stopped containers..."
sudo docker container prune -f
echo "   - Removing unused images..."
sudo docker image prune -a -f
echo "   - Removing unused networks..."
sudo docker network prune -f
echo "   - Removing build cache..."
sudo docker builder prune -a -f
echo "   ✓ Docker cleaned"
echo ""

# 2. Truncate Docker logs
echo "2. Truncating Docker logs..."
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log 2>/dev/null || true
echo "   ✓ Docker logs truncated"
echo ""

# 3. Clean system logs
echo "3. Cleaning system logs (keeping last 7 days)..."
sudo journalctl --vacuum-time=7d
echo "   ✓ System logs cleaned"
echo ""

# 4. Clean APT cache
echo "4. Cleaning APT cache..."
sudo apt-get clean
sudo apt-get autoclean
echo "   ✓ APT cache cleaned"
echo ""

# 5. Remove old kernels (optional, be careful)
echo "5. Checking for old kernels..."
CURRENT_KERNEL=$(uname -r)
OLD_KERNELS=$(dpkg -l | grep linux-image | grep -v "$CURRENT_KERNEL" | awk '{print $2}' | grep -v "linux-image-generic")
if [ -n "$OLD_KERNELS" ]; then
    echo "   Found old kernels:"
    echo "$OLD_KERNELS"
    read -p "   Remove old kernels? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$OLD_KERNELS" | xargs sudo apt-get purge -y
        echo "   ✓ Old kernels removed"
    else
        echo "   Skipped kernel removal"
    fi
else
    echo "   No old kernels to remove"
fi
echo ""

# 6. Clean temporary files
echo "6. Cleaning temporary files..."
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*
echo "   ✓ Temporary files cleaned"
echo ""

# 7. Clean Python cache and git
echo "7. Cleaning Python cache and git..."
cd ~/abparts
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
git gc --aggressive --prune=now 2>/dev/null || true
echo "   ✓ Python cache and git cleaned"
echo ""

# 8. Show large files
echo "8. Largest files in /var:"
sudo du -sh /var/* 2>/dev/null | sort -h | tail -5
echo ""

# 9. Show Docker disk usage
echo "9. Docker disk usage:"
sudo docker system df
echo ""

# Final disk usage
echo "========================================="
echo "Cleanup Complete!"
echo "========================================="
echo ""
echo "Disk usage after cleanup:"
df -h /
echo ""

# Show space freed
echo "To see detailed breakdown:"
echo "  sudo du -sh /* | sort -h | tail -10"
echo ""
echo "To restart services:"
echo "  cd ~/abparts && docker compose -f docker-compose.prod.yml restart"
echo ""
