"""
Email service for AI Assistant escalation notifications.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending escalation notification emails."""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        self.use_tls = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        self.use_ssl = os.getenv('SMTP_USE_SSL', 'false').lower() == 'true'
        
        # Support email address
        self.support_email = 'abparts_support@oraseas.com'
        
    def send_escalation_notification(
        self,
        ticket_data: Dict[str, Any],
        user_info: Optional[Dict[str, Any]] = None,
        machine_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send escalation notification email to support team.
        
        Args:
            ticket_data: Support ticket information
            user_info: User information from session
            machine_info: Machine context information
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            subject = f"🚨 AI Assistant Escalation - Ticket #{ticket_data.get('ticket_number', 'Unknown')}"
            
            # Create email content
            html_content = self._create_escalation_email_html(ticket_data, user_info, machine_info)
            text_content = self._create_escalation_email_text(ticket_data, user_info, machine_info)
            
            # Send email
            success = self._send_email(
                to_email=self.support_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                logger.info(f"Escalation email sent successfully for ticket {ticket_data.get('ticket_number')}")
            else:
                logger.error(f"Failed to send escalation email for ticket {ticket_data.get('ticket_number')}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending escalation notification: {e}")
            return False
    
    def _create_escalation_email_html(
        self,
        ticket_data: Dict[str, Any],
        user_info: Optional[Dict[str, Any]] = None,
        machine_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create HTML email content for escalation notification."""
        
        # Priority styling
        priority = ticket_data.get('priority', 'medium')
        priority_colors = {
            'low': '#10B981',      # Green
            'medium': '#F59E0B',   # Yellow
            'high': '#EF4444',     # Red
            'urgent': '#DC2626'    # Dark Red
        }
        priority_color = priority_colors.get(priority, '#F59E0B')
        
        # Escalation reason mapping
        reason_labels = {
            'user_request': 'User requested expert help',
            'low_confidence': 'AI has low confidence in solution',
            'steps_exceeded': 'Too many troubleshooting steps attempted',
            'safety_concern': 'Safety concern identified',
            'complex_issue': 'Complex technical issue detected',
            'expert_required': 'Expert knowledge required'
        }
        
        escalation_reason = ticket_data.get('escalation_reason', 'user_request')
        reason_label = reason_labels.get(escalation_reason, escalation_reason)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant Escalation - Ticket #{ticket_data.get('ticket_number', 'Unknown')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background-color: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .header .ticket-number {{ font-size: 18px; opacity: 0.9; margin-top: 5px; }}
        .priority-badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase; color: white; background-color: {priority_color}; }}
        .content {{ padding: 30px; }}
        .section {{ margin-bottom: 25px; }}
        .section h2 {{ color: #4a5568; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 15px; }}
        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
        .info-item {{ background-color: #f7fafc; padding: 15px; border-radius: 6px; border-left: 4px solid #667eea; }}
        .info-item strong {{ color: #2d3748; }}
        .session-summary {{ background-color: #f0f4f8; padding: 20px; border-radius: 6px; border: 1px solid #cbd5e0; }}
        .session-summary pre {{ white-space: pre-wrap; font-family: 'Courier New', monospace; font-size: 12px; margin: 0; }}
        .machine-info {{ background-color: #edf2f7; padding: 15px; border-radius: 6px; }}
        .footer {{ background-color: #f7fafc; padding: 20px; border-radius: 0 0 8px 8px; text-align: center; color: #718096; font-size: 14px; }}
        .urgent {{ animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} 100% {{ opacity: 1; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header {'urgent' if priority == 'urgent' else ''}">
            <h1>🚨 AI Assistant Escalation</h1>
            <div class="ticket-number">Ticket #{ticket_data.get('ticket_number', 'Unknown')}</div>
            <div style="margin-top: 10px;">
                <span class="priority-badge">{priority.upper()} PRIORITY</span>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📋 Escalation Details</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Reason:</strong><br>
                        {reason_label}
                    </div>
                    <div class="info-item">
                        <strong>Created:</strong><br>
                        {datetime.fromisoformat(ticket_data.get('created_at', datetime.utcnow().isoformat())).strftime('%Y-%m-%d %H:%M:%S UTC')}
                    </div>
                    <div class="info-item">
                        <strong>Session ID:</strong><br>
                        {ticket_data.get('session_id', 'Unknown')}
                    </div>
                    <div class="info-item">
                        <strong>Status:</strong><br>
                        {ticket_data.get('status', 'open').upper()}
                    </div>
                </div>
                
                {f'''
                <div class="info-item" style="grid-column: 1 / -1;">
                    <strong>Additional Notes:</strong><br>
                    {ticket_data.get('additional_notes', 'No additional notes provided.')}
                </div>
                ''' if ticket_data.get('additional_notes') else ''}
            </div>
            
            {f'''
            <div class="section">
                <h2>👤 User Information</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Name:</strong><br>
                        {user_info.get('full_name', 'Unknown')}
                    </div>
                    <div class="info-item">
                        <strong>Email:</strong><br>
                        {user_info.get('email', 'Unknown')}
                    </div>
                    <div class="info-item">
                        <strong>Organization:</strong><br>
                        {user_info.get('organization_name', 'Unknown')}
                    </div>
                    <div class="info-item">
                        <strong>Role:</strong><br>
                        {user_info.get('role', 'Unknown')}
                    </div>
                </div>
            </div>
            ''' if user_info else ''}
            
            {f'''
            <div class="section">
                <h2>🔧 Machine Information</h2>
                <div class="machine-info">
                    <strong>Machine:</strong> {machine_info.get('name', 'Unknown')}<br>
                    <strong>Model:</strong> {machine_info.get('model_type', 'Unknown')}<br>
                    <strong>Serial:</strong> {machine_info.get('serial_number', 'Unknown')}<br>
                    <strong>Hours:</strong> {machine_info.get('latest_hours', 'Unknown')} hours<br>
                    <strong>Location:</strong> {machine_info.get('location', 'Unknown')}
                </div>
            </div>
            ''' if machine_info else ''}
            
            <div class="section">
                <h2>📝 Session Summary</h2>
                <div class="session-summary">
                    <pre>{ticket_data.get('session_summary', 'No session summary available.')}</pre>
                </div>
            </div>
            
            {f'''
            <div class="section">
                <h2>📞 Expert Contact Information</h2>
                <div class="info-item">
                    {self._format_expert_contact_info(ticket_data.get('expert_contact_info', {}))}
                </div>
            </div>
            ''' if ticket_data.get('expert_contact_info') else ''}
        </div>
        
        <div class="footer">
            <p>This escalation was automatically generated by the ABParts AI Assistant system.</p>
            <p>Please respond to this ticket as soon as possible based on the priority level.</p>
            <p><strong>ABParts Support System</strong> | Oraseas EE</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def _create_escalation_email_text(
        self,
        ticket_data: Dict[str, Any],
        user_info: Optional[Dict[str, Any]] = None,
        machine_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create plain text email content for escalation notification."""
        
        reason_labels = {
            'user_request': 'User requested expert help',
            'low_confidence': 'AI has low confidence in solution',
            'steps_exceeded': 'Too many troubleshooting steps attempted',
            'safety_concern': 'Safety concern identified',
            'complex_issue': 'Complex technical issue detected',
            'expert_required': 'Expert knowledge required'
        }
        
        escalation_reason = ticket_data.get('escalation_reason', 'user_request')
        reason_label = reason_labels.get(escalation_reason, escalation_reason)
        
        text = f"""
🚨 AI ASSISTANT ESCALATION - TICKET #{ticket_data.get('ticket_number', 'Unknown')}

ESCALATION DETAILS:
==================
Reason: {reason_label}
Priority: {ticket_data.get('priority', 'medium').upper()}
Created: {datetime.fromisoformat(ticket_data.get('created_at', datetime.utcnow().isoformat())).strftime('%Y-%m-%d %H:%M:%S UTC')}
Session ID: {ticket_data.get('session_id', 'Unknown')}
Status: {ticket_data.get('status', 'open').upper()}

{f"Additional Notes: {ticket_data.get('additional_notes')}" if ticket_data.get('additional_notes') else ''}

{f'''USER INFORMATION:
==================
Name: {user_info.get('full_name', 'Unknown')}
Email: {user_info.get('email', 'Unknown')}
Organization: {user_info.get('organization_name', 'Unknown')}
Role: {user_info.get('role', 'Unknown')}

''' if user_info else ''}

{f'''MACHINE INFORMATION:
====================
Machine: {machine_info.get('name', 'Unknown')}
Model: {machine_info.get('model_type', 'Unknown')}
Serial: {machine_info.get('serial_number', 'Unknown')}
Hours: {machine_info.get('latest_hours', 'Unknown')} hours
Location: {machine_info.get('location', 'Unknown')}

''' if machine_info else ''}

SESSION SUMMARY:
================
{ticket_data.get('session_summary', 'No session summary available.')}

{f'''EXPERT CONTACT INFORMATION:
============================
{self._format_expert_contact_info_text(ticket_data.get('expert_contact_info', {}))}

''' if ticket_data.get('expert_contact_info') else ''}

---
This escalation was automatically generated by the ABParts AI Assistant system.
Please respond to this ticket as soon as possible based on the priority level.

ABParts Support System | Oraseas EE
        """
        
        return text.strip()
    
    def _format_expert_contact_info(self, contact_info: Dict[str, Any]) -> str:
        """Format expert contact information for HTML email."""
        if not contact_info:
            return "No expert contact information available."
        
        primary = contact_info.get('primary_contact', {})
        if not primary:
            return "No primary contact information available."
        
        return f"""
        <strong>Primary Contact:</strong><br>
        Name: {primary.get('name', 'Unknown')}<br>
        Phone: {primary.get('phone', 'Unknown')}<br>
        Email: {primary.get('email', 'Unknown')}<br>
        Hours: {primary.get('hours', 'Unknown')}<br>
        Specialization: {primary.get('specialization', 'General support')}
        """
    
    def _format_expert_contact_info_text(self, contact_info: Dict[str, Any]) -> str:
        """Format expert contact information for plain text email."""
        if not contact_info:
            return "No expert contact information available."
        
        primary = contact_info.get('primary_contact', {})
        if not primary:
            return "No primary contact information available."
        
        return f"""Primary Contact:
Name: {primary.get('name', 'Unknown')}
Phone: {primary.get('phone', 'Unknown')}
Email: {primary.get('email', 'Unknown')}
Hours: {primary.get('hours', 'Unknown')}
Specialization: {primary.get('specialization', 'General support')}"""
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """Send email using SMTP."""
        try:
            # Check if SMTP is properly configured
            if not self.smtp_username or not self.smtp_password:
                logger.warning("SMTP credentials not configured - email sending disabled")
                logger.info(f"Would send email to {to_email} with subject: {subject}")
                logger.debug(f"Email content preview: {text_content[:200]}...")
                return False  # Return False but don't raise exception
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Create text and HTML parts
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            # Add parts to message
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.starttls()
            
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
            
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False


# Global email service instance
email_service = EmailService()