# ABParts Troubleshooting & Maintenance Guide

**Version:** 1.0.0  
**Last Updated:** January 2025  
**Target Environment:** Production & Development  

---

## 📋 **Overview**

This comprehensive guide covers troubleshooting procedures, maintenance tasks, and operational best practices for the ABParts inventory management system. The guide is organized by component and includes both reactive troubleshooting and proactive maintenance procedures.

### **System Architecture Quick Reference**
- **Frontend:** React 18 SPA (Port 3000)
- **Backend API:** FastAPI Python (Port 8000)
- **Database:** PostgreSQL 15 (Port 5432)
- **Cache/Queue:** Redis 7 (Port 6379)
- **Reverse Proxy:** Nginx (Ports 80/443)
- **Containerization:** Docker & Docker Compose

---

## 🚨 **Emergency Procedures**

### **System Down - Complete Outage**

#### **Immediate Response (First 5 minutes)**
```bash
# 1. Check overall system status
docker-compose ps

# 2. Check container logs for errors
docker-compose logs --tail=50

# 3. Restart all services if needed
docker-compose restart

# 4. Verify database connectivity
docker-compose exec db pg_isready -U abparts_user
```

#### **If Database is Down**
```bash
# Check database container
docker-compose logs db

# Check disk space
df -h

# Restart database service
docker-compose restart db

# Verify database integrity
docker-compose exec db psql -U abparts_user -d abparts_prod -c "SELECT 1;"
```

#### **If API is Down**
```bash
# Check API logs
docker-compose logs api --tail=100

# Check for Python errors
docker-compose exec api python -c "import app.main; print('Import successful')"

# Restart API service
docker-compose restart api

# Test API health
curl -f http://localhost:8000/health
```

### **Data Corruption Emergency**
```bash
# 1. Stop all services immediately
docker-compose stop

# 2. Create emergency backup
docker-compose start db
docker-compose exec db pg_dump -U abparts_user abparts_prod > emergency_backup_$(date +%Y%m%d_%H%M%S).sql

# 3. Assess corruption extent
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del 
FROM pg_stat_user_tables 
ORDER BY n_tup_ins DESC;"

# 4. Contact support with backup and assessment
```

---

## 🔧 **Component-Specific Troubleshooting**

### **Database Issues**

#### **Connection Problems**
**Symptoms:** API cannot connect to database, connection timeouts
```bash
# Diagnose connection issues
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT count(*) as active_connections, 
       max_conn, 
       max_conn - count(*) as available_connections
FROM pg_stat_activity, 
     (SELECT setting::int as max_conn FROM pg_settings WHERE name='max_connections') mc;"

# Check for blocking queries
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT blocked_locks.pid AS blocked_pid,
       blocked_activity.usename AS blocked_user,
       blocking_locks.pid AS blocking_pid,
       blocking_activity.usename AS blocking_user,
       blocked_activity.query AS blocked_statement,
       blocking_activity.query AS current_statement_in_blocking_process
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;"

# Kill blocking queries if necessary
# docker-compose exec db psql -U abparts_user -d abparts_prod -c "SELECT pg_terminate_backend(PID);"
```

#### **Performance Issues**
**Symptoms:** Slow queries, high CPU usage, timeouts
```bash
# Check slow queries
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT query, calls, total_time, mean_time, rows
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"

# Check database size and growth
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
       pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY size_bytes DESC;"

# Check index usage
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats 
WHERE schemaname = 'public' 
ORDER BY n_distinct DESC;"
```

#### **Disk Space Issues**
**Symptoms:** Database write failures, transaction rollbacks
```bash
# Check disk usage
df -h

# Check database size
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT pg_size_pretty(pg_database_size('abparts_prod')) as db_size;"

# Clean up old WAL files (if safe)
docker-compose exec db psql -U abparts_user -d abparts_prod -c "CHECKPOINT;"

# Vacuum large tables
docker-compose exec db psql -U abparts_user -d abparts_prod -c "VACUUM ANALYZE;"
```

### **API Issues**

#### **High Response Times**
**Symptoms:** Slow API responses, timeouts, high CPU usage
```bash
# Check API process status
docker-compose exec api ps aux

# Monitor API logs for errors
docker-compose logs api --tail=100 -f

# Check memory usage
docker stats api

# Test specific endpoints
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/users/me/
```

