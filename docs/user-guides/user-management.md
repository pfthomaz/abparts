# User Management Guide

This comprehensive guide covers user lifecycle management, role-based access control, and security administration for organization administrators.

## User Lifecycle Management

### Understanding User States

Users in ABParts can have different statuses throughout their lifecycle:

#### User Status Types
- **Active**: Normal operational status, full access to assigned features
- **Inactive**: Temporarily disabled, cannot log in or access system
- **Pending Invitation**: Invitation sent but not yet accepted
- **Locked**: Temporarily locked due to security issues (failed logins)

#### Status Transitions
```
Invitation Sent → Pending Invitation
    ↓ (User accepts invitation)
Active ← → Inactive (Admin control)
    ↓ (Security issues)
Locked → Active (After timeout or admin unlock)
```

### User Invitation System

#### Sending Invitations

1. **Navigate to User Management**
   - Go to **Users** in the main navigation
   - Click **Invite New User**

2. **Invitation Details**
   - **Email Address**: User's work email (required)
   - **Full Name**: First and last name
   - **Role**: Select appropriate role (User or Admin)
   - **Department**: Optional organizational unit
   - **Welcome Message**: Custom message for invitation

3. **Invitation Process**
   - System generates secure invitation token
   - Email sent with registration link (valid 7 days)
   - User receives welcome email with instructions
   - Invitation status tracked in system

#### Managing Pending Invitations

1. **Viewing Pending Invitations**
   - Filter users by "Pending Invitation" status
   - See invitation sent date and expiry
   - Track invitation acceptance rates

2. **Invitation Actions**
   - **Resend**: Send new invitation email
   - **Cancel**: Remove pending invitation
   - **Extend**: Reset expiry date
   - **Modify**: Change role or details before acceptance

### User Onboarding Process

#### New User Registration

1. **User Receives Invitation**
   - Email with secure registration link
   - Link valid for 7 days from sending
   - Clear instructions for account setup

2. **Account Setup Process**
   - Click invitation link
   - Verify email address
   - Set secure password (meets policy requirements)
   - Complete profile information
   - Accept terms and conditions

3. **Account Activation**
   - System automatically activates account
   - User gains access based on assigned role
   - Welcome dashboard and orientation materials
   - Initial notification preferences set

#### Post-Registration Setup

1. **Profile Completion**
   - Contact information and preferences
   - Notification settings
   - Security preferences (2FA if available)
   - Department and location details

2. **Initial Training**
   - Role-specific orientation materials
   - System navigation tutorial
   - Key feature demonstrations
   - Safety and security guidelines

## Role-Based Access Control

### Role Assignment and Management

#### Understanding Roles in Your Organization

**User Role Capabilities:**
- Order parts and manage personal orders
- Record part usage in machines
- View inventory levels and availability
- Manage personal profile and settings
- Access organization's machines and warehouses

**Admin Role Capabilities:**
- All user capabilities plus:
- Invite and manage organization users
- Create and manage warehouses
- Adjust inventory levels and perform reconciliation
- Register and manage machines
- Generate reports and analytics
- Manage supplier relationships

#### Assigning and Changing Roles

1. **Role Assignment During Invitation**
   - Select appropriate role when sending invitation
   - Consider user's responsibilities and experience
   - Start with User role, promote to Admin as needed

2. **Changing Existing User Roles**
   - Navigate to **Users** → Select user
   - Click **Edit Role**
   - Select new role and confirm change
   - User notified of role change
   - New permissions take effect immediately

3. **Role Change Restrictions**
   - Cannot remove last admin from organization
   - Only super admins can create super admin users
   - Role changes logged in audit trail

### Permission Management

#### Organization-Scoped Access

All non-super admin users automatically have access limited to:
- Their own organization's data only
- All warehouses within their organization
- Machines owned by their organization
- Transactions involving their organization
- Users within their organization

#### Feature-Level Permissions

**Inventory Management:**
- **Users**: View inventory, record usage
- **Admins**: All user permissions plus adjust stock, manage warehouses

**User Management:**
- **Users**: Manage own profile only
- **Admins**: Invite users, manage roles, deactivate users

**Reporting:**
- **Users**: Basic inventory and usage reports
- **Admins**: Advanced analytics, custom reports, data export

**Machine Management:**
- **Users**: Record usage, view maintenance history
- **Admins**: Register machines, manage machine details

## User Administration

### User Search and Filtering

#### Advanced Search Options

1. **Basic Filters**
   - **Status**: Active, Inactive, Pending, Locked
   - **Role**: User, Admin
   - **Department**: Organizational units
   - **Last Login**: Recent activity

2. **Advanced Filters**
   - **Registration Date**: When user joined
   - **Invitation Status**: Pending, accepted, expired
   - **Activity Level**: Based on recent usage
   - **Permission Groups**: Specific access levels

#### Bulk Operations

1. **Selecting Multiple Users**
   - Use checkboxes to select users
   - Select all with header checkbox
   - Filter first, then select relevant users

2. **Available Bulk Actions**
   - **Activate/Deactivate**: Change status for multiple users
   - **Send Notifications**: Broadcast messages
   - **Export Data**: Generate user reports
   - **Role Changes**: Bulk role assignments (with caution)

### User Profile Management

#### Viewing User Details

1. **User Profile Overview**
   - Basic information (name, email, role)
   - Organization and department
   - Account status and last login
   - Contact information and preferences

2. **Activity Summary**
   - Recent login history
   - Transaction activity
   - Order history
   - System usage patterns

