#!/bin/bash

# Test Mobile Access Script
# Verifies that mobile access is working correctly

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

# Get HOST_IP from environment
get_host_ip() {
    local host_ip=""
    
    # Try .env first (Docker Compose default)
    if [ -f ".env" ] && grep -q "HOST_IP=" ".env"; then
        host_ip=$(grep "HOST_IP=" .env | cut -d'=' -f2)
    fi
    
    # Fallback to .env.local
    if [ -z "$host_ip" ] && [ -f ".env.local" ] && grep -q "HOST_IP=" ".env.local"; then
        host_ip=$(grep "HOST_IP=" .env.local | cut -d'=' -f2)
    fi
    
    echo "$host_ip"
}

# Test API accessibility
test_api_access() {
    local host_ip=$1
    local url="http://${host_ip}:8000"
    
    print_info "Testing API access at $url"
    
    if curl -s --connect-timeout 5 "$url/docs" >/dev/null 2>&1; then
        print_success "API is accessible at $url"
        return 0
    else
        print_error "API is not accessible at $url"
        return 1
    fi
}

# Test CORS configuration
test_cors() {
    local host_ip=$1
    local api_url="http://${host_ip}:8000"
    local origin="http://${host_ip}:3000"
    
    print_info "Testing CORS for origin $origin"
    
    # Test CORS preflight request
    local cors_response=$(curl -s -H "Origin: $origin" -H "Access-Control-Request-Method: GET" -X OPTIONS "$api_url/" -I 2>/dev/null)
    
    if echo "$cors_response" | grep -q "access-control-allow-origin: $origin"; then
        print_success "CORS is configured correctly for $origin"
        return 0
    else
        print_error "CORS is not configured for $origin"
        print_info "CORS response headers:"
        echo "$cors_response" | grep -i "access-control" || echo "No CORS headers found"
        return 1
    fi
}

# Test frontend accessibility
test_frontend_access() {
    local host_ip=$1
    local url="http://${host_ip}:3000"
    
    print_info "Testing frontend access at $url"
    
    if curl -s --connect-timeout 5 "$url" >/dev/null 2>&1; then
        print_success "Frontend is accessible at $url"
        return 0
    else
        print_error "Frontend is not accessible at $url"
        return 1
    fi
}

# Test admin interface accessibility
test_admin_access() {
    local host_ip=$1
    local url="http://${host_ip}:8080"
    
    print_info "Testing admin interface at $url"
    
    if curl -s --connect-timeout 5 "$url" >/dev/null 2>&1; then
        print_success "Admin interface is accessible at $url"
        return 0
    else
        print_error "Admin interface is not accessible at $url"
        return 1
    fi
}

# Main execution
main() {
    echo ""
    print_info "=== ABParts Mobile Access Test ==="
    echo ""
    
    # Get host IP
    HOST_IP=$(get_host_ip)
    if [ -z "$HOST_IP" ]; then
        print_error "Could not find HOST_IP in environment files"
        print_info "Run: bash scripts/detect-host-ip.sh"
        exit 1
    fi
    
    print_info "Testing mobile access for IP: $HOST_IP"
    echo ""
    
    local tests_passed=0
    local tests_total=4
    
    # Test API access
    if test_api_access "$HOST_IP"; then
        tests_passed=$((tests_passed + 1))
    fi
    echo ""
    
    # Test CORS
    if test_cors "$HOST_IP"; then
        tests_passed=$((tests_passed + 1))
    fi
    echo ""
    
    # Test frontend access
    if test_frontend_access "$HOST_IP"; then
        tests_passed=$((tests_passed + 1))
    fi
    echo ""
    
    # Test admin access
    if test_admin_access "$HOST_IP"; then
        tests_passed=$((tests_passed + 1))
    fi
    echo ""
    
    # Summary
    print_info "=== Test Results ==="
    print_info "Tests passed: $tests_passed/$tests_total"
    
    if [ $tests_passed -eq $tests_total ]; then
        print_success "All tests passed! Mobile access is working correctly."
        echo ""
        print_info "Mobile Access URLs:"
        echo "  📱 Frontend: http://$HOST_IP:3000"
        echo "  🔧 API: http://$HOST_IP:8000"
        echo "  📚 API Docs: http://$HOST_IP:8000/docs"
        echo "  🗄️ Admin: http://$HOST_IP:8080"
        echo ""
        print_info "Connect your mobile device to the same WiFi network and access these URLs."
        return 0
    else
        print_error "Some tests failed. Mobile access may not work correctly."
        print_info "Try running: bash scripts/troubleshoot-mobile-access.sh"
        return 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Test ABParts mobile access functionality"
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