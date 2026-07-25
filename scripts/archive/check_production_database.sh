#!/bin/bash
echo "🔍 Checking Production Database Configuration"
echo "============================================="

echo "1. Checking what databases exist in production..."
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -l

echo -e "\n2. Checking environment variables in production containers..."
echo "Database URL in API container:"
docker compose -f docker-compose.prod.yml exec api python -c "import os; print('DATABASE_URL:', repr(os.getenv('DATABASE_URL')))"

echo -e "\nDatabase URL in AI Assistant container:"
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "import os; print('DATABASE_URL:', repr(os.getenv('DATABASE_URL')))"

echo -e "\n3. Let's try connecting to the actual database..."
echo "Trying to connect to the database that exists..."
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -c "\l"