#!/bin/bash

# Network IP Detection Utility for Docker Services
# Detects the host machine's IP address for mobile access configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to detect IP on different platforms
detect_ip() {
    local ip=""
    
    # Method 1: Windows ipconfig (works in Git Bash)
    if command -v ipconfig >/dev/null 2>&1; then
        # Prioritize 192.168.1.x network for mobile access
        ip=$(ipconfig | grep -E "IPv4.*192\.168\.1\." | head -1 | sed 's/.*: //' | tr -d '\r')
        if [ -n "$ip" ]; then
            print_info "Found IP using ipconfig (192.168.1.x priority): $ip" >&2
        else
            # Fallback to other 192.168.x.x or 10.x.x.x networks
            ip=$(ipconfig | grep -E "IPv4.*192\.168\.|IPv4.*10\." | head -1 | sed 's/.*: //' | tr -d '\r')
            if [ -n "$ip" ]; then
                print_info "Found IP using ipconfig (fallback): $ip" >&2
            fi
        fi
    fi
    
    # Method 2: hostname -I (Linux/Unix)
    if [ -z "$ip" ] && command -v hostname >/dev/null 2>&1; then
        ip=$(hostname -I 2>/dev/null | awk '{print $1}' | head -1)
        if [ -n "$ip" ]; then
            print_info "Found IP using hostname -I: $ip" >&2
        fi
    fi
    
    # Method 3: ip route (Modern Linux)
    if [ -z "$ip" ] && command -v ip >/dev/null 2>&1; then
        ip=$(ip route get 8.8.8.8 2>/dev/null | grep -oP 'src \K\S+' | head -1)
        if [ -n "$ip" ]; then
            print_info "Found IP using ip route: $ip" >&2
        fi
    fi
    
    # Method 4: ifconfig fallback
    if [ -z "$ip" ] && command -v ifconfig >/dev/null 2>&1; then
        ip=$(ifconfig 2>/dev/null | grep -E 'inet [0-9]' | grep -v '127.0.0.1' | awk '{print $2}' | head -1 | sed 's/addr://')
        if [ -n "$ip" ]; then
            print_info "Found IP using ifconfig: $ip" >&2
        fi
    fi
    
    # Method 5: Windows WSL detection
    if [ -z "$ip" ] && [ -n "$WSL_DISTRO_NAME" ]; then
        ip=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}' | head -1)
        if [ -n "$ip" ]; then
            print_info "Found IP using WSL method: $ip" >&2
        fi
    fi
    
    # Method 6: Alternative Windows method using powershell
    if [ -z "$ip" ] && command -v powershell.exe >/dev/null 2>&1; then
        # Try 192.168.1.x first
        ip=$(powershell.exe -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like '192.168.1.*'} | Select-Object -First 1 -ExpandProperty IPAddress" 2>/dev/null | tr -d '\r')
        if [ -n "$ip" ]; then
            print_info "Found IP using PowerShell (192.168.1.x priority): $ip" >&2
        else
            # Fallback to other networks
            ip=$(powershell.exe -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like '192.168.*' -or $_.IPAddress -like '10.*'} | Select-Object -First 1 -ExpandProperty IPAddress" 2>/dev/null | tr -d '\r')
            if [ -n "$ip" ]; then
                print_info "Found IP using PowerShell (fallback): $ip" >&2
            fi
        fi
    fi
    
    echo "$ip"
}

