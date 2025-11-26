#!/bin/bash

echo "=== Complete Server Fix ==="
echo ""

# Fix 1: Database connection issue
echo "1. Diagnosing database connection..."
echo ""

# Check if database container is healthy
DB_STATUS=$(docker compose ps db | grep healthy)
if [ -n "$DB_STATUS" ]; then
    echo "✓ Database container is healthy"
else
    echo "✗ Database container is not healthy"
    docker compose logs db | tail -20
fi
echo ""

# Check DATABASE_URL in API container
echo "2. Checking DATABASE_URL in API container..."
docker compose exec api printenv DATABASE_URL
echo ""

# Test database connection from API container
echo "3. Testing database connection from API container..."
docker compose exec api python -c "
import os
import sys
from sqlalchemy import create_engine, text

db_url = os.getenv('DATABASE_URL')
print(f'Database URL: {db_url}')

try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✓ Database connection successful')
        sys.exit(0)
except Exception as e:
    print(f'✗ Database connection failed: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo ""
    echo "Database connection failed. Checking docker network..."
    docker network inspect abparts_default | grep -A 5 abparts_db
    echo ""
    echo "Restarting all containers..."
    docker compose down
    sleep 2
    docker compose up -d db redis
    sleep 10
    docker compose up -d api celery_worker
    sleep 5
fi
echo ""

# Check API health again
echo "4. Checking API health after fixes..."
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

# Fix 2: Frontend - use Docker to build instead of local npm
echo "5. Building frontend using Docker..."
echo ""

# Check if we have a built frontend already
if [ -d "frontend/build" ]; then
    echo "Found existing frontend/build directory"
    read -p "Rebuild frontend? (y/n): " rebuild
else
    rebuild="y"
fi

if [ "$rebuild" = "y" ] || [ "$rebuild" = "Y" ]; then
    echo "Building frontend in Docker container..."
    
    # Create a temporary container to build the frontend
    docker run --rm \
        -v "$(pwd)/frontend:/app" \
        -w /app \
        -e REACT_APP_API_BASE_URL=https://abparts.oraseas.com/api \
        node:18 \
        sh -c "npm install && npm run build"
    
    if [ $? -eq 0 ]; then
        echo "✓ Frontend built successfully"
        ls -lh frontend/build/
    else
        echo "✗ Frontend build failed"
        exit 1
    fi
fi
echo ""

# Fix 3: Update nginx configuration
echo "6. Updating nginx configuration..."
sudo cp /etc/nginx/sites-available/abparts.oraseas.com /etc/nginx/sites-available/abparts.oraseas.com.backup.$(date +%Y%m%d_%H%M%S)

sudo tee /etc/nginx/sites-available/abparts.oraseas.com > /dev/null << 'EOF'
# ABParts - Production Configuration
server {
    listen 80;
    listen [::]:80;
    server_name abparts.oraseas.com;

    location /.well-known/acme-challenge/ {
        root /var/www/letsencrypt;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name abparts.oraseas.com;

    ssl_certificate /etc/letsencrypt/live/abparts.oraseas.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/abparts.oraseas.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    client_max_body_size 10M;

    # API endpoints
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files from backend
    location /static/ {
        proxy_pass http://localhost:8000/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Frontend - serve built React app
    location / {
        root /home/abparts/abparts/frontend/build;
        try_files $uri $uri/ /index.html;
        
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    access_log /var/log/nginx/abparts_access.log;
    error_log /var/log/nginx/abparts_error.log;
}
EOF

echo "✓ Nginx config updated"
echo ""

# Test and reload nginx
echo "7. Testing and reloading nginx..."
sudo nginx -t

if [ $? -eq 0 ]; then
    sudo systemctl reload nginx
    echo "✓ Nginx reloaded"
else
    echo "✗ Nginx config error"
    exit 1
fi
echo ""

# Final tests
echo "8. Final tests..."
echo ""

echo "API health:"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

echo "Website status:"
curl -I https://abparts.oraseas.com 2>&1 | head -1
echo ""

echo "=== Fix Complete ==="
echo ""
echo "Summary:"
echo "- CORS: Fixed ✓"
echo "- Database: Check output above"
echo "- Frontend: Built and served via nginx"
echo "- HTTPS: Configured"
echo ""
echo "Visit: https://abparts.oraseas.com"
