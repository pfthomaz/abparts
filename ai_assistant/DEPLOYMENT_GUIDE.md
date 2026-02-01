# AutoBoss AI Assistant - Production Deployment Guide

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Deployment Steps](#deployment-steps)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Health Checks](#health-checks)
8. [Troubleshooting](#troubleshooting)
9. [Rollback Procedures](#rollback-procedures)
10. [Maintenance](#maintenance)

## Overview

The AutoBoss AI Assistant is a microservice that provides intelligent troubleshooting support for AutoBoss machines. This guide covers the complete deployment process for production environments.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Production Environment                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Nginx      │───▶│ AI Assistant │───▶│  PostgreSQL  │  │
│  │  (Reverse    │    │   Service    │    │   Database   │  │
│  │   Proxy)     │    │  (Port 8001) │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                               │
│         │                    ▼                               │
│         │            ┌──────────────┐                        │
│         │            │    Redis     │                        │
│         │            │   (Session   │                        │
│         │            │   Storage)   │                        │
│         │            └──────────────┘                        │
│         │                    │                               │
│         ▼                    ▼                               │
│  ┌──────────────┐    ┌──────────────┐                       │
│  │   ABParts    │    │   OpenAI     │                       │
│  │   Frontend   │    │     API      │                       │
│  └──────────────┘    └──────────────┘                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 20.04 LTS or later (or equivalent Linux distribution)
- **Docker**: Version 20.10 or later
- **Docker Compose**: Version 2.0 or later
- **Memory**: Minimum 2GB RAM allocated to AI Assistant container
- **Storage**: Minimum 10GB free disk space
- **Network**: Outbound HTTPS access to OpenAI API (api.openai.com)

### Required Accounts and Keys

1. **OpenAI API Key**: Required for LLM functionality
   - Sign up at https://platform.openai.com/
   - Generate API key with GPT-4 access
   - Ensure sufficient credits/quota

2. **SMTP Credentials**: Required for escalation emails
   - Gmail, Microsoft 365, or custom SMTP server
   - App-specific password if using 2FA

3. **Database Access**: PostgreSQL database credentials
   - Shared with main ABParts application
   - Requires CREATE TABLE permissions

### Software Dependencies

All dependencies are containerized. The following are included in the Docker image:

- Python 3.11
- FastAPI 0.104.1
- OpenAI Python SDK 1.3.7
- SQLAlchemy 2.0.23
- Redis client 5.0.1
- Additional dependencies in `requirements.txt`

## Environment Configuration

### 1. Create Production Environment File

Copy the template and fill in actual values:

```bash
cp .env.production.template .env.production
```

### 2. Required Environment Variables

Edit `.env.production` and configure the following:

#### Core Configuration

```bash
# Environment
ENVIRONMENT=production
DEBUG=false

# Database (shared with ABParts)
DATABASE_URL=postgresql://abparts_user:YOUR_PASSWORD@db:5432/abparts_prod
POSTGRES_USER=abparts_user
POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD
POSTGRES_DB=abparts_prod

# Redis (use separate database number)
REDIS_URL=redis://redis:6379/2
```

#### OpenAI Configuration

```bash
# OpenAI API
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4
OPENAI_FALLBACK_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7
OPENAI_TIMEOUT=30
```

#### SMTP Configuration (for escalation emails)

```bash
# Email Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your.noreply@gmail.com
SMTP_PASSWORD=your_app_specific_password
FROM_EMAIL=your.noreply@gmail.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

#### CORS Configuration

```bash
# CORS (adjust for your domain)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### Integration Configuration

```bash
# ABParts Integration
ABPARTS_API_URL=http://api:8000
ABPARTS_API_BASE_URL=http://api:8000/api
```

### 3. Security Best Practices

- **Never commit `.env.production` to version control**
- Use strong, unique passwords for all services
- Rotate API keys regularly (every 90 days recommended)
- Use environment-specific credentials (don't reuse dev credentials)
- Enable 2FA on all external service accounts
- Store backup copies of credentials in secure password manager

### 4. Validate Configuration

Run the validation script:

```bash
./ai_assistant/scripts/validate_config.sh
```

This checks:
- All required variables are set
- Database connectivity
- Redis connectivity
- OpenAI API key validity
- SMTP configuration

## Database Setup

### 1. Database Tables

The AI Assistant requires the following tables:

- `ai_sessions` - Conversation sessions
- `ai_messages` - Chat messages
- `knowledge_documents` - Knowledge base content
- `ai_escalations` - Support escalations
- `ai_analytics_events` - Usage analytics
- `ai_user_consents` - Privacy consents
- `ai_audit_logs` - Audit trail

### 2. Create Tables

Tables are automatically created on first startup. To manually create:

```bash
# Using Docker Compose
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import asyncio
from app.database import init_database
asyncio.run(init_database())
"
```

### 3. Verify Tables

```bash
# Connect to database
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod

# List AI Assistant tables
\dt ai_*

# Check table structure
\d ai_sessions
\d ai_messages
\d knowledge_documents
```

### 4. Initial Data

Upload AutoBoss manuals to the knowledge base:

1. Access admin interface: `https://yourdomain.com/ai/admin`
2. Upload PDF manuals for each machine model
3. Verify documents are indexed correctly

## Deployment Steps

### Method 1: Automated Deployment Script (Recommended)

```bash
# Navigate to AI Assistant directory
cd ai_assistant

# Make script executable
chmod +x deploy_production.sh

# Run deployment
./deploy_production.sh

# With options
./deploy_production.sh --skip-backup  # Skip backup creation
./deploy_production.sh --skip-tests   # Skip health checks
./deploy_production.sh --force        # Force deployment even if checks fail
```

The script will:
1. Check prerequisites
2. Validate environment variables
3. Create backups
4. Build Docker image
5. Stop existing service
6. Start new service
7. Run health checks
8. Setup monitoring
9. Display deployment summary

### Method 2: Manual Deployment

#### Step 1: Pull Latest Code

```bash
cd /path/to/abparts
git pull origin main
```

#### Step 2: Build AI Assistant Image

```bash
docker compose -f docker-compose.prod.yml build ai_assistant
```

#### Step 3: Stop Existing Service

```bash
docker compose -f docker-compose.prod.yml stop ai_assistant
```

#### Step 4: Start New Service

```bash
docker compose -f docker-compose.prod.yml up -d ai_assistant
```

#### Step 5: Verify Deployment

```bash
# Check service status
docker compose -f docker-compose.prod.yml ps ai_assistant

# Check logs
docker compose -f docker-compose.prod.yml logs -f ai_assistant

# Test health endpoint
curl http://localhost:8001/health
```

### Method 3: Zero-Downtime Deployment

For production environments requiring zero downtime:

```bash
# Start new container with different name
docker compose -f docker-compose.prod.yml up -d --scale ai_assistant=2

# Wait for new container to be healthy
sleep 30

# Stop old container
docker compose -f docker-compose.prod.yml stop ai_assistant

# Scale back to 1
docker compose -f docker-compose.prod.yml up -d --scale ai_assistant=1
```

## Monitoring and Logging

### 1. Log Locations

Logs are stored in the following locations:

```
logs/ai_assistant/
├── ai_assistant.log          # All logs
├── ai_assistant_errors.log   # Errors only
└── monitor.sh                # Monitoring script
```

### 2. View Logs

```bash
# Real-time logs
docker compose -f docker-compose.prod.yml logs -f ai_assistant

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100 ai_assistant

# Logs from specific time
docker compose -f docker-compose.prod.yml logs --since="2024-01-15T10:00:00" ai_assistant

# Error logs only
docker compose -f docker-compose.prod.yml logs ai_assistant | grep ERROR
```

### 3. Monitoring Script

Run the monitoring script for comprehensive status:

```bash
./logs/ai_assistant/monitor.sh
```

This displays:
- Service status
- Health check results
- Recent logs
- Resource usage
- OpenAI API connectivity

### 4. Metrics and Alerts

If Prometheus is configured:

- **Metrics endpoint**: `http://localhost:8001/metrics`
- **Prometheus UI**: `http://localhost:9090`
- **Grafana dashboards**: `http://localhost:3000`

Key metrics to monitor:
- Request rate and latency
- Error rate
- OpenAI API usage and costs
- Database query performance
- Memory and CPU usage
- Active session count

### 5. Log Rotation

Configure log rotation to prevent disk space issues:

```bash
# Copy logrotate config
sudo cp ai_assistant/monitoring/logrotate.conf /etc/logrotate.d/ai_assistant

# Test configuration
sudo logrotate -d /etc/logrotate.d/ai_assistant

# Force rotation
sudo logrotate -f /etc/logrotate.d/ai_assistant
```

## Health Checks

### 1. Service Health Endpoint

```bash
curl http://localhost:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "openai": "ok"
  }
}
```

### 2. Service Info Endpoint

```bash
curl http://localhost:8001/info
```

Returns service configuration and capabilities.

### 3. Component Health Checks

#### Database Connectivity

```bash
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
from app.database import engine
with engine.connect() as conn:
    print('Database: OK')
"
```

#### Redis Connectivity

```bash
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
from app.session_manager import session_manager
import asyncio
asyncio.run(session_manager.initialize())
print('Redis: OK')
"
```

#### OpenAI API

```bash
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
from app.llm_client import LLMClient
import asyncio
async def test():
    client = LLMClient()
    await client.initialize()
    print('OpenAI: OK')
asyncio.run(test())
"
```

### 4. Automated Health Monitoring

Set up a cron job for continuous monitoring:

```bash
# Add to crontab
*/5 * * * * /path/to/abparts/logs/ai_assistant/monitor.sh >> /var/log/ai_assistant_health.log 2>&1
```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start

**Symptoms**: Container exits immediately or fails to start

**Diagnosis**:
```bash
# Check logs
docker compose -f docker-compose.prod.yml logs ai_assistant

# Check container status
docker compose -f docker-compose.prod.yml ps ai_assistant
```

**Common Causes**:
- Missing environment variables
- Database connection failure
- Port 8001 already in use
- Invalid OpenAI API key

**Solutions**:
```bash
# Verify environment variables
docker compose -f docker-compose.prod.yml config

# Check port availability
sudo netstat -tulpn | grep 8001

# Test database connection
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "SELECT 1"

# Validate OpenAI API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### 2. OpenAI API Errors

**Symptoms**: "OpenAI API error" in logs, chat responses fail

**Diagnosis**:
```bash
# Check OpenAI API status
curl https://status.openai.com/api/v2/status.json

# Test API key
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import openai
openai.api_key = 'YOUR_KEY'
print(openai.Model.list())
"
```

**Common Causes**:
- Invalid or expired API key
- Insufficient credits/quota
- Rate limiting
- Network connectivity issues

**Solutions**:
- Verify API key in OpenAI dashboard
- Check billing and usage limits
- Implement exponential backoff
- Use fallback model (GPT-3.5-turbo)

#### 3. Database Connection Issues

**Symptoms**: "Database connection failed" errors

**Diagnosis**:
```bash
# Check database container
docker compose -f docker-compose.prod.yml ps db

# Test connection
docker compose -f docker-compose.prod.yml exec db pg_isready
```

**Solutions**:
```bash
# Restart database
docker compose -f docker-compose.prod.yml restart db

# Check connection string
echo $DATABASE_URL

# Verify credentials
docker compose -f docker-compose.prod.yml exec db psql -U $POSTGRES_USER -d $POSTGRES_DB
```

#### 4. High Memory Usage

**Symptoms**: Container using excessive memory, OOM kills

**Diagnosis**:
```bash
# Check memory usage
docker stats ai_assistant --no-stream

# Check for memory leaks
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import psutil
print(f'Memory: {psutil.virtual_memory().percent}%')
"
```

**Solutions**:
- Increase container memory limit
- Implement session cleanup
- Reduce concurrent requests
- Monitor for memory leaks

#### 5. Slow Response Times

**Symptoms**: Chat responses take >30 seconds

**Diagnosis**:
```bash
# Check OpenAI API latency
time curl http://localhost:8001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "session_id": "test"}'

# Check database query performance
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
"
```

**Solutions**:
- Optimize database queries
- Implement caching
- Use faster OpenAI model
- Increase timeout values

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Set in .env.production
DEBUG=true
LOG_LEVEL=DEBUG

# Restart service
docker compose -f docker-compose.prod.yml restart ai_assistant
```

**Warning**: Debug mode logs sensitive information. Disable in production after troubleshooting.

## Rollback Procedures

### Quick Rollback

If deployment fails, rollback to previous version:

```bash
# Stop new service
docker compose -f docker-compose.prod.yml stop ai_assistant

# Restore from backup
BACKUP_DIR="backups/ai_assistant_YYYYMMDD_HHMMSS"
cp $BACKUP_DIR/docker-compose.prod.yml docker-compose.prod.yml
cp $BACKUP_DIR/.env.production .env.production

# Rebuild and restart
docker compose -f docker-compose.prod.yml build ai_assistant
docker compose -f docker-compose.prod.yml up -d ai_assistant
```

### Database Rollback

If database changes need to be reverted:

```bash
# Restore from database backup
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod < backup.sql

# Or drop AI Assistant tables
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
DROP TABLE IF EXISTS ai_sessions CASCADE;
DROP TABLE IF EXISTS ai_messages CASCADE;
DROP TABLE IF EXISTS knowledge_documents CASCADE;
"
```

## Maintenance

### Regular Maintenance Tasks

#### Daily
- Monitor error logs
- Check OpenAI API usage and costs
- Verify health checks passing

#### Weekly
- Review escalation patterns
- Update knowledge base content
- Check disk space usage
- Review performance metrics

#### Monthly
- Rotate API keys
- Update dependencies
- Review and optimize database
- Backup knowledge base
- Review and update documentation

### Database Maintenance

```bash
# Vacuum database
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "VACUUM ANALYZE;"

# Check table sizes
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename LIKE 'ai_%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# Clean old sessions (older than 30 days)
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
DELETE FROM ai_sessions 
WHERE created_at < NOW() - INTERVAL '30 days';
"
```

### Knowledge Base Maintenance

```bash
# Backup knowledge base
docker compose -f docker-compose.prod.yml exec db pg_dump -U abparts_user -d abparts_prod \
  -t knowledge_documents > knowledge_base_backup.sql

# Reindex knowledge base
curl -X POST http://localhost:8001/ai/knowledge/reindex \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Update Procedures

#### Minor Updates (patches, bug fixes)

```bash
git pull origin main
docker compose -f docker-compose.prod.yml build ai_assistant
docker compose -f docker-compose.prod.yml up -d ai_assistant
```

#### Major Updates (new features, breaking changes)

1. Review changelog and migration guide
2. Create full backup
3. Test in staging environment
4. Schedule maintenance window
5. Deploy with monitoring
6. Verify all functionality
7. Monitor for 24 hours

## Support and Resources

### Documentation
- API Documentation: `http://localhost:8001/docs`
- Admin Interface: `http://localhost:8001/admin`
- Analytics Dashboard: `http://localhost:8001/analytics`

### Logs and Monitoring
- Application Logs: `logs/ai_assistant/`
- Docker Logs: `docker compose -f docker-compose.prod.yml logs ai_assistant`
- Monitoring Script: `logs/ai_assistant/monitor.sh`

### External Resources
- OpenAI Status: https://status.openai.com/
- OpenAI Documentation: https://platform.openai.com/docs
- FastAPI Documentation: https://fastapi.tiangolo.com/

### Emergency Contacts
- System Administrator: [contact info]
- Database Administrator: [contact info]
- OpenAI Support: https://help.openai.com/

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Maintained By**: ABParts Development Team
