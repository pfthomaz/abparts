# Server Security Deployment - Ready to Deploy

## Overview

Your ABParts server security system is ready to deploy. This will protect your server from:

- ✓ Brute force SSH attacks
- ✓ Brute force login attempts  
- ✓ DDoS attacks
- ✓ Bad bots and scrapers
- ✓ Script injection attempts
- ✓ Excessive API usage

## What Will Be Installed

### 1. Fail2ban
Automatically bans IP addresses that show malicious behavior:
- **SSH attacks**: Ban after 3 failed attempts for 2 hours
- **HTTP/HTTPS attacks**: Ban after 5 failed attempts for 1 hour
- **Bad bots**: Ban after 2 attempts
- **Rate limit violations**: Ban after 10 violations in 1 minute

### 2. UFW Firewall
Controls which ports are accessible:
- **Allowed**: SSH (22), HTTP (80), HTTPS (443)
- **Blocked**: All other incoming traffic
- **Outgoing**: All allowed (for updates, API calls, etc.)

### 3. Nginx Rate Limiting
Prevents brute force and DDoS attacks:
- **Login endpoint**: 5 attempts per minute (burst 3)
- **API endpoints**: 100 requests per minute (burst 20)
- **General traffic**: 200 requests per minute (burst 50)
- **Max connections**: 10 per IP address

### 4. Automatic Security Updates
Keeps your system patched with latest security fixes automatically.

## Deployment Steps

### Step 1: Upload Scripts to Server

From your local machine, upload the security scripts:

```bash
# SSH to your server
ssh diogo@46.62.131.135

# Navigate to project directory
cd /home/diogo/abparts

# Verify the script exists
ls -la deploy_server_security.sh
```

If you need to upload from local machine:
```bash
# From your local machine
scp deploy_server_security.sh diogo@46.62.131.135:/home/diogo/abparts/
scp check_security_status.sh diogo@46.62.131.135:/home/diogo/abparts/
```

### Step 2: Run Deployment Script

**IMPORTANT**: Make sure you're connected via SSH before running this. The script won't lock you out, but it's good practice to have a backup connection ready.

```bash
# Make script executable (if not already)
chmod +x deploy_server_security.sh

# Run the deployment
sudo ./deploy_server_security.sh
```

The script will:
1. Install Fail2ban and UFW
2. Configure Fail2ban with protection rules
3. Configure UFW firewall
4. Create nginx rate limiting zones
5. Update nginx configuration with rate limits
6. Enable automatic security updates
7. Restart all services
8. Display status summary

**Expected Duration**: 2-3 minutes

### Step 3: Verify Deployment

After deployment completes, verify everything is working:

```bash
# Check security status
sudo ./check_security_status.sh
```

You should see:
- ✓ Fail2ban running with multiple jails active
- ✓ UFW firewall enabled with ports 22, 80, 443 allowed
- ✓ Nginx running with rate limiting configured
- ✓ Docker containers running
- ✓ Automatic updates enabled
- ✓ SSL certificate valid

### Step 4: Test Your Application

1. **Test normal access**:
   - Visit https://abparts.oraseas.com
   - Login with your credentials
   - Navigate through the app
   - Everything should work normally

2. **Test rate limiting** (optional):
   ```bash
   # From your local machine, try rapid requests
   for i in {1..10}; do curl -I https://abparts.oraseas.com/api/health; done
   ```
   
   You should see normal responses for first ~100 requests, then 429 (Too Many Requests) after that.

## What to Expect

### Normal Operation

- **Users won't notice anything different** - rate limits are generous for normal use
- **Legitimate traffic flows normally** - no delays or blocks
- **Malicious traffic gets blocked** - attackers are automatically banned

### When Rate Limits Trigger

If a user hits a rate limit, they'll see:
- **HTTP 429**: Too Many Requests
- **HTTP 503**: Service Temporarily Unavailable

This is normal and protects your server. The limit resets after 1 minute.

### When IPs Get Banned

If an IP is banned by Fail2ban:
- **SSH**: Can't connect for 2 hours
- **HTTP/HTTPS**: Can't access site for 1 hour
- **Automatic unban**: After ban time expires

## Monitoring

### Quick Status Check

```bash
# Run anytime to see current status
sudo ./check_security_status.sh
```

### View Real-Time Logs

```bash
# Watch Fail2ban activity
sudo tail -f /var/log/fail2ban.log

# Watch nginx errors (rate limits)
sudo tail -f /var/log/nginx/error.log

# Watch all access attempts
sudo tail -f /var/log/nginx/access.log
```

