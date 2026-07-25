# Port Conflict Resolution - ABParts & Aquaculture App

## Step 1: Check Existing Ports on New Server

First, let's see what ports are already in use by the aquaculture-app:

```bash
# SSH to new server
ssh diogo@46.62.131.135

# Check all listening ports
sudo netstat -tulpn | grep LISTEN

# Or using ss (more modern)
sudo ss -tulpn | grep LISTEN

# Check Docker containers and their ports
docker ps --format "table {{.Names}}\t{{.Ports}}"

# Check Nginx configuration
sudo cat /etc/nginx/sites-enabled/*
```

## Common Port Usage

### Default ABParts Ports (we may need to change these):
- **3000** - Frontend (React)
- **8000** - Backend API (FastAPI)
- **8001** - AI Assistant API (if using)
- **5432** - PostgreSQL (internal to Docker, not exposed)
- **6379** - Redis (internal to Docker, not exposed)

### Typical Aquaculture App Ports (check yours):
- Likely using **3000** or **80/443** for frontend
- Likely using **8000** or **5000** for backend API
- May have its own database on **5432** or **5433**

## Step 2: Identify Port Conflicts

Run this script to check for conflicts:

```bash
# On new server
cat > ~/check_ports.sh << 'EOF'
#!/bin/bash
echo "=== Checking Port Usage ==="
echo ""

ports=(3000 8000 8001 5432 6379 80 443)

for port in "${ports[@]}"; do
    if sudo lsof -i :$port > /dev/null 2>&1; then
        echo "❌ Port $port is IN USE:"
        sudo lsof -i :$port | grep LISTEN
    else
        echo "✅ Port $port is AVAILABLE"
    fi
    echo ""
done

echo "=== Docker Containers ==="
docker ps --format "table {{.Names}}\t{{.Ports}}" 2>/dev/null || echo "No Docker containers running"

echo ""
echo "=== Nginx Sites ==="
sudo ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "No Nginx sites configured"
EOF

chmod +x ~/check_ports.sh
~/check_ports.sh
```

## Step 3: Configure ABParts with Different Ports

Based on what you find, we'll need to modify ABParts to use available ports.

### Option A: Use Different Internal Ports

Edit `docker-compose.prod.yml` to use different ports:

```yaml
# Example: If 3000 and 8000 are taken, use 3001 and 8002

services:
  web:
    ports:
      - "3001:3000"  # External:Internal
    # Frontend will be accessible on port 3001

  api:
    ports:
      - "8002:8000"  # External:Internal
    # API will be accessible on port 8002

  ai_assistant:
    ports:
      - "8003:8000"  # External:Internal
    # AI Assistant will be accessible on port 8003

  db:
    # No external port needed - only internal
    # ports:
    #   - "5432:5432"  # Comment this out

  redis:
    # No external port needed - only internal
```

### Option B: Use Nginx as Single Entry Point (RECOMMENDED)

This is the **best approach** - use Nginx to route both applications:

**Aquaculture App**: `http://46.62.131.135/aquaculture/` or subdomain
**ABParts**: `http://46.62.131.135/abparts/` or subdomain

Or use subdomains:
- `aquaculture.yourdomain.com`
- `abparts.yourdomain.com`

## Step 4: Recommended Port Configuration

### Scenario 1: Aquaculture App Uses 3000 and 8000

**ABParts Configuration:**

```yaml
# docker-compose.prod.yml
services:
  web:
    ports:
      - "3001:3000"  # Frontend on 3001
  
  api:
    ports:
      - "8002:8000"  # API on 8002
  
  ai_assistant:
    ports:
      - "8003:8000"  # AI Assistant on 8003
```

**Nginx Configuration for ABParts:**

```nginx
# /etc/nginx/sites-available/abparts

server {
    listen 80;
    server_name abparts.yourdomain.com;  # Or use path-based routing

    client_max_body_size 100M;

    # Frontend
    location / {
        proxy_pass http://localhost:3001;  # Changed from 3000
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8002/api/;  # Changed from 8000
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    # AI Assistant API
    location /api/ai/ {
        proxy_pass http://localhost:8003/;  # Changed from 8001
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    # Static files
    location /static/ {
        alias /home/diogo/abparts/backend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Scenario 2: Path-Based Routing (Both Apps on Same Domain)

If you want both apps accessible from the same domain:

```nginx
# /etc/nginx/sites-available/apps