Create `curl-format.txt`:
```
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
```

#### **Memory Leaks**
**Symptoms:** Gradually increasing memory usage, eventual crashes
```bash
# Monitor memory usage over time
docker stats api --no-stream

# Check for memory leaks in Python
docker-compose exec api python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"

# Restart API if memory usage is excessive
docker-compose restart api
```

#### **Authentication Issues**
**Symptoms:** Login failures, token validation errors, permission denied
```bash
# Check JWT configuration
docker-compose exec api python -c "
from app.auth import verify_token
print('JWT configuration loaded successfully')
"

# Test token generation
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=password"

# Check user status in database
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT id, username, email, role, user_status, failed_login_attempts, locked_until
FROM users 
WHERE email = 'admin@example.com';"
```

### **Frontend Issues**

#### **Build Failures**
**Symptoms:** Frontend container fails to start, build errors
```bash
# Check frontend build logs
docker-compose logs web

# Rebuild frontend container
docker-compose build --no-cache web

# Check Node.js and npm versions
docker-compose exec web node --version
docker-compose exec web npm --version

# Clear npm cache and rebuild
docker-compose exec web npm cache clean --force
docker-compose exec web npm install
```

#### **API Connection Issues**
**Symptoms:** Frontend cannot reach backend, CORS errors
```bash
# Check frontend environment variables
docker-compose exec web env | grep REACT_APP

# Test API connectivity from frontend container
docker-compose exec web curl -f http://api:8000/health

# Check CORS configuration in backend
docker-compose logs api | grep -i cors
```

### **Redis Issues**

#### **Connection Problems**
**Symptoms:** Cache misses, session issues, task queue failures
```bash
# Check Redis connectivity
docker-compose exec redis redis-cli ping

# Check Redis memory usage
docker-compose exec redis redis-cli info memory

# Check Redis connections
docker-compose exec redis redis-cli info clients

# Clear Redis cache if needed
docker-compose exec redis redis-cli flushall
```

#### **Memory Issues**
**Symptoms:** Redis out of memory, eviction warnings
```bash
# Check Redis memory configuration
docker-compose exec redis redis-cli config get maxmemory

# Check memory usage details
docker-compose exec redis redis-cli info memory | grep used_memory

# Set memory limit if needed
docker-compose exec redis redis-cli config set maxmemory 256mb
docker-compose exec redis redis-cli config set maxmemory-policy allkeys-lru
```

---

## 🔍 **Diagnostic Tools & Commands**

### **System Health Checks**
```bash
# Complete system health check script
#!/bin/bash
echo "=== ABParts System Health Check ==="
echo "Timestamp: $(date)"
echo

echo "=== Container Status ==="
docker-compose ps
echo

echo "=== Database Health ==="
docker-compose exec db pg_isready -U abparts_user
echo

echo "=== API Health ==="
curl -s http://localhost:8000/health | jq .
echo

echo "=== Redis Health ==="
docker-compose exec redis redis-cli ping
echo

echo "=== Disk Usage ==="
df -h
echo

echo "=== Memory Usage ==="
free -h
echo

echo "=== Recent Errors ==="
docker-compose logs --tail=10 | grep -i error
```

### **Performance Monitoring**
```bash
# Monitor system resources
watch -n 5 'docker stats --no-stream'

# Monitor database performance
watch -n 10 'docker-compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT count(*) as connections, 
       state, 
       wait_event_type 
FROM pg_stat_activity 
GROUP BY state, wait_event_type 
ORDER BY connections DESC;"'

# Monitor API response times
while true; do
  curl -w "API Response Time: %{time_total}s\n" -o /dev/null -s http://localhost:8000/health
  sleep 30
done
```

### **Log Analysis**
```bash
# Search for specific errors
docker-compose logs | grep -i "error\|exception\|failed"

# Monitor real-time logs
docker-compose logs -f --tail=50

# Export logs for analysis
docker-compose logs > system_logs_$(date +%Y%m%d_%H%M%S).log

# Analyze error patterns
docker-compose logs | grep -i error | sort | uniq -c | sort -nr
```

---

## 🛠️ **Maintenance Procedures**

### **Daily Maintenance Tasks**

