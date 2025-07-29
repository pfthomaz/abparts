#!/bin/bash

# Test script for IP detection functionality
# Validates that the IP detection utility works correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Function to validate IP address format
validate_ip() {
    local ip=$1
    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        # Check each octet is between 0-255
        IFS='.' read -ra ADDR <<< "$ip"
        for i in "${ADDR[@]}"; do
            if [[ $i -gt 255 ]]; then
                return 1
            fi
        done
        return 0
    else
        return 1
    fi
}

# Test IP detection methods individually
test_ip_detection_methods() {
    print_info "Testing individual IP detection methods..."
    
    local methods_tested=0
    local methods_successful=0
    
    # Test ipconfig (Windows) - prioritize 192.168.1.x
    if command -v ipconfig >/dev/null 2>&1; then
        methods_tested=$((methods_tested + 1))
        # Try 192.168.1.x first
        local ip=$(ipconfig | grep -E "IPv4.*192\.168\.1\." | head -1 | sed 's/.*: //' | tr -d '\r')
        if [ -z "$ip" ]; then
            # Fallback to other networks
            ip=$(ipconfig | grep -E "IPv4.*192\.168\.|IPv4.*10\." | head -1 | sed 's/.*: //' | tr -d '\r')
        fi
        if [ -n "$ip" ] && validate_ip "$ip"; then
            print_success "ipconfig: $ip"
            methods_successful=$((methods_successful + 1))
        else
            print_error "ipconfig: failed or invalid IP"
        fi
    fi
    
    # Test hostname -I
    if command -v hostname >/dev/null 2>&1; then
        methods_tested=$((methods_tested + 1))
        local ip=$(hostname -I 2>/dev/null | awk '{print $1}' | head -1)
        if [ -n "$ip" ] && validate_ip "$ip"; then
            print_success "hostname -I: $ip"
            methods_successful=$((methods_successful + 1))
        else
            print_error "hostname -I: failed or invalid IP"
        fi
    fi
    
    # Test ip route
    if command -v ip >/dev/null 2>&1; then
        methods_tested=$((methods_tested + 1))
        local ip=$(ip route get 8.8.8.8 2>/dev/null | grep -oP 'src \K\S+' | head -1)
        if [ -n "$ip" ] && validate_ip "$ip"; then
            print_success "ip route: $ip"
            methods_successful=$((methods_successful + 1))
        else
            print_error "ip route: failed or invalid IP"
        fi
    fi
    
    # Test ifconfig
    if command -v ifconfig >/dev/null 2>&1; then
        methods_tested=$((methods_tested + 1))
        local ip=$(ifconfig 2>/dev/null | grep -E 'inet [0-9]' | grep -v '127.0.0.1' | awk '{print $2}' | head -1 | sed 's/addr://')
        if [ -n "$ip" ] && validate_ip "$ip"; then
            print_success "ifconfig: $ip"
            methods_successful=$((methods_successful + 1))
        else
            print_error "ifconfig: failed or invalid IP"
        fi
    fi
    
    print_info "IP detection methods: $methods_successful/$methods_tested successful"
    
    if [ $methods_successful -eq 0 ]; then
        print_error "No IP detection methods worked"
        return 1
    fi
    
    return 0
}

# Test the main IP detection script
test_main_script() {
    print_info "Testing main IP detection script..."
    
    if [ ! -f "scripts/detect-host-ip.sh" ]; then
        print_error "Main script not found: scripts/detect-host-ip.sh"
        return 1
    fi
    
    # Create a temporary .env.local backup if it exists
    if [ -f ".env.local" ]; then
        cp ".env.local" ".env.local.test.backup"
    fi
    
    # Run the script in test mode (capture output)
    if bash scripts/detect-host-ip.sh > /tmp/ip_test_output.log 2>&1; then
        print_success "Main script executed successfully"
        
        # Check if HOST_IP was set in .env.local
        if [ -f ".env.local" ] && grep -q "^HOST_IP=" ".env.local"; then
            local detected_ip=$(grep "^HOST_IP=" .env.local | cut -d'=' -f2)
            if validate_ip "$detected_ip"; then
                print_success "Valid IP detected and saved: $detected_ip"
            else
                print_error "Invalid IP saved to .env.local: $detected_ip"
                return 1
            fi
        else
            print_error "HOST_IP not found in .env.local after script execution"
            return 1
        fi
    else
        print_error "Main script failed to execute"
        cat /tmp/ip_test_output.log
        return 1
    fi
    
    # Restore backup if it existed
    if [ -f ".env.local.test.backup" ]; then
        mv ".env.local.test.backup" ".env.local"
    fi
    
    return 0
}

# Test environment configuration
test_env_configuration() {
    print_info "Testing environment configuration..."
    
    if [ ! -f ".env.local" ]; then
        print_error ".env.local file not found"
        return 1
    fi
    
    # Check required variables (HOST_IP might be at the end of the file)
    local required_vars=("HOST_IP" "CORS_ALLOWED_ORIGINS")
    local missing_vars=0
    
    for var in "${required_vars[@]}"; do
        if grep -q "${var}=" ".env.local"; then
            print_success "$var is configured"
        else
            print_error "$var is missing from .env.local"
            missing_vars=$((missing_vars + 1))
        fi
    done
    
    if [ $missing_vars -gt 0 ]; then
        return 1
    fi
    
    return 0
}

# Main test execution
main() {
    echo ""
    print_info "=== IP Detection Utility Test Suite ==="
    echo ""
    
    local tests_passed=0
    local tests_total=3
    
    # Test 1: Individual IP detection methods
    if test_ip_detection_methods; then
        tests_passed=$((tests_passed + 1))
    fi
    echo ""
    
    # Test 2: Main script functionality
    if test_main_script; then
        tests_passed=$((tests_passed + 1))
    fi
    echo ""
    
    # Test 3: Environment configuration
    if test_env_configuration; then
        tests_passed=$((tests_passed + 1))
    fi
    echo ""
    
    # Summary
    print_info "=== Test Results ==="
    print_info "Tests passed: $tests_passed/$tests_total"
    
    if [ $tests_passed -eq $tests_total ]; then
        print_success "All tests passed! IP detection utility is working correctly."
        echo ""
        print_info "You can now run: bash scripts/configure-mobile-access.sh"
        return 0
    else
        print_error "Some tests failed. Please check the output above."
        return 1
    fi
}

# Clean up function
cleanup() {
    rm -f /tmp/ip_test_output.log
    rm -f .env.local.test.backup
}

# Set up cleanup trap
trap cleanup EXIT

# Run main function
main "$@"