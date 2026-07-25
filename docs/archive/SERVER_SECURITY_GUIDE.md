# Server Security Guide

## Overview

Your ABParts server is now protected with multiple layers of security:

1. **Fail2ban** - Automatically bans IPs showing malicious behavior
2. **UFW Firewall** - Controls which ports are accessible
3. **Nginx Rate Limiting** - Prevents brute force and DDoS attacks
4. **Automatic Security Updates** - Keeps system patched

## Deployment

### Initial Setup

Run the deployment script on your production server:

```bash
cd /home/diogo/abparts
sudo ./deploy_server_security.sh
```

This will:
- Install and configure Fail2ban
- Configure UFW firewall
- Add nginx rate limiting
- Enable automatic security updates
- Restart all services

**IMPORTANT**: Make sure you're connected via SSH before running this. The script is designed to not lock you out, but it's good practice to have a backup connection.

## Security Configuration

### Fail2ban Settings

**Ban Times:**
- SSH attacks: 2 hours (7200 seconds)
- HTTP/HTTPS attacks: 1 hour (3600 seconds)

**Thresholds:**
- SSH: 3 failed attempts in 10 minutes
- Nginx: 5 failed attempts in 10 minutes
- Bad bots: 2 attempts
- Script attacks: 6 attempts

**Protected Services:**
- SSH (port 22)
- Nginx HTTP/HTTPS (ports 80, 443)
- Bad bots and proxies
- Script attacks
- Rate limit violations

### Nginx Rate Limiting

**Login Endpoint (`/api/token`):**
- 5 requests per minute
- Burst: 3 additional requests
- Max connections: 5 per IP

**API Endpoints (`/api/*`):**
- 100 requests per minute
- Burst: 20 additional requests
- Max connections: 10 per IP

**General Traffic (`/`):**
- 200 requests per minute
- Burst: 50 additional requests
- Max connections: 10 per IP

### Firewall Rules

**Allowed Ports:**
- 22 (SSH)
- 80 (HTTP)
- 443 (HTTPS)

**Default Policy:**
- Incoming: DENY
- Outgoing: ALLOW

## Monitoring

### Check Banned IPs

```bash
# View all Fail2ban jails
sudo fail2ban-client status

# Check specific jail (SSH)
sudo fail2ban-client status sshd

# Check nginx rate limiting jail
sudo fail2ban-client status nginx-limit-req

# Check nginx bad bots jail
sudo fail2ban-client status nginx-badbots
```

### View Logs

```bash
# Fail2ban log (shows bans/unbans)
sudo tail -f /var/log/fail2ban.log

# Nginx error log (shows rate limit violations)
sudo tail -f /var/log/nginx/error.log

# Nginx access log (shows all requests)
sudo tail -f /var/log/nginx/access.log

# System auth log (shows SSH attempts)
sudo tail -f /var/log/auth.log
```

### Check Firewall Status

```bash
# View firewall status
sudo ufw status verbose

# View firewall rules numbered
sudo ufw status numbered
```

## Management

### Unban an IP Address

If a legitimate user gets banned:

```bash
# Unban from SSH jail
sudo fail2ban-client set sshd unbanip 1.2.3.4

# Unban from nginx jail
sudo fail2ban-client set nginx-limit-req unbanip 1.2.3.4

# Unban from all jails
sudo fail2ban-client unban 1.2.3.4
```

### Whitelist an IP Address

To permanently whitelist an IP (like your office):

```bash
# Edit Fail2ban config
sudo nano /etc/fail2ban/jail.local

# Add IP to ignoreip line:
ignoreip = 127.0.0.1/8 ::1 YOUR.IP.ADDRESS.HERE

# Restart Fail2ban
sudo systemctl restart fail2ban
```

### Adjust Rate Limits

If legitimate users are hitting rate limits:

```bash
# Edit rate limit config
sudo nano /etc/nginx/conf.d/rate-limit.conf

# Increase the rate (e.g., from 5r/m to 10r/m)
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=10r/m;

# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

### Restart Services

```bash
# Restart Fail2ban
sudo systemctl restart fail2ban

# Reload Nginx (no downtime)
sudo systemctl reload nginx

# Restart Nginx (brief downtime)
sudo systemctl restart nginx

# Check service status
sudo systemctl status fail2ban
sudo systemctl status nginx
```

## Testing

### Test Rate Limiting

```bash
# Test login rate limit (should get 429 after 5 requests)
for i in {1..10}; do 
  curl -X POST https://abparts.oraseas.com/api/token \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=test&password=test"
  echo ""
done

# Test API rate limit
for i in {1..110}; do 
  curl -I https://abparts.oraseas.com/api/health
done

# Test general rate limit
for i in {1..210}; do 
  curl -I https://abparts.oraseas.com/
