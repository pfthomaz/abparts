# AI Assistant Deployment Guide

This guide ensures seamless deployment of the AI Assistant from development to production.

## Current Status

✅ **Production Deployment Complete**
- AI Assistant service running on port 8001
- Admin interface accessible at `https://abparts.oraseas.com/ai/admin`
- Knowledge base tables created and functional
- Document upload working correctly

✅ **Development Environment Ready**
- AI Assistant service running locally on port 8001
- Database schema synchronized with production
- Alembic migrations up to date
- Knowledge base endpoints functional
- Admin interface accessible at `http://localhost:8001/admin`

## Development Environment Setup

### 1. Database Schema Sync

The production database now has AI Assistant tables that need to be replicated in development:

```bash
# Option A: Run the sync script (recommended)
python sync_production_schema.py --dev

# Option B: Manual Alembic migration
docker-compose up -d db
docker-compose exec api alembic upgrade head
```

### 2. Environment Variables

Add to your `.env` file:

```bash
# AI Assistant Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_FALLBACK_MODEL=gpt-3.5-turbo

# AI Assistant URLs
REACT_APP_AI_ASSISTANT_URL=http://localhost:8001
```

### 3. Start Development Environment

```bash
# Start all services including AI Assistant
docker-compose up -d

# Check AI Assistant health
curl http://localhost:8001/health

# Access admin interface
open http://localhost:8001/admin
```

## Key Changes Made

### 1. Router Configuration Fix
- **File**: `ai_assistant/app/main.py`
- **Change**: Knowledge base router prefix changed from `/api/ai` to `` (empty)
- **Reason**: Matches nginx proxy configuration `/ai/` → AI Assistant service

### 2. Admin Interface URL Fix
- **File**: `ai_assistant/app/static/admin.html`
- **Change**: API_BASE changed from `/api/ai/knowledge` to `/ai/knowledge`
- **Reason**: Aligns with nginx routing and router prefix

### 3. Database Schema
- **Tables Created**:
  - `knowledge_documents`: Stores document metadata
  - `document_chunks`: Stores document content chunks (note: not `knowledge_chunks`)
- **Key Fields**:
  - `knowledge_documents.chunk_count`: INTEGER DEFAULT 0
  - `document_chunks.id`: VARCHAR(255) (handles compound IDs like `uuid_chunk_0`)

## Production Deployment Process

### 1. Code Changes
```bash
# Commit and push changes
git add .
git commit -m "AI Assistant production deployment fixes"
git push origin main
```

### 2. Production Deployment
```bash
# On production server
git pull origin main
docker compose -f docker-compose.prod.yml build --no-cache ai_assistant
docker compose -f docker-compose.prod.yml restart ai_assistant
```

### 3. Database Migration (if needed)
```bash
# Run Alembic migration on production
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

## Testing Checklist

### Development Testing
- [ ] AI Assistant service starts without errors
- [ ] Health endpoint responds: `curl http://localhost:8001/health`
- [ ] Admin interface loads: `http://localhost:8001/admin`
- [ ] Document upload works
- [ ] Knowledge base API endpoints respond correctly

### Production Testing
- [ ] AI Assistant service healthy in production
- [ ] Admin interface accessible: `https://abparts.oraseas.com/ai/admin`
- [ ] Document upload and processing works
- [ ] No console errors in browser
- [ ] Knowledge base search functionality works

## Troubleshooting

### Common Issues

1. **404 on knowledge endpoints**
   - Check router prefix in `ai_assistant/app/main.py`
   - Ensure nginx proxy configuration is correct

2. **401 Unauthorized errors**
   - Verify API_BASE URL in `admin.html`
   - Check nginx routing configuration

3. **Database table not found**
   - Run Alembic migration: `alembic upgrade head`
   - Or manually create tables using `sync_production_schema.py`

4. **Container build issues**
   - Use `--no-cache` flag: `docker compose build --no-cache ai_assistant`
   - Check Dockerfile and dependencies

### Logs and Debugging

```bash
# Check AI Assistant logs
docker compose -f docker-compose.prod.yml logs ai_assistant

# Check specific service health
docker compose -f docker-compose.prod.yml ps

# Test API endpoints directly
curl -X GET "http://localhost:8001/knowledge/documents"
curl -X GET "http://localhost:8001/knowledge/stats"
```

## Future Deployments

With this setup, future AI Assistant deployments should be seamless:

1. Make changes in development
2. Test locally with `docker-compose up ai_assistant`
3. Commit and push changes
4. Deploy to production with standard Docker commands
5. Run migrations if database schema changes

The development and production environments now have matching configurations and database schemas.