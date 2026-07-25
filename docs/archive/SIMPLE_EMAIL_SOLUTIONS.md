# Simple Email Solutions for Escalation System

## Option 1: Gmail SMTP (Recommended - Easiest)

### Setup Steps:
1. **Create Gmail Account**: `abparts.support@gmail.com`
2. **Enable 2-Factor Authentication** on the Gmail account
3. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
4. **Update Environment Variables**:

```bash
# In .env.production
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=abparts.support@gmail.com
SMTP_PASSWORD=your_app_password_here
SMTP_FROM_EMAIL=abparts.support@gmail.com
SMTP_FROM_NAME=ABParts Support
```

### Pros:
- ✅ Works immediately
- ✅ No tenant configuration needed
- ✅ Reliable delivery
- ✅ Free for low volume

### Cons:
- ⚠️ Uses Gmail domain instead of oraseas.com
- ⚠️ Daily sending limits (500 emails/day)

---

## Option 2: SendGrid (Professional)

### Setup Steps:
1. **Create SendGrid Account** (free tier: 100 emails/day)
2. **Get API Key** from SendGrid dashboard
3. **Update Email Service** to use SendGrid API instead of SMTP

```python
# Update ai_assistant/app/services/email_service.py
import sendgrid
from sendgrid.helpers.mail import Mail

class EmailService:
    def __init__(self):
        self.sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
    
    def send_escalation_notification(self, ticket_data, user_info, machine_info):
        message = Mail(
            from_email='support@oraseas.com',
            to_emails='abparts_support@oraseas.com',
            subject=f'Escalation Ticket: {ticket_data["ticket_number"]}',
            html_content=self._build_html_email(ticket_data, user_info, machine_info)
        )
        
        try:
            response = self.sg.send(message)
            return response.status_code == 202
        except Exception as e:
            self.logger.error(f"SendGrid error: {e}")
            return False
```

### Environment Variables:
```bash
SENDGRID_API_KEY=your_sendgrid_api_key_here
```

### Pros:
- ✅ Professional email service
- ✅ Uses your domain (support@oraseas.com)
- ✅ Better deliverability
- ✅ Detailed analytics

### Cons:
- ⚠️ Requires code changes
- ⚠️ Costs money after free tier

---

## Option 3: Fix Microsoft 365 (Current Setup)

### Quick Fix Commands:
```bash
# Enable SMTP AUTH for the organization (requires admin)
Connect-ExchangeOnline
Set-TransportConfig -SmtpClientAuthenticationDisabled $false

# OR enable for specific mailbox
Set-CASMailbox -Identity "abparts_support@oraseas.com" -SmtpClientAuthenticationDisabled $false
```

### Alternative - Use OAuth2:
Update the email service to use Microsoft Graph API instead of SMTP.

---

## Recommended Solution: Gmail SMTP

**For immediate functionality, use Gmail SMTP:**

1. **Create Gmail account**: `abparts.support@gmail.com`
2. **Generate app password**
3. **Update production environment**:

```bash
# Run these commands on production server:
docker compose -f docker-compose.prod.yml exec ai_assistant sh -c '
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587  
export SMTP_USERNAME=abparts.support@gmail.com
export SMTP_PASSWORD=your_app_password_here
export SMTP_FROM_EMAIL=abparts.support@gmail.com
export SMTP_FROM_NAME="ABParts Support"
'

# Restart AI assistant to pick up new environment
docker compose -f docker-compose.prod.yml restart ai_assistant
```

4. **Test escalation** - emails should now work immediately!

---

## Quick Test Script

```python
# test_gmail_smtp.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_gmail_smtp():
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    username = "abparts.support@gmail.com"  
    password = "your_app_password_here"
    
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = "abparts_support@oraseas.com"
    msg['Subject'] = "Test Escalation Email"
    
    body = "This is a test escalation email from ABParts AI Assistant."
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        print("✅ Email sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

if __name__ == "__main__":
    test_gmail_smtp()
```

**Gmail SMTP is the fastest solution - you can have emails working in 5 minutes!**