3. **Security Information**
   - Failed login attempts
   - Password last changed
   - Active sessions
   - Security events

#### Editing User Information

1. **Editable Fields (Admin)**
   - Name and contact information
   - Role and department
   - Account status (active/inactive)
   - Notification preferences

2. **Restricted Fields**
   - Email address (requires verification process)
   - Password (user must change themselves)
   - Organization (system-controlled)
   - Creation date and system IDs

### Account Security Management

#### Password and Authentication

1. **Password Policies**
   - Minimum length and complexity requirements
   - Regular password change recommendations
   - Prevention of password reuse
   - Secure password reset procedures

2. **Account Lockout Management**
   - **Automatic Lockout**: After 5 failed login attempts
   - **Lockout Duration**: 15 minutes automatic unlock
   - **Manual Unlock**: Admin can unlock immediately
   - **Lockout Notifications**: User and admin alerts

3. **Session Management**
   - **Session Duration**: 8 hours maximum
   - **Multiple Sessions**: Users can have concurrent sessions
   - **Session Termination**: On password change or deactivation
   - **Inactive Session Cleanup**: Automatic cleanup of old sessions

#### Security Monitoring

1. **Login Activity Monitoring**
   - Track successful and failed login attempts
   - Monitor unusual login patterns
   - Geographic and time-based anomaly detection
   - Suspicious activity alerts

2. **User Activity Auditing**
   - All user actions logged with timestamps
   - Data access and modification tracking
   - Permission usage monitoring
   - Compliance reporting capabilities

## User Deactivation and Reactivation

### Deactivation Process

#### When to Deactivate Users

1. **Employee Departure**
   - Immediate deactivation upon termination
   - Coordinate with HR processes
   - Secure handover of responsibilities

2. **Extended Absence**
   - Long-term medical leave
   - Sabbatical or extended vacation
   - Temporary role changes

3. **Security Concerns**
   - Suspected account compromise
   - Policy violations
   - Pending investigation

#### Deactivation Procedure

1. **Immediate Actions**
   - Change user status to "Inactive"
   - Terminate all active sessions immediately
   - Prevent new login attempts
   - Notify relevant stakeholders

2. **Data and Access Review**
   - Review user's recent activity
   - Secure any sensitive data access
   - Transfer ownership of critical processes
   - Document deactivation reasons

3. **Communication**
   - Notify user of deactivation (if appropriate)
   - Inform team members of status change
   - Update contact lists and responsibilities
   - Document handover procedures

### Reactivation Process

#### Reactivation Criteria

1. **Return from Absence**
   - Employee returns from leave
   - Role responsibilities resume
   - Security clearance confirmed

2. **Issue Resolution**
   - Security concerns addressed
   - Policy compliance restored
   - Investigation completed

#### Reactivation Procedure

1. **Pre-Reactivation Checks**
   - Verify authorization for reactivation
   - Confirm role and permission requirements
   - Check for any system changes during absence
   - Update contact information if needed

2. **Reactivation Process**
   - Change status back to "Active"
   - Verify role and permissions are correct
   - Send reactivation notification to user
   - Monitor initial login and activity

3. **Post-Reactivation**
   - Provide system updates and training if needed
   - Verify access to required resources
   - Update team on user's return
   - Monitor for any access issues

## Audit and Compliance

### User Management Auditing

#### Audit Trail Components

1. **User Account Changes**
   - Account creation and invitation
   - Role changes and permission updates
   - Status changes (activation/deactivation)
   - Profile modifications

2. **Access and Activity Logs**
   - Login and logout events
   - Failed authentication attempts
   - Data access and modifications
   - System feature usage

3. **Administrative Actions**
   - Admin actions on user accounts
   - Bulk operations and changes
   - Security interventions
   - Policy enforcement actions

#### Compliance Reporting

1. **Regular Reports**
   - User access reviews (quarterly)
   - Role assignment audits
   - Inactive user identification
   - Security incident summaries

2. **Ad-Hoc Reports**
   - Investigation support
   - Compliance inquiries
   - Security assessments
   - Process improvement analysis

### Data Protection and Privacy

#### User Data Handling

1. **Data Collection**
   - Collect only necessary information
   - Obtain appropriate consent
   - Document data usage purposes
   - Maintain data accuracy

2. **Data Storage and Security**
   - Encrypt sensitive user data
   - Implement access controls
   - Regular security assessments
   - Backup and recovery procedures

3. **Data Retention**
   - Follow organizational retention policies
   - Secure deletion of expired data
   - Archive requirements compliance
   - User data portability support

## Best Practices

### User Management Excellence

1. **Proactive Management**
   - Regular user access reviews
   - Prompt handling of role changes
   - Timely deactivation of departed users
   - Continuous security monitoring

2. **Communication**
   - Clear invitation and onboarding processes
   - Regular updates on system changes
   - Responsive support for user issues
   - Transparent security policies

3. **Security First**
   - Principle of least privilege
   - Regular security training
   - Prompt incident response
   - Continuous improvement of security measures

### Common Pitfalls to Avoid

1. **Access Management**
   - Don't leave inactive users active
   - Avoid over-privileged accounts
   - Don't ignore failed login patterns
   - Prevent role creep over time

2. **Process Management**
   - Don't skip proper onboarding
   - Avoid inconsistent role assignments
   - Don't ignore audit trail gaps
   - Prevent manual process dependencies

---

**Need Technical Support?** Contact your super administrator or refer to the [System Administration Guide](admin-guides/system-setup.md) for advanced user management configuration.