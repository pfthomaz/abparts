# Security and Privacy Features

## Overview

The AutoBoss AI Assistant implements comprehensive security and privacy features to protect user data and ensure GDPR compliance. This document describes the security measures in place and how to use the privacy features.

## Features Implemented

### 1. End-to-End Encryption (Requirement 10.1)

All AI conversation messages are encrypted at rest using industry-standard encryption:

- **Algorithm**: Fernet (AES-128-CBC with HMAC for authentication)
- **Key Derivation**: PBKDF2-SHA256 with 100,000 iterations
- **Transport Security**: TLS/HTTPS required for all API communications

**How it works:**
- User messages are encrypted before being stored in the database
- AI responses are encrypted before storage
- Messages are automatically decrypted when retrieved
- Each encryption uses a unique initialization vector (IV) for security

**Configuration:**
```bash
# Set encryption key in environment variables
AI_ENCRYPTION_KEY=your-secure-encryption-key-here
```

If no key is provided, a temporary key is generated (suitable for development only).

### 2. Data Retention Policies (Requirement 10.3)

Automatic data cleanup based on configurable retention periods:

| Data Type | Retention Period | Description |
|-----------|-----------------|-------------|
| Active Sessions | 30 days | Currently active conversations |
| Completed Sessions | 90 days | Successfully resolved troubleshooting |
| Escalated Sessions | 365 days | Sessions escalated to support |
| Abandoned Sessions | 7 days | Inactive/abandoned conversations |
| Analytics Data | 730 days | Learning and performance metrics |
| Audit Logs | 1095 days | Security audit trail |

**Automatic Cleanup:**
```bash
# Run cleanup manually
curl -X POST http://localhost:8001/api/ai/privacy/cleanup-expired-data \
  -H "Authorization: Bearer YOUR_TOKEN"

# Or set up a cron job for daily cleanup
0 2 * * * curl -X POST http://localhost:8001/api/ai/privacy/cleanup-expired-data
```

### 3. GDPR Compliance (Requirements 10.3, 10.5)

Full support for GDPR user rights:

#### Right to Access
Users can view all their data through the session history endpoints.

#### Right to Data Portability
Export all user data in structured JSON format:

```bash
curl -X POST http://localhost:8001/api/ai/privacy/users/{user_id}/export-data \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid",
    "include_messages": true,
    "include_expert_knowledge": true
  }'
```

**Export includes:**
- All conversation sessions
- All messages (decrypted)
- Expert knowledge contributions
- Session metadata and timestamps

#### Right to Be Forgotten
Permanently delete all user data:

```bash
curl -X POST http://localhost:8001/api/ai/privacy/users/{user_id}/delete-data \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid",
    "confirmation": true,
    "reason": "User requested deletion"
  }'
```

**Deletion includes:**
- All AI sessions
- All messages
- Troubleshooting steps
- Expert knowledge contributions
- Expert feedback
- Support tickets (anonymized, not deleted)

#### Right to Rectification
Users can update their data through the standard API endpoints.

### 4. Sensitive Data Detection and Filtering (Requirement 10.4)

Automatic detection and redaction of sensitive information:

**Detected Patterns:**
- Email addresses
- Phone numbers
- Credit card numbers
- Social Security Numbers (SSN)
- IP addresses
- API keys
- Passwords

**How it works:**
- Messages are scanned for sensitive patterns before processing
- Detected sensitive data is automatically redacted with `[REDACTED_TYPE]` markers
- Original sensitive values are never stored or logged
- Detection events are logged for audit purposes

**Manual Check:**
```bash
curl -X POST http://localhost:8001/api/ai/privacy/check-sensitive-data \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Contact me at user@example.com or call 555-1234",
    "redact": true
  }'
```

**Response:**
```json
{
  "has_sensitive_data": true,
  "detections": [
    {"type": "email", "position": {"start": 14, "end": 32}},
    {"type": "phone", "position": {"start": 41, "end": 49}}
  ],
  "filtered_content": "Contact me at [REDACTED_EMAIL] or call [REDACTED_PHONE]",
  "message": "Found 2 sensitive data pattern(s)"
}
```

## API Endpoints

### Privacy Management

#### Get Retention Policy
```
GET /api/ai/privacy/retention-policy
```
Returns information about data retention periods and user rights.

#### Export User Data
```
POST /api/ai/privacy/users/{user_id}/export-data
```
Export all user data for GDPR compliance.

