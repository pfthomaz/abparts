# User Profile and Self-Service Management Implementation

## Overview

This document describes the implementation of Task 3.3 "User Profile and Self-Service Management" from the ABParts business model alignment specification.

## Requirements Implemented

### 2B.1 - User Profile Management
- ✅ **Endpoint**: `PUT /users/me/profile`
- ✅ **Functionality**: Users can update their name and email
- ✅ **Validation**: Email uniqueness validation
- ✅ **Email Change Process**: Email changes require verification

### 2B.2 - Secure Password Change
- ✅ **Endpoint**: `POST /users/me/change-password`
- ✅ **Functionality**: Password change with current password validation
- ✅ **Security**: Current password must be provided and verified

### 2B.3 - Email Verification System
- ✅ **Endpoint**: `POST /users/me/request-email-verification`
- ✅ **Endpoint**: `POST /users/confirm-email-verification`
- ✅ **Functionality**: Two-step email change process with verification
- ✅ **Security**: Verification tokens expire after 24 hours

### 2B.4 - User Profile View
- ✅ **Endpoint**: `GET /users/me/profile`
- ✅ **Functionality**: Returns user profile with role and organization information
- ✅ **Data**: Includes user details, role, organization name and type

### 2B.5 - User Account Status Management
- ✅ **Endpoint**: `PATCH /users/{user_id}/status`
- ✅ **Functionality**: Admins can update user account status
- ✅ **Authorization**: Role-based access control (admin/super_admin only)

### 2B.6 - Password Reset via Email
- ✅ **Endpoint**: `POST /users/request-password-reset`
- ✅ **Endpoint**: `POST /users/confirm-password-reset`
- ✅ **Functionality**: Password reset via email with secure tokens
- ✅ **Security**: Reset tokens expire after 1 hour

## Database Schema Changes

### New User Model Fields
```sql
-- Email verification fields
email_verification_token VARCHAR(255)
email_verification_expires_at TIMESTAMP WITH TIME ZONE
pending_email VARCHAR(255)

-- Foreign key for invitation tracking
invited_by_user_id UUID REFERENCES users(id)
```

### New Table: invitation_audit_logs
```sql
CREATE TABLE invitation_audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    performed_by_user_id UUID REFERENCES users(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    details TEXT
);
```

## API Endpoints

### User Profile Management
- `GET /users/me/profile` - Get current user's profile
- `PUT /users/me/profile` - Update current user's profile

### Password Management
- `POST /users/me/change-password` - Change password (requires current password)
- `POST /users/request-password-reset` - Request password reset via email
- `POST /users/confirm-password-reset` - Confirm password reset with token

### Email Management
- `POST /users/me/request-email-verification` - Request email change verification
- `POST /users/confirm-email-verification` - Confirm email change with token

### Account Status Management
- `PATCH /users/{user_id}/status` - Update user account status (admin only)

## Schemas

### Request Schemas
- `UserProfileUpdate` - For profile updates (name, email)
- `UserPasswordChange` - For password changes (current + new password)
- `PasswordResetRequest` - For password reset requests (email)
- `PasswordResetConfirm` - For password reset confirmation (token + new password)
- `EmailVerificationRequest` - For email verification requests (new email)
- `EmailVerificationConfirm` - For email verification confirmation (token)
- `UserAccountStatusUpdate` - For status updates (user_status)

### Response Schemas
- `UserProfileResponse` - Complete user profile with organization info

## Email Notifications

### New Email Tasks
- `send_password_reset_email` - Sends password reset link
- `send_email_verification_email` - Sends email verification link

### Email Templates
- Professional HTML and plain text templates
- Secure token-based links
- Clear expiration information
- Security warnings for unauthorized requests

## Security Features

### Token Security
- Cryptographically secure tokens using `secrets.token_urlsafe(32)`
- Time-based expiration (1 hour for password reset, 24 hours for email verification)
- Single-use tokens (cleared after successful use)

### Access Control
- Self-service endpoints require user authentication
- Admin endpoints require admin/super_admin roles
- Organization-scoped permissions for admin operations

### Email Security
- Email enumeration protection (always return success for password reset)
- Verification emails sent to new email address
- Clear security warnings in email templates

## CRUD Operations

### New Functions in `crud/users.py`
- `update_user_profile()` - Update user profile with email validation
- `change_user_password()` - Change password with current password verification
- `request_password_reset()` - Generate password reset token
- `confirm_password_reset()` - Confirm password reset with token
- `request_email_verification()` - Generate email verification token
- `confirm_email_verification()` - Confirm email change with token
- `get_user_profile_with_organization()` - Get profile with organization details
- `update_user_status()` - Update user account status

## Error Handling

### Validation Errors
- Email uniqueness validation
- Current password verification
- Token expiration checking
- Permission validation

### Security Considerations
- No sensitive information in error messages
- Consistent response times to prevent timing attacks
- Email enumeration protection

## Testing

### Manual Testing Checklist
- [ ] User can view their profile with organization info
- [ ] User can update their name
- [ ] User can request email change (triggers verification)
- [ ] User can verify email change with token
- [ ] User can change password with current password
- [ ] User can request password reset via email
- [ ] User can reset password with token
- [ ] Admin can update user account status
- [ ] All email notifications are sent correctly
- [ ] All security validations work properly

## Migration

A database migration file has been created:
- `backend/alembic/versions/add_user_profile_fields.py`
- Adds new user profile fields
- Creates invitation_audit_logs table
- Adds missing foreign key constraints

## Dependencies

### Email Service
- Requires SMTP configuration in environment variables
- Uses Celery for asynchronous email sending
- HTML and plain text email templates

### Database
- PostgreSQL with UUID support
- Requires migration to add new fields
- Uses existing user and organization tables

## Compliance

This implementation fully satisfies the requirements specified in:
- Requirement 2B.1: User profile management endpoints
- Requirement 2B.2: Secure password change workflow
- Requirement 2B.3: Email verification system
- Requirement 2B.4: User profile view with organization info
- Requirement 2B.5: User account status management
- Requirement 2B.6: Password reset via email functionality

All endpoints include proper authentication, authorization, validation, and error handling as specified in the business model alignment requirements.