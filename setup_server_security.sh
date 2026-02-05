#!/bin/bash

# Comprehensive Server Security Setup
# Installs and configures Fail2ban, UFW firewall, and security hardening

set -e

echo "=========================================="
echo "Server Security Setup"
echo "=========================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo"
    exit 1
fi

echo "This script will:"
echo "  1. Install and configure Fail2ban (auto-ban attackers)"
echo "  2. Configure UFW firewall"
echo "  3. Set up SSH protection"
echo "  4. Configure nginx rate limiting"
echo "  5. Enable automatic security updates"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo ""
echo "=========================================="
echo "Step 1: Installing Fail2ban"
echo "=========================================="
apt-get update
apt-get install -y fail2ban

echo ""
echo "Step 2: Configuring Fail2ban"
echo "=========================================="

# Create local configuration
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
# Ban for 1 hour (3600 seconds)
bantime = 3600

# Check for attacks in last 10 minutes
findtime = 600

# Ban after 5 failed attempts
maxretry = 5

# Email notifications (optional - configure if you want alerts)
# destemail = your-email@example.com
# sendername = Fail2Ban
# action = %(action_mwl)s

# Ignore local IPs (add your home/office IP if you have a static one)
ignoreip = 127.0.0.1/8 ::1

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
bantime = 7200

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-noscript]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2

[nginx-noproxy]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
findtime = 60
bantime = 3600
EOF

echo ""
echo "Step 3: Installing UFW Firewall"
echo "=========================================="
apt-get install -y ufw

# Configure UFW
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (IMPORTANT - don't lock yourself out!)
ufw allow ssh
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow your application ports (if needed)
# ufw allow 8000/tcp  # Backend API
# ufw allow 3001/tcp  # Frontend

echo ""
echo "Step 4: Enabling UFW"
echo "=========================================="
echo "y" | ufw enable

echo ""
echo "Step 5: Installing automatic security updates"
echo "=========================================="
apt-get install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

echo ""
echo "Step 6: Restarting services"
echo "=========================================="
systemctl restart fail2ban
systemctl enable fail2ban

echo ""
echo "=========================================="
echo "✓ Security Setup Complete!"
echo "=========================================="
echo ""
echo "Fail2ban Configuration:"
echo "  - Ban time: 1 hour (3600 seconds)"
echo "  - Find time: 10 minutes (600 seconds)"
echo "  - Max retries: 5 attempts"
echo "  - SSH max retries: 3 attempts (2 hour ban)"
echo ""
echo "Protected Services:"
echo "  ✓ SSH (port 22)"
echo "  ✓ Nginx HTTP/HTTPS (ports 80, 443)"
echo "  ✓ Bad bots and proxies"
echo "  ✓ Script attacks"
echo ""
echo "Firewall (UFW) Status:"
ufw status verbose
echo ""
echo "Fail2ban Status:"
fail2ban-client status
echo ""
echo "Useful Commands:"
echo "  - Check banned IPs: sudo fail2ban-client status sshd"
echo "  - Unban an IP: sudo fail2ban-client set sshd unbanip <IP>"
echo "  - Check firewall: sudo ufw status"
echo "  - View fail2ban log: sudo tail -f /var/log/fail2ban.log"
echo "  - View banned IPs: sudo fail2ban-client banned"
echo ""
