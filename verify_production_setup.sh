#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "Production Setup Verification"
echo "========================================="
echo ""

# Function to check status
check_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        return 0
    else
        echo -e "${RED}✗${NC} $2"
        return 1
    fi
}

# Function to check warning
check_warning() {
    if [ $1 -eq 0 ]; then
        echo -e "${YELLOW}⚠${NC} $2"
        return 0
    else
        echo -e "${GREEN}✓${NC} $2"
        return 1
    fi
}

ISSUES=0

# 1. Check .env file
echo -e "${BLUE}1. Environment Configuration${NC}"
if [ -f .env ]; then
    check_status 0 ".env file exists"
    
    # Check CORS
    if grep -q "^CORS_ALLOWED_ORIGINS=https://" .env; then
        check_status 0 "CORS_ALLOWED_ORIGINS set to HTTPS"
    else
        check_status 1 "CORS_ALLOWED_ORIGINS not set to HTTPS"
        ISSUES=$((ISSUES + 1))
    fi
    
    # Check ENVIRONMENT
    if grep -q "^ENVIRONMENT=production" .env; then
        check_status 0 "ENVIRONMENT set to production"
    else
        check_warning 0 "ENVIRONMENT not set to production"
    fi
    
    # Check SECRET_KEY
    if grep -q "^SECRET_KEY=.\{20,\}" .env; then
        check_status 0 "SECRET_KEY is set"
    else
        check_status 1 "SECRET_KEY is missing or too short"
        ISSUES=$((ISSUES + 1))
    fi
else
    check_status 1 ".env file not found"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# 2. Check Docker Compose
echo -e "${BLUE}2. Docker Compose Configuration${NC}"
if [ -f docker-compose.prod.yml ]; then
    check_status 0 "docker-compose.prod.yml exists"
    
    # Check web service
    if grep -q "web:" docker-compose.prod.yml; then
        check_status 0 "Web service configured"
    else
        check_status 1 "Web service not found"
        ISSUES=$((ISSUES + 1))
    fi
    
    # Check restart policy
    if grep -A 10 "web:" docker-compose.prod.yml | grep -q "restart: unless-stopped"; then
        check_status 0 "Web service has restart policy"
    else
        check_status 1 "Web service missing restart policy"
        ISSUES=$((ISSUES + 1))
    fi
else
    check_status 1 "docker-compose.prod.yml not found"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# 3. Check Running Containers
echo -e "${BLUE}3. Running Services${NC}"
if command -v docker &> /dev/null; then
    # Check if containers are running
    if docker compose ps | grep -q "Up"; then
        check_status 0 "Docker Compose services are running"
        
        # Check individual services
        for service in db redis api web celery_worker; do
            if docker compose ps | grep -q "${service}.*Up"; then
                check_status 0 "$service is running"
            else
                check_status 1 "$service is not running"
                ISSUES=$((ISSUES + 1))
            fi
        done
    else
        check_warning 0 "No services are currently running"
    fi
else
    check_status 1 "Docker is not installed or not in PATH"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# 4. Check API Health
echo -e "${BLUE}4. API Health Check${NC}"
if docker compose ps | grep -q "api.*Up"; then
    if docker compose exec -T api curl -f http://localhost:8000/health > /dev/null 2>&1; then
        check_status 0 "API health endpoint responding"
        
        # Get detailed health info
        HEALTH=$(docker compose exec -T api curl -s http://localhost:8000/health 2>/dev/null)
        if echo "$HEALTH" | grep -q '"status":"healthy"'; then
            check_status 0 "API status is healthy"
        else
            check_status 1 "API status is not healthy"
            ISSUES=$((ISSUES + 1))
        fi
        
        if echo "$HEALTH" | grep -q '"database":"connected"'; then
            check_status 0 "Database is connected"
        else
            check_status 1 "Database is not connected"
            ISSUES=$((ISSUES + 1))
        fi
        
        if echo "$HEALTH" | grep -q '"redis":"connected"'; then
            check_status 0 "Redis is connected"
        else
            check_status 1 "Redis is not connected"
            ISSUES=$((ISSUES + 1))
        fi
    else
        check_status 1 "API health endpoint not responding"
        ISSUES=$((ISSUES + 1))
    fi
else
    check_warning 0 "API container not running, skipping health check"
fi
echo ""

# 5. Check CORS Configuration
echo -e "${BLUE}5. CORS Configuration${NC}"
if docker compose ps | grep -q "api.*Up"; then
    CORS_LOG=$(docker compose logs api 2>/dev/null | grep "CORS configuration" | tail -1)
    if [ -n "$CORS_LOG" ]; then
        check_status 0 "CORS configuration found in logs"
        echo "   $CORS_LOG"
    else
        check_warning 0 "CORS configuration not found in logs (may need restart)"
    fi
else
    check_warning 0 "API not running, cannot check CORS"
fi
echo ""

# 6. Check Migration Status
echo -e "${BLUE}6. Database Migration Status${NC}"
if docker compose ps | grep -q "db.*Up"; then
    MIGRATION=$(docker compose exec -T db psql -U abparts_user -d abparts_prod -c "SELECT version_num FROM alembic_version;" -t 2>/dev/null | tr -d ' ')
    if [ -n "$MIGRATION" ]; then
        check_status 0 "Migration version: $MIGRATION"
    else
        check_status 1 "Could not retrieve migration version"
        ISSUES=$((ISSUES + 1))
    fi
else
    check_warning 0 "Database not running, cannot check migrations"
fi
echo ""

# 7. Check Scripts
echo -e "${BLUE}7. Deployment Scripts${NC}"
for script in reset_migrations_clean.sh deploy_production_clean.sh; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            check_status 0 "$script exists and is executable"
        else
            check_warning 0 "$script exists but not executable (run: chmod +x $script)"
        fi
    else
        check_status 1 "$script not found"
        ISSUES=$((ISSUES + 1))
    fi
done
echo ""

# Summary
echo "========================================="
echo "Summary"
echo "========================================="
if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Your production setup is ready."
    echo ""
    echo "Next steps:"
    echo "  1. If services are not running: ./deploy_production_clean.sh"
    echo "  2. If migrations are messy: ./reset_migrations_clean.sh"
    echo "  3. Access your app: https://abparts.oraseas.com"
else
    echo -e "${RED}✗ Found $ISSUES issue(s)${NC}"
    echo ""
    echo "Please review the issues above and fix them."
    echo ""
    echo "Common fixes:"
    echo "  - Missing .env: cp .env.production.example .env && nano .env"
    echo "  - Services not running: docker compose -f docker-compose.prod.yml up -d"
    echo "  - Scripts not executable: chmod +x *.sh"
fi
echo ""
