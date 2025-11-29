#!/bin/bash
# Deploy Image Storage System to Production
# Run this on the production server after pulling latest code

set -e  # Exit on error

echo "=========================================="
echo "  ABParts Image Storage Deployment"
echo "=========================================="
echo ""

# Check if running on production
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: docker-compose.prod.yml not found"
    echo "   Are you in the project root directory?"
    exit 1
fi

echo "📋 Pre-deployment checks..."
echo ""

# Check database columns exist
echo "Checking database schema..."
docker-compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod -c "\d users" | grep -q "profile_photo_data" && echo "✅ users.profile_photo_data exists" || echo "⚠️  users.profile_photo_data missing"
docker-compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod -c "\d organizations" | grep -q "logo_data" && echo "✅ organizations.logo_data exists" || echo "⚠️  organizations.logo_data missing"
echo ""

# Check nginx config
echo "Checking nginx configuration..."
if grep -q "location ^~ /images/" frontend/nginx.conf; then
    echo "✅ Nginx /images/ proxy configured"
else
    echo "⚠️  Nginx /images/ proxy not found in config"
fi
echo ""

# Confirm deployment
read -p "Continue with deployment? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""
echo "🔨 Building services..."
docker-compose -f docker-compose.prod.yml build api web

echo ""
echo "🔄 Restarting services..."
docker-compose -f docker-compose.prod.yml up -d api web

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "🔍 Checking service status..."
docker-compose -f docker-compose.prod.yml ps api web

echo ""
echo "📊 Checking API health..."
if docker-compose -f docker-compose.prod.yml exec -T api curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is healthy"
else
    echo "⚠️  API health check failed"
fi

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test image upload in browser:"
echo "   - Profile photo: https://abparts.oraseas.com/profile"
echo "   - Org logo: https://abparts.oraseas.com/organizations"
echo ""
echo "2. Monitor logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f api web"
echo ""
echo "3. Check for errors:"
echo "   docker-compose -f docker-compose.prod.yml logs api | grep -i error"
echo ""
