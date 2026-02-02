#!/bin/bash
# Port Conflict Detection Script for New Hetzner Server
# Run this on the new server (46.62.131.135) to check what ports are in use

echo "=========================================="
echo "ABParts Port Conflict Detection"
echo "Server: 46.62.131.135"
echo "Date: $(date)"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ports we want to check for ABParts
ABPARTS_PORTS=(3000 3001 8000 8001 8002 8003 5432 6379 80 443)

echo "=== CHECKING CRITICAL PORTS ==="
echo ""

for port in "${ABPARTS_PORTS[@]}"; do
    if sudo lsof -i :$port > /dev/null 2>&1; then
        echo -e "${RED}❌ Port $port is IN USE${NC}"
        echo "   Process details:"
        sudo lsof -i :$port | grep LISTEN | awk '{printf "   - PID: %s, Command: %s, User: %s\n", $2, $1, $3}'
        echo ""
    else
        echo -e "${GREEN}✅ Port $port is AVAILABLE${NC}"
    fi
done

echo ""
echo "=== ALL LISTENING PORTS ==="
echo ""
sudo netstat -tulpn 2>/dev/null | grep LISTEN || sudo ss -tulpn | grep LISTEN

echo ""
echo "=== DOCKER CONTAINERS ==="
echo ""
if command -v docker &> /dev/null; then
    if docker ps > /dev/null 2>&1; then
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        echo ""
        echo "=== DOCKER COMPOSE PROJECTS ==="
        echo ""
        # Try to find docker-compose projects
        for dir in /home/*/*/; do
            if [ -f "${dir}docker-compose.yml" ] || [ -f "${dir}docker-compose.yaml" ]; then
                echo "Found docker-compose in: $dir"
                echo "Services:"
                cd "$dir" && docker compose ps 2>/dev/null || docker-compose ps 2>/dev/null
                echo ""
            fi
        done
    else
        echo "Docker is installed but not running or no permission"
    fi
else
    echo "Docker is not installed"
fi

echo ""
echo "=== NGINX CONFIGURATION ==="
echo ""
if [ -d "/etc/nginx/sites-enabled" ]; then
    echo "Nginx sites enabled:"
    ls -la /etc/nginx/sites-enabled/
    echo ""
    
    echo "Nginx configurations:"
    for conf in /etc/nginx/sites-enabled/*; do
        if [ -f "$conf" ]; then
            echo ""
            echo "--- File: $conf ---"
            # Show server_name and listen directives
            grep -E "server_name|listen|proxy_pass" "$conf" | head -20
        fi
    done
else
    echo "Nginx sites-enabled directory not found"
fi

echo ""
echo "=== SYSTEMD SERVICES ==="
echo ""
echo "Active services that might use ports:"
systemctl list-units --type=service --state=running | grep -E "nginx|docker|node|python|postgres|redis" || echo "No relevant services found"

echo ""
echo "=== FIREWALL STATUS ==="
echo ""
if command -v ufw &> /dev/null; then
    sudo ufw status verbose
else
    echo "UFW not installed"
fi

echo ""
echo "=== DISK SPACE ==="
echo ""
df -h | grep -E "Filesystem|/$|/home"

echo ""
echo "=== MEMORY USAGE ==="
echo ""
free -h

echo ""
echo "=========================================="
echo "RECOMMENDATIONS FOR ABPARTS"
echo "=========================================="
echo ""

# Analyze and provide recommendations
PORTS_IN_USE=()
PORTS_AVAILABLE=()

for port in 3000 3001 8000 8001 8002 8003; do
    if sudo lsof -i :$port > /dev/null 2>&1; then
        PORTS_IN_USE+=($port)
    else
        PORTS_AVAILABLE+=($port)
    fi
done

if [ ${#PORTS_IN_USE[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All standard ABParts ports are available!${NC}"
    echo ""
    echo "Recommended configuration:"
    echo "  - Frontend (web):        Port 3000"
    echo "  - Backend API (api):     Port 8000"
    echo "  - AI Assistant:          Port 8001"
    echo ""
    echo "You can use the default docker-compose.prod.yml configuration."
else
    echo -e "${YELLOW}⚠️  Some ports are in use. Recommended alternative configuration:${NC}"
    echo ""
    
    # Suggest available ports
    FRONTEND_PORT=3000
    API_PORT=8000
    AI_PORT=8001
    
    # Find available ports
    for port in 3000 3001 3002; do
        if ! sudo lsof -i :$port > /dev/null 2>&1; then
            FRONTEND_PORT=$port
            break
        fi
    done
    
    for port in 8000 8002 8004; do
        if ! sudo lsof -i :$port > /dev/null 2>&1; then
            API_PORT=$port
            break
        fi
    done
    
    for port in 8001 8003 8005; do
        if ! sudo lsof -i :$port > /dev/null 2>&1; then
            AI_PORT=$port
            break
        fi
    done
    
    echo "Suggested ABParts port configuration:"
    echo "  - Frontend (web):        Port $FRONTEND_PORT"
    echo "  - Backend API (api):     Port $API_PORT"
    echo "  - AI Assistant:          Port $AI_PORT"
    echo ""
    echo "Update docker-compose.prod.yml with these ports:"
    echo ""
    echo "  web:"
    echo "    ports:"
    echo "      - \"$FRONTEND_PORT:80\""
    echo ""
    echo "  api:"
    echo "    ports:"
    echo "      - \"$API_PORT:8000\""
    echo ""
    echo "  ai_assistant:"
    echo "    ports:"
    echo "      - \"$AI_PORT:8001\""
fi

echo ""
echo "=========================================="
echo "NEXT STEPS"
echo "=========================================="
echo ""
echo "1. Review the port usage above"
echo "2. If ports are in use, update docker-compose.prod.yml with available ports"
echo "3. Configure Nginx to proxy to the correct ports"
echo "4. Proceed with migration following HETZNER_NEW_SERVER_MIGRATION.md"
echo ""
echo "For detailed instructions, see:"
echo "  - HETZNER_NEW_SERVER_MIGRATION.md"
echo "  - PORT_CONFLICT_RESOLUTION.md"
echo ""
