#!/bin/bash

# Mobile Access Troubleshooting Script
# Helps diagnose and fix common mobile access issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to check Docker services
check_docker_services() {
    print_step "1. Checking Docker services status..."
    
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker is not installed or not in PATH"
        return 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running"
        return 1
    fi
    
    # Check if services are running
    local running_services=$(docker-compose ps --services --filter "status=running" | wc -l)
    local total_services=$(docker-compose ps --services | wc -l)
    
    if [ "$running_services" -eq "$total_services" ] && [ "$running_services" -gt 0 ]; then
        print_success "All Docker services are running ($running_services/$total_services)"
    else
        print_warning "Some Docker services may not be running ($running_services/$total_services)"
        print_info "Service status:"
        docker-compose ps
    fi
    
    # Check port bindings
    print_info "Checking port bindings..."
    local ports=("3000" "8000" "8080")
    for port in "${ports[@]}"; do
        if docker-compose ps | grep -q "0.0.0.0:${port}"; then
            print_success "Port $port is bound to all interfaces (0.0.0.0)"
        else
            print_error "Port $port is not properly bound for external access"
        fi
    done
}

# Function to test local connectivity
test_local_connectivity() {
    print_step "2. Testing local connectivity..."
    
    # Get HOST_IP from .env.local
    if [ -f ".env.local" ] && grep -q "HOST_IP=" ".env.local"; then
        local host_ip=$(grep "HOST_IP=" .env.local | cut -d'=' -f2)
        print_info "Using HOST_IP: $host_ip"
    else
        print_error "HOST_IP not found in .env.local"
        return 1
    fi
    
    # Test localhost access first
    print_info "Testing localhost access..."
    local ports=("3000" "8000" "8080")
    for port in "${ports[@]}"; do
        if curl -s --connect-timeout 5 "http://localhost:${port}" >/dev/null 2>&1; then
            print_success "localhost:$port is accessible"
        else
            print_warning "localhost:$port is not responding"
        fi
    done
    
    # Test host IP access
    print_info "Testing host IP access..."
    for port in "${ports[@]}"; do
        if curl -s --connect-timeout 5 "http://${host_ip}:${port}" >/dev/null 2>&1; then
            print_success "${host_ip}:$port is accessible"
        else
            print_error "${host_ip}:$port is not accessible (likely firewall)"
        fi
    done
}

# Function to check Windows Firewall
check_windows_firewall() {
    print_step "3. Checking Windows Firewall..."
    
    if command -v netsh >/dev/null 2>&1; then
        print_info "Windows Firewall status:"
        netsh advfirewall show allprofiles state 2>/dev/null || print_warning "Could not check firewall status"
        
        print_info "Checking for existing Docker rules..."
        netsh advfirewall firewall show rule name="Docker" 2>/dev/null || print_info "No Docker firewall rules found"
        
        print_info "Checking for port-specific rules..."
        local ports=("3000" "8000" "8080")
        for port in "${ports[@]}"; do
            if netsh advfirewall firewall show rule name="ABParts Port $port" 2>/dev/null | grep -q "Rule Name"; then
                print_success "Firewall rule exists for port $port"
            else
                print_warning "No firewall rule found for port $port"
            fi
        done
    else
        print_warning "Cannot check Windows Firewall from this environment"
    fi
}

# Function to provide firewall fix commands
provide_firewall_fixes() {
    print_step "4. Firewall Fix Commands"
    
    echo ""
    print_info "EASY FIX OPTIONS:"
    echo ""
    print_success "Option 1: Run the automated firewall fix (RECOMMENDED)"
    echo "  Right-click 'scripts/fix-firewall.bat' and select 'Run as administrator'"
    echo ""
    print_success "Option 2: Use PowerShell script"
    echo "  Right-click PowerShell, select 'Run as administrator', then run:"
    echo "  .\\scripts\\configure-windows-firewall.ps1"
    echo ""
    print_info "Option 3: Manual commands (run in Administrator Command Prompt):"
    echo "netsh advfirewall firewall add rule name=\"ABParts Frontend\" dir=in action=allow protocol=TCP localport=3000"
    echo "netsh advfirewall firewall add rule name=\"ABParts API\" dir=in action=allow protocol=TCP localport=8000"
    echo "netsh advfirewall firewall add rule name=\"ABParts Admin\" dir=in action=allow protocol=TCP localport=8080"
    echo ""
    print_warning "Option 4: Temporarily disable Windows Firewall for testing:"
    echo "netsh advfirewall set allprofiles state off"
    echo "# Remember to turn it back on after testing:"
    echo "netsh advfirewall set allprofiles state on"
}

# Function to test network connectivity
test_network_connectivity() {
    print_step "5. Network Connectivity Tests"
    
    # Get HOST_IP from .env.local
    if [ -f ".env.local" ] && grep -q "HOST_IP=" ".env.local"; then
        local host_ip=$(grep "HOST_IP=" .env.local | cut -d'=' -f2)
    else
        print_error "HOST_IP not found in .env.local"
        return 1
    fi
    
    print_info "Testing if ports are listening..."
    local ports=("3000" "8000" "8080")
    for port in "${ports[@]}"; do
        if netstat -an 2>/dev/null | grep -q ":${port}.*LISTENING"; then
            print_success "Port $port is listening"
        else
            print_error "Port $port is not listening"
        fi
    done
    
    print_info "Your mobile device should connect to:"
    echo "  📱 Frontend: http://${host_ip}:3000"
    echo "  🔧 API: http://${host_ip}:8000"
    echo "  📚 API Docs: http://${host_ip}:8000/docs"
    echo "  🗄️  Admin: http://${host_ip}:8080"
}

# Function to provide mobile testing steps
provide_mobile_testing_steps() {
    print_step "6. Mobile Testing Steps"
    
    # Get HOST_IP from .env.local
    if [ -f ".env.local" ] && grep -q "HOST_IP=" ".env.local"; then
        local host_ip=$(grep "HOST_IP=" .env.local | cut -d'=' -f2)
    else
        print_error "HOST_IP not found in .env.local"
        return 1
    fi
    
    echo ""
    print_info "Mobile Device Testing Checklist:"
    echo ""
    echo "1. ✅ Ensure mobile device is on the same WiFi network"
    echo "2. ✅ Try accessing the API docs first: http://${host_ip}:8000/docs"
    echo "3. ✅ If API docs work, try the frontend: http://${host_ip}:3000"
    echo "4. ✅ Check browser console for any CORS errors"
    echo "5. ✅ Try different browsers on mobile (Chrome, Safari, Firefox)"
    echo ""
    print_info "If still not working:"
    echo "• Restart Docker services: docker-compose down && docker-compose up -d"
    echo "• Check your router's client isolation settings"
    echo "• Try connecting from another device on the same network"
    echo "• Verify the IP address hasn't changed: ipconfig"
}

# Main execution
main() {
    echo ""
    print_info "=== ABParts Mobile Access Troubleshooting ==="
    echo ""
    
    check_docker_services
    echo ""
    
    test_local_connectivity
    echo ""
    
    check_windows_firewall
    echo ""
    
    provide_firewall_fixes
    echo ""
    
    test_network_connectivity
    echo ""
    
    provide_mobile_testing_steps
    echo ""
    
    print_success "Troubleshooting complete!"
    print_info "If issues persist, try the firewall commands above in an Administrator Command Prompt."
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Troubleshoot ABParts mobile access issues"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo ""
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac