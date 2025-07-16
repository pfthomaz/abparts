# User Invitation and Onboarding System

## Overview

The User Invitation and Onboarding System provides a secure, email-based workflow for inviting new users to join organizations within the ABParts application. This system implements all requirements from the business model alignment specification (Requirements 2A.1 through 2A.6).

## Features

### ✅ Implemented Features

1. **Secure User Invitations** (Req 2A.1, 2A.2)
   - Email-based invitation system with secure tokens
   - Role-based invitation permissions
   - Organization-scoped invitations

2. **Complete Account Setup** (Req 2A.3)
   - Username and password setup during acceptance
   - Profile completion workflow
   - Automatic account activation

3. **Invitation Management** (Req 2A.4)
   - 7-day invitation expiry
   - Invitation resend functionality
   - Token regeneration for security

4. **Automatic User Activation** (Req 2A.5)
   - Seamless activation upon invitation acceptance
   - Status transition from pending to active
   - Immediate system access

5. **Comprehensive Audit Trail** (Req 2A.6)
   - Complete invitation lifecycle tracking
   - Admin action logging
   - Audit log queries and reporting

6. **Automated Cleanup**
   - Daily expired invitation cleanup
   - Admin notifications for expired invitations
   - Automatic status management

## API Endpoints

### POST /users/invite
Send an invitation to a new user.

**Permissions:** `super_admin`, `admin`

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "User Name",
  "role": "user",
  "organization_id": "uuid"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "role": "user",
  "organization_id": "uuid",
  "invitation_token": "secure_token",
  "invitation_expires_at": "2024-01-01T00:00:00Z",
  "user_status": "pending_invitation",
  "invited_by_user_id": "uuid",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### POST /users/accept-invitation
Accept a user invitation and complete account setup.

**Public endpoint** (no authentication required)

**Request Body:**
```json
{
  "invitation_token": "secure_token",
  "username": "chosen_username",
  "password": "secure_password",
  "name": "Full Name"
}
```

### POST /users/resend-invitation
Resend an invitation with a new token.

**Permissions:** `super_admin`, `admin`

**Request Body:**
```json
{
  "user_id": "uuid"
}
```

### GET /users/pending-invitations
Get all pending invitations (filtered by organization for admins).

**Permissions:** `super_admin`, `admin`

**Query Parameters:**
- `skip`: Pagination offset (default: 0)
- `limit`: Results per page (default: 100)

### GET /users/{user_id}/invitation-audit
Get invitation audit logs for a specific user.

**Permissions:** `super_admin`, `admin` (own organization only)

## Database Schema

### User Model Extensions
```sql
-- New fields added to users table
invitation_token VARCHAR(255),
invitation_expires_at TIMESTAMP,
invited_by_user_id UUID REFERENCES users(id),
user_status user_status_enum DEFAULT 'active'
```

### InvitationAuditLog Model
```sql
CREATE TABLE invitation_audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    performed_by_user_id UUID REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT NOW(),
    details TEXT
);
```

## Email Templates

The system includes professional HTML and plain text email templates for:

1. **Invitation Email**
   - Welcome message with organization context
   - Secure invitation link
   - Clear instructions and expiry notice
   - Professional branding

2. **Acceptance Notification**
   - Admin notification when user joins
   - User details and organization context
   - Confirmation of successful onboarding

3. **Expiry Notification**
   - Admin notification for expired invitations
   - User details and suggested actions
   - Automated cleanup notifications

## Security Features

### Token Security
- Cryptographically secure tokens using `secrets.token_urlsafe(32)`
- 7-day expiration for all invitation tokens
- Automatic token invalidation upon acceptance
- New token generation for resends

### Permission Controls
- **Super Admins**: Can invite users to any organization
- **Admins**: Can only invite users to their own organization
- **Role Restrictions**: Admins cannot invite super_admins
- **Organization Validation**: Super admin role only for Oraseas EE

### Data Protection
- Sensitive fields excluded from API responses
- Secure password hashing with bcrypt
- Email validation and sanitization
- SQL injection protection via ORM

## Background Tasks

### Celery Tasks

1. **send_invitation_email**
   - Asynchronous email delivery
   - Retry logic with exponential backoff
   - Professional HTML/text templates
   - SMTP error handling

2. **send_invitation_accepted_notification**
   - Admin notification system
   - User onboarding confirmations
   - Organization context inclusion

3. **send_invitation_expired_notification**
   - Automated expiry notifications
   - Admin action suggestions
   - Cleanup process notifications

