# Docker Migration Guide for User Profile Features

## Database Migration Steps

### 1. Apply the Migration
Run the migration inside the backend container:

```bash
# If using docker-compose
docker-compose exec backend alembic upgrade head

# Or if running containers directly
docker exec -it <backend-container-name> alembic upgrade head
```

### 2. Alternative: Manual SQL Execution
If Alembic isn't available, you can run the SQL directly:

```bash
# Connect to PostgreSQL container
docker-compose exec postgres psql -U <username> -d <database_name>

# Then run the SQL commands:
ALTER TABLE users ADD COLUMN email_verification_token VARCHAR(255);
ALTER TABLE users ADD COLUMN email_verification_expires_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN pending_email VARCHAR(255);

CREATE TABLE invitation_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    action VARCHAR(50) NOT NULL,
    performed_by_user_id UUID REFERENCES users(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    details TEXT
);
```

## Environment Variables

### Required Email Configuration
Add these to your `.env` file or docker-compose environment:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
BASE_URL=http://localhost:3000

# Redis for Celery (if not already configured)
REDIS_URL=redis://redis:6379/0
```

## Docker Compose Updates

### Ensure Celery Worker is Running
Your `docker-compose.yml` should include a Celery worker for email tasks:

```yaml
services:
  backend:
    # ... existing backend config
    
  celery-worker:
    build: ./backend
    command: celery -A app.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
    depends_on:
      - redis
      - postgres
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/dbname
      - REDIS_URL=redis://redis:6379/0
      - SMTP_SERVER=${SMTP_SERVER}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Testing the Implementation

### 1. API Endpoint Testing
Once deployed, test the new endpoints:

```bash
# Get user profile
curl -X GET "http://localhost:8000/users/me/profile" \
  -H "Authorization: Bearer <your-token>"

# Update profile
curl -X PUT "http://localhost:8000/users/me/profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"name": "New Name", "email": "new@example.com"}'

# Change password
curl -X POST "http://localhost:8000/users/me/change-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"current_password": "old123", "new_password": "new123456"}'

# Request password reset
curl -X POST "http://localhost:8000/users/request-password-reset" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### 2. Email Testing
- Configure SMTP settings in environment variables
- Test email sending by requesting password reset
- Check email delivery and token functionality

### 3. Database Verification
```bash
# Connect to database
docker-compose exec postgres psql -U <username> -d <database_name>

# Check new columns exist
\d users

# Check audit log table
\d invitation_audit_logs
```

## Troubleshooting

### Common Issues:

1. **Migration Fails**: Ensure database is running and accessible
2. **Email Not Sending**: Check SMTP credentials and network connectivity
3. **Celery Tasks Not Running**: Ensure Redis is running and Celery worker is started
4. **Token Errors**: Check that new database fields are properly added

### Logs to Check:
```bash
# Backend logs
docker-compose logs backend

# Celery worker logs
docker-compose logs celery-worker

# Database logs
docker-compose logs postgres
```

## Security Considerations

1. **SMTP Credentials**: Use app passwords, not regular passwords
2. **Token Security**: Ensure tokens are properly generated and validated
3. **HTTPS**: Use HTTPS in production for secure token transmission
4. **Email Links**: Ensure BASE_URL points to your actual domain in production

## Production Deployment

For production deployment:

1. Use proper SMTP service (SendGrid, AWS SES, etc.)
2. Set secure BASE_URL to your production domain
3. Use environment-specific configuration
4. Enable proper logging and monitoring
5. Set up proper backup for database with new fields