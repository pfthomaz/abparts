# Role-Based Access Control Training

This training guide helps users understand ABParts' role-based access control (RBAC) system, their permissions, and how to work effectively within their assigned role.

## Learning Objectives

By the end of this training, you will:
- Understand the three user roles and their capabilities
- Know what data and features you can access
- Recognize security boundaries and why they exist
- Apply best practices for your role
- Know how to request additional access when needed

## Understanding RBAC Fundamentals

### What is Role-Based Access Control?

RBAC is a security model that restricts system access based on a user's role within the organization. Instead of giving individual permissions to each user, permissions are assigned to roles, and users are assigned to roles.

#### Benefits of RBAC
- **Security**: Users only access what they need for their job
- **Simplicity**: Easier to manage permissions by role than by individual
- **Compliance**: Helps meet regulatory requirements
- **Efficiency**: Reduces administrative overhead

### ABParts RBAC Model

```
ABParts Role Hierarchy

Super Admin (Oraseas EE only)
├── Full system access
├── All organizations visible
├── System configuration
└── Cross-organization reporting

Admin (Per organization)
├── Organization management
├── User management within org
├── Warehouse and inventory control
└── Advanced reporting

User (Per organization)
├── Daily operations
├── Parts ordering and usage
├── Basic inventory viewing
└── Personal profile management
```

## Role-Specific Training

### User Role Training

#### Your Capabilities

**Parts and Inventory Operations:**
- ✅ View parts catalog and specifications
- ✅ Check inventory levels across your organization's warehouses
- ✅ Search and filter parts by various criteria
- ✅ View parts usage history and trends

**Ordering and Receiving:**
- ✅ Create part orders from approved suppliers
- ✅ Track order status and delivery information
- ✅ Record receipt of parts into warehouses
- ✅ Update order status when parts arrive

**Machine Operations:**
- ✅ Record part usage in machines
- ✅ View machine maintenance history
- ✅ Add maintenance notes and observations
- ✅ Track parts consumption by machine

**Personal Management:**
- ✅ Update your profile information
- ✅ Change your password
- ✅ Manage notification preferences
- ✅ View your activity history

#### What You Cannot Do

**Inventory Management:**
- ❌ Adjust inventory levels directly
- ❌ Create or modify warehouses
- ❌ Transfer inventory between warehouses
- ❌ Set minimum stock levels

**User Management:**
- ❌ Invite new users
- ❌ Change other users' roles or status
- ❌ Access other users' personal information
- ❌ View system audit logs

**System Configuration:**
- ❌ Modify organization settings
- ❌ Manage supplier relationships
- ❌ Configure system-wide settings
- ❌ Access other organizations' data

#### Daily Workflow Example

**Morning Routine:**
1. Check dashboard for notifications and alerts
2. Review any pending orders or deliveries
3. Check inventory levels for planned maintenance
4. Plan parts usage for the day

**During Operations:**
1. Record parts usage as maintenance is performed
2. Update order status when deliveries arrive
3. Create new orders for needed parts
4. Document any issues or observations

**End of Day:**
1. Complete any pending transaction entries
2. Review daily activity summary
3. Plan for next day's requirements
4. Update any maintenance records

### Admin Role Training

#### Your Additional Capabilities

**Organization Management:**
- ✅ Update organization information and settings
- ✅ Manage organization preferences and policies
- ✅ View organization-wide analytics and reports
- ✅ Configure business rules and workflows

**User Management:**
- ✅ Invite new users to your organization
- ✅ Assign and change user roles (User/Admin)
- ✅ Activate and deactivate user accounts
- ✅ View user activity and audit logs
- ✅ Reset user passwords and unlock accounts

**Warehouse and Inventory Management:**
- ✅ Create and configure warehouses
- ✅ Adjust inventory levels with proper documentation
- ✅ Transfer inventory between warehouses
- ✅ Set minimum stock levels and reorder points
- ✅ Perform inventory reconciliation

**Advanced Operations:**
- ✅ Register and manage machines
- ✅ Manage supplier relationships
- ✅ Approve high-value orders
- ✅ Generate advanced reports and analytics
- ✅ Export data for external analysis

#### Administrative Responsibilities

**User Lifecycle Management:**
1. **Onboarding**: Invite new users with appropriate roles
2. **Training**: Ensure users understand their capabilities
3. **Monitoring**: Review user activity and performance
4. **Maintenance**: Regular access reviews and updates
5. **Offboarding**: Properly deactivate departing users