4. **cleanup_expired_invitations**
   - Daily automated cleanup (2:00 AM UTC)
   - Batch processing of expired invitations
   - Audit log creation
   - Admin notification dispatch

### Celery Beat Configuration
```python
beat_schedule = {
    'cleanup-expired-invitations': {
        'task': 'app.tasks.cleanup_expired_invitations',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2:00 AM
        'options': {'queue': 'default'}
    },
}
```

## Configuration

### Environment Variables
```bash
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=noreply@abparts.com
BASE_URL=https://your-domain.com

# Redis Configuration (for Celery)
REDIS_URL=redis://localhost:6379/0
```

### Email Service Setup
1. Configure SMTP credentials in environment
2. Enable "App Passwords" for Gmail if using Gmail SMTP
3. Test email delivery with the provided test script
4. Monitor email delivery logs in Celery worker output

## Testing

### Manual Testing
Run the comprehensive test script:
```bash
cd backend
python test_invitation_system.py
```

### Test Coverage
The test script validates:
- ✅ Organization and user creation
- ✅ Invitation creation and token generation
- ✅ Token lookup and validation
- ✅ Invitation acceptance workflow
- ✅ Username uniqueness validation
- ✅ Pending invitations queries
- ✅ Invitation resend functionality
- ✅ Audit log creation and retrieval
- ✅ Expired invitation handling
- ✅ Data cleanup and integrity

### API Testing
Use the following curl commands to test the endpoints:

```bash
# 1. Send invitation (requires admin token)
curl -X POST "http://localhost:8000/users/invite" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "name": "New User",
    "role": "user",
    "organization_id": "your-org-uuid"
  }'

# 2. Accept invitation (public endpoint)
curl -X POST "http://localhost:8000/users/accept-invitation" \
  -H "Content-Type: application/json" \
  -d '{
    "invitation_token": "token-from-email",
    "username": "newusername",
    "password": "securepassword123",
    "name": "Full Name"
  }'

# 3. Get pending invitations (requires admin token)
curl -X GET "http://localhost:8000/users/pending-invitations" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Monitoring and Maintenance

### Health Checks
- Monitor Celery worker status
- Check Redis connectivity
- Validate SMTP configuration
- Track email delivery rates

### Metrics to Monitor
- Invitation acceptance rate
- Average time to acceptance
- Expired invitation count
- Email delivery failures
- Token security incidents

### Maintenance Tasks
- Regular cleanup of old audit logs
- Email template updates
- Security token rotation
- Performance optimization

## Troubleshooting

### Common Issues

1. **Email Not Delivered**
   - Check SMTP credentials
   - Verify firewall/network settings
   - Check spam folders
   - Review Celery worker logs

2. **Token Validation Errors**
   - Verify token hasn't expired
   - Check for URL encoding issues
   - Validate database connectivity
   - Review invitation status

3. **Permission Denied**
   - Verify user role and organization
   - Check JWT token validity
   - Validate organization relationships
   - Review permission logic

### Debug Commands
```bash
# Check Celery worker status
celery -A app.celery_app inspect active

# Test email configuration
python -c "from app.tasks import send_invitation_email; print('Email config OK')"

# Validate database schema
python -c "from app.models import User, InvitationAuditLog; print('Schema OK')"
```

## Future Enhancements

### Planned Features
- [ ] Bulk invitation import from CSV
- [ ] Custom email templates per organization
- [ ] Multi-language email support
- [ ] Advanced invitation analytics
- [ ] Integration with external identity providers
- [ ] Mobile app invitation handling

### Performance Optimizations
- [ ] Email template caching
- [ ] Batch email processing
- [ ] Database query optimization
- [ ] Redis caching for frequent lookups

## Compliance and Security

### Data Privacy
- GDPR compliance for email handling
- User consent for email communications
- Data retention policies for audit logs
- Secure token storage and transmission

### Security Best Practices
- Regular security audits
- Token entropy validation
- Email spoofing protection
- Rate limiting for invitation endpoints

---

## Requirements Mapping

This implementation satisfies all specified requirements:

- **2A.1** ✅ Email invitation with secure registration link
- **2A.2** ✅ User password setup and profile completion
- **2A.3** ✅ 7-day invitation expiry
- **2A.4** ✅ Invitation resend functionality
- **2A.5** ✅ Automatic user activation upon acceptance
- **2A.6** ✅ Complete invitation audit trail and tracking

The system is production-ready and provides a secure, user-friendly onboarding experience for the ABParts application.