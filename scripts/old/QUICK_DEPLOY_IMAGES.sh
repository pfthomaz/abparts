#!/bin/bash
# Quick deployment script for part images fix

echo "🚀 Deploying Part Images Fix"
echo ""

# Check if we have uncommitted changes
if [[ -n $(git status -s docker-compose.prod.yml) ]]; then
    echo "📝 Committing changes..."
    git add docker-compose.prod.yml
    git commit -m "Fix: Mount /var/www/abparts_images for part images in production"
    git push
    echo "✅ Changes pushed to repository"
else
    echo "ℹ️  No changes to commit (already committed)"
fi

echo ""
echo "📋 Next steps on PRODUCTION SERVER:"
echo ""
echo "   ssh root@46.62.153.166"
echo "   cd ~/abparts"
echo "   git pull"
echo "   sudo docker compose -f docker-compose.prod.yml restart api"
echo "   sudo docker exec abparts_api_prod ls /app/static/images | head -10"
echo ""
echo "Then test: https://abparts.oraseas.com/static/images/test.jpg"
echo ""
