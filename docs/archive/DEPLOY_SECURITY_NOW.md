# Deploy Server Security - Quick Start

## TL;DR

Protect your server from attacks in 3 commands:

```bash
ssh diogo@46.62.131.135
cd /home/diogo/abparts
sudo ./deploy_server_security.sh
```

## What This Does

Installs automatic protection against:
- Brute force attacks (SSH, login attempts)
- DDoS attacks
- Bad bots and scrapers
- Script injection attempts

## Before You Start

✓ You're connected via SSH to the server
✓ You're in the `/home/diogo/abparts` directory
✓ You have sudo access

## Deployment

### 1. Connect to Server

```bash
ssh diogo@46.62.131.135
cd /home/diogo/abparts
```

### 2. Run Deployment

```bash
sudo ./deploy_server_security.sh
```

**Duration**: 2-3 minutes

The script will:
- Install Fail2ban (auto-ban attackers)
- Configure UFW firewall
- Add nginx rate limiting
- Enable automatic security updates
- Restart services

### 3. Verify

```bash
sudo ./check_security_status.sh
```

You should see:
- ✓ Fail2ban running
- ✓ UFW firewall enabled
- ✓ Nginx with rate limiting
- ✓ All Docker containers running

### 4. Test

Visit https://abparts.oraseas.com and login normally.

Everything should work exactly as before - users won't notice any difference.

## What Gets Protected

### Fail2ban (Auto-Ban)
- **SSH**: Ban after 3 failed attempts (2 hours)
- **Login**: Ban after 5 failed attempts (1 hour)
- **Bad bots**: Ban after 2 attempts (1 hour)

### Firewall (UFW)
- **Allowed**: SSH (22), HTTP (80), HTTPS (443)
- **Blocked**: Everything else

### Rate Limiting
- **Login**: 5 attempts per minute
- **API**: 100 requests per minute
- **General**: 200 requests per minute

## Monitoring

### Quick Status
```bash
sudo ./check_security_status.sh
```

### View Banned IPs
```bash
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

### Watch Logs
```bash
sudo tail -f /var/log/fail2ban.log
sudo tail -f /var/log/nginx/error.log
```

## Common Tasks

### Unban an IP
```bash
sudo fail2ban-client unban 1.2.3.4
```

### Whitelist Your IP
```bash
sudo nano /etc/fail2ban/jail.local
# Add your IP to: ignoreip = 127.0.0.1/8 ::1 YOUR.IP.HERE
sudo systemctl restart fail2ban
```

## Troubleshooting

**Can't SSH?**
- Your IP might be banned
- Use Hetzner console to access
- Unban: `sudo fail2ban-client set sshd unbanip YOUR_IP`

**Users getting "Too Many Requests"?**
- Check if legitimate: `sudo tail /var/log/nginx/error.log`
- Unban if needed: `sudo fail2ban-client unban IP_ADDRESS`
- Increase limits if necessary

**Need to disable temporarily?**
```bash
sudo systemctl stop fail2ban
sudo ufw disable
```

## Documentation

- **Full Guide**: `SERVER_SECURITY_GUIDE.md`
- **Deployment Details**: `SERVER_SECURITY_DEPLOYMENT.md`
- **Status Check**: `./check_security_status.sh`

## Summary

Your server will be protected against common attacks while allowing legitimate traffic to flow normally.

**Ready?** Run: `sudo ./deploy_server_security.sh`

---

**Questions?** Check `SERVER_SECURITY_GUIDE.md` for detailed information.
