#!/bin/bash

# Quick Security Status Check
# Run this anytime to see current security status

echo "=========================================="
echo "ABParts Server Security Status"
echo "=========================================="
echo ""
echo "Server: abparts.oraseas.com (46.62.131.135)"
echo "Date: $(date)"
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Note: Run with sudo for full status"
    echo "Usage: sudo ./check_security_status.sh"
    echo ""
fi

# Check Fail2ban
echo "=========================================="
echo "1. FAIL2BAN STATUS"
echo "=========================================="
if command -v fail2ban-client &> /dev/null; then
    if [ "$EUID" -eq 0 ]; then
        fail2ban-client status
        echo ""
        echo "Active Bans:"
        fail2ban-client status sshd 2>/dev/null | grep "Currently banned" || echo "  SSH: No banned IPs"
        fail2ban-client status nginx-limit-req 2>/dev/null | grep "Currently banned" || echo "  Nginx Rate Limit: No banned IPs"
        fail2ban-client status nginx-badbots 2>/dev/null | grep "Currently banned" || echo "  Bad Bots: No banned IPs"
    else
        echo "  ⚠ Run with sudo to see Fail2ban status"
    fi
else
    echo "  ✗ Fail2ban not installed"
fi
echo ""

# Check UFW
echo "=========================================="
echo "2. FIREWALL (UFW) STATUS"
echo "=========================================="
if command -v ufw &> /dev/null; then
    if [ "$EUID" -eq 0 ]; then
        ufw status verbose
    else
        echo "  ⚠ Run with sudo to see firewall status"
    fi
else
    echo "  ✗ UFW not installed"
fi
echo ""

# Check Nginx
echo "=========================================="
echo "3. NGINX STATUS"
echo "=========================================="
if command -v nginx &> /dev/null; then
    if systemctl is-active --quiet nginx; then
        echo "  ✓ Nginx is running"
        
        # Check if rate limiting is configured
        if [ -f /etc/nginx/conf.d/rate-limit.conf ]; then
            echo "  ✓ Rate limiting configured"
            echo ""
            echo "  Rate Limit Zones:"
            grep "limit_req_zone" /etc/nginx/conf.d/rate-limit.conf 2>/dev/null | sed 's/^/    /'
        else
            echo "  ✗ Rate limiting not configured"
        fi
        
        # Check recent rate limit violations
        if [ "$EUID" -eq 0 ] && [ -f /var/log/nginx/error.log ]; then
            VIOLATIONS=$(grep "limiting requests" /var/log/nginx/error.log 2>/dev/null | tail -5 | wc -l)
            if [ "$VIOLATIONS" -gt 0 ]; then
                echo ""
                echo "  Recent Rate Limit Violations (last 5):"
                grep "limiting requests" /var/log/nginx/error.log 2>/dev/null | tail -5 | sed 's/^/    /'
            fi
        fi
    else
        echo "  ✗ Nginx is not running"
    fi
else
    echo "  ✗ Nginx not installed"
fi
echo ""

# Check Docker containers
echo "=========================================="
echo "4. DOCKER CONTAINERS"
echo "=========================================="
if command -v docker &> /dev/null; then
    if [ "$EUID" -eq 0 ]; then
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "abparts|NAME"
    else
        echo "  ⚠ Run with sudo to see Docker status"
    fi
else
    echo "  ✗ Docker not installed"
fi
echo ""

# Check recent security events
echo "=========================================="
echo "5. RECENT SECURITY EVENTS"
echo "=========================================="
if [ "$EUID" -eq 0 ]; then
    echo "Recent Fail2ban Bans (last 10):"
    if [ -f /var/log/fail2ban.log ]; then
        grep "Ban " /var/log/fail2ban.log 2>/dev/null | tail -10 | sed 's/^/  /' || echo "  No recent bans"
    else
        echo "  Log file not found"
    fi
    
    echo ""
    echo "Recent SSH Login Attempts (last 5):"
    if [ -f /var/log/auth.log ]; then
        grep "Failed password" /var/log/auth.log 2>/dev/null | tail -5 | sed 's/^/  /' || echo "  No recent failed attempts"
    else
        echo "  Log file not found"
    fi
else
    echo "  ⚠ Run with sudo to see security events"
fi
echo ""

# System updates
echo "=========================================="
echo "6. SYSTEM UPDATES"
echo "=========================================="
if [ "$EUID" -eq 0 ]; then
    if command -v apt &> /dev/null; then
        UPDATES=$(apt list --upgradable 2>/dev/null | grep -c upgradable)
        if [ "$UPDATES" -gt 1 ]; then
            echo "  ⚠ $((UPDATES - 1)) updates available"
            echo "  Run: sudo apt update && sudo apt upgrade"
        else
            echo "  ✓ System is up to date"
        fi
        
        # Check if unattended-upgrades is enabled
        if systemctl is-enabled unattended-upgrades &>/dev/null; then
            echo "  ✓ Automatic security updates enabled"
        else
            echo "  ⚠ Automatic security updates not enabled"
        fi
    fi
else
    echo "  ⚠ Run with sudo to check for updates"
fi
echo ""

# SSL Certificate
echo "=========================================="
echo "7. SSL CERTIFICATE"
echo "=========================================="
if [ "$EUID" -eq 0 ]; then
    if [ -f /etc/letsencrypt/live/abparts.oraseas.com/cert.pem ]; then
        EXPIRY=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/abparts.oraseas.com/cert.pem | cut -d= -f2)
        echo "  ✓ SSL certificate found"
        echo "  Expires: $EXPIRY"
        
        # Check if expiring soon (within 30 days)
        EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
        NOW_EPOCH=$(date +%s)
        DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))
        
        if [ "$DAYS_LEFT" -lt 30 ]; then
            echo "  ⚠ Certificate expires in $DAYS_LEFT days - renewal needed soon"
        else
            echo "  ✓ Certificate valid for $DAYS_LEFT days"
        fi
    else
        echo "  ✗ SSL certificate not found"
    fi
else
    echo "  ⚠ Run with sudo to check SSL certificate"
fi
echo ""

# Summary
echo "=========================================="
echo "QUICK ACTIONS"
echo "=========================================="
echo ""
echo "View detailed logs:"
echo "  sudo tail -f /var/log/fail2ban.log"
echo "  sudo tail -f /var/log/nginx/error.log"
echo ""
echo "Unban an IP:"
echo "  sudo fail2ban-client set sshd unbanip <IP>"
echo "  sudo fail2ban-client set nginx-limit-req unbanip <IP>"
echo ""
echo "Check specific jail:"
echo "  sudo fail2ban-client status sshd"
echo "  sudo fail2ban-client status nginx-limit-req"
echo ""
echo "For full guide, see: SERVER_SECURITY_GUIDE.md"
echo ""

