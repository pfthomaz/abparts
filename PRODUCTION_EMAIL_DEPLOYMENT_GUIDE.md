# Production Email System Deployment Guide

## Overview

This guide covers deploying the escalation email system to production, ensuring SMTP environment variables are properly configured.

## 🚀 Deployment Steps

### 1. Push Changes to Repository

```bash
# Commit and push the docker-compose changes
git add docker-compose.yml docker-compose.prod.yml
git add ai_assistant/app/services/escalation_service.py
git commit -m "Add SMTP configuration for AI assistant escalation emails"
git push origin main
```

### 2. Production Server Setup

On your production server, you need to:

#### A. Pull Latest Changes
```bash
# Connect to production server
ssh user@your-production-server

# Navigate to project directory
cd /path/to/abparts

# Pull latest changes
git pull origin main
```

#### B. Configure Production Environment Variables

Create or update the production `.env` file with SMTP settings:

```bash
# Edit the production .env file
nano .env
```

Add these SMTP configuration lines to your production `.env` file:

```bash
# Microsoft Exchange SMTP Configuration
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=diogothomaz@oraseas.com
SMTP_PASSWORD=!mcmFT1994!
FROM_EMAIL=abparts_support@oraseas.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

**⚠️ Important Security Notes:**
- Never commit the production `.env` file to the repository
- Use strong passwords and consider app passwords for Microsoft 365
- Ensure the `.env` file has proper permissions: `chmod 600 .env`

### 3. Enable Microsoft 365 SMTP AUTH

Before deployment, ensure SMTP AUTH is enabled in your Microsoft 365 tenant:

#### Option A: Microsoft 365 Admin Center
1. Go to **admin.microsoft.com**
2. Navigate to **Settings** → **Org settings** → **Mail flow**
3. Enable **SMTP AUTH**

#### Option B: Exchange Admin Center
1. Go to **admin.exchange.microsoft.com**
2. Navigate to **Mail flow** → **Receive connectors**
3. Enable SMTP authentication

#### Option C: PowerShell (Admin)
```powershell
Connect-ExchangeOnline
Set-TransportConfig -SmtpClientAuthenticationDisabled $false
Set-CASMailbox -Identity "diogothomaz@oraseas.com" -SmtpClientAuthenticationDisabled $false
```

### 4. Deploy to Production

```bash
# Stop current services
docker compose -f docker-compose.prod.yml down

# Rebuild and start services
docker compose -f docker-compose.prod.yml up -d --build

# Check that all services are running
docker compose -f docker-compose.prod.yml ps
```

### 5. Verify Email Configuration

Test the email configuration in production:

```bash
# Test environment variables are loaded
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import os
print('SMTP_SERVER:', repr(os.getenv('SMTP_SERVER')))
print('SMTP_USERNAME:', repr(os.getenv('SMTP_USERNAME')))
print('FROM_EMAIL:', repr(os.getenv('FROM_EMAIL')))
print('SMTP_USE_TLS:', repr(os.getenv('SMTP_USE_TLS')))
"

# Test email service functionality
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import sys
sys.path.append('/app')
from app.services.email_service import EmailService
from datetime import datetime

email_service = EmailService()
print('Email Service Configuration:')
print(f'Server: {email_service.smtp_server}')
print(f'Username: {email_service.smtp_username}')
print(f'From: {email_service.from_email}')

# Test email sending
ticket_data = {
    'ticket_number': 'AB-PROD-TEST-001',
    'priority': 'medium',
    'status': 'open',
    'escalation_reason': 'user_request',
    'session_id': 'prod-test-session',
    'session_summary': 'Production email test',
    'created_at': datetime.utcnow().isoformat(),
    'additional_notes': 'Testing production email configuration'
}

user_info = {
    'full_name': 'Production Test User',
    'email': 'test@oraseas.com',
    'role': 'admin',
    'organization_name': 'Oraseas EE'
}

print('\nTesting email sending...')
try:
    result = email_service.send_escalation_notification(ticket_data, user_info, None)
    print(f'Email send result: {result}')
    if result:
        print('✅ Production email system is working!')
    else:
        print('❌ Email sending failed - check SMTP configuration')
