# Audit Logging and Compliance Guide

## Overview

The AutoBoss AI Assistant includes comprehensive audit logging and compliance features to ensure transparency, accountability, and regulatory compliance. This guide explains how to use these features effectively.

## Table of Contents

1. [Audit Logging](#audit-logging)
2. [User Consent Management](#user-consent-management)
3. [Privacy Policy Integration](#privacy-policy-integration)
4. [Compliance Reporting](#compliance-reporting)
5. [Data Handling Documentation](#data-handling-documentation)
6. [API Reference](#api-reference)
7. [Best Practices](#best-practices)

## Audit Logging

### What is Logged?

The AI Assistant automatically logs all interactions and events, including:

**AI Interactions:**
- Session start and end
- User messages sent
- AI responses generated
- Machine selection
- Feedback provided
- Escalation requests

**Data Management:**
- Data exports
- Data deletions
- Consent changes

**System Events:**
- Sensitive data detections
- Encryption operations
- Data cleanup activities

**Security Events:**
- Authentication failures
- Unauthorized access attempts
- Suspicious activities

### Automatic Logging

Most audit logging happens automatically through database triggers:

```sql
-- Automatically triggered when a message is created
INSERT INTO ai_messages (...)
-- Triggers: log_ai_message_audit()
-- Result: Audit log entry created automatically
```

### Manual Audit Logging

For custom events, use the audit service:

```python
from app.services.audit_service import get_audit_service, AuditEventType, AuditSeverity

audit_service = get_audit_service()

# Log a custom event
await audit_service.log_ai_interaction(
    db=db,
    event_type=AuditEventType.MACHINE_SELECTED,
    user_id="user-123",
    session_id="session-456",
    details={"machine_id": "machine-789", "model": "V4.0"},
    severity=AuditSeverity.INFO,
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0..."
)
```

### Retrieving Audit Trails

Get a user's complete audit trail:

```bash
POST /api/ai/audit-compliance/audit/trail
{
  "user_id": "user-123",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-01-31T23:59:59Z",
  "event_types": ["message_sent", "ai_response_generated"],
  "limit": 100
}
```

Response:
```json
{
  "user_id": "user-123",
  "total_events": 45,
  "events": [
    {
      "audit_id": "abc123...",
      "event_type": "message_sent",
      "user_id": "user-123",
      "session_id": "session-456",
      "message_id": "msg-789",
      "details": {"message_type": "text", "language": "en"},
      "severity": "info",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### System Audit Summary

Get system-wide audit metrics (admin only):

```bash
GET /api/ai/audit-compliance/audit/summary?days=30
```

Response includes:
- Event distribution by type and severity
- Daily activity trends
- Top users by activity
- Total event counts

## User Consent Management

### Consent Types

The AI Assistant requires consent for various data processing activities:

**Required Consents:**
1. **DATA_PROCESSING**: Processing personal data for AI assistance
2. **AI_INTERACTION**: AI interaction and conversation storage
3. **DATA_STORAGE**: Storage of conversation data

**Optional Consents:**
4. **ANALYTICS**: Usage analytics and performance monitoring
5. **MARKETING**: Marketing communications
6. **THIRD_PARTY_SHARING**: Sharing data with third-party services

### Recording Consent

Record user consent with full audit trail:

```bash
POST /api/ai/audit-compliance/consent/record
{
  "user_id": "user-123",
  "consent_type": "data_processing",
  "status": "granted",
  "consent_text": "I consent to processing of my data for AI assistance",
  "privacy_policy_version": "1.0"
}
```

The system automatically captures:
- IP address (from X-Forwarded-For header)
- User agent (from User-Agent header)
- Timestamp
- Consent version

### Checking Consent

Verify if a user has granted consent:

```python
from app.services.consent_service import get_consent_service, ConsentType

consent_service = get_consent_service()

has_consent = await consent_service.check_consent(
    db=db,
    user_id="user-123",
    consent_type=ConsentType.DATA_PROCESSING
)

if not has_consent:
    # Prompt user for consent
    pass
```

### Withdrawing Consent

Users can withdraw consent at any time:

```bash
POST /api/ai/audit-compliance/consent/user-123/withdraw?consent_type=analytics&reason=No%20longer%20wish%20to%20participate
```

This:
- Updates consent status to "withdrawn"
- Records reason for withdrawal
- Creates audit log entry
- Triggers data processing changes

### Getting Consent Records

Retrieve all consent records for a user:

```bash
GET /api/ai/audit-compliance/consent/user-123
```

Optional filtering by consent type:
```bash
GET /api/ai/audit-compliance/consent/user-123?consent_type=analytics
```

### Required Consents List

Get information about all consent types:

```bash
GET /api/ai/audit-compliance/consent/required
```

Response:
```json
{
  "required_consents": [
    {
      "consent_type": "data_processing",
      "required": true,
      "description": "Processing of personal data for AI assistance",
      "purpose": "To provide AI-powered troubleshooting assistance"
    },
    ...
  ]
}
```

## Privacy Policy Integration

### Recording Privacy Policy Acceptance

Track when users accept the privacy policy:

```bash
POST /api/ai/audit-compliance/privacy-policy/accept
{
  "user_id": "user-123",
  "policy_version": "1.0",
  "policy_text": "Full privacy policy text here..."
}
```

This records:
- Policy version accepted
- Full policy text (for legal compliance)
- Acceptance timestamp
- IP address and user agent

### Getting Privacy Policy Acceptance

Retrieve a user's latest privacy policy acceptance:

```bash
GET /api/ai/audit-compliance/privacy-policy/user-123
```

Response:
```json
{
  "acceptance_id": "acc123...",
  "user_id": "user-123",
  "policy_version": "1.0",
  "policy_text": "Full privacy policy text...",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "accepted_at": "2025-01-15T10:00:00Z"
}
```

### Privacy Policy Versioning

When updating the privacy policy:

1. Increment the version number (e.g., "1.0" → "1.1")
2. Prompt users to accept the new version
3. Record new acceptance with updated version
4. System maintains history of all acceptances

## Compliance Reporting

### Generating Compliance Reports

Generate comprehensive compliance reports (admin only):

```bash
POST /api/ai/audit-compliance/compliance/report
{
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-01-31T23:59:59Z",
  "report_type": "full"
}
```

**Report Types:**
- `full`: Complete compliance report
- `gdpr`: GDPR-specific compliance
- `security`: Security events and incidents
- `data_access`: Data access tracking

**Report Contents:**

1. **AI Interactions**:
   - Total interactions
   - Unique users
   - Total sessions

2. **Data Access**:
   - Access events by type (read, export, delete)
   - Accessor and accessed user tracking

3. **GDPR Requests**:
   - Deletion requests by status
   - Export requests
   - Consent withdrawals

4. **Sensitive Data Detections**:
   - Detection counts by type
   - Redaction actions taken

5. **Security Events**:
   - Authentication failures
   - Unauthorized access attempts
   - Suspicious activities

6. **User Consent**:
   - Consent by type and status
   - Consent grant/withdrawal trends

7. **Data Retention**:
   - Records by type
   - Deletion compliance rates

### Consent Summary Report

Get consent statistics (admin only):

```bash
GET /api/ai/audit-compliance/compliance/consent-summary?start_date=2025-01-01T00:00:00Z&end_date=2025-01-31T23:59:59Z
```

Response:
```json
{
  "consent_by_type": {
    "data_processing": {
      "granted": 150,
      "denied": 5,
      "withdrawn": 2
    },
    "analytics": {
      "granted": 120,
      "denied": 30,
      "withdrawn": 7
    }
  },
  "privacy_policy_acceptances": {
    "1.0": 145,
    "1.1": 12
  },
  "total_consent_records": 331,
  "total_policy_acceptances": 157
}
```

## Data Handling Documentation

### Getting Data Handling Documentation

Retrieve comprehensive data handling documentation:

```bash
GET /api/ai/audit-compliance/compliance/data-handling-documentation
```

This endpoint provides:

1. **Data Collection**:
   - Types of data collected
   - Purpose for each type
   - Retention periods
   - Encryption methods

2. **Data Processing**:
   - Processing activities
   - Data shared with third parties
   - Safeguards in place

3. **Data Protection**:
   - Security measures
   - Encryption details
   - Access controls

4. **User Rights**:
   - Right to access
   - Right to data portability
   - Right to erasure
   - Right to rectification
   - Right to withdraw consent
   - Right to object

5. **Contact Information**:
   - Data protection officer
   - Support contact
   - Privacy website

## API Reference

### Base URL
```
http://localhost:8001/api/ai/audit-compliance
```

### Authentication
Most endpoints require authentication via Bearer token:
```
Authorization: Bearer YOUR_TOKEN
```

### Endpoints Summary

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/consent/record` | POST | Record user consent | Yes |
| `/consent/{user_id}` | GET | Get user consent records | Yes |
| `/consent/{user_id}/withdraw` | POST | Withdraw consent | Yes |
| `/privacy-policy/accept` | POST | Record policy acceptance | Yes |
| `/privacy-policy/{user_id}` | GET | Get policy acceptance | Yes |
| `/consent/required` | GET | Get required consents | No |
| `/audit/trail` | POST | Get user audit trail | Yes |
| `/audit/summary` | GET | Get system audit summary | Admin |
| `/compliance/report` | POST | Generate compliance report | Admin |
| `/compliance/consent-summary` | GET | Get consent summary | Admin |
| `/compliance/data-handling-documentation` | GET | Get data handling docs | No |

## Best Practices

### For Developers

1. **Always Log Important Events**:
   ```python
   await audit_service.log_ai_interaction(
       db=db,
       event_type=AuditEventType.CUSTOM_EVENT,
       user_id=user_id,
       details={"action": "important_action"},
       severity=AuditSeverity.INFO
   )
   ```

2. **Check Consent Before Processing**:
   ```python
   if not await consent_service.check_consent(db, user_id, ConsentType.ANALYTICS):
       # Skip analytics processing
       return
   ```

3. **Use Appropriate Severity Levels**:
   - INFO: Normal operations
   - WARNING: Unusual but not critical
   - ERROR: Errors that need attention
   - CRITICAL: Security incidents

4. **Include Context in Details**:
   ```python
   details={
       "machine_id": machine_id,
       "problem_type": "pressure_issue",
       "resolution_time": 120
   }
   ```

### For Administrators

1. **Regular Compliance Reports**:
   - Generate monthly compliance reports
   - Review for anomalies
   - Archive for regulatory requirements

2. **Monitor Audit Logs**:
   - Set up alerts for CRITICAL events
   - Review ERROR events daily
   - Analyze trends in audit summary

3. **Consent Management**:
   - Track consent withdrawal trends
   - Update privacy policy as needed
   - Ensure all users have required consents

4. **Data Retention**:
   - Review retention compliance regularly
   - Ensure automated cleanup is working
   - Archive old audit logs appropriately

### For Users

1. **Review Your Audit Trail**:
   - Check what data is being collected
   - Verify AI interactions are logged correctly
   - Request audit trail via support if needed

2. **Manage Your Consents**:
   - Review consent settings regularly
   - Withdraw optional consents if desired
   - Understand what each consent enables

3. **Privacy Policy**:
   - Read and understand the privacy policy
   - Accept new versions when prompted
   - Contact support with questions

## Troubleshooting

### Audit Logs Not Appearing

1. Check database triggers are installed:
   ```sql
   SELECT trigger_name FROM information_schema.triggers 
   WHERE trigger_name IN ('ai_message_audit_trigger', 'ai_session_audit_trigger');
   ```

2. Verify audit service is initialized:
   ```python
   from app.services.audit_service import get_audit_service
   audit_service = get_audit_service()
   ```

3. Check database permissions

### Consent Not Being Recorded

1. Verify unique constraint on (user_id, consent_type)
2. Check for database errors in logs
3. Ensure IP address and user agent headers are present

### Compliance Report Generation Fails

1. Check date range is valid
2. Verify admin authentication
3. Check database connectivity
4. Review error logs for details

## Support

For questions or issues:
- **Email**: support@abparts.com
- **Privacy**: privacy@abparts.com
- **Documentation**: https://abparts.com/docs/audit-compliance

## Version History

- **v1.0.0** (January 2025): Initial implementation
  - Comprehensive audit logging
  - User consent management
  - Privacy policy integration
  - Compliance reporting
  - Data handling documentation
