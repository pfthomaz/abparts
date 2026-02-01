#!/bin/bash

# ============================================================================
# AI Assistant Configuration Validation Script
# ============================================================================
# This script validates that all required configuration is in place
# before deployment.
# ============================================================================

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
ERRORS=0
WARNINGS=0
CHECKS=0

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    CHECKS=$((CHECKS + 1))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    WARNINGS=$((WARNINGS + 1))
    CHECKS=$((CHECKS + 1))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ERRORS=$((ERRORS + 1))
    CHECKS=$((CHECKS + 1))
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Load environment file
load_environment() {
    if [ -f ".env.production" ]; then
        source .env.production
        print_success "Loaded .env.production"
    elif [ -f ".env" ]; then
        source .env
        print_warning "Using .env (production file not found)"
    else
        print_error "No environment file found"
        exit 1
    fi
}

# Check required variables
check_required_variables() {
    print_header "Checking Required Environment Variables"
    
    # Critical variables
    REQUIRED_VARS=(
        "OPENAI_API_KEY:OpenAI API key for LLM functionality"
        "DATABASE_URL:PostgreSQL database connection string"
        "REDIS_URL:Redis connection string for session storage"
    )
    
    for var_desc in "${REQUIRED_VARS[@]}"; do
        IFS=':' read -r var desc <<< "$var_desc"
        if [ -z "${!var}" ]; then
            print_error "$var is not set - $desc"
        else
            # Mask sensitive values
            if [[ $var == *"KEY"* ]] || [[ $var == *"PASSWORD"* ]]; then
                masked_value="${!var:0:10}..."
                print_success "$var is set ($masked_value)"
            else
                print_success "$var is set"
            fi
        fi
    done
}

# Check optional but recommended variables
check_optional_variables() {
    print_header "Checking Optional Environment Variables"
    
    OPTIONAL_VARS=(
        "OPENAI_MODEL:OpenAI model to use (defaults to gpt-4)"
        "OPENAI_FALLBACK_MODEL:Fallback model (defaults to gpt-3.5-turbo)"
        "CORS_ALLOWED_ORIGINS:CORS configuration for frontend"
        "SMTP_SERVER:SMTP server for escalation emails"
        "SMTP_USERNAME:SMTP username"
        "SMTP_PASSWORD:SMTP password"
        "FROM_EMAIL:From email address"
    )
    
    for var_desc in "${OPTIONAL_VARS[@]}"; do
        IFS=':' read -r var desc <<< "$var_desc"
        if [ -z "${!var}" ]; then
            print_warning "$var is not set - $desc"
        else
            if [[ $var == *"PASSWORD"* ]]; then
                print_success "$var is set"
            else
                print_success "$var is set (${!var})"
            fi
        fi
    done
}