except Exception as e:
    print(f'❌ Email error: {e}')
"
```

## 🔧 Production Environment Variables Checklist

Ensure your production `.env` file contains all required variables:

### Database Configuration
```bash
POSTGRES_DB=abparts_prod
POSTGRES_USER=abparts_user
POSTGRES_PASSWORD=your_secure_production_password
```

### SMTP Configuration (NEW)
```bash
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=diogothomaz@oraseas.com
SMTP_PASSWORD=your_email_password
FROM_EMAIL=abparts_support@oraseas.com
SMTP_USE_TLS=true
SMTP_USE_SSL=false
```

### Application Configuration
```bash
BASE_URL=https://yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
ENVIRONMENT=production
SECRET_KEY=your_production_secret_key
JWT_SECRET_KEY=your_production_jwt_secret
```

### AI Assistant Configuration
```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_FALLBACK_MODEL=gpt-3.5-turbo
```

## 🧪 Testing the Deployment

### 1. Test Email System
Create an escalation through the production UI and verify:
- Email is sent to `abparts_support@oraseas.com`
- Email contains complete escalation details
- No errors in AI assistant logs

### 2. Check Logs
```bash
# Monitor AI assistant logs
docker compose -f docker-compose.prod.yml logs -f ai_assistant

# Look for successful email sending messages
docker compose -f docker-compose.prod.yml logs ai_assistant | grep -i email
```

### 3. Verify Email Delivery
- Check `abparts_support@oraseas.com` inbox
- Verify email formatting and content
- Test escalation workflow end-to-end

## 🚨 Troubleshooting

### Common Issues

#### 1. SMTP Authentication Failed
**Error**: `Authentication unsuccessful, SmtpClientAuthentication is disabled`
**Solution**: Enable SMTP AUTH in Microsoft 365 Admin Center

#### 2. Environment Variables Not Loaded
**Error**: `SMTP credentials not configured`
**Solution**: 
- Verify `.env` file exists in production directory
- Check file permissions: `chmod 600 .env`
- Restart AI assistant: `docker compose -f docker-compose.prod.yml restart ai_assistant`

#### 3. Email Not Received
**Possible Causes**:
- Check spam/junk folder
- Verify `FROM_EMAIL` is correct
- Check Microsoft 365 mail flow rules
- Verify network connectivity from production server

### Debug Commands

```bash
# Check environment variables in container
docker compose -f docker-compose.prod.yml exec ai_assistant env | grep SMTP

# Test SMTP connection
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import smtplib
try:
    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()
    print('✅ SMTP connection successful')
    server.quit()
except Exception as e:
    print(f'❌ SMTP connection failed: {e}')
"

# Check AI assistant health
curl http://your-production-server:8001/health
```

## 📋 Post-Deployment Checklist

- [ ] Code pushed to repository
- [ ] Production `.env` file updated with SMTP settings
- [ ] Microsoft 365 SMTP AUTH enabled
- [ ] Production services redeployed
- [ ] Environment variables verified in containers
- [ ] Email test successful
- [ ] Escalation workflow tested end-to-end
- [ ] Email delivery confirmed
- [ ] Logs show no errors

## 🔒 Security Considerations

1. **Environment File Security**:
   - Never commit production `.env` to repository
   - Use `chmod 600 .env` for proper permissions
   - Consider using Docker secrets for sensitive data

2. **Email Security**:
   - Use app passwords instead of regular passwords when possible
   - Enable MFA on email accounts
   - Monitor email sending for abuse

3. **Network Security**:
   - Ensure production server can reach `smtp.office365.com:587`
   - Consider firewall rules for SMTP traffic
   - Use TLS encryption for email transmission

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review AI assistant logs for specific error messages
3. Verify Microsoft 365 SMTP settings
4. Test email configuration using the debug commands

The escalation email system is now production-ready and will automatically send professional notification emails to the support team when users escalate issues through the AI assistant!