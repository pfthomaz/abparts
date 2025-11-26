#!/bin/bash

echo "=== Fixing Production Setup ==="
echo ""

# Check database connection
echo "1. Checking database connection..."
docker compose exec db psql -U abparts_user -d abparts_dev -c "SELECT 1;" 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Database is accessible from host"
else
    echo "✗ Database connection failed"
fi
echo ""

# Check if API can reach database
echo "2. Checking API to database connection..."
docker compose exec api python -c "
import os
from sqlalchemy import create_engine, text
try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✓ API can connect to database')
except Exception as e:
    print(f'✗ API cannot connect to database: {e}')
"
echo ""

# Restart API to fix database connection
echo "3. Restarting API container..."
docker compose restart api
sleep 5
echo ""

# Check API health
echo "4. Checking API health..."
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

# For production, we need to build and serve the React app
echo "5. Checking frontend setup..."
echo ""
echo "⚠ IMPORTANT: For production, you should NOT run 'npm start'"
echo "   Instead, you need to:"
echo "   1. Build the React app"
echo "   2. Serve it with nginx"
echo ""
echo "Would you like to:"
echo "   A) Build and serve production frontend (recommended)"
echo "   B) Start development frontend on port 3000 (temporary)"
echo ""
read -p "Enter choice (A/B): " choice

if [ "$choice" = "A" ] || [ "$choice" = "a" ]; then
    echo ""
    echo "Building production frontend..."
    
    # Build the React app
    cd frontend
    npm install
    npm run build
    cd ..
    
    # Create nginx config to serve the built app
    echo "Creating nginx config for built frontend..."
    
    # We'll update the nginx config to serve from the build directory
    echo "✓ Frontend built successfully"
    echo ""
    echo "Next step: Update nginx to serve from frontend/build directory"
    echo "Run: sudo nano /etc/nginx/sites-available/abparts.oraseas.com"
    echo ""
    echo "Change the frontend location block to:"
    echo "    location / {"
    echo "        root /home/abparts/abparts/frontend/build;"
    echo "        try_files \$uri \$uri/ /index.html;"
    echo "    }"
    
elif [ "$choice" = "B" ] || [ "$choice" = "b" ]; then
    echo ""
    echo "Starting development frontend..."
    docker compose up -d web
    sleep 10
    
    echo "Checking frontend status..."
    curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3000/
else
    echo "Invalid choice"
fi

echo ""
echo "=== Done ==="