#### **Automated Daily Script**
```bash
#!/bin/bash
# /opt/abparts/scripts/daily_maintenance.sh

LOG_FILE="/opt/abparts/logs/maintenance_$(date +%Y%m%d).log"
exec > >(tee -a $LOG_FILE)
exec 2>&1

echo "=== Daily Maintenance Started: $(date) ==="

# 1. Health check
echo "Performing health check..."
docker-compose exec db pg_isready -U abparts_user
curl -f http://localhost:8000/health

# 2. Database maintenance
echo "Running database maintenance..."
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
ANALYZE;
SELECT pg_stat_reset();
"

# 3. Log rotation
echo "Rotating logs..."
find /opt/abparts/logs -name "*.log" -mtime +7 -delete

# 4. Backup verification
echo "Verifying latest backup..."
LATEST_BACKUP=$(ls -t /opt/abparts/backups/backup_*.sql.gz | head -1)
if [ -f "$LATEST_BACKUP" ]; then
    echo "Latest backup: $LATEST_BACKUP"
    echo "Backup size: $(du -h $LATEST_BACKUP | cut -f1)"
else
    echo "WARNING: No recent backup found!"
fi

# 5. Security check
echo "Checking for failed login attempts..."
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT COUNT(*) as failed_attempts, ip_address 
FROM security_events 
WHERE event_type = 'login_failed' 
  AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY ip_address 
HAVING COUNT(*) > 10
ORDER BY failed_attempts DESC;"

echo "=== Daily Maintenance Completed: $(date) ==="
```

### **Weekly Maintenance Tasks**

#### **Automated Weekly Script**
```bash
#!/bin/bash
# /opt/abparts/scripts/weekly_maintenance.sh

LOG_FILE="/opt/abparts/logs/weekly_maintenance_$(date +%Y%m%d).log"
exec > >(tee -a $LOG_FILE)
exec 2>&1

echo "=== Weekly Maintenance Started: $(date) ==="

# 1. Database optimization
echo "Optimizing database..."
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
VACUUM ANALYZE;
REINDEX DATABASE abparts_prod;
"

# 2. Update container images
echo "Updating container images..."
docker-compose pull
docker-compose up -d

# 3. Clean up Docker resources
echo "Cleaning up Docker resources..."
docker system prune -f
docker volume prune -f

# 4. Security updates
echo "Checking for security updates..."
docker-compose exec api pip list --outdated
docker-compose exec web npm audit

# 5. Performance analysis
echo "Analyzing performance metrics..."
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC 
LIMIT 10;"

echo "=== Weekly Maintenance Completed: $(date) ==="
```

### **Monthly Maintenance Tasks**

#### **Database Maintenance**
```bash
# Full database maintenance
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
-- Update table statistics
ANALYZE;

-- Rebuild indexes
REINDEX DATABASE abparts_prod;

-- Check for bloated tables
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
       pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

#### **Security Audit**
```bash
# Security audit script
#!/bin/bash
echo "=== Monthly Security Audit ==="

# Check for suspicious login patterns
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT event_type, COUNT(*) as count, 
       DATE_TRUNC('day', timestamp) as day
FROM security_events 
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY event_type, DATE_TRUNC('day', timestamp)
ORDER BY day DESC, count DESC;"

# Check user account status
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT user_status, COUNT(*) as count
FROM users 
GROUP BY user_status;"

# Check for inactive users
docker-compose exec db psql -U abparts_user -d abparts_prod -c "
SELECT username, email, last_login, 
       EXTRACT(days FROM NOW() - last_login) as days_since_login
FROM users 
WHERE last_login < NOW() - INTERVAL '30 days'
  AND user_status = 'active'
ORDER BY last_login ASC;"
```

### **Backup Procedures**

#### **Automated Backup Script**
```bash
#!/bin/bash
# /opt/abparts/scripts/backup.sh

BACKUP_DIR="/opt/abparts/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

echo "Starting backup at $(date)"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create database backup
docker-compose exec -T db pg_dump -U abparts_user abparts_prod > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "Database backup successful: $BACKUP_FILE"
    
    # Compress backup
    gzip $BACKUP_FILE
    echo "Backup compressed: $BACKUP_FILE.gz"
    
    # Upload to cloud storage (if configured)
    if [ ! -z "$AWS_S3_BUCKET" ]; then
        aws s3 cp $BACKUP_FILE.gz s3://$AWS_S3_BUCKET/backups/
        echo "Backup uploaded to S3"
    fi
    
    # Clean up old backups (keep last 30 days)
    find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
    echo "Old backups cleaned up"
    
