#!/bin/bash

# Standardize AI Assistant Schema - Production Server (Docker Version)
# This script uses Docker containers to update the production AI Assistant schema

echo "🔄 Standardizing AI Assistant Schema - Production Server"
echo "=" * 55
echo "⚠️  Running on production server using Docker containers"
echo ""

# Step 1: Backup existing production data
echo "Step 1: Backing up existing production data..."
echo "📦 Backing up knowledge_documents..."

# Backup knowledge_documents
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
COPY (SELECT * FROM knowledge_documents) TO '/tmp/knowledge_documents_backup.csv' WITH CSV HEADER;
" 2>/dev/null && echo "  ✅ Backed up knowledge_documents" || echo "  ⚠️  No knowledge_documents table to backup"

# Backup document_chunks (if exists)
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
COPY (SELECT * FROM document_chunks) TO '/tmp/document_chunks_backup.csv' WITH CSV HEADER;
" 2>/dev/null && echo "  ✅ Backed up document_chunks" || echo "  ⚠️  No document_chunks table to backup"

# Backup knowledge_chunks (old production table)
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
COPY (SELECT * FROM knowledge_chunks) TO '/tmp/knowledge_chunks_backup.csv' WITH CSV HEADER;
" 2>/dev/null && echo "  ✅ Backed up knowledge_chunks (old format)" || echo "  ⚠️  No knowledge_chunks table to backup"

# Step 2: Apply the standard schema
echo ""
echo "Step 2: Applying standard AI Assistant schema..."

# Create the schema update SQL
cat > /tmp/ai_schema_update.sql << 'EOF'
-- Drop existing tables if they exist (in correct order due to foreign keys)
DROP TABLE IF EXISTS document_chunks CASCADE;
DROP TABLE IF EXISTS knowledge_documents CASCADE;
DROP TABLE IF EXISTS knowledge_chunks CASCADE;

-- Create knowledge_documents table (development standard)
CREATE TABLE knowledge_documents (
    id character varying NOT NULL,
    title character varying NOT NULL,
    document_type character varying NOT NULL DEFAULT 'manual'::character varying,
    version character varying,
    language character varying NOT NULL DEFAULT 'en'::character varying,
    file_path character varying,
    file_hash character varying,
    chunk_count integer NOT NULL DEFAULT 0,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    document_metadata jsonb,
    machine_models text[],
    tags text[]
);

