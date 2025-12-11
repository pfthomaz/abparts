# User Profile Features - Docker Deployment Guide

## Quick Start

### 1. Run the Implementation Test
```bash
# Test the implementation inside the backend container
docker-compose exec backend python test_user_profile.py
```

### 2. Apply Database Migration
```bash
# Run the migration to add new user profile fields
docker-compose exec backend alembic upgrade head

# Or manually apply the SQL if needed
docker-compose exec postgres psql -U postgres -d abparts -c "
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_expires_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS pending_email VARCHAR(255);
"
```

### 3. Configure Environment Variables
Add to your `.env` file or docker-compose.yml:

```env
# Email Configuration (required for password reset and email verification)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
BASE_URL=http://localhost:3000

# Redis (required for Celery email tasks)
REDIS_URL=redis://redis:6379/0
```

### 4. Ensure Celery Worker is Running
Your docker-compose.yml should include:

```yaml
services:
  celery-worker:
    build: ./backend
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SMTP_SERVER=${SMTP_SERVER}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - FROM_EMAIL=${FROM_EMAIL}
      - BASE_URL=${BASE_URL}
    depends_on:
      - redis
      - postgres
```

## API Endpoints Reference

### User Profile Management

#### Get Current User Profile
```bash
curl -X GET "http://localhost:8000/users/me/profile" \
  -H "Authorization: Bearer <your-jwt-token>"
```

**Response:**
```json
{
  "id": "uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "name": "John Doe",
  "role": "USER",
  "user_status": "ACTIVE",
  "organization_id": "uuid",
  "organization_name": "Acme Corp",
  "organization_type": "customer",
  "last_login": "2025-07-16T10:30:00Z",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-07-16T10:30:00Z"
}
```

#### Update User Profile
```bash
curl -X PUT "http://localhost:8000/users/me/profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "name": "John Smith",
    "email": "john.smith@example.com"
  }'
```

**Note:** Email changes require verification via email.

### Password Management

#### Change Password (Requires Current Password)
```bash
curl -X POST "http://localhost:8000/users/me/change-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "current_password": "oldpassword123",
    "new_password": "newpassword456"
  }'
```

#### Request Password Reset (Public Endpoint)
```bash
curl -X POST "http://localhost:8000/users/request-password-reset" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

#### Confirm Password Reset
```bash
curl -X POST "http://localhost:8000/users/confirm-password-reset" \
  -H "Content-Type: application/json" \
  -d '{
    "reset_token": "secure-token-from-email",
    "new_password": "newpassword123"
  }'
```

### Email Verification

#### Request Email Verification
```bash
curl -X POST "http://localhost:8000/users/me/request-email-verification" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "new_email": "newemail@example.com"
  }'
```

#### Confirm Email Verification
```bash
curl -X POST "http://localhost:8000/users/confirm-email-verification" \
  -H "Content-Type: application/json" \
  -d '{
    "verification_token": "secure-token-from-email"
  }'
```

### Admin Functions

#### Update User Status (Admin Only)
```bash
curl -X PATCH "http://localhost:8000/users/{user_id}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin-jwt-token>" \
  -d '{
    "user_status": "INACTIVE"
  }'
```

**Valid statuses:** `ACTIVE`, `INACTIVE`, `PENDING_INVITATION`, `LOCKED`

## Testing in Docker Environment

### 1. Container Health Check
```bash
# Check if backend is running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Check Celery worker logs
docker-compose logs celery-worker
```

### 2. Database Verification
```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d abparts

# Check user table structure
\d users

# Check if new columns exist
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('email_verification_token', 'email_verification_expires_at', 'pending_email');

# Check invitation audit logs table
\d invitation_audit_logs
```

### 3. Email Testing
```bash
# Test SMTP connection (inside backend container)
docker-compose exec backend python -c "
import smtplib
import os
try:
    server = smtplib.SMTP(os.getenv('SMTP_SERVER', 'smtp.gmail.com'), int(os.getenv('SMTP_PORT', '587')))
    server.starttls()
    server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
    print('✅ SMTP connection successful')
    server.quit()
except Exception as e:
    print(f'❌ SMTP connection failed: {e}')
"
```

### 4. Redis/Celery Testing
```bash
# Check Redis connection
docker-compose exec backend python -c "
import redis
import os
try:
    r = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'))
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
"

# Check Celery tasks
docker-compose exec celery-worker celery -A app.celery_app inspect active
```

## Troubleshooting

### Common Issues

1. **Migration Fails**
   ```bash
   # Check database connection
   docker-compose exec backend python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"
   
   # Manual migration
   docker-compose exec postgres psql -U postgres -d abparts -f /path/to/migration.sql
   ```

2. **Email Not Sending**
   ```bash
   # Check environment variables
   docker-compose exec backend env | grep SMTP
   
   # Check Celery worker is running
   docker-compose ps celery-worker
   
   # Check Celery logs
   docker-compose logs celery-worker
   ```

3. **Token Validation Errors**
   ```bash
   # Check if new database fields exist
   docker-compose exec postgres psql -U postgres -d abparts -c "SELECT email_verification_token FROM users LIMIT 1;"
   ```

4. **API Endpoints Not Found**
   ```bash
   # Restart backend container
   docker-compose restart backend
   
   # Check if routes are loaded
   docker-compose exec backend python -c "from app.main import app; print([route.path for route in app.routes])"
   ```

### Performance Monitoring

```bash
# Monitor container resources
docker stats

# Check database connections
docker-compose exec postgres psql -U postgres -d abparts -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor Celery task queue
docker-compose exec celery-worker celery -A app.celery_app inspect stats
```

## Security Considerations

1. **Environment Variables**: Never commit SMTP credentials to version control
2. **Token Security**: Ensure tokens are properly validated and expired
3. **HTTPS**: Use HTTPS in production for secure token transmission
4. **Rate Limiting**: Consider implementing rate limiting for password reset requests
5. **Email Validation**: Validate email addresses before sending verification emails

## Production Deployment

For production with Docker:

1. Use Docker secrets for sensitive environment variables
2. Set up proper logging and monitoring
3. Use a production-grade SMTP service
4. Configure proper backup strategies
5. Set up health checks and auto-restart policies
6. Use HTTPS with proper SSL certificates
7. Configure proper firewall rules

## Support

If you encounter issues:

1. Run the test script: `docker-compose exec backend python test_user_profile.py`
2. Check logs: `docker-compose logs backend celery-worker`
3. Verify database schema: Connect to PostgreSQL and check table structure
4. Test email configuration: Use the SMTP test commands above