#### Delete User Data
```
POST /api/ai/privacy/users/{user_id}/delete-data
```
Permanently delete all user data (right to be forgotten).

#### Check Sensitive Data
```
POST /api/ai/privacy/check-sensitive-data
```
Check content for sensitive information and optionally redact it.

#### Cleanup Expired Data
```
POST /api/ai/privacy/cleanup-expired-data
```
Manually trigger cleanup of expired data (admin only).

#### Get Encryption Status
```
GET /api/ai/privacy/encryption-status
```
Get information about encryption configuration.

## Database Schema

### Security Audit Logs
```sql
CREATE TABLE security_audit_logs (
    id VARCHAR(32) PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Data Retention Tracking
```sql
CREATE TABLE data_retention_tracking (
    id VARCHAR(32) PRIMARY KEY,
    record_type VARCHAR(50) NOT NULL,
    record_id VARCHAR(255) NOT NULL,
    retention_period_days INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP,
    deletion_reason VARCHAR(100)
);
```

### User Data Deletion Requests
```sql
CREATE TABLE user_data_deletion_requests (
    id VARCHAR(32) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    request_date TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    completed_date TIMESTAMP,
    deleted_records JSONB,
    notes TEXT
);
```

### Sensitive Data Detections
```sql
CREATE TABLE sensitive_data_detections (
    id VARCHAR(32) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    message_id VARCHAR(255),
    detection_type VARCHAR(50) NOT NULL,
    detected_at TIMESTAMP DEFAULT NOW(),
    action_taken VARCHAR(50) NOT NULL,
    details JSONB
);
```

## Setup Instructions

### 1. Install Dependencies
```bash
cd ai_assistant
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Add to .env file
AI_ENCRYPTION_KEY=your-secure-32-character-key-here
```

### 3. Create Database Tables
```bash
python setup_security_tables.py
```

### 4. Verify Setup
```bash
# Check encryption status
curl http://localhost:8001/api/ai/privacy/encryption-status

# Check retention policy
curl http://localhost:8001/api/ai/privacy/retention-policy
```

## Security Best Practices

### For Administrators

1. **Encryption Key Management**
   - Use a strong, randomly generated encryption key
   - Store the key securely (e.g., AWS Secrets Manager, HashiCorp Vault)
   - Rotate keys periodically (requires re-encryption of existing data)
   - Never commit keys to version control

2. **Regular Data Cleanup**
   - Set up automated daily cleanup jobs
   - Monitor cleanup logs for issues
   - Review retention periods quarterly

3. **Audit Log Monitoring**
   - Regularly review security audit logs
   - Set up alerts for suspicious activities
   - Retain audit logs for compliance requirements

4. **Access Control**
   - Restrict privacy endpoints to authenticated users
   - Implement role-based access for admin functions
   - Log all data access and modifications

### For Developers

1. **Always Use Encryption**
   - Never store sensitive data in plain text
   - Use the SecurityService for all message storage
   - Test encryption/decryption in development

2. **Sensitive Data Handling**
   - Always filter user input for sensitive data
   - Redact sensitive information before logging
   - Never include sensitive data in error messages

3. **Testing**
   - Run property-based tests regularly
   - Test GDPR compliance features
   - Verify encryption/decryption workflows

## Compliance

This implementation provides:

- ✅ **GDPR Compliance**: Right to access, portability, erasure, and rectification
- ✅ **Data Protection**: End-to-end encryption for all stored messages
- ✅ **Privacy by Design**: Automatic sensitive data detection and filtering
- ✅ **Transparency**: Clear retention policies and user rights documentation
- ✅ **Audit Trail**: Comprehensive logging of all security-sensitive actions

## Testing

Run the security and privacy tests:

```bash
cd ai_assistant
pytest tests/test_security_and_privacy.py -v
```

The test suite includes:
- Encryption/decryption property tests
- Sensitive data detection tests
- Data retention policy tests
- GDPR compliance tests
- Integration tests

## Support

For questions or issues related to security and privacy features:

1. Review this documentation
2. Check the API documentation at `/docs`
3. Review audit logs for troubleshooting
4. Contact the development team

## Version History

- **v1.0.0** (2024-01-08): Initial implementation
  - End-to-end encryption
  - Data retention policies
  - GDPR compliance features
  - Sensitive data detection and filtering
