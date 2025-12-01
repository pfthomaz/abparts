#!/bin/bash
# Setup Disk Space Monitoring and Alerts

echo "=== Setting Up Disk Space Monitoring ==="
echo ""

# Create monitoring script
cat > ~/check_disk_space.sh <<'EOF'
#!/bin/bash
# Check disk space and alert if usage is above threshold

THRESHOLD=80
CURRENT=$(df / | grep / | awk '{ print $5}' | sed 's/%//g')
HOSTNAME=$(hostname)

if [ "$CURRENT" -gt "$THRESHOLD" ]; then
    echo "WARNING: Disk usage is at ${CURRENT}% on ${HOSTNAME}"
    echo "Current disk usage:"
    df -h
    echo ""
    echo "Top 10 largest directories in /var:"
    sudo du -sh /var/* 2>/dev/null | sort -h | tail -10
    echo ""
    echo "Docker disk usage:"
    sudo docker system df
fi
EOF

chmod +x ~/check_disk_space.sh

echo "Created monitoring script at ~/check_disk_space.sh"
echo ""

# Setup cron job
echo "Setting up daily cron job..."
(crontab -l 2>/dev/null; echo "0 9 * * * ~/check_disk_space.sh") | crontab -

echo ""
echo "Cron job added. It will run daily at 9 AM."
echo ""
echo "To test the monitoring script now:"
echo "  ~/check_disk_space.sh"
echo ""
echo "To view cron jobs:"
echo "  crontab -l"
echo ""