**Inventory Oversight:**
1. **Stock Management**: Monitor inventory levels and trends
2. **Reconciliation**: Regular physical counts and adjustments
3. **Optimization**: Analyze usage patterns and optimize stock
4. **Reporting**: Generate inventory reports for management

**Security Management:**
1. **Access Control**: Ensure appropriate user permissions
2. **Monitoring**: Watch for unusual activity or security issues
3. **Compliance**: Maintain audit trails and documentation
4. **Incident Response**: Handle security incidents promptly

#### Admin Best Practices

**User Management:**
- Assign minimum necessary permissions (principle of least privilege)
- Regularly review user access and activity
- Promptly remove access for departing employees
- Document role assignments and changes

**Inventory Control:**
- Implement regular cycle counting procedures
- Require documentation for all inventory adjustments
- Monitor for unusual inventory movements
- Maintain accurate warehouse and location data

### Super Admin Role Training

#### System-Wide Responsibilities

**Cross-Organization Management:**
- ✅ View and manage all organizations
- ✅ Create new organizations and set types
- ✅ Manage organization hierarchy and relationships
- ✅ Transfer data between organizations

**System Administration:**
- ✅ Create super admin users
- ✅ Configure system-wide settings and policies
- ✅ Monitor system performance and health
- ✅ Manage system integrations and backups

**Business Process Management:**
- ✅ Register AutoBoss machines and assign to customers
- ✅ Manage machine sales and ownership transfers
- ✅ Configure business workflows and approval processes
- ✅ Set system-wide inventory and ordering policies

#### Super Admin Responsibilities

**System Governance:**
1. **Policy Setting**: Establish system-wide policies and procedures
2. **Compliance**: Ensure regulatory compliance across all organizations
3. **Security**: Maintain system security and access controls
4. **Performance**: Monitor and optimize system performance

**Business Operations:**
1. **Machine Management**: Track machine sales and deployments
2. **Distribution**: Manage parts flow from manufacturers to customers
3. **Relationships**: Oversee supplier and customer relationships
4. **Analytics**: Generate business intelligence and insights

## Data Access and Security Boundaries

### Organization-Scoped Access

#### What This Means
- **Your Data Only**: You can only see data from your own organization
- **Automatic Filtering**: System automatically limits what you can access
- **No Cross-Organization**: Cannot see other organizations' information
- **Exception**: Super admins can access all organizations

#### Examples of Organization Scoping

**Inventory Views:**
- You see only your organization's warehouses
- Inventory levels shown for your warehouses only
- Cannot see other organizations' stock levels

**User Management:**
- Admins see only users in their organization
- Cannot invite users to other organizations
- User lists automatically filtered by organization

**Reporting:**
- Reports include only your organization's data
- Analytics based on your organization's activity
- Cannot generate cross-organization reports (except super admins)

### Permission Enforcement

#### How Permissions Work

1. **Login Authentication**: System verifies your identity
2. **Role Assignment**: System determines your role and organization
3. **Permission Checking**: Every action checked against your permissions
4. **Data Filtering**: Results automatically filtered to your scope
5. **Audit Logging**: All actions logged for security and compliance

#### Permission Denied Scenarios

**Common Permission Denied Messages:**
- "You don't have permission to access this resource"
- "This action requires admin privileges"
- "You can only access your organization's data"
- "This feature is not available for your role"

**What to Do When Denied:**
1. **Verify Need**: Confirm you actually need this access for your job
2. **Check Role**: Ensure you understand your role's capabilities
3. **Request Access**: Contact your admin to request additional permissions
4. **Document Justification**: Explain why you need the access

## Security Best Practices by Role

### For All Users

#### Password Security
- **Strong Passwords**: Use complex, unique passwords
- **Regular Changes**: Change passwords regularly
- **No Sharing**: Never share your login credentials
- **Secure Storage**: Use password managers if available

#### Session Management
- **Logout**: Always log out when finished
- **Screen Lock**: Lock your screen when away
- **Public Computers**: Never use public computers for ABParts
- **Multiple Sessions**: Be aware of active sessions

#### Data Protection
- **Screen Privacy**: Protect screen from unauthorized viewing
- **Data Handling**: Follow organization's data handling policies
- **Reporting**: Report suspicious activity immediately
- **Compliance**: Follow all security policies and procedures

### For Admins

#### User Management Security
- **Access Reviews**: Regularly review user access and permissions
- **Prompt Deactivation**: Immediately deactivate departing users
- **Role Appropriateness**: Ensure roles match job responsibilities
- **Documentation**: Document all user management actions

