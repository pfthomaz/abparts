#!/bin/bash

# ============================================================================
# AutoBoss AI Assistant - Production Deployment Script
# ============================================================================
# This script handles the complete deployment of the AI Assistant service
# to production, including health checks, monitoring setup, and verification.
#
# Usage: ./deploy_production.sh [options]
# Options:
#   --skip-backup    Skip backup creation
#   --skip-tests     Skip health checks
#   --force          Force deployment even if checks fail
# ============================================================================

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
SERVICE_NAME="ai_assistant"
BACKUP_DIR="backups/ai_assistant_$(date +%Y%m%d_%H%M%S)"
LOG_DIR="logs/ai_assistant"

# Parse command line arguments
SKIP_BACKUP=false
SKIP_TESTS=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker is installed"
    
    # Check if docker-compose is available
    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available"
        exit 1
    fi
    print_success "Docker Compose is available"
    
    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    print_success "Compose file found: $COMPOSE_FILE"
    
    # Check if .env.production exists
    if [ ! -f ".env.production" ]; then
        print_warning ".env.production not found, using .env"
        if [ ! -f ".env" ]; then
            print_error "No environment file found"
            exit 1
        fi
    else
        print_success "Environment file found"
    fi
}

# Validate environment variables
validate_environment() {
    print_header "Validating Environment Variables"
    
    # Source environment file
    if [ -f ".env.production" ]; then
        source .env.production
    else
        source .env
    fi
    
    # Check required variables
    REQUIRED_VARS=(
        "OPENAI_API_KEY"
        "DATABASE_URL"
        "REDIS_URL"
    )
    
    MISSING_VARS=()
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            MISSING_VARS+=("$var")
            print_error "Missing required variable: $var"
        else
            print_success "$var is set"
        fi
    done
    
    if [ ${#MISSING_VARS[@]} -gt 0 ] && [ "$FORCE" = false ]; then
        print_error "Missing required environment variables. Use --force to override."
        exit 1
    fi
    
    # Check optional but recommended variables
    OPTIONAL_VARS=(
        "OPENAI_MODEL"
        "CORS_ALLOWED_ORIGINS"
        "SMTP_SERVER"
        "SMTP_USERNAME"
    )
    
    for var in "${OPTIONAL_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            print_warning "Optional variable not set: $var"
        else
            print_success "$var is set"
        fi
    done
}

# Create backup
create_backup() {
    if [ "$SKIP_BACKUP" = true ]; then
        print_info "Skipping backup (--skip-backup flag)"
        return
    fi
    
    print_header "Creating Backup"
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup docker-compose file
    if [ -f "$COMPOSE_FILE" ]; then
        cp "$COMPOSE_FILE" "$BACKUP_DIR/"
        print_success "Backed up $COMPOSE_FILE"
    fi
    
    # Backup environment file
    if [ -f ".env.production" ]; then
        cp ".env.production" "$BACKUP_DIR/"
        print_success "Backed up .env.production"
    fi
    
    # Backup AI Assistant code
    if [ -d "ai_assistant" ]; then
        tar -czf "$BACKUP_DIR/ai_assistant_code.tar.gz" ai_assistant/
        print_success "Backed up AI Assistant code"
    fi
    
    print_success "Backup created at: $BACKUP_DIR"
}

# Build AI Assistant image
build_service() {
    print_header "Building AI Assistant Service"
    
    print_info "Building Docker image..."
    if docker compose -f "$COMPOSE_FILE" build "$SERVICE_NAME"; then
        print_success "AI Assistant image built successfully"
    else
        print_error "Failed to build AI Assistant image"
        exit 1
    fi
}

# Stop existing service
stop_service() {
    print_header "Stopping Existing Service"
    
    if docker compose -f "$COMPOSE_FILE" ps | grep -q "$SERVICE_NAME"; then
        print_info "Stopping $SERVICE_NAME..."
        docker compose -f "$COMPOSE_FILE" stop "$SERVICE_NAME"
        print_success "Service stopped"
    else
        print_info "Service is not running"
    fi
}

# Start service
start_service() {
    print_header "Starting AI Assistant Service"
    
    print_info "Starting $SERVICE_NAME..."
    if docker compose -f "$COMPOSE_FILE" up -d "$SERVICE_NAME"; then
        print_success "Service started"
    else
        print_error "Failed to start service"
        exit 1
    fi
    
    # Wait for service to be ready
    print_info "Waiting for service to be ready..."
    sleep 10
}

# Run health checks
run_health_checks() {
    if [ "$SKIP_TESTS" = true ]; then
        print_info "Skipping health checks (--skip-tests flag)"
        return
    fi
    
    print_header "Running Health Checks"
    
    # Check if container is running
    if docker compose -f "$COMPOSE_FILE" ps | grep -q "$SERVICE_NAME.*Up"; then
        print_success "Container is running"
    else
        print_error "Container is not running"
        docker compose -f "$COMPOSE_FILE" logs --tail=50 "$SERVICE_NAME"
        exit 1
    fi
    
    # Check health endpoint
    print_info "Testing health endpoint..."
    MAX_RETRIES=5
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -f -s http://localhost:8001/health > /dev/null 2>&1; then
            print_success "Health endpoint is responding"
            break
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                print_warning "Health check failed, retrying... ($RETRY_COUNT/$MAX_RETRIES)"
                sleep 5
            else
                print_error "Health endpoint is not responding after $MAX_RETRIES attempts"
                if [ "$FORCE" = false ]; then
                    exit 1
                fi
            fi
        fi
    done
    
    # Check info endpoint
    print_info "Testing info endpoint..."
    if curl -f -s http://localhost:8001/info > /dev/null 2>&1; then
        print_success "Info endpoint is responding"
    else
        print_warning "Info endpoint is not responding"
    fi
    
    # Check database connectivity
    print_info "Checking database connectivity..."
    if docker compose -f "$COMPOSE_FILE" exec -T "$SERVICE_NAME" python -c "
from app.database import engine
try:
    with engine.connect() as conn:
        print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
" 2>&1 | grep -q "successful"; then
        print_success "Database connection is working"
    else
        print_warning "Database connection check failed"
    fi
    
    # Check Redis connectivity
    print_info "Checking Redis connectivity..."
    if docker compose -f "$COMPOSE_FILE" exec -T "$SERVICE_NAME" python -c "
from app.session_manager import session_manager
import asyncio
try:
    asyncio.run(session_manager.initialize())
    print('Redis connection successful')
except Exception as e:
    print(f'Redis connection failed: {e}')
    exit(1)
" 2>&1 | grep -q "successful"; then
        print_success "Redis connection is working"
    else
        print_warning "Redis connection check failed"
    fi
}

# Setup monitoring
setup_monitoring() {
    print_header "Setting Up Monitoring"
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    print_success "Log directory created: $LOG_DIR"
    
    # Create monitoring script
    cat > "$LOG_DIR/monitor.sh" << 'EOF'
#!/bin/bash
# AI Assistant Monitoring Script
# Run this script to monitor the AI Assistant service

COMPOSE_FILE="docker-compose.prod.yml"
SERVICE_NAME="ai_assistant"

echo "=== AI Assistant Service Monitor ==="
echo ""

# Check service status
echo "Service Status:"
docker compose -f "$COMPOSE_FILE" ps "$SERVICE_NAME"
echo ""

# Check health endpoint
echo "Health Check:"
curl -s http://localhost:8001/health | jq '.' || echo "Health endpoint not responding"
echo ""

# Check recent logs
echo "Recent Logs (last 20 lines):"
docker compose -f "$COMPOSE_FILE" logs --tail=20 "$SERVICE_NAME"
echo ""

# Check resource usage
echo "Resource Usage:"
docker stats "$SERVICE_NAME" --no-stream
echo ""

# Check OpenAI API connectivity
echo "OpenAI API Check:"
docker compose -f "$COMPOSE_FILE" exec -T "$SERVICE_NAME" python -c "
from app.llm_client import LLMClient
import asyncio
async def test():
    client = LLMClient()
    await client.initialize()
    print('OpenAI API: Connected')
asyncio.run(test())
" 2>&1 || echo "OpenAI API: Not responding"
EOF
    
    chmod +x "$LOG_DIR/monitor.sh"
    print_success "Monitoring script created: $LOG_DIR/monitor.sh"
    
    # Create log rotation config
    cat > "$LOG_DIR/logrotate.conf" << EOF
$LOG_DIR/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF
    
    print_success "Log rotation config created: $LOG_DIR/logrotate.conf"
}

# Display deployment summary
display_summary() {
    print_header "Deployment Summary"
    
    echo -e "${GREEN}✅ AI Assistant has been successfully deployed!${NC}\n"
    
    echo "Service Information:"
    echo "  - Service Name: $SERVICE_NAME"
    echo "  - Health Endpoint: http://localhost:8001/health"
    echo "  - Info Endpoint: http://localhost:8001/info"
    echo "  - Admin Interface: http://localhost:8001/admin"
    echo "  - Analytics Dashboard: http://localhost:8001/analytics"
    echo ""
    
    echo "Useful Commands:"
    echo "  - View logs: docker compose -f $COMPOSE_FILE logs -f $SERVICE_NAME"
    echo "  - Restart service: docker compose -f $COMPOSE_FILE restart $SERVICE_NAME"
    echo "  - Stop service: docker compose -f $COMPOSE_FILE stop $SERVICE_NAME"
    echo "  - Monitor service: $LOG_DIR/monitor.sh"
    echo ""
    
    echo "Next Steps:"
    echo "  1. Test the AI Assistant in the web interface"
    echo "  2. Upload AutoBoss manuals to the knowledge base (http://localhost:8001/admin)"
    echo "  3. Configure monitoring and alerting"
    echo "  4. Review logs for any warnings or errors"
    echo ""
    
    if [ -d "$BACKUP_DIR" ]; then
        echo "Backup Location: $BACKUP_DIR"
        echo ""
    fi
    
    print_info "For troubleshooting, check: $LOG_DIR/monitor.sh"
}

# Main deployment flow
main() {
    print_header "AutoBoss AI Assistant - Production Deployment"
    
    check_prerequisites
    validate_environment
    create_backup
    build_service
    stop_service
    start_service
    run_health_checks
    setup_monitoring
    display_summary
    
    print_success "Deployment completed successfully!"
}

# Run main function
main