else
    echo "ERROR: Database backup failed!"
    exit 1
fi

echo "Backup completed at $(date)"
```

#### **Backup Verification**
```bash
#!/bin/bash
# Verify backup integrity
LATEST_BACKUP=$(ls -t /opt/abparts/backups/backup_*.sql.gz | head -1)

if [ -f "$LATEST_BACKUP" ]; then
    echo "Verifying backup: $LATEST_BACKUP"
    
    # Test backup file integrity
    gunzip -t $LATEST_BACKUP
    if [ $? -eq 0 ]; then
        echo "Backup file integrity: OK"
    else
        echo "ERROR: Backup file is corrupted!"
        exit 1
    fi
    
    # Test restore (to temporary database)
    echo "Testing restore process..."
    docker-compose exec db createdb -U abparts_user test_restore
    gunzip -c $LATEST_BACKUP | docker-compose exec -T db psql -U abparts_user test_restore
    
    if [ $? -eq 0 ]; then
        echo "Backup restore test: OK"
        docker-compose exec db dropdb -U abparts_user test_restore
    else
        echo "ERROR: Backup restore test failed!"
        docker-compose exec db dropdb -U abparts_user test_restore
        exit 1
    fi
else
    echo "ERROR: No backup file found!"
    exit 1
fi
```

---

## 📊 **Monitoring & Alerting**

### **Key Metrics to Monitor**

#### **System Metrics**
- CPU usage > 80% for 5+ minutes
- Memory usage > 90% for 5+ minutes
- Disk usage > 85%
- Network connectivity issues

#### **Database Metrics**
- Connection count > 80% of max_connections
- Query response time > 5 seconds
- Database size growth > 10% per week
- Failed transactions > 1% of total

#### **Application Metrics**
- API response time > 2 seconds
- Error rate > 5% of requests
- Failed login attempts > 10 per hour from single IP
- Session count > expected maximum

### **Alerting Configuration**

#### **Email Alerts Script**
```bash
#!/bin/bash
# /opt/abparts/scripts/send_alert.sh

ALERT_TYPE=$1
ALERT_MESSAGE=$2
ALERT_EMAIL="admin@yourdomain.com"

# Send email alert
echo "Subject: ABParts Alert - $ALERT_TYPE
Date: $(date)
System: $(hostname)

$ALERT_MESSAGE

Please investigate immediately.

System Status:
$(docker-compose ps)
" | sendmail $ALERT_EMAIL

# Log alert
echo "$(date): ALERT - $ALERT_TYPE - $ALERT_MESSAGE" >> /opt/abparts/logs/alerts.log
```

#### **Health Check with Alerting**
```bash
#!/bin/bash
# /opt/abparts/scripts/health_check_with_alerts.sh

# Check database
if ! docker-compose exec db pg_isready -U abparts_user > /dev/null 2>&1; then
    /opt/abparts/scripts/send_alert.sh "DATABASE_DOWN" "PostgreSQL database is not responding"
fi

# Check API
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    /opt/abparts/scripts/send_alert.sh "API_DOWN" "FastAPI service is not responding"
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    /opt/abparts/scripts/send_alert.sh "DISK_SPACE_LOW" "Disk usage is at $DISK_USAGE%"
fi

# Check memory usage
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEMORY_USAGE -gt 90 ]; then
    /opt/abparts/scripts/send_alert.sh "MEMORY_HIGH" "Memory usage is at $MEMORY_USAGE%"
fi
```

---

## 🔄 **Recovery Procedures**

### **Database Recovery**

#### **Point-in-Time Recovery**
```bash
# Stop all services
docker-compose stop

# Restore from backup
BACKUP_FILE="/opt/abparts/backups/backup_20250120_140000.sql.gz"

# Create new database
docker-compose start db
docker-compose exec db createdb -U abparts_user abparts_prod_new

# Restore backup
gunzip -c $BACKUP_FILE | docker-compose exec -T db psql -U abparts_user abparts_prod_new

# Rename databases
docker-compose exec db psql -U abparts_user -c "
ALTER DATABASE abparts_prod RENAME TO abparts_prod_old;
ALTER DATABASE abparts_prod_new RENAME TO abparts_prod;
"

