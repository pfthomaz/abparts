#!/bin/bash

# AI Assistant Production Verification Script
# Checks that all components are working correctly

echo "========================================="
echo "AI Assistant Production Verification"
echo "========================================="
echo ""

# Check 1: Database tables
echo "Check 1: Verifying database tables..."
docker compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
    AND table_name IN (
        'ai_sessions', 
        'ai_messages', 
        'knowledge_documents', 
        'document_embeddings',
        'troubleshooting_steps',
        'session_outcomes',
        'machine_facts',
        'solution_effectiveness'
    )
ORDER BY table_name;
"

echo ""

# Check 2: troubleshooting_steps schema
echo "Check 2: Verifying troubleshooting_steps schema..."
docker compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT 
    column_name, 
    data_type, 
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'troubleshooting_steps' 
    AND column_name IN ('id', 'updated_at', 'session_id', 'step_number')
ORDER BY ordinal_position;
"

echo ""

# Check 3: Container status
echo "Check 3: Verifying container status..."
docker compose ps web ai_assistant db

echo ""

# Check 4: AI Assistant health
echo "Check 4: Checking AI Assistant health endpoint..."
curl -s http://localhost:8001/health | python3 -m json.tool || echo "Health check failed"

echo ""

# Check 5: Frontend build
echo "Check 5: Checking frontend build..."
if docker compose exec web ls -lh /app/build/index.html 2>/dev/null; then
    echo "✓ Frontend build exists"
else
    echo "✗ Frontend build not found"
fi

echo ""

# Check 6: Translation files
echo "Check 6: Checking translation files..."
docker compose exec web ls -lh /app/src/locales/*.json

echo ""

echo "========================================="
echo "Verification Complete"
echo "========================================="
echo ""
echo "Manual Testing Required:"
echo "1. Open https://your-domain.com"
echo "2. Login with: dthomaz/amFT1999!"
echo "3. Click AI Assistant chat icon"
echo "4. Verify AutoBoss machine icon (larger)"
echo "5. Select a machine"
echo "6. Type: 'Machine won't start'"
echo "7. Verify step-by-step guidance appears"
echo "8. Check that 'Step {{number}}' shows as 'Step 1' (not placeholder)"
echo ""
