# User Roles Overview

ABParts uses a role-based access control system to ensure users have appropriate permissions for their responsibilities. This guide explains each role and their capabilities.

## Role Hierarchy

```
Super Admin (Oraseas EE only)
    ↓ Full system access
Admin (Per organization)
    ↓ Organization management
User (Per organization)
    ↓ Basic operations
```

## User Role

**Who**: Regular employees who work with parts and machines daily
**Organization**: Any organization type
**Primary Focus**: Day-to-day parts operations

### Capabilities

#### Parts and Inventory
- ✅ View parts catalog and specifications
- ✅ Check inventory levels across organization warehouses
- ✅ Search and filter parts by type, availability
- ✅ View parts usage history
- ❌ Cannot adjust inventory levels
- ❌ Cannot create or edit parts

#### Ordering and Receiving
- ✅ Create part orders from approved suppliers
- ✅ Update order status when parts arrive
- ✅ View order history and status
- ✅ Receive parts into warehouses
- ❌ Cannot approve high-value orders
- ❌ Cannot manage supplier relationships

#### Machine Operations
- ✅ Record part usage in machines
- ✅ View machine maintenance history
- ✅ Add maintenance notes and observations
- ❌ Cannot register new machines
- ❌ Cannot transfer machine ownership

#### Profile Management
- ✅ Update personal profile information
- ✅ Change password
- ✅ View role and organization information
- ✅ Manage notification preferences
- ❌ Cannot change role or organization

### Data Access Scope
- Own organization's data only
- All warehouses within organization
- Machines owned by organization
- Transactions involving organization

## Admin Role

**Who**: Department managers, warehouse supervisors, organization administrators
**Organization**: Any organization type
**Primary Focus**: Organization management and oversight

### Capabilities

#### All User Capabilities Plus:

#### Organization Management
- ✅ Update organization information
- ✅ Manage organization settings
- ✅ View organization analytics and reports
- ❌ Cannot change organization type
- ❌ Cannot delete organization

#### Warehouse Management
- ✅ Create and configure warehouses
- ✅ Edit warehouse details and locations
- ✅ Activate/deactivate warehouses
- ✅ Transfer inventory between warehouses
- ✅ Set minimum stock levels

#### Inventory Management
- ✅ Adjust inventory levels (with audit trail)
- ✅ Perform stock reconciliation
- ✅ Create inventory reports
- ✅ Set reorder points and recommendations
- ✅ Bulk inventory operations

#### User Management
- ✅ Invite new users to organization
- ✅ Manage user roles (user/admin within org)
- ✅ Activate/deactivate users
- ✅ View user activity and audit logs
- ✅ Reset user passwords
- ❌ Cannot create super admin users

#### Machine Management
- ✅ Register new machines (if super admin approved)
- ✅ Update machine information
- ✅ View machine performance analytics
- ✅ Manage machine-parts relationships
- ✅ Transfer machines between locations

#### Supplier Management
- ✅ Manage organization's supplier relationships
- ✅ Add/remove suppliers
- ✅ Set supplier preferences and terms
- ✅ View supplier performance metrics

#### Advanced Reporting
- ✅ Generate detailed inventory reports
- ✅ Create usage analytics
- ✅ Export data for external analysis
- ✅ Schedule automated reports

### Data Access Scope
- Own organization's data only
- All warehouses, users, and machines within organization
- All transactions involving organization
- Supplier relationships for organization

## Super Admin Role

**Who**: Oraseas EE system administrators and key personnel
**Organization**: Oraseas EE only
**Primary Focus**: System-wide management and oversight

### Capabilities

#### All Admin Capabilities Plus:

#### Cross-Organization Access
- ✅ View and manage all organizations
- ✅ Access data from any organization
- ✅ Generate system-wide reports
- ✅ Monitor system health and performance

#### Organization Management
- ✅ Create new organizations
- ✅ Set organization types and relationships
- ✅ Manage organization hierarchy
- ✅ Deactivate organizations
- ✅ Transfer data between organizations

#### System User Management
- ✅ Create super admin users
- ✅ Manage users across all organizations
- ✅ Override organization-level restrictions
- ✅ View system-wide user activity
- ✅ Manage system security settings

#### Machine Registration
- ✅ Register new AutoBoss machines
- ✅ Assign machines to customer organizations
- ✅ Track machine sales and deployments
- ✅ Manage machine warranties and service

#### Business Workflow Management
- ✅ Configure system-wide business rules
- ✅ Manage transaction approval workflows
- ✅ Set system-wide inventory policies
- ✅ Configure automated processes

#### System Administration
- ✅ Manage system configuration
- ✅ Monitor system performance
- ✅ Access audit logs and security events
- ✅ Manage data backups and migrations
- ✅ Configure system integrations

### Data Access Scope
- All organizations and their data
- All warehouses, users, machines, and transactions
- System configuration and audit logs
- Cross-organization analytics and reporting

## Role Assignment Rules

### Business Rules
1. **Super Admin**: Only Oraseas EE employees can be super admins
2. **Organization Requirement**: Each organization must have at least one admin
3. **Role Inheritance**: Higher roles include all lower role capabilities
4. **Data Isolation**: Non-super admin users only see their organization's data

### Role Changes
- **User → Admin**: Can be done by existing admin or super admin
- **Admin → User**: Can be done by super admin or another admin (if not last admin)
- **Any → Super Admin**: Only existing super admin can assign
- **Role Removal**: Cannot remove last admin from organization

## Security Considerations

### Session Management
- **Session Duration**: 8 hours for all roles
- **Automatic Logout**: After session expiration or inactivity
- **Multi-Session**: Users can have multiple active sessions
- **Termination**: Sessions terminated on password change or deactivation

### Access Control
- **Organization Scoping**: Automatic filtering of data by organization
- **Permission Checking**: Every action validated against role permissions
- **Audit Logging**: All actions logged with user and timestamp
- **Failed Attempts**: Account lockout after 5 failed login attempts

### Data Protection
- **Encryption**: All sensitive data encrypted in transit and at rest
- **Backup Access**: Only super admins can access backup data
- **Export Controls**: Data export limited by role and organization
- **Retention**: Audit logs retained according to compliance requirements

## Best Practices

### For Users
- Keep profile information current
- Use strong passwords and change regularly
- Report suspicious activity immediately
- Follow organization's data handling policies

### For Admins
- Regularly review user access and roles
- Monitor inventory levels and set appropriate alerts
- Maintain accurate warehouse and supplier information
- Document important processes and procedures

### For Super Admins
- Regularly audit cross-organization access
- Monitor system performance and security
- Keep system configuration documented
- Maintain disaster recovery procedures

---

**Questions about your role?** Contact your organization administrator or refer to the role-specific guides in the main documentation menu.