# Validate OpenAI API key
validate_openai_key() {
    print_header "Validating OpenAI API Key"
    
    if [ -z "$OPENAI_API_KEY" ]; then
        print_error "OPENAI_API_KEY not set"
        return
    fi
    
    print_info "Testing OpenAI API connectivity..."
    
    response=$(curl -s -w "\n%{http_code}" https://api.openai.com/v1/models \
        -H "Authorization: Bearer $OPENAI_API_KEY" 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        print_success "OpenAI API key is valid"
        
        # Check if GPT-4 is available
        if echo "$body" | grep -q "gpt-4"; then
            print_success "GPT-4 access confirmed"
        else
            print_warning "GPT-4 access not detected - may need to request access"
        fi
    elif [ "$http_code" = "401" ]; then
        print_error "OpenAI API key is invalid"
    elif [ "$http_code" = "429" ]; then
        print_warning "OpenAI API rate limit reached - key is valid but quota exceeded"
    else
        print_warning "Could not validate OpenAI API key (HTTP $http_code)"
    fi
}

# Check database connectivity
check_database() {
    print_header "Checking Database Connectivity"
    
    if [ -z "$DATABASE_URL" ]; then
        print_error "DATABASE_URL not set"
        return
    fi
    
    print_info "Testing database connection..."
    
    # Extract connection details from DATABASE_URL
    # Format: postgresql://user:pass@host:port/dbname
    if [[ $DATABASE_URL =~ postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
        DB_USER="${BASH_REMATCH[1]}"
        DB_PASS="${BASH_REMATCH[2]}"
        DB_HOST="${BASH_REMATCH[3]}"
        DB_PORT="${BASH_REMATCH[4]}"
        DB_NAME="${BASH_REMATCH[5]}"
        
        # Test connection using psql if available
        if command -v psql &> /dev/null; then
            if PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" &> /dev/null; then
                print_success "Database connection successful"
                
                # Check if AI tables exist
                table_count=$(PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name LIKE 'ai_%'
                " 2>/dev/null | tr -d ' ')
                
                if [ "$table_count" -gt 0 ]; then
                    print_success "Found $table_count AI Assistant tables"
                else
                    print_warning "No AI Assistant tables found - will be created on first run"
                fi
            else
                print_error "Database connection failed"
            fi
        else
            print_warning "psql not available - skipping database connection test"
        fi
    else
        print_error "Invalid DATABASE_URL format"
    fi
}

# Check Redis connectivity
check_redis() {
    print_header "Checking Redis Connectivity"
    
    if [ -z "$REDIS_URL" ]; then
        print_error "REDIS_URL not set"
        return
    fi
    
    print_info "Testing Redis connection..."
    
    # Extract connection details from REDIS_URL
    # Format: redis://host:port/db
    if [[ $REDIS_URL =~ redis://([^:]+):([^/]+)/(.+) ]]; then
        REDIS_HOST="${BASH_REMATCH[1]}"
        REDIS_PORT="${BASH_REMATCH[2]}"
        REDIS_DB="${BASH_REMATCH[3]}"
        
        # Test connection using redis-cli if available
        if command -v redis-cli &> /dev/null; then
            if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -n "$REDIS_DB" PING &> /dev/null; then
                print_success "Redis connection successful"
            else
                print_error "Redis connection failed"
            fi
        else
            print_warning "redis-cli not available - skipping Redis connection test"
        fi
    else
        print_error "Invalid REDIS_URL format"
    fi
}

# Check SMTP configuration
check_smtp() {
    print_header "Checking SMTP Configuration"
    
    if [ -z "$SMTP_SERVER" ]; then
        print_warning "SMTP not configured - escalation emails will not work"
        return
    fi
    
    SMTP_VARS=("SMTP_SERVER" "SMTP_PORT" "SMTP_USERNAME" "SMTP_PASSWORD" "FROM_EMAIL")
    
    for var in "${SMTP_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            print_warning "$var not set"
        else
            print_success "$var is configured"
        fi
    done
    
    # Test SMTP connection if openssl is available
    if command -v openssl &> /dev/null && [ -n "$SMTP_SERVER" ] && [ -n "$SMTP_PORT" ]; then
        print_info "Testing SMTP connectivity..."
        if timeout 5 openssl s_client -connect "$SMTP_SERVER:$SMTP_PORT" -starttls smtp </dev/null 2>&1 | grep -q "CONNECTED"; then
            print_success "SMTP server is reachable"
        else
            print_warning "Could not connect to SMTP server"
        fi
    fi
}

# Check Docker setup
check_docker() {
    print_header "Checking Docker Configuration"
    
    # Check if docker-compose.prod.yml exists
    if [ -f "docker-compose.prod.yml" ]; then
        print_success "docker-compose.prod.yml found"
        
        # Check if AI Assistant service is defined
        if grep -q "ai_assistant:" docker-compose.prod.yml; then
            print_success "AI Assistant service defined in docker-compose.prod.yml"
        else
            print_error "AI Assistant service not found in docker-compose.prod.yml"
        fi
    else
        print_error "docker-compose.prod.yml not found"
    fi
    
    # Check if Dockerfile exists
    if [ -f "ai_assistant/Dockerfile" ]; then
        print_success "AI Assistant Dockerfile found"
    else
        print_error "AI Assistant Dockerfile not found"
    fi
    
    # Check if requirements.txt exists
    if [ -f "ai_assistant/requirements.txt" ]; then
        print_success "requirements.txt found"
    else
        print_error "requirements.txt not found"
    fi
}

# Check disk space
check_disk_space() {
    print_header "Checking Disk Space"
    
    available_space=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    
    if [ "$available_space" -gt 10 ]; then
        print_success "Sufficient disk space available (${available_space}GB)"
    elif [ "$available_space" -gt 5 ]; then
        print_warning "Low disk space (${available_space}GB) - recommend at least 10GB"
    else
        print_error "Insufficient disk space (${available_space}GB) - need at least 10GB"
    fi
}

# Check network connectivity
check_network() {
    print_header "Checking Network Connectivity"
    
    # Check OpenAI API
    if curl -s --max-time 5 https://api.openai.com &> /dev/null; then
        print_success "Can reach OpenAI API"
    else
        print_error "Cannot reach OpenAI API - check firewall/proxy settings"
    fi
    
    # Check if port 8001 is available
    if command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":8001 "; then
            print_warning "Port 8001 is already in use"
        else
            print_success "Port 8001 is available"
        fi
    fi
}

# Generate summary
generate_summary() {
    print_header "Validation Summary"
    
    echo "Total Checks: $CHECKS"
    echo -e "${GREEN}Passed: $((CHECKS - ERRORS - WARNINGS))${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    echo -e "${RED}Errors: $ERRORS${NC}"
    echo ""
    
    if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✅ All checks passed! Ready for deployment.${NC}"
        exit 0
    elif [ $ERRORS -eq 0 ]; then
        echo -e "${YELLOW}⚠️  Validation passed with warnings. Review warnings before deployment.${NC}"
        exit 0
    else
        echo -e "${RED}❌ Validation failed. Fix errors before deployment.${NC}"
        exit 1
    fi
}

# Main execution
main() {
    print_header "AI Assistant Configuration Validation"
    
    load_environment
    check_required_variables
    check_optional_variables
    validate_openai_key
    check_database
    check_redis
    check_smtp
    check_docker
    check_disk_space
    check_network
    generate_summary
}

main
