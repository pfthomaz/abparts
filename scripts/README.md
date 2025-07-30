# ABParts Mobile Access Scripts

This directory contains utilities for configuring ABParts to be accessible from mobile devices on your local network.

## Scripts Overview

### `detect-host-ip.sh`
Automatically detects your host machine's IP address and configures environment variables for mobile access.

**Usage:**
```bash
bash scripts/detect-host-ip.sh
```

**What it does:**
- Detects your network IP address using multiple methods
- Updates `.env.local` with `HOST_IP`, `CORS_ALLOWED_ORIGINS`, and `BASE_URL`
- Creates backups of existing configuration files
- Provides detailed output about the configuration process

### `configure-mobile-access.sh`
Complete setup script that configures and starts Docker services for mobile access.

**Usage:**
```bash
# Full setup (detect IP, configure, and start services)
bash scripts/configure-mobile-access.sh

# Only detect and configure IP (don't restart services)
bash scripts/configure-mobile-access.sh --ip-only

# Show help
bash scripts/configure-mobile-access.sh --help
```

**What it does:**
- Runs IP detection
- Stops existing Docker services
- Starts services with mobile access configuration
- Displays access URLs and setup instructions

### `test-ip-detection.sh`
Test suite to verify that IP detection is working correctly.

**Usage:**
```bash
bash scripts/test-ip-detection.sh
```

**What it tests:**
- Individual IP detection methods
- Main script functionality
- Environment configuration validity

### `troubleshoot-mobile-access.sh`
Comprehensive troubleshooting script for mobile access issues.

**Usage:**
```bash
bash scripts/troubleshoot-mobile-access.sh
```

**What it checks:**
- Docker services status and port bindings
- Local and network connectivity
- Windows Firewall configuration
- Provides specific fix commands

### `fix-firewall.bat`
Windows batch file to quickly fix firewall issues (run as Administrator).

**Usage:**
- Right-click the file and select "Run as administrator"

### `configure-windows-firewall.ps1`
PowerShell script for advanced firewall management.

**Usage:**
```powershell
# Add firewall rules (run as Administrator)
.\scripts\configure-windows-firewall.ps1

# Remove firewall rules
.\scripts\configure-windows-firewall.ps1 -Remove

# Show help
.\scripts\configure-windows-firewall.ps1 -Help
```

### `test-mobile-access.sh`
Comprehensive test suite to verify mobile access is working correctly.

**Usage:**
```bash
bash scripts/test-mobile-access.sh
```

**What it tests:**
- API accessibility from network IP
- CORS configuration for mobile origins
- Frontend accessibility
- Admin interface accessibility

## Quick Start

1. **Test IP detection:**
   ```bash
   bash scripts/test-ip-detection.sh
   ```

2. **Configure for mobile access:**
   ```bash
   bash scripts/configure-mobile-access.sh
   ```

3. **Access from mobile device:**
   - Connect your mobile device to the same WiFi network
   - Open browser and navigate to `http://YOUR_IP:3000`
   - Log in with your ABParts credentials

## Supported Platforms

- **Windows** (Git Bash, WSL)
- **Linux** (Ubuntu, CentOS, etc.)
- **macOS**

## IP Detection Methods

The scripts try multiple methods to detect your IP address, with priority given to 192.168.1.x networks for mobile access:

1. **Windows:** `ipconfig` command (prioritizes 192.168.1.x)
2. **Linux/Unix:** `hostname -I`
3. **Modern Linux:** `ip route`
4. **Fallback:** `ifconfig`
5. **WSL:** `/etc/resolv.conf` parsing
6. **PowerShell:** Windows PowerShell cmdlets (prioritizes 192.168.1.x)

## Configuration Files

### `.env.local`
Updated with the following variables:
- `HOST_IP` - Your detected network IP address
- `CORS_ALLOWED_ORIGINS` - CORS configuration including your IP
- `BASE_URL` - API base URL using your IP

### Backups
- Configuration backups are created with timestamps
- Format: `.env.local.backup.YYYYMMDD_HHMMSS`

## Troubleshooting

### IP Detection Fails
```bash
# Manually find your IP
ipconfig                    # Windows
ip addr show               # Linux
ifconfig                   # macOS/older Linux

# Set manually
export HOST_IP=192.168.1.100
echo "HOST_IP=192.168.1.100" >> .env.local
```

### Mobile Access Not Working

**Quick Diagnosis:**
```bash
bash scripts/troubleshoot-mobile-access.sh
```

**Common Fixes:**

1. **Windows Firewall (Most Common Issue):**
   - **Easy Fix:** Right-click `scripts/fix-firewall.bat` and "Run as administrator"
   - **PowerShell:** Run `.\scripts\configure-windows-firewall.ps1` as Administrator
   - **Manual:** Add firewall rules for ports 3000, 8000, 8080

2. **Network Issues:**
   - Verify mobile device is on same WiFi network
   - Test API docs first: `http://YOUR_IP:8000/docs`
   - Check if IP address changed: `ipconfig`

3. **Docker Issues:**
   - Restart services: `docker-compose down && docker-compose up -d`
   - Verify services running: `docker-compose ps`

### CORS Errors
- Verify `CORS_ALLOWED_ORIGINS` includes your IP address
- Restart Docker services after configuration changes
- Check browser console for specific CORS error messages

## Security Notes

- Services become accessible to all devices on your local network
- Ensure you're on a trusted network (home/office WiFi)
- Authentication is still required for application access
- Consider using VPN for remote access scenarios

## Integration with Docker Compose

The scripts work with your existing `docker-compose.yml` by:
- Using environment variables from `.env.local`
- Configuring CORS origins dynamically
- Setting appropriate base URLs for mobile access

No changes to `docker-compose.yml` are required - everything is handled through environment variables.