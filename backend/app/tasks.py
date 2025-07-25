# backend/app/tasks.py
# This file will contain your Celery tasks.

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from .celery_app import celery

logger = logging.getLogger(__name__)

# Email configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)
BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")

@celery.task(bind=True, max_retries=3)
def send_invitation_email(self, email: str, name: Optional[str], invitation_token: str, invited_by_name: str, organization_name: str):
    """
    Send invitation email to a new user.
    """
    try:
        if not all([SMTP_USERNAME, SMTP_PASSWORD]):
            logger.error("SMTP credentials not configured")
            return {"success": False, "error": "SMTP credentials not configured"}

        # Create invitation URL
        invitation_url = f"{BASE_URL}/accept-invitation?token={invitation_token}"
        
        # Create email content
        subject = f"Invitation to join {organization_name} on ABParts"
        
        # HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>ABParts Invitation</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">You're invited to join ABParts!</h2>
                
                <p>Hello{f" {name}" if name else ""},</p>
                
                <p>{invited_by_name} has invited you to join <strong>{organization_name}</strong> on ABParts, the AutoBoss parts management system.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>What's next?</strong></p>
                    <ol style="margin: 10px 0;">
                        <li>Click the invitation link below</li>
                        <li>Set up your username and password</li>
                        <li>Start managing parts and inventory</li>
                    </ol>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{invitation_url}" 
                       style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Accept Invitation
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    <strong>Important:</strong> This invitation will expire in 7 days. If you don't accept it by then, you'll need to request a new invitation.
                </p>
                
                <p style="color: #666; font-size: 14px;">
                    If you can't click the button above, copy and paste this link into your browser:<br>
                    <a href="{invitation_url}">{invitation_url}</a>
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px;">
                    This email was sent by ABParts. If you received this email by mistake, please ignore it.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
        You're invited to join ABParts!
        
        Hello{f" {name}" if name else ""},
        
        {invited_by_name} has invited you to join {organization_name} on ABParts, the AutoBoss parts management system.
        
        To accept this invitation:
        1. Click this link: {invitation_url}
        2. Set up your username and password
        3. Start managing parts and inventory
        
        Important: This invitation will expire in 7 days.
        
        If you can't click the link, copy and paste it into your browser:
        {invitation_url}
        
        ---
        This email was sent by ABParts. If you received this email by mistake, please ignore it.
        """

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = email

        # Attach both plain text and HTML versions
        text_part = MIMEText(text_body, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Invitation email sent successfully to {email}")
        return {"success": True, "message": f"Invitation email sent to {email}"}

    except Exception as exc:
        logger.error(f"Failed to send invitation email to {email}: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))

@celery.task(bind=True, max_retries=3)
def send_invitation_accepted_notification(self, admin_email: str, user_name: str, user_email: str, organization_name: str):
    """
    Send notification to admin when a user accepts an invitation.
    """
    try:
        if not all([SMTP_USERNAME, SMTP_PASSWORD]):
            logger.error("SMTP credentials not configured")
            return {"success": False, "error": "SMTP credentials not configured"}

        subject = f"New user joined {organization_name} - {user_name}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>New User Notification</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #27ae60;">New User Joined!</h2>
                
                <p>Good news! A new user has accepted their invitation and joined your organization.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>User Details:</strong></p>
                    <ul style="margin: 10px 0;">
                        <li><strong>Name:</strong> {user_name}</li>
                        <li><strong>Email:</strong> {user_email}</li>
                        <li><strong>Organization:</strong> {organization_name}</li>
                    </ul>
                </div>
                
                <p>The user can now access ABParts and start working with your team.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px;">
                    This is an automated notification from ABParts.
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        New User Joined!
        
        Good news! A new user has accepted their invitation and joined your organization.
        
        User Details:
        - Name: {user_name}
        - Email: {user_email}
        - Organization: {organization_name}
        
        The user can now access ABParts and start working with your team.
        
        ---
        This is an automated notification from ABParts.
        """

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = admin_email

        # Attach both versions
        text_part = MIMEText(text_body, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"User acceptance notification sent to {admin_email}")
        return {"success": True, "message": f"Notification sent to {admin_email}"}

    except Exception as exc:
        logger.error(f"Failed to send notification to {admin_email}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))

# For example, your ML recommendation task would go here:
# from .celery_app import celery
# from your_ml_module import YourMLModel

# @celery.task
# def update_recommendations_task():
#     """
#     Task to update minimum stock recommendations.
#     """
#     # Placeholder for your ML logic
#     print("Running update_recommendations_task...")
#     # Example:
#     # model = YourMLModel()
#     # recommendations = model.generate_recommendations()
#     # Update database with new recommendations
#     # ...
#     return "Recommendations updated successfully."

@celery.task
def cleanup_expired_invitations():
    """
    Periodic task to mark expired invitations and send notifications.
    This task should be run daily via Celery Beat.
    """
    from .database import SessionLocal
    from .crud.users import mark_invitations_as_expired, get_expired_invitations
    from .crud.organizations import get_organization
    
    db = SessionLocal()
    try:
        # Get expired invitations before marking them
        expired_invitations = get_expired_invitations(db)
        
        if not expired_invitations:
            logger.info("No expired invitations found")
            return {"expired_count": 0, "notifications_sent": 0}
        
        # Mark invitations as expired
        expired_count = mark_invitations_as_expired(db)
        
        # Send notifications to admins about expired invitations
        notifications_sent = 0
        for user in expired_invitations:
            try:
                # Get organization details
                organization = get_organization(db, user.organization_id)
                if not organization:
                    continue
                
                # Get the admin who sent the invitation
                if user.invited_by_user_id:
                    from .crud.users import get_user
                    inviting_admin = get_user(db, user.invited_by_user_id)
                    if inviting_admin and inviting_admin.email:
                        # Send notification about expired invitation
                        send_invitation_expired_notification.delay(
                            admin_email=inviting_admin.email,
                            user_email=user.email,
                            user_name=user.name or "Unknown",
                            organization_name=organization.name
                        )
                        notifications_sent += 1
            except Exception as e:
                logger.error(f"Failed to send expiry notification for user {user.email}: {str(e)}")
        
        logger.info(f"Processed {expired_count} expired invitations, sent {notifications_sent} notifications")
        return {"expired_count": expired_count, "notifications_sent": notifications_sent}
        
    except Exception as e:
        logger.error(f"Failed to cleanup expired invitations: {str(e)}")
        raise
    finally:
        db.close()

@celery.task(bind=True, max_retries=3)
def send_invitation_expired_notification(self, admin_email: str, user_email: str, user_name: str, organization_name: str):
    """
    Send notification to admin when an invitation expires.
    """
    try:
        if not all([SMTP_USERNAME, SMTP_PASSWORD]):
            logger.error("SMTP credentials not configured")
            return {"success": False, "error": "SMTP credentials not configured"}

        subject = f"Invitation expired for {user_name} - {organization_name}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Invitation Expired</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #e74c3c;">Invitation Expired</h2>
                
                <p>An invitation you sent has expired and needs to be resent if you still want the user to join your organization.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Expired Invitation Details:</strong></p>
                    <ul style="margin: 10px 0;">
                        <li><strong>User Name:</strong> {user_name}</li>
                        <li><strong>Email:</strong> {user_email}</li>
                        <li><strong>Organization:</strong> {organization_name}</li>
                    </ul>
                </div>
                
                <p>If you still want this user to join your organization, please send a new invitation through the ABParts system.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px;">
                    This is an automated notification from ABParts.
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Invitation Expired
        
        An invitation you sent has expired and needs to be resent if you still want the user to join your organization.
        
        Expired Invitation Details:
        - User Name: {user_name}
        - Email: {user_email}
        - Organization: {organization_name}
        
        If you still want this user to join your organization, please send a new invitation through the ABParts system.
        
        ---
        This is an automated notification from ABParts.
        """

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = admin_email

        # Attach both versions
        text_part = MIMEText(text_body, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Invitation expiry notification sent to {admin_email}")
        return {"success": True, "message": f"Notification sent to {admin_email}"}

    except Exception as exc:
        logger.error(f"Failed to send expiry notification to {admin_email}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))

@celery.task(bind=True, max_retries=3)
def send_password_reset_email(self, email: str, name: Optional[str], reset_token: str):
    """
    Send password reset email to user.
    """
    try:
        if not all([SMTP_USERNAME, SMTP_PASSWORD]):
            logger.error("SMTP credentials not configured")
            return {"success": False, "error": "SMTP credentials not configured"}

        # Create password reset URL
        reset_url = f"{BASE_URL}/reset-password?token={reset_token}"
        
        # Create email content
        subject = "Password Reset Request - ABParts"
        
        # HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset - ABParts</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Password Reset Request</h2>
                
                <p>Hello{f" {name}" if name else ""},</p>
                
                <p>We received a request to reset your password for your ABParts account.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>To reset your password:</strong></p>
                    <ol style="margin: 10px 0;">
                        <li>Click the reset link below</li>
                        <li>Enter your new password</li>
                        <li>Confirm your new password</li>
                    </ol>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #e74c3c; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    <strong>Important:</strong> This password reset link will expire in 1 hour for security reasons.
                </p>
                
                <p style="color: #666; font-size: 14px;">
                    If you didn't request a password reset, please ignore this email. Your password will remain unchanged.
                </p>
                
                <p style="color: #666; font-size: 14px;">
                    If you can't click the button above, copy and paste this link into your browser:<br>
                    <a href="{reset_url}">{reset_url}</a>
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px;">
                    This email was sent by ABParts. If you received this email by mistake, please ignore it.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
        Password Reset Request
        
        Hello{f" {name}" if name else ""},
        
        We received a request to reset your password for your ABParts account.
        
        To reset your password:
        1. Click this link: {reset_url}
        2. Enter your new password
        3. Confirm your new password
        
        Important: This password reset link will expire in 1 hour for security reasons.
        
        If you didn't request a password reset, please ignore this email. Your password will remain unchanged.
        
        If you can't click the link, copy and paste it into your browser:
        {reset_url}
        
        ---
        This email was sent by ABParts. If you received this email by mistake, please ignore it.
        """

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = email

        # Attach both plain text and HTML versions
        text_part = MIMEText(text_body, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Password reset email sent successfully to {email}")
        return {"success": True, "message": f"Password reset email sent to {email}"}

    except Exception as exc:
        logger.error(f"Failed to send password reset email to {email}: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))

@celery.task(bind=True, max_retries=3)
def send_email_verification_email(self, email: str, name: Optional[str], verification_token: str, new_email: str):
    """
    Send email verification email for email change.
    """
    try:
        if not all([SMTP_USERNAME, SMTP_PASSWORD]):
            logger.error("SMTP credentials not configured")
            return {"success": False, "error": "SMTP credentials not configured"}

        # Create email verification URL
        verification_url = f"{BASE_URL}/verify-email?token={verification_token}"
        
        # Create email content
        subject = "Email Verification Required - ABParts"
        
        # HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Email Verification - ABParts</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Email Verification Required</h2>
                
                <p>Hello{f" {name}" if name else ""},</p>
                
                <p>You requested to change your email address to <strong>{new_email}</strong>.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>To complete this change:</strong></p>
                    <ol style="margin: 10px 0;">
                        <li>Click the verification link below</li>
                        <li>Your email address will be updated</li>
                        <li>You can continue using ABParts with your new email</li>
                    </ol>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Verify Email Address
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    <strong>Important:</strong> This verification link will expire in 24 hours for security reasons.
                </p>
                
                <p style="color: #666; font-size: 14px;">
                    If you didn't request this email change, please contact your administrator immediately.
                </p>
                
                <p style="color: #666; font-size: 14px;">
                    If you can't click the button above, copy and paste this link into your browser:<br>
                    <a href="{verification_url}">{verification_url}</a>
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px;">
                    This email was sent by ABParts. If you received this email by mistake, please ignore it.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
        Email Verification Required
        
        Hello{f" {name}" if name else ""},
        
        You requested to change your email address to {new_email}.
        
        To complete this change:
        1. Click this link: {verification_url}
        2. Your email address will be updated
        3. You can continue using ABParts with your new email
        
        Important: This verification link will expire in 24 hours for security reasons.
        
        If you didn't request this email change, please contact your administrator immediately.
        
        If you can't click the link, copy and paste it into your browser:
        {verification_url}
        
        ---
        This email was sent by ABParts. If you received this email by mistake, please ignore it.
        """

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = new_email  # Send to the new email address

        # Attach both plain text and HTML versions
        text_part = MIMEText(text_body, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email verification email sent successfully to {new_email}")
        return {"success": True, "message": f"Email verification email sent to {new_email}"}

    except Exception as exc:
        logger.error(f"Failed to send email verification email to {new_email}: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))

@celery.task(bind=True, max_retries=3)
def send_user_reactivation_notification(self, user_email: str, user_name: str, admin_name: str, organization_name: str):
    """
    Send notification to user when their account is reactivated.
    Requirements: 2C.4
    """
    try:
        if not all([SMTP_USERNAME, SMTP_PASSWORD]):
            logger.error("SMTP credentials not configured")
            return {"success": False, "error": "SMTP credentials not configured"}

        subject = f"Your ABParts account has been reactivated - {organization_name}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Account Reactivated - ABParts</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #27ae60;">Account Reactivated!</h2>
                
                <p>Hello {user_name},</p>
                
                <p>Good news! Your ABParts account has been reactivated by {admin_name}.</p>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Account Details:</strong></p>
                    <ul style="margin: 10px 0;">
                        <li><strong>Organization:</strong> {organization_name}</li>
                        <li><strong>Status:</strong> Active</li>
                        <li><strong>Reactivated by:</strong> {admin_name}</li>
                    </ul>
                </div>
                
                <p>You can now log in to ABParts and access all your previous functionality. If you have any questions, please contact your administrator.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{BASE_URL}/login" 
                       style="background-color: #27ae60; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Login to ABParts
                    </a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #999; font-size: 12px;">
                    This is an automated notification from ABParts.
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Account Reactivated!
        
        Hello {user_name},
        
        Good news! Your ABParts account has been reactivated by {admin_name}.
        
        Account Details:
        - Organization: {organization_name}
        - Status: Active
        - Reactivated by: {admin_name}
        
        You can now log in to ABParts and access all your previous functionality. If you have any questions, please contact your administrator.
        
        Login at: {BASE_URL}/login
        
        ---
        This is an automated notification from ABParts.
        """

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = user_email

        # Attach both versions
        text_part = MIMEText(text_body, 'plain')
        html_part = MIMEText(html_body, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)

        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"User reactivation notification sent to {user_email}")
        return {"success": True, "message": f"Notification sent to {user_email}"}

    except Exception as exc:
        logger.error(f"Failed to send reactivation notification to {user_email}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