### Check Banned IPs

```bash
# View all jails
sudo fail2ban-client status

# Check SSH bans
sudo fail2ban-client status sshd

# Check nginx rate limit bans
sudo fail2ban-client status nginx-limit-req
```

## Common Tasks

### Unban an IP Address

If someone gets banned accidentally:

```bash
# Unban from SSH
sudo fail2ban-client set sshd unbanip 1.2.3.4

# Unban from nginx
sudo fail2ban-client set nginx-limit-req unbanip 1.2.3.4

# Unban from all jails
sudo fail2ban-client unban 1.2.3.4
```

### Whitelist Your IP

To prevent your own IP from ever being banned:

```bash
# Edit Fail2ban config
sudo nano /etc/fail2ban/jail.local

# Add your IP to the ignoreip line:
ignoreip = 127.0.0.1/8 ::1 YOUR.IP.ADDRESS.HERE

# Restart Fail2ban
sudo systemctl restart fail2ban
```

### Adjust Rate Limits

If legitimate users are hitting limits:

```bash
# Edit rate limit config
sudo nano /etc/nginx/conf.d/rate-limit.conf

# Change the rate (e.g., from 5r/m to 10r/m)
# Then reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

## Troubleshooting

### Issue: Can't SSH to Server

**Cause**: Your IP might be banned

**Solution**:
1. Use Hetzner console to access server
2. Check: `sudo fail2ban-client status sshd`
3. Unban: `sudo fail2ban-client set sshd unbanip YOUR_IP`
4. Whitelist your IP to prevent future bans

### Issue: Users Getting "Too Many Requests"

**Cause**: Hitting rate limits

**Solution**:
1. Check if it's legitimate traffic or attack
2. If legitimate, increase rate limits
3. If attack, let Fail2ban handle it

### Issue: Service Not Starting

**Cause**: Configuration error

**Solution**:
1. Check logs: `sudo journalctl -xe`
2. Test nginx: `sudo nginx -t`
3. Restore backup if needed

## Rollback (Emergency Only)

If you need to disable security temporarily:

```bash
# Stop Fail2ban
sudo systemctl stop fail2ban

# Disable firewall
sudo ufw disable

# Remove rate limiting
sudo mv /etc/nginx/conf.d/rate-limit.conf /etc/nginx/conf.d/rate-limit.conf.disabled
sudo systemctl reload nginx
```

To re-enable:
```bash
sudo systemctl start fail2ban
sudo ufw enable
sudo mv /etc/nginx/conf.d/rate-limit.conf.disabled /etc/nginx/conf.d/rate-limit.conf
sudo systemctl reload nginx
```

## Files Created/Modified

**Created:**
- `/etc/fail2ban/jail.local` - Fail2ban configuration
- `/etc/nginx/conf.d/rate-limit.conf` - Rate limiting zones
- `/etc/nginx/sites-available/abparts.oraseas.com` - Updated nginx config

**Backed Up:**
- `/etc/nginx/sites-available/abparts.oraseas.com.backup.TIMESTAMP`

**Logs:**
- `/var/log/fail2ban.log` - Fail2ban activity
- `/var/log/nginx/error.log` - Nginx errors and rate limits
- `/var/log/nginx/access.log` - All access attempts
- `/var/log/auth.log` - SSH attempts

## Next Steps After Deployment

1. **Monitor for 24 hours**
   - Check logs regularly
   - Watch for false positives
   - Verify legitimate users aren't blocked

2. **Whitelist Known IPs**
   - Add your office/home IP
   - Add any monitoring services
   - Document why each IP is whitelisted

3. **Adjust Thresholds**
   - Start strict, relax if needed
   - Monitor user complaints
   - Balance security vs usability

4. **Set Up Monitoring**
   - Check security status weekly
   - Review banned IPs monthly
   - Update whitelist as needed

## Support Resources

- **Full Guide**: `SERVER_SECURITY_GUIDE.md`
- **Status Check**: `sudo ./check_security_status.sh`
- **Deployment Script**: `deploy_server_security.sh`

## Summary

Your security deployment is ready. The system will:

✓ Automatically ban attackers
✓ Rate limit excessive requests  
✓ Block unauthorized ports
✓ Apply security updates
✓ Log all security events

Run `sudo ./deploy_server_security.sh` on your server to begin deployment.

After deployment, your server will be protected against common attacks while allowing legitimate traffic to flow normally.
