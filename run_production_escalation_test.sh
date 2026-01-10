#!/bin/bash
echo "🧪 Running Production Escalation System Test"
echo "============================================"

echo "The test needs to run inside the AI assistant container."
echo "Copying test file to the correct location and running it..."
echo ""

# Copy the test file to the AI assistant container
echo "1. Copying test file to AI assistant container..."
docker compose -f docker-compose.prod.yml cp ai_assistant/test_production_escalation_complete.py ai_assistant:/app/

# Make sure the file is executable
echo "2. Making test file executable..."
docker compose -f docker-compose.prod.yml exec ai_assistant chmod +x /app/test_production_escalation_complete.py

# Run the test
echo "3. Running the escalation system test..."
echo ""
docker compose -f docker-compose.prod.yml exec ai_assistant python /app/test_production_escalation_complete.py

echo ""
echo "✅ Test execution complete!"