server {
    listen 80;
    server_name 46.62.131.135;

    client_max_body_size 100M;

    # Aquaculture App (existing)
    location /aquaculture/ {
        proxy_pass http://localhost:3000/;
        # ... other proxy settings
    }

    # ABParts (new)
    location /abparts/ {
        proxy_pass http://localhost:3001/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # ABParts API
    location /abparts/api/ {
        proxy_pass http://localhost:8002/api/;
        # ... other proxy settings
    }

    # ABParts AI Assistant
    location /abparts/api/ai/ {
        proxy_pass http://localhost:8003/;
        # ... other proxy settings
    }

    # ABParts Static Files
    location /abparts/static/ {
        alias /home/diogo/abparts/backend/static/;
        expires 30d;
    }
}
```

### Scenario 3: Subdomain-Based Routing (BEST FOR PRODUCTION)

```nginx
# /etc/nginx/sites-available/aquaculture
server {
    listen 80;
    server_name aquaculture.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        # ... proxy settings
    }
}

# /etc/nginx/sites-available/abparts
server {
    listen 80;
    server_name abparts.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3001;
        # ... proxy settings
    }
    
    location /api/ {
        proxy_pass http://localhost:8002/api/;
        # ... proxy settings
    }
}
```

## Step 5: Update docker-compose.prod.yml

Create a custom `docker-compose.prod.yml` with your chosen ports:

```bash
cd ~/abparts
nano docker-compose.prod.yml
```

**Example with custom ports:**

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - abparts_network
    restart: unless-stopped
    # No external port - only internal access

  redis:
    image: redis:7-alpine
    networks:
      - abparts_network
    restart: unless-stopped
    # No external port - only internal access

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    env_file:
      - .env.production
    ports:
      - "8002:8000"  # CHANGED: External port 8002
    volumes:
      - ./backend/static:/app/static
    depends_on:
      - db
      - redis
    networks:
      - abparts_network
    restart: unless-stopped

  web:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "3001:3000"  # CHANGED: External port 3001
    depends_on:
      - api
    networks:
      - abparts_network
    restart: unless-stopped
    environment:
      - REACT_APP_API_BASE_URL=/api

  ai_assistant:
    build:
      context: ./ai_assistant
      dockerfile: Dockerfile
    env_file:
      - .env.production
    ports:
      - "8003:8000"  # CHANGED: External port 8003
    depends_on:
      - ai_db
    networks:
      - abparts_network
    restart: unless-stopped

  ai_db:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_assistant
      POSTGRES_USER: ${AI_DB_USER}
      POSTGRES_PASSWORD: ${AI_DB_PASSWORD}
    volumes:
      - ai_postgres_data:/var/lib/postgresql/data
    networks:
      - abparts_network
    restart: unless-stopped
    # No external port - only internal access

volumes:
  postgres_data:
  ai_postgres_data:

networks:
  abparts_network:
    driver: bridge
```

## Step 6: Test Configuration

```bash
# Test Docker Compose configuration
cd ~/abparts
docker compose -f docker-compose.prod.yml config

# Start containers
docker compose -f docker-compose.prod.yml up -d

# Check ports
docker compose -f docker-compose.prod.yml ps

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Test endpoints
curl http://localhost:3001  # Frontend
curl http://localhost:8002/api/health  # API
curl http://localhost:8003/health  # AI Assistant
```

## Step 7: Quick Port Check Script

Save this for future reference:

```bash
cat > ~/abparts/check_abparts_ports.sh << 'EOF'
#!/bin/bash
echo "=== ABParts Port Status ==="
echo ""

echo "Frontend (3001):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 && echo " - OK" || echo " - FAIL"

echo "API (8002):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/api/health && echo " - OK" || echo " - FAIL"

echo "AI Assistant (8003):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8003/health && echo " - OK" || echo " - FAIL"

echo ""
echo "=== Docker Containers ==="
docker compose -f ~/abparts/docker-compose.prod.yml ps
EOF

chmod +x ~/abparts/check_abparts_ports.sh
```

## Recommended Approach

1. **Check existing ports** on the new server
2. **Use ports 3001, 8002, 8003** for ABParts (if available)
3. **Use Nginx subdomain routing** for clean separation:
   - `aquaculture.yourdomain.com` → Aquaculture App
   - `abparts.yourdomain.com` → ABParts
4. **Keep databases internal** (no external ports)

## Next Steps

1. Run `~/check_ports.sh` to see what's in use
2. Share the output with me
3. I'll help you configure the exact ports to use
4. Update `docker-compose.prod.yml` accordingly
5. Configure Nginx with the right routing

Would you like me to help you check the ports now?