# Start all services
docker-compose up -d

# Verify recovery
curl -f http://localhost:8000/health
```

#### **Disaster Recovery**
```bash
# Complete system recovery procedure
#!/bin/bash
echo "=== DISASTER RECOVERY PROCEDURE ==="
echo "Starting at: $(date)"

# 1. Stop all services
echo "Stopping all services..."
docker-compose down

# 2. Backup current state (if possible)
echo "Creating emergency backup of current state..."
if docker-compose start db; then
    docker-compose exec db pg_dump -U abparts_user abparts_prod > emergency_backup_$(date +%Y%m%d_%H%M%S).sql
    docker-compose stop db
fi

# 3. Clean up containers and volumes
echo "Cleaning up containers and volumes..."
docker-compose down -v
docker system prune -f

# 4. Restore from latest backup
echo "Restoring from latest backup..."
LATEST_BACKUP=$(ls -t /opt/abparts/backups/backup_*.sql.gz | head -1)
echo "Using backup: $LATEST_BACKUP"

# 5. Start database service
docker-compose up -d db
sleep 30

# 6. Restore database
gunzip -c $LATEST_BACKUP | docker-compose exec -T db psql -U abparts_user abparts_prod

# 7. Start all services
echo "Starting all services..."
docker-compose up -d

# 8. Verify recovery
echo "Verifying recovery..."
sleep 60
curl -f http://localhost:8000/health

echo "=== DISASTER RECOVERY COMPLETED ==="
echo "Completed at: $(date)"
```

---

## 📞 **Support & Escalation**

### **Support Levels**

#### **Level 1: Basic Issues**
- Service restarts
- Log analysis
- Basic configuration changes
- User account issues

#### **Level 2: Advanced Issues**
- Database performance problems
- Security incidents
- Complex configuration issues
- Integration problems

#### **Level 3: Critical Issues**
- Data corruption
- Security breaches
- System architecture changes
- Disaster recovery

### **Escalation Procedures**

#### **When to Escalate**
- System down for > 30 minutes
- Data integrity issues
- Security incidents
- Performance degradation > 50%
- Multiple component failures

#### **Escalation Contacts**
- **Level 1 Support:** support@yourdomain.com
- **Level 2 Support:** technical@yourdomain.com
- **Level 3 Support:** emergency@yourdomain.com
- **Security Issues:** security@yourdomain.com

### **Incident Response**

#### **Incident Classification**
- **P1 (Critical):** System down, data loss, security breach
- **P2 (High):** Major functionality impaired, performance issues
- **P3 (Medium):** Minor functionality issues, workarounds available
- **P4 (Low):** Cosmetic issues, feature requests

#### **Response Times**
- **P1:** 15 minutes
- **P2:** 2 hours
- **P3:** 24 hours
- **P4:** 72 hours

---

## 📚 **Reference Information**

### **Important File Locations**
- **Configuration:** `/opt/abparts/.env`
- **Logs:** `/opt/abparts/logs/`
- **Backups:** `/opt/abparts/backups/`
- **Scripts:** `/opt/abparts/scripts/`
- **SSL Certificates:** `/opt/abparts/nginx/ssl/`

### **Default Credentials**
- **Database:** `abparts_user` / (see .env file)
- **PgAdmin:** `admin@abparts.com` / `admin123`
- **Default Super Admin:** (created during setup)

### **Port Reference**
- **Frontend:** 3000
- **Backend API:** 8000
- **Database:** 5432
- **Redis:** 6379
- **PgAdmin:** 8080
- **Nginx HTTP:** 80
- **Nginx HTTPS:** 443

### **Useful Commands Quick Reference**
```bash
# System status
docker-compose ps
docker-compose logs --tail=50

# Database access
docker-compose exec db psql -U abparts_user abparts_prod

# API testing
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Backup
docker-compose exec db pg_dump -U abparts_user abparts_prod > backup.sql

# Restart services
docker-compose restart
docker-compose restart api
docker-compose restart db

# View resource usage
docker stats
df -h
free -h
```

---

**Last Updated:** January 2025  
**Version:** 1.0.0  
**Next Review:** February 2025

For additional support, consult the deployment guide and API documentation, or contact the support team.