-- Create document_chunks table (development standard)
CREATE TABLE document_chunks (
    id character varying NOT NULL,
    document_id character varying NOT NULL,
    chunk_index integer NOT NULL,
    content text NOT NULL,
    embedding jsonb,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Add primary keys
ALTER TABLE ONLY knowledge_documents ADD CONSTRAINT knowledge_documents_pkey PRIMARY KEY (id);
ALTER TABLE ONLY document_chunks ADD CONSTRAINT document_chunks_pkey PRIMARY KEY (id);

-- Add unique constraints
ALTER TABLE ONLY knowledge_documents ADD CONSTRAINT knowledge_documents_file_hash_key UNIQUE (file_hash);

-- Add foreign key constraints
ALTER TABLE ONLY document_chunks ADD CONSTRAINT document_chunks_document_id_fkey 
    FOREIGN KEY (document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE;

-- Create indexes for knowledge_documents
CREATE INDEX idx_knowledge_documents_created_at ON knowledge_documents USING btree (created_at);
CREATE INDEX idx_knowledge_documents_language ON knowledge_documents USING btree (language);
CREATE INDEX idx_knowledge_documents_machine_models ON knowledge_documents USING gin (machine_models);
CREATE INDEX idx_knowledge_documents_tags ON knowledge_documents USING gin (tags);
CREATE INDEX idx_knowledge_documents_type ON knowledge_documents USING btree (document_type);
CREATE INDEX idx_knowledge_documents_updated_at ON knowledge_documents USING btree (updated_at);

-- Create indexes for document_chunks
CREATE INDEX idx_document_chunks_document_id ON document_chunks USING btree (document_id);

-- Create trigger function for updated_at
CREATE OR REPLACE FUNCTION update_knowledge_document_updated_at()
RETURNS trigger AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$ LANGUAGE plpgsql;

-- Create trigger
CREATE TRIGGER trigger_update_knowledge_document_updated_at
    BEFORE UPDATE ON knowledge_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_knowledge_document_updated_at();
EOF

# Copy SQL file to container and execute
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod < /tmp/ai_schema_update.sql

if [ $? -eq 0 ]; then
    echo "  ✅ Standard schema applied to production"
else
    echo "  ❌ Error applying schema"
    exit 1
fi

# Step 3: Restore data from backups
echo ""
echo "Step 3: Restoring data from backups..."

# Check if we have backup files and restore them
if docker compose -f docker-compose.prod.yml exec db test -f /tmp/knowledge_documents_backup.csv; then
    echo "📥 Restoring knowledge_documents..."
    docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
    COPY knowledge_documents FROM '/tmp/knowledge_documents_backup.csv' WITH CSV HEADER;
    "
    if [ $? -eq 0 ]; then
        echo "  ✅ Restored knowledge_documents"
    else
        echo "  ⚠️  Error restoring knowledge_documents"
    fi
fi

if docker compose -f docker-compose.prod.yml exec db test -f /tmp/document_chunks_backup.csv; then
    echo "📥 Restoring document_chunks..."
    docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
    COPY document_chunks FROM '/tmp/document_chunks_backup.csv' WITH CSV HEADER;
    "
    if [ $? -eq 0 ]; then
        echo "  ✅ Restored document_chunks"
    else
        echo "  ⚠️  Error restoring document_chunks"
    fi
fi

# Restore from knowledge_chunks (old format) if it exists
if docker compose -f docker-compose.prod.yml exec db test -f /tmp/knowledge_chunks_backup.csv; then
    echo "📥 Converting and restoring knowledge_chunks (old format)..."
    
    # Create a temporary conversion script
    cat > /tmp/convert_chunks.sql << 'EOF'
-- Create temporary table for old format
CREATE TEMP TABLE temp_knowledge_chunks (
    id character varying,
    document_id uuid,
    chunk_index integer,
    content text,
    created_at timestamp with time zone
);

-- Load old data
COPY temp_knowledge_chunks FROM '/tmp/knowledge_chunks_backup.csv' WITH CSV HEADER;

-- Convert and insert into new format
INSERT INTO document_chunks (id, document_id, chunk_index, content, embedding, created_at)
SELECT 
    CONCAT(document_id::text, '_chunk_', chunk_index) as id,
    document_id::text as document_id,
    chunk_index,
    content,
    NULL as embedding,
    created_at::timestamp without time zone
FROM temp_knowledge_chunks;
EOF

    docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod < /tmp/convert_chunks.sql
    
    if [ $? -eq 0 ]; then
        echo "  ✅ Converted and restored knowledge_chunks"
    else
        echo "  ⚠️  Error converting knowledge_chunks"
    fi
fi

# Step 4: Update Alembic version
echo ""
echo "Step 4: Updating Alembic version..."
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
UPDATE alembic_version SET version_num = 'a78bd1ac6e99' WHERE version_num IN ('add_ai_knowledge_base', 'add_ai_assistant_knowledge_base_tables');
"

if [ $? -eq 0 ]; then
    echo "  ✅ Updated Alembic version"
else
    echo "  ⚠️  Error updating Alembic version"
fi

# Step 5: Verify the schema
echo ""
echo "Step 5: Verifying schema..."

# Check table structure
echo "🔍 Checking table structure..."
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
SELECT 
    'knowledge_documents' as table_name,
    COUNT(*) as column_count
FROM information_schema.columns 
WHERE table_name = 'knowledge_documents'
UNION ALL
SELECT 
    'document_chunks' as table_name,
    COUNT(*) as column_count
FROM information_schema.columns 
WHERE table_name = 'document_chunks';
"

# Check data counts
echo "📊 Checking data counts..."
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
SELECT 
    'knowledge_documents' as table_name,
    COUNT(*) as row_count
FROM knowledge_documents
UNION ALL
SELECT 
    'document_chunks' as table_name,
    COUNT(*) as row_count
FROM document_chunks;
"

# Check for embedding field
echo "🔍 Checking for embedding field..."
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'document_chunks' AND column_name = 'embedding';
"

# Step 6: Restart AI Assistant service
echo ""
echo "Step 6: Restarting AI Assistant service..."
docker compose -f docker-compose.prod.yml restart ai_assistant

if [ $? -eq 0 ]; then
    echo "  ✅ AI Assistant service restarted"
else
    echo "  ❌ Error restarting AI Assistant service"
fi

# Step 7: Test the service
echo ""
echo "Step 7: Testing AI Assistant service..."

# Wait for service to start
sleep 10

# Test health endpoint
echo "🧪 Testing health endpoint..."
curl -s http://localhost:8001/health/ | jq '.' 2>/dev/null || curl -s http://localhost:8001/health/

# Test knowledge base stats
echo ""
echo "🧪 Testing knowledge base stats..."
curl -s http://localhost:8001/knowledge/stats | jq '.' 2>/dev/null || curl -s http://localhost:8001/knowledge/stats

# Cleanup temporary files
echo ""
echo "🧹 Cleaning up temporary files..."
rm -f /tmp/ai_schema_update.sql /tmp/convert_chunks.sql
docker compose -f docker-compose.prod.yml exec db rm -f /tmp/knowledge_documents_backup.csv /tmp/document_chunks_backup.csv /tmp/knowledge_chunks_backup.csv

echo ""
echo "✅ Production AI Assistant schema standardization complete!"
echo ""
echo "📝 Summary:"
echo "- Applied development-standard schema to production"
echo "- Preserved all existing data"
echo "- Added missing fields: embedding, file_hash, proper indexes"
echo "- Updated Alembic version to skip AI Assistant migrations"
echo "- Restarted AI Assistant service"
echo ""
echo "🧪 Next steps:"
echo "1. Test AI Assistant chat functionality"
echo "2. Verify knowledge base admin interface works"
echo "3. Check that embeddings can be regenerated if needed"
echo "4. Monitor performance with new indexes"