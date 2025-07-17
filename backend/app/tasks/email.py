# backend/app/tasks/email.py

import logging
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task
def send_invitation_email(email, name, invitation_token, invited_by_name, organization_name):
    """Send invitation email to new user."""
    logger.info(f"Sending invitation email to {email}")
    # Implementation would connect to email service

@shared_task
def send_invitation_accepted_notification(admin_email, user_name, user_email, organization_name):
    """Send notification to admin when invitation is accepted."""
    logger.info(f"Sending invitation accepted notification to {admin_email}")
    # Implementation would connect to email service

@shared_task
def send_password_reset_email(email, name, reset_token):
    """Send password reset email."""
    logger.info(f"Sending password reset email to {email}")
    # Implementation would connect to email service

@shared_task
def send_email_verification_email(email, name, verification_token, new_email):
    """Send email verification for email change."""
    logger.info(f"Sending email verification to {email} for new email {new_email}")
    # Implementation would connect to email service

@shared_task
def send_user_reactivation_notification(user_email, user_name, admin_name, organization_name):
    """Send notification when user account is reactivated."""
    logger.info(f"Sending reactivation notification to {user_email}")
    # Implementation would connect to email service