done
```

When rate limited, you'll see:
- HTTP 429 (Too Many Requests)
- HTTP 503 (Service Temporarily Unavailable)

### Test Fail2ban

```bash
# Simulate SSH attack (from another machine)
# This will ban your IP after 3 failed attempts
for i in {1..5}; do 
  ssh wronguser@abparts.oraseas.com
done

# Check if you got banned
sudo fail2ban-client status sshd
```

## Common Scenarios

### Scenario 1: User Can't Login

**Symptoms:** User gets "Too Many Requests" error

**Cause:** Hit login rate limit (5 attempts per minute)

**Solution:**
1. Wait 1 minute for rate limit to reset
2. If still blocked, check if IP is banned:
   ```bash
   sudo fail2ban-client status nginx-limit-req
   ```
3. Unban if needed:
   ```bash
   sudo fail2ban-client set nginx-limit-req unbanip <IP>
   ```

### Scenario 2: API Requests Failing

**Symptoms:** API returns 429 or 503 errors

**Cause:** Hit API rate limit (100 requests per minute)

**Solution:**
1. Check if it's a legitimate user or bot
2. If legitimate, increase rate limit in `/etc/nginx/conf.d/rate-limit.conf`
3. If bot, let Fail2ban handle it

### Scenario 3: Locked Out of SSH

**Symptoms:** Can't SSH to server

**Cause:** IP banned after failed login attempts

**Solution:**
1. Use Hetzner console to access server
2. Check banned IPs:
   ```bash
   sudo fail2ban-client status sshd
   ```
3. Unban your IP:
   ```bash
   sudo fail2ban-client set sshd unbanip <YOUR_IP>
   ```
4. Add your IP to whitelist to prevent future bans

### Scenario 4: Monitoring Attack Attempts

**Check recent bans:**
```bash
# View recent Fail2ban activity
sudo tail -100 /var/log/fail2ban.log | grep Ban

# View rate limit violations
sudo grep "limiting requests" /var/log/nginx/error.log | tail -20

# View bad bot attempts
sudo fail2ban-client status nginx-badbots
```

## Security Best Practices

1. **Monitor Regularly**
   - Check logs weekly: `sudo tail -100 /var/log/fail2ban.log`
   - Review banned IPs monthly
   - Monitor for unusual patterns

2. **Keep Whitelist Updated**
   - Add your office/home IP to Fail2ban whitelist
   - Document why each IP is whitelisted

3. **Adjust Thresholds**
   - Start strict, relax if needed
   - Monitor false positives
   - Balance security vs usability

4. **Backup Configuration**
   - Configs are in `/etc/fail2ban/` and `/etc/nginx/`
   - Backup before making changes
   - Test changes before applying

5. **Stay Updated**
   - Automatic security updates are enabled
   - Manually update monthly: `sudo apt update && sudo apt upgrade`
   - Review security advisories

## Configuration Files

**Fail2ban:**
- Main config: `/etc/fail2ban/jail.local`
- Logs: `/var/log/fail2ban.log`

**Nginx:**
- Rate limits: `/etc/nginx/conf.d/rate-limit.conf`
- Site config: `/etc/nginx/sites-available/abparts.oraseas.com`
- Error log: `/var/log/nginx/error.log`
- Access log: `/var/log/nginx/access.log`

**UFW:**
- Status: `sudo ufw status`
- Rules: `/etc/ufw/`

## Emergency Procedures

### Disable All Security (Emergency Only)

```bash
# Stop Fail2ban
sudo systemctl stop fail2ban

# Disable UFW
sudo ufw disable

# Remove rate limiting from nginx
sudo mv /etc/nginx/conf.d/rate-limit.conf /etc/nginx/conf.d/rate-limit.conf.disabled
sudo systemctl reload nginx
```

### Re-enable Security

```bash
# Start Fail2ban
sudo systemctl start fail2ban

# Enable UFW
sudo ufw enable

# Restore rate limiting
sudo mv /etc/nginx/conf.d/rate-limit.conf.disabled /etc/nginx/conf.d/rate-limit.conf
sudo systemctl reload nginx
```

## Support

If you encounter issues:

1. Check logs first (see Monitoring section)
2. Try unban/whitelist solutions
3. Temporarily disable specific protection to isolate issue
4. Document the issue and solution for future reference

## Summary

Your server is now protected against:
- ✓ Brute force SSH attacks
- ✓ Brute force login attempts
- ✓ DDoS attacks
- ✓ Bad bots and scrapers
- ✓ Script injection attempts
- ✓ Excessive API usage

The system will automatically:
- ✓ Ban malicious IPs
- ✓ Rate limit excessive requests
- ✓ Apply security updates
- ✓ Log all security events

Monitor regularly and adjust thresholds as needed based on your traffic patterns.