# Function to validate IP address format
validate_ip() {
    local ip=$1
    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to update environment configuration
update_env_config() {
    local host_ip=$1
    
    print_info "Updating environment configuration..."
    
    # Update both .env and .env.local files
    local env_files=(".env" ".env.local")
    
    for env_file in "${env_files[@]}"; do
        if [ -f "$env_file" ]; then
            # Create backup if file exists
            cp "$env_file" "${env_file}.backup.$(date +%Y%m%d_%H%M%S)"
            print_info "Created backup of existing $env_file"
            
            # Update or add HOST_IP
            if grep -q "^HOST_IP=" "$env_file"; then
                sed -i.tmp "s/^HOST_IP=.*/HOST_IP=$host_ip/" "$env_file" && rm -f "${env_file}.tmp"
                print_success "Updated HOST_IP in $env_file"
            else
                echo "HOST_IP=$host_ip" >> "$env_file"
                print_success "Added HOST_IP to $env_file"
            fi
            
            # Update CORS configuration to include the new IP (preserve existing origins)
            local cors_origins="http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,http://${host_ip}:3000,http://${host_ip}:8000"
            if grep -q "^CORS_ALLOWED_ORIGINS=" "$env_file"; then
                sed -i.tmp "s|^CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=$cors_origins|" "$env_file" && rm -f "${env_file}.tmp"
                print_success "Updated CORS_ALLOWED_ORIGINS in $env_file"
            else
                echo "CORS_ALLOWED_ORIGINS=$cors_origins" >> "$env_file"
                print_success "Added CORS_ALLOWED_ORIGINS to $env_file"
            fi
            
            # Update REACT_APP_API_BASE_URL for mobile access
            local react_api_url="http://${host_ip}:8000"
            if grep -q "^REACT_APP_API_BASE_URL=" "$env_file"; then
                sed -i.tmp "s|^REACT_APP_API_BASE_URL=.*|REACT_APP_API_BASE_URL=$react_api_url|" "$env_file" && rm -f "${env_file}.tmp"
                print_success "Updated REACT_APP_API_BASE_URL in $env_file"
            else
                echo "REACT_APP_API_BASE_URL=$react_api_url" >> "$env_file"
                print_success "Added REACT_APP_API_BASE_URL to $env_file"
            fi
        fi
    done
}

# Function to display mobile access information
display_access_info() {
    local host_ip=$1
    
    echo ""
    print_success "=== Mobile Access Configuration Complete ==="
    echo ""
    print_info "Your services will be accessible at:"
    echo "  Frontend (React):     http://${host_ip}:3000"
    echo "  Backend API:          http://${host_ip}:8000"
    echo "  API Documentation:    http://${host_ip}:8000/docs"
    echo "  Database Admin:       http://${host_ip}:8080"
    echo ""
    print_info "Next steps:"
    echo "  1. Restart your Docker services: docker-compose down && docker-compose up"
    echo "  2. Connect your mobile device to the same WiFi network"
    echo "  3. Open your mobile browser and navigate to http://${host_ip}:3000"
    echo ""
    print_warning "Security Note: Services are now accessible to all devices on your local network"
    echo ""
}

# Function to test network connectivity
test_connectivity() {
    local host_ip=$1
    
    print_info "Testing network connectivity..."
    
    # Test if we can bind to the IP (basic check)
    if command -v nc >/dev/null 2>&1; then
        if nc -z "$host_ip" 22 2>/dev/null || nc -z "$host_ip" 80 2>/dev/null; then
            print_success "Network connectivity test passed"
        else
            print_warning "Could not verify network connectivity - this may be normal"
        fi
    else
        print_info "netcat not available - skipping connectivity test"
    fi
}

# Main execution
main() {
    echo ""
    print_info "=== ABParts Mobile Access Configuration ==="
    echo ""
    
    print_info "Detecting host machine IP address..."
    
    HOST_IP=$(detect_ip)
    
    if [ -z "$HOST_IP" ]; then
        print_error "Could not detect host IP address automatically"
        echo ""
        print_info "Manual detection options:"
        echo "  1. Run 'ip addr show' or 'ifconfig' to find your network interface IP"
        echo "  2. Check your router's admin panel for connected devices"
        echo "  3. Use 'hostname -I' on Linux systems"
        echo ""
        print_info "Once you find your IP, set it manually:"
        echo "  export HOST_IP=YOUR_IP_ADDRESS"
        echo "  echo 'HOST_IP=YOUR_IP_ADDRESS' >> .env.local"
        exit 1
    fi
    
    if ! validate_ip "$HOST_IP"; then
        print_error "Detected IP address '$HOST_IP' is not valid"
        print_info "Please check your network configuration"
        exit 1
    fi
    
    print_success "Detected Host IP: $HOST_IP"
    
    # Export for use in other scripts
    export HOST_IP
    
    # Update environment configuration
    update_env_config "$HOST_IP"
    
    # Test connectivity
    test_connectivity "$HOST_IP"
    
    # Display access information
    display_access_info "$HOST_IP"
}

# Run main function
main "$@"