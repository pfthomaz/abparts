#!/bin/bash

# Mobile Access Configuration Helper
# Configures ABParts Docker services for mobile device access

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

# Function to check if Docker is running
check_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    print_success "Docker is running"
}

# Function to check if docker-compose is available
check_docker_compose() {
    if command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    else
        print_error "Neither docker-compose nor 'docker compose' is available"
        exit 1
    fi
    
    print_success "Using: $COMPOSE_CMD"
}

# Function to stop existing services
stop_services() {
    print_info "Stopping existing Docker services..."
    
    if $COMPOSE_CMD ps -q | grep -q .; then
        $COMPOSE_CMD down
        print_success "Stopped existing services"
    else
        print_info "No running services found"
    fi
}

# Function to start services with mobile access
start_services() {
    print_info "Starting Docker services with mobile access configuration..."
    
    # Start services in detached mode
    $COMPOSE_CMD up -d
    
    print_success "Services started successfully"
    
    # Wait a moment for services to initialize
    sleep 3
    
    # Check service health
    print_info "Checking service status..."
    $COMPOSE_CMD ps
}

# Function to display final instructions
display_instructions() {
    local host_ip=$1
    
    echo ""
    print_success "=== Mobile Access Setup Complete ==="
    echo ""
    print_info "Services are now accessible from mobile devices at:"
    echo "  📱 Frontend:          http://${host_ip}:3000"
    echo "  🔧 API:               http://${host_ip}:8000"
    echo "  📚 API Docs:          http://${host_ip}:8000/docs"
    echo "  🗄️  Database Admin:    http://${host_ip}:8080"
    echo ""
    print_info "Mobile Setup Instructions:"
    echo "  1. Connect your mobile device to the same WiFi network"
    echo "  2. Open a web browser on your mobile device"
    echo "  3. Navigate to: http://${host_ip}:3000"
    echo "  4. Log in with your ABParts credentials"
    echo ""
    print_warning "Troubleshooting:"
    echo "  • If mobile access doesn't work, check your firewall settings"
    echo "  • Ensure your mobile device is on the same network"
    echo "  • Try accessing http://${host_ip}:8000/docs first to test API connectivity"
    echo ""
    print_info "To stop services: $COMPOSE_CMD down"
    print_info "To view logs: $COMPOSE_CMD logs -f"
    echo ""
}

# Main execution
main() {
    echo ""
    print_info "=== ABParts Mobile Access Setup ==="
    echo ""
    
    # Check prerequisites
    check_docker
    check_docker_compose
    
    # Run IP detection
    print_info "Running IP detection..."
    if [ -f "scripts/detect-host-ip.sh" ]; then
        bash scripts/detect-host-ip.sh
    else
        print_error "IP detection script not found at scripts/detect-host-ip.sh"
        exit 1
    fi
    
    # Source the HOST_IP from .env.local
    if [ -f ".env.local" ] && grep -q "^HOST_IP=" ".env.local"; then
        HOST_IP=$(grep "^HOST_IP=" .env.local | cut -d'=' -f2)
        print_success "Using detected IP: $HOST_IP"
    else
        print_error "Could not find HOST_IP in .env.local"
        exit 1
    fi
    
    # Stop existing services
    stop_services
    
    # Start services with new configuration
    start_services
    
    # Display final instructions
    display_instructions "$HOST_IP"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Configure ABParts for mobile device access"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --ip-only      Only detect and configure IP, don't restart services"
        echo ""
        exit 0
        ;;
    --ip-only)
        print_info "Running IP detection only..."
        bash scripts/detect-host-ip.sh
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac