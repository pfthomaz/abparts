# AI Assistant Operations Runbook

## Quick Reference

### Service Information
- **Service Name**: AI Assistant (ai_assistant)
- **Port**: 8001
- **Health Check**: http://localhost:8001/health
- **Admin Interface**: http://localhost:8001/admin
- **Analytics**: http://localhost:8001/analytics
- **API Docs**: http://localhost:8001/docs

### Common Commands

```bash
# Service Management
docker compose -f docker-compose.prod.yml ps ai_assistant          # Check status
docker compose -f docker-compose.prod.yml logs -f ai_assistant     # View logs
docker compose -f docker-compose.prod.yml restart ai_assistant     # Restart
docker compose -f docker-compose.prod.yml stop ai_assistant        # Stop
docker compose -f docker-compose.prod.yml up -d ai_assistant       # Start

# Health Checks
curl http://localhost:8001/health                                  # Service health
curl http://localhost:8001/info                                    # Service info
./logs/ai_assistant/monitor.sh                                     # Full monitoring

# Logs
docker compose -f docker-compose.prod.yml logs --tail=100 ai_assistant  # Last 100 lines
docker compose -f docker-compose.prod.yml logs --since="1h" ai_assistant # Last hour
tail -f logs/ai_assistant/ai_assistant.log                              # Application logs
tail -f logs/ai_assistant/ai_assistant_errors.log                       # Error logs only
```

## Standard Operating Procedures

### SOP-001: Service Restart

**When to Use**: Service is unresponsive, high memory usage, after configuration changes

**Steps**:
1. Check current status:
   ```bash
   docker compose -f docker-compose.prod.yml ps ai_assistant
   ```

2. Review recent logs for errors:
   ```bash
   docker compose -f docker-compose.prod.yml logs --tail=50 ai_assistant
   ```

3. Restart service:
   ```bash
   docker compose -f docker-compose.prod.yml restart ai_assistant
   ```

4. Wait 30 seconds for service to start

5. Verify health:
   ```bash
   curl http://localhost:8001/health
   ```

6. Monitor logs for errors:
   ```bash
   docker compose -f docker-compose.prod.yml logs -f ai_assistant
   ```

**Expected Duration**: 1-2 minutes  
**Impact**: Brief service interruption (30-60 seconds)

### SOP-002: Configuration Update

**When to Use**: Changing environment variables, updating API keys

**Steps**:
1. Create backup of current configuration:
   ```bash
   cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
   ```

2. Edit configuration:
   ```bash
   nano .env.production
   ```

3. Validate configuration:
   ```bash
   ./ai_assistant/scripts/validate_config.sh
   ```

4. Restart service to apply changes:
   ```bash
   docker compose -f docker-compose.prod.yml restart ai_assistant
   ```

5. Verify service is working:
   ```bash
   curl http://localhost:8001/health
   curl http://localhost:8001/info
   ```

6. Test functionality with sample chat

**Expected Duration**: 5-10 minutes  
**Impact**: Brief service interruption during restart

### SOP-003: Knowledge Base Update

**When to Use**: Adding new manuals, updating existing documentation

**Steps**:
1. Access admin interface:
   ```
   https://yourdomain.com/ai/admin
   ```

2. Click "Upload Document"

3. Select PDF file (AutoBoss manual)

4. Fill in metadata:
   - Title: Clear, descriptive name
   - Machine Models: Select applicable models
   - Tags: Add relevant tags (startup, troubleshooting, maintenance, etc.)
   - Language: Select document language

5. Click "Upload"

6. Wait for processing (may take 1-2 minutes)

7. Verify document appears in list

8. Test search functionality:
   - Search for key terms from the manual
   - Verify relevant results returned

9. Test in chat:
   - Ask question related to new content
   - Verify AI uses new information

**Expected Duration**: 5-10 minutes per document  
**Impact**: None (no service interruption)

### SOP-004: Log Review

**When to Use**: Daily monitoring, troubleshooting, incident investigation

**Steps**:
1. Check error logs:
   ```bash
   tail -100 logs/ai_assistant/ai_assistant_errors.log
   ```

2. Look for patterns:
   - Repeated errors
   - OpenAI API failures
   - Database connection issues
   - High response times

3. Check application logs:
   ```bash
   tail -200 logs/ai_assistant/ai_assistant.log | grep -i error
   ```

4. Review Docker logs:
   ```bash
   docker compose -f docker-compose.prod.yml logs --since="24h" ai_assistant | grep -i error
   ```

5. Check for warnings:
   ```bash
   docker compose -f docker-compose.prod.yml logs --since="24h" ai_assistant | grep -i warning
   ```

6. Document any issues found

7. Create tickets for recurring problems

**Expected Duration**: 10-15 minutes  
**Frequency**: Daily

### SOP-005: Performance Monitoring

**When to Use**: Daily monitoring, performance issues, capacity planning

**Steps**:
1. Run monitoring script:
   ```bash
   ./logs/ai_assistant/monitor.sh
   ```

2. Check resource usage:
   ```bash
   docker stats ai_assistant --no-stream
   ```

3. Review key metrics:
   - CPU usage (should be <50% average)
   - Memory usage (should be <1GB)
   - Response times (should be <5 seconds)
   - Error rate (should be <1%)

4. Check OpenAI API usage:
   - Log into OpenAI dashboard
   - Review token usage
   - Check costs
   - Verify rate limits

5. Review database performance:
   ```bash
   docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
   SELECT query, mean_exec_time, calls 
   FROM pg_stat_statements 
   WHERE query LIKE '%ai_%'
   ORDER BY mean_exec_time DESC 
   LIMIT 10;
   "
   ```

6. Document trends and anomalies

**Expected Duration**: 15-20 minutes  
**Frequency**: Daily

### SOP-006: Database Maintenance

**When to Use**: Weekly maintenance, performance degradation

**Steps**:
1. Check database size:
   ```bash
   docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
   SELECT 
       tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
   FROM pg_tables
   WHERE tablename LIKE 'ai_%'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
   "
   ```

2. Vacuum and analyze:
   ```bash
   docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
   VACUUM ANALYZE ai_sessions;
   VACUUM ANALYZE ai_messages;
   VACUUM ANALYZE knowledge_documents;
   "
   ```

3. Clean old sessions (older than 30 days):
   ```bash
   docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
   DELETE FROM ai_messages WHERE session_id IN (
       SELECT session_id FROM ai_sessions 
       WHERE created_at < NOW() - INTERVAL '30 days'
   );
   DELETE FROM ai_sessions WHERE created_at < NOW() - INTERVAL '30 days';
   "
   ```

4. Reindex tables:
   ```bash
   docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
   REINDEX TABLE ai_sessions;
   REINDEX TABLE ai_messages;
   "
   ```

5. Update statistics:
   ```bash
   docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
   ANALYZE;
   "
   ```

**Expected Duration**: 10-30 minutes  
**Frequency**: Weekly  
**Impact**: Minimal (operations continue during maintenance)

### SOP-007: Backup and Recovery

**When to Use**: Before major changes, regular backups, disaster recovery

**Backup Steps**:
1. Create backup directory:
   ```bash
   mkdir -p backups/ai_assistant_$(date +%Y%m%d)
   ```

2. Backup configuration:
   ```bash
   cp .env.production backups/ai_assistant_$(date +%Y%m%d)/
   cp docker-compose.prod.yml backups/ai_assistant_$(date +%Y%m%d)/
   ```

3. Backup database:
   ```bash
   docker compose -f docker-compose.prod.yml exec db pg_dump -U abparts_user -d abparts_prod \
       -t ai_sessions -t ai_messages -t knowledge_documents -t ai_escalations \
       > backups/ai_assistant_$(date +%Y%m%d)/ai_assistant_db.sql
   ```

4. Backup knowledge base:
   ```bash
   docker compose -f docker-compose.prod.yml exec db pg_dump -U abparts_user -d abparts_prod \
       -t knowledge_documents \
       > backups/ai_assistant_$(date +%Y%m%d)/knowledge_base.sql
   ```

5. Verify backup files created

**Recovery Steps**:
1. Stop service:
   ```bash
   docker compose -f docker-compose.prod.yml stop ai_assistant
   ```

2. Restore configuration:
   ```bash
   cp backups/ai_assistant_YYYYMMDD/.env.production .env.production
   ```

3. Restore database:
   ```bash
   docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod \
       < backups/ai_assistant_YYYYMMDD/ai_assistant_db.sql
   ```

4. Restart service:
   ```bash
   docker compose -f docker-compose.prod.yml up -d ai_assistant
   ```

5. Verify service is working

**Expected Duration**: 15-30 minutes  
**Frequency**: Weekly (backup), As needed (recovery)

## Troubleshooting Guide

### Issue: Service Won't Start

**Symptoms**:
- Container exits immediately
- Health check fails
- No response on port 8001

**Diagnosis**:
```bash
# Check container status
docker compose -f docker-compose.prod.yml ps ai_assistant

# Check logs
docker compose -f docker-compose.prod.yml logs --tail=50 ai_assistant

# Check port availability
sudo netstat -tulpn | grep 8001
```

**Common Causes & Solutions**:

1. **Missing environment variables**
   ```bash
   # Validate configuration
   ./ai_assistant/scripts/validate_config.sh
   ```

2. **Database connection failure**
   ```bash
   # Test database connection
   docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "SELECT 1"
   ```

3. **Port already in use**
   ```bash
   # Find process using port
   sudo lsof -i :8001
   # Kill process or change port
   ```

4. **Invalid OpenAI API key**
   ```bash
   # Test API key
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

### Issue: Slow Response Times

**Symptoms**:
- Chat responses take >10 seconds
- Timeout errors
- Users complaining about performance

**Diagnosis**:
```bash
# Check resource usage
docker stats ai_assistant --no-stream

# Check OpenAI API latency
time curl -X POST http://localhost:8001/api/ai/chat \
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

1. **High database load**
   - Run database maintenance (SOP-006)
   - Add indexes if needed
   - Optimize slow queries

2. **OpenAI API slow**
   - Check OpenAI status: https://status.openai.com/
   - Switch to fallback model (gpt-3.5-turbo)
   - Increase timeout values

3. **High memory usage**
   - Restart service
   - Increase container memory limit
   - Check for memory leaks

4. **Too many concurrent sessions**
   - Scale horizontally (add more containers)
   - Implement rate limiting
   - Clean up old sessions

### Issue: OpenAI API Errors

**Symptoms**:
- "OpenAI API error" in logs
- Chat responses fail
- Rate limit errors

**Diagnosis**:
```bash
# Check logs for OpenAI errors
docker compose -f docker-compose.prod.yml logs ai_assistant | grep -i openai

# Check API key validity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check OpenAI status
curl https://status.openai.com/api/v2/status.json
```

**Solutions**:

1. **Invalid API key**
   - Verify key in OpenAI dashboard
   - Update .env.production
   - Restart service

2. **Rate limit exceeded**
   - Check usage in OpenAI dashboard
   - Implement request queuing
   - Upgrade OpenAI plan

3. **Insufficient credits**
   - Add credits to OpenAI account
   - Set up billing alerts

4. **Model not available**
   - Check GPT-4 access
   - Use fallback model
   - Request access if needed

### Issue: Knowledge Base Not Working

**Symptoms**:
- Search returns no results
- AI doesn't use manual content
- Upload fails

**Diagnosis**:
```bash
# Check knowledge documents
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
SELECT document_id, title, document_type, language 
FROM knowledge_documents 
LIMIT 10;
"

# Check document count
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
SELECT COUNT(*) FROM knowledge_documents;
"

# Test search
curl -X POST http://localhost:8001/ai/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query": "startup procedure", "machine_model": "V4.0"}'
```

**Solutions**:

1. **No documents uploaded**
   - Upload manuals via admin interface
   - Follow SOP-003

2. **Documents not indexed**
   - Reindex knowledge base
   - Check embedding generation

3. **Search not finding relevant content**
   - Improve document metadata
   - Add more tags
   - Upload more comprehensive manuals

### Issue: High Error Rate

**Symptoms**:
- Many errors in logs
- Users reporting failures
- Alerts triggered

**Diagnosis**:
```bash
# Count errors in last hour
docker compose -f docker-compose.prod.yml logs --since="1h" ai_assistant | grep -c ERROR

# Check error types
docker compose -f docker-compose.prod.yml logs --since="1h" ai_assistant | grep ERROR | sort | uniq -c

# Check health endpoint
curl http://localhost:8001/health
```

**Solutions**:

1. **Dependency failures**
   - Check database connectivity
   - Check Redis connectivity
   - Check OpenAI API status

2. **Code errors**
   - Review recent deployments
   - Check for exceptions in logs
   - Consider rollback

3. **Resource exhaustion**
   - Check memory usage
   - Check CPU usage
   - Check disk space
   - Scale resources

## Escalation Procedures

### Level 1: On-Call Engineer
- Service restart
- Configuration changes
- Log review
- Basic troubleshooting

### Level 2: Senior Engineer
- Complex troubleshooting
- Performance optimization
- Database issues
- Code fixes

### Level 3: Development Team
- Critical bugs
- Architecture changes
- Major incidents
- Security issues

### Escalation Criteria

**Immediate Escalation** (Level 2+):
- Service down >15 minutes
- Data loss or corruption
- Security breach
- Complete functionality failure

**Escalate Within 1 Hour** (Level 2):
- High error rate (>10%)
- Severe performance degradation
- Repeated service crashes
- Database issues

**Escalate Within 4 Hours** (Level 2):
- Moderate performance issues
- Intermittent failures
- Configuration problems
- Knowledge base issues

## Monitoring and Alerts

### Key Metrics

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| Response Time | <5s | 5-10s | >10s |
| Error Rate | <1% | 1-5% | >5% |
| CPU Usage | <50% | 50-80% | >80% |
| Memory Usage | <1GB | 1-1.5GB | >1.5GB |
| Active Sessions | <50 | 50-100 | >100 |

### Alert Response

**Critical Alerts**:
- Respond within 15 minutes
- Follow troubleshooting guide
- Escalate if not resolved in 30 minutes

**Warning Alerts**:
- Respond within 1 hour
- Investigate root cause
- Document findings

**Info Alerts**:
- Review during business hours
- Track trends
- Plan improvements

## Maintenance Windows

### Scheduled Maintenance
- **Frequency**: Monthly
- **Duration**: 1-2 hours
- **Day**: First Sunday of month
- **Time**: 02:00-04:00 (low traffic period)

### Maintenance Activities
- Dependency updates
- Database optimization
- Knowledge base updates
- Performance tuning
- Security patches

### Communication
- Notify users 1 week in advance
- Send reminder 24 hours before
- Post status updates during maintenance
- Confirm completion after maintenance

## Contact Information

### On-Call Rotation
- Primary: [Name] - [Phone] - [Email]
- Secondary: [Name] - [Phone] - [Email]
- Manager: [Name] - [Phone] - [Email]

### External Support
- OpenAI Support: https://help.openai.com/
- Database Admin: [Contact]
- Network Team: [Contact]
- Security Team: [Contact]

### Documentation
- Deployment Guide: `ai_assistant/DEPLOYMENT_GUIDE.md`
- Production Checklist: `ai_assistant/PRODUCTION_CHECKLIST.md`
- API Documentation: http://localhost:8001/docs

---

**Runbook Version**: 1.0  
**Last Updated**: January 2024  
**Next Review**: [Date]  
**Owner**: [Team Name]
