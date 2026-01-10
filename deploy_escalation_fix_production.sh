#!/bin/bash
echo "🚀 Deploying Escalation Service Fix to Production"
echo "================================================"

echo "The escalation service has been updated to use correct column names."
echo "This script will deploy the fixes to production."
echo ""

echo "1. Checking current git status..."
git status

echo -e "\n2. Adding updated escalation service to git..."
git add ai_assistant/app/services/escalation_service.py
git add docker-compose.yml docker-compose.prod.yml

echo -e "\n3. Committing the escalation service fixes..."
git commit -m "Fix escalation service database column references

- Update all queries to use 'id' instead of 'session_id' for ai_sessions table
- Fix user and machine lookup queries  
- Add SMTP environment variables to docker-compose files
- Escalation service now compatible with SQLAlchemy model schema"

echo -e "\n4. Pushing changes to repository..."
git push origin main

echo -e "\n5. Production deployment instructions:"
echo "   Run these commands on your production server:"
echo ""
echo "   # Pull latest changes"
echo "   git pull origin main"
echo ""
echo "   # Restart AI assistant service to load updated code"
echo "   docker compose -f docker-compose.prod.yml restart ai_assistant"
echo ""
echo "   # Verify the service is running"
echo "   docker compose -f docker-compose.prod.yml ps ai_assistant"
echo ""
echo "   # Test the escalation system"
echo "   docker compose -f docker-compose.prod.yml exec ai_assistant python test_production_escalation_complete.py"

echo -e "\n✅ Escalation fix deployment preparation complete!"
echo ""
echo "NEXT STEPS:"
echo "==========="
echo "1. Run the commands above on your production server"
echo "2. Test escalation through the production UI"
echo "3. Verify emails are sent to abparts_support@oraseas.com"
echo "4. Enable Microsoft 365 SMTP AUTH if needed"