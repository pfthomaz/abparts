#!/bin/bash
# Quick Deployment Script for diogo@46.62.153.166
# ABParts Application in ~/ABParts

set -e  # Exit on error

echo "🚀 ABParts Deployment Script"
echo "================================"
echo ""

# Navigate to app directory
cd ~/ABParts

echo "📍 Current directory: $(pwd)"
echo ""

# Step 1: Backup
echo "📦 Step 1: Creating backup..."
BACKUP_FILE=~/backup_$(date +%Y%m%d_%H%M%S).sql
sudo docker compose exec -T db pg_dump -U abparts_user abparts_dev > $BACKUP_FILE
echo "✅ Backup created: $BACKUP_FILE"
echo ""

# Step 2: Pull latest code
echo "📥 Step 2: Pulling latest code from GitHub..."
git pull origin main
echo "✅ Code updated"
echo ""

# Step 3: Run database migration
echo "🗄️  Step 3: Running database migration..."
cat > /tmp/migration.sql << 'EOF'
-- Add profile photo URL to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(500);

-- Add logo URL to organizations table
ALTER TABLE organizations 
ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);

-- Add shipped_by_user_id to customer_orders
ALTER TABLE customer_orders 
ADD COLUMN IF NOT EXISTS shipped_by_user_id UUID REFERENCES users(id);

-- Verify changes
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('users', 'organizations', 'customer_orders')
    AND column_name IN ('profile_photo_url', 'logo_url', 'shipped_by_user_id')
ORDER BY table_name, column_name;
EOF

sudo docker compose exec -T db psql -U abparts_user -d abparts_dev < /tmp/migration.sql
rm /tmp/migration.sql
echo "✅ Database migration completed"
echo ""

# Step 4: Create static directory
echo "📁 Step 4: Creating static files directory..."
mkdir -p backend/static/images
chmod 755 backend/static
chmod 755 backend/static/images
echo "✅ Static directory created"
echo ""

# Step 5: Rebuild and restart containers
echo "🔄 Step 5: Rebuilding and restarting containers..."
echo "   This may take 5-10 minutes..."
sudo docker compose down
sudo docker compose build --no-cache
sudo docker compose up -d
echo "✅ Containers restarted"
echo ""

# Step 6: Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15
echo ""

# Step 7: Check status
echo "🔍 Step 7: Checking service status..."
sudo docker compose ps
echo ""

# Step 8: Check for errors
echo "📋 Checking API logs for errors..."
sudo docker compose logs api --tail=30 | grep -i error || echo "No errors found"
echo ""

echo "================================"
echo "✅ Deployment completed!"
echo ""
echo "📝 Next steps:"
echo "1. Check logs: sudo docker compose logs -f api"
echo "2. Test in browser: http://46.62.153.166:3000"
echo "3. Test profile photo upload"
echo "4. Test part usage workflow"
echo ""
echo "💾 Backup location: $BACKUP_FILE"
echo ""
