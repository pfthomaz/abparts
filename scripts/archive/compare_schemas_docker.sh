#!/bin/bash

echo "🔍 Development vs Production Schema Comparison (Docker Method)"
echo "=" * 65
echo ""

# Check if development environment is running
echo "📋 Step 1: Checking development environment..."
if ! docker compose ps | grep -q "Up"; then
    echo "⚠️  Development environment not running. Starting it..."
    docker compose up -d
    echo "⏳ Waiting for services to start..."
    sleep 10
fi

echo "✅ Development environment is running"

echo ""
echo "📊 Step 2: Getting development schema information..."

# Get development schema using Docker
echo "🔍 Development database tables:"
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
AND table_name NOT IN ('knowledge_documents', 'document_chunks', 'knowledge_chunks')
ORDER BY table_name;
"

echo ""
echo "📊 Development database detailed schema:"
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
    t.table_name,
    c.column_name,
    c.data_type,
    c.is_nullable,
    c.column_default
FROM information_schema.tables t
JOIN information_schema.columns c ON t.table_name = c.table_name
WHERE t.table_schema = 'public' 
AND t.table_type = 'BASE TABLE'
AND t.table_name NOT IN ('knowledge_documents', 'document_chunks', 'knowledge_chunks')
ORDER BY t.table_name, c.ordinal_position;
" > dev_schema_detailed.txt

echo "✅ Development schema saved to dev_schema_detailed.txt"

echo ""
echo "📋 Step 3: Instructions for production comparison..."
echo "=" * 50
echo ""
echo "🚨 To compare with production, run these commands on your PRODUCTION SERVER:"
echo ""
echo "# SSH to production server as diogo, then switch to abparts:"
echo "ssh diogo@your-production-server"
echo "sudo su - abparts"
echo "cd ~/abparts"
echo ""
echo "# Get production schema:"
echo "docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c \""
echo "SELECT "
echo "    table_name,"
echo "    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count"
echo "FROM information_schema.tables t"
echo "WHERE table_schema = 'public' "
echo "AND table_type = 'BASE TABLE'"
echo "AND table_name NOT IN ('knowledge_documents', 'document_chunks', 'knowledge_chunks')"
echo "ORDER BY table_name;"
echo "\""
echo ""
echo "# Get detailed production schema:"
echo "docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c \""
echo "SELECT "
echo "    t.table_name,"
echo "    c.column_name,"
echo "    c.data_type,"
echo "    c.is_nullable,"
echo "    c.column_default"
echo "FROM information_schema.tables t"
echo "JOIN information_schema.columns c ON t.table_name = c.table_name"
echo "WHERE t.table_schema = 'public' "
echo "AND t.table_type = 'BASE TABLE'"
echo "AND t.table_name NOT IN ('knowledge_documents', 'document_chunks', 'knowledge_chunks')"
echo "ORDER BY t.table_name, c.ordinal_position;"
echo "\" > prod_schema_detailed.txt"

echo ""
echo "📋 Step 4: Current development migration status..."
echo ""
echo "🔍 Current Alembic revision in development:"
docker compose exec api alembic current

echo ""
echo "🔍 Alembic history in development:"
docker compose exec api alembic history --verbose | head -20

echo ""
echo "✅ Development schema analysis complete!"
echo ""
echo "📝 Next steps:"
echo "1. Run the production commands shown above on your production server"
echo "2. Compare the outputs to see if schemas match"
echo "3. If they match, proceed with migration reset using ./reset_migrations_clean.sh"
echo "4. If they don't match, we need to standardize first"
echo ""
echo "📄 Files created:"
echo "- dev_schema_detailed.txt (development schema details)"
echo ""
echo "🎯 Goal: Ensure both environments have identical schemas before resetting migrations"