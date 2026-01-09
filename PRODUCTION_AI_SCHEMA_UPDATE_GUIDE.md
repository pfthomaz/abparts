# Production AI Assistant Schema Update Guide

## Overview

The development environment has been standardized with the superior AI Assistant schema. Now you need to update production to match.

## What Was Done in Development

✅ **Development Schema Standardized**
- Applied the comprehensive schema with all features
- Removed AI Assistant from Alembic management
- Cleaned up migration conflicts

## What Needs to Be Done on Production Server

### Step 1: Copy the Production Script

Copy `standardize_production_ai_schema.py` to your production server:

```bash
# On your local machine
scp standardize_production_ai_schema.py user@production-server:~/abparts/
```

### Step 2: Run the Schema Update on Production

**SSH into your production server** and run:

```bash
cd ~/abparts
python3 standardize_production_ai_schema.py
```

This script will:
- ✅ Backup existing production AI Assistant data
- ✅ Apply the standardized schema (matching development)
- ✅ Restore all existing data (converts UUID format to string format)
- ✅ Add missing fields: `embedding`, `file_hash`, proper indexes
- ✅ Convert `knowledge_chunks` table to `document_chunks`

### Step 3: Update Production Alembic Version

Still on the production server:

```bash
# Update Alembic version to skip AI Assistant migration
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
UPDATE alembic_version SET version_num = 'a78bd1ac6e99' WHERE version_num = 'add_ai_knowledge_base';
"
```

### Step 4: Restart AI Assistant Service

```bash
docker compose -f docker-compose.prod.yml restart ai_assistant
```

### Step 5: Test Everything Works

```bash
# Test health endpoint
curl https://abparts.oraseas.com/ai/health/

# Test knowledge base
curl https://abparts.oraseas.com/ai/knowledge/stats

# Test chat functionality
curl -X POST https://abparts.oraseas.com/ai/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "language": "en"}'
```

## Expected Results

After completion, both development and production will have:

### Identical Schema Structure
- ✅ `knowledge_documents` table with all fields
- ✅ `document_chunks` table with `embedding` field
- ✅ Proper indexing for performance
- ✅ Triggers for `updated_at` maintenance

### Data Preservation
- ✅ All existing knowledge base documents preserved
- ✅ All existing document chunks preserved
- ✅ Converted from production UUID format to development string format

### No Migration Conflicts
- ✅ AI Assistant tables managed independently of Alembic
- ✅ Future deployments won't have schema conflicts
- ✅ Clean separation between ABParts core and AI Assistant

## Troubleshooting

### If the Script Fails
1. Check database connectivity: `docker compose -f docker-compose.prod.yml ps db`
2. Check database credentials in the script
3. Look for specific error messages in the output

### If AI Assistant Doesn't Work After Update
1. Check service logs: `docker compose -f docker-compose.prod.yml logs ai_assistant`
2. Verify OpenAI API key is configured
3. Test endpoints individually

### If You Need to Rollback
The script creates backups, but if needed:
1. The original production schema can be recreated
2. Contact for assistance with rollback procedures

## Success Indicators

✅ **Schema Update Successful**: Script completes without errors  
✅ **Data Preserved**: Same number of documents and chunks as before  
✅ **AI Assistant Working**: Chat responses work without "technical difficulties"  
✅ **Knowledge Base Functional**: Admin interface shows documents and stats  

## Next Steps After Success

1. **Test Thoroughly**: Verify all AI Assistant functionality
2. **Monitor Performance**: Check that queries are fast with new indexes
3. **Regenerate Embeddings**: If needed for better search results
4. **Document Changes**: Update any documentation about the schema

The development environment is now ready for seamless deployment to production! 🚀