#### Inventory Security
- **Adjustment Documentation**: Require proper documentation for adjustments
- **Approval Workflows**: Implement approval for significant changes
- **Audit Trails**: Maintain complete audit trails
- **Physical Security**: Coordinate with physical warehouse security

### For Super Admins

#### System Security
- **Access Monitoring**: Monitor system access and unusual activity
- **Security Updates**: Keep system security measures current
- **Backup Verification**: Regularly verify backup integrity
- **Incident Response**: Have incident response procedures ready

#### Cross-Organization Oversight
- **Data Segregation**: Ensure proper data segregation between organizations
- **Policy Enforcement**: Enforce security policies consistently
- **Compliance Monitoring**: Monitor compliance across all organizations
- **Risk Assessment**: Regular security risk assessments

## Training Exercises

### Exercise 1: Role Identification

**Scenario**: You need to adjust inventory levels because of a counting error.

**Questions**:
1. Can you do this with a User role?
2. What role is required?
3. What documentation would be needed?
4. Who would you contact if you don't have the right permissions?

**Answers**:
1. No, Users cannot adjust inventory levels
2. Admin role is required for inventory adjustments
3. Documentation of the counting error and correction needed
4. Contact your organization administrator

### Exercise 2: Data Access Boundaries

**Scenario**: You want to compare your inventory levels with another customer organization.

**Questions**:
1. Can you access another organization's inventory data?
2. Why or why not?
3. Who could access this information?
4. How might you get this comparison done?

**Answers**:
1. No, you cannot access other organizations' data
2. Organization-scoped access prevents cross-organization data access
3. Only super admins can access all organizations' data
4. Request the comparison through your admin who can contact super admin

### Exercise 3: Permission Escalation

**Scenario**: You need to register a new machine but get a permission denied error.

**Questions**:
1. What role is required for machine registration?
2. How would you request this capability?
3. What information would you need to provide?
4. Are there alternatives to getting this done?

**Answers**:
1. Admin role (or super admin approval for initial registration)
2. Contact your organization administrator to request admin role or assistance
3. Justification for why you need machine registration capability
4. Ask an existing admin to register the machine for you

## Frequently Asked Questions

### General RBAC Questions

**Q: Why can't I see all the data in the system?**
A: ABParts uses organization-scoped access to protect each organization's data privacy and security. You can only see data from your own organization.

**Q: How do I know what I can and cannot do?**
A: Check the [User Roles Overview](../user-roles-overview.md) guide for your specific role, or try the action - the system will tell you if you don't have permission.

**Q: Can my role be changed?**
A: Yes, organization admins can change roles within the organization. Contact your admin if you need different permissions for your job.

### Permission Issues

**Q: I get "permission denied" errors. What should I do?**
A: First, verify you actually need this access for your job. Then contact your organization administrator to discuss your access needs.

**Q: Why do some features disappear from my interface?**
A: The interface adapts to your role, hiding features you cannot use. This reduces confusion and focuses on your available capabilities.

**Q: Can I temporarily get higher permissions?**
A: No, there are no temporary permission elevations. If you need different access, your role must be changed by an administrator.

### Security Concerns

**Q: What if I suspect someone has inappropriate access?**
A: Report this immediately to your organization administrator or super administrator. Security issues should be addressed promptly.

**Q: How do I know if my account has been compromised?**
A: Watch for unusual activity in your account, unexpected password reset emails, or login notifications from unfamiliar locations.

**Q: What happens if I violate security policies?**
A: Security violations can result in account suspension, role changes, or other disciplinary actions depending on the severity.

## Conclusion and Next Steps

### Key Takeaways

1. **Role Understanding**: Know your role's capabilities and limitations
2. **Security Awareness**: Understand why access controls exist
3. **Proper Procedures**: Follow established procedures for requesting access
4. **Best Practices**: Apply security best practices in daily work
5. **Continuous Learning**: Stay updated on system changes and security practices

### Continuing Education

- **Regular Reviews**: Periodically review your role capabilities
- **System Updates**: Stay informed about system changes
- **Security Training**: Participate in ongoing security training
- **Best Practices**: Share and learn best practices with colleagues

### Getting Help

- **Documentation**: Refer to role-specific guides and documentation
- **Administrators**: Contact your organization administrator for access issues
- **Training**: Request additional training if needed
- **Support**: Use established support channels for technical issues

---

**Training Complete?** Test your understanding with the [RBAC Assessment Quiz](rbac-assessment.md) or proceed to [Organization Types Training](organization-types-training.md) to learn about the business model.