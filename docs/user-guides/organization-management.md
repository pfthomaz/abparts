# Organization Management Guide

This guide is for administrators who need to manage their organization's settings, relationships, and overall configuration within ABParts.

## Understanding Organization Types

ABParts supports four distinct organization types, each with specific roles in the AutoBoss ecosystem:

### Oraseas EE (Single Instance)
- **Role**: App owner and primary distributor
- **Capabilities**: System-wide access, machine sales, parts distribution
- **Users**: Super admins only
- **Relationships**: Parent to suppliers, sells to customers

### BossAqua (Single Instance)
- **Role**: Manufacturer of AutoBoss machines and proprietary parts
- **Capabilities**: Parts manufacturing, inventory creation
- **Users**: Admins and users
- **Relationships**: Supplies parts to Oraseas EE

### Customer Organizations
- **Role**: AutoBoss machine owners who need parts
- **Capabilities**: Order parts, manage machines, track usage
- **Users**: Admins and users
- **Relationships**: Buy from Oraseas EE and suppliers

### Supplier Organizations
- **Role**: Third-party parts suppliers
- **Capabilities**: Supply parts to customers or Oraseas EE
- **Users**: Admins and users
- **Relationships**: Must have parent organization (Oraseas EE or Customer)

## Managing Organization Information

### Updating Basic Information

1. **Navigate to Organization Settings**
   - Go to **Settings** → **Organization**
   - Or click your organization name in the top navigation

2. **Editable Fields**
   - Organization name (must be unique)
   - Address and location information
   - Contact information (phone, email)
   - Description and notes

3. **Restricted Fields**
   - Organization type (set during creation)
   - Parent organization (managed by super admin)
   - Creation date and system IDs

### Organization Hierarchy Visualization

The system displays your organization's relationships:

```
Oraseas EE (Primary Distributor)
├── Supplier A (Parts Supplier)
├── Supplier B (Parts Supplier)
└── Customer Organizations
    ├── Customer 1
    │   └── Supplier C (Customer's Supplier)
    └── Customer 2
        └── Supplier D (Customer's Supplier)

BossAqua (Manufacturer)
└── Supplies to Oraseas EE
```

### Managing Supplier Relationships

#### For Customer Organizations

1. **Adding Suppliers**
   - Go to **Settings** → **Suppliers**
   - Click **Add Supplier**
   - Enter supplier organization details
   - Set relationship terms and preferences

2. **Supplier Configuration**
   - Default payment terms
   - Preferred contact methods
   - Parts categories they supply
   - Delivery preferences

3. **Supplier Performance Tracking**
   - Order fulfillment rates
   - Delivery times
   - Quality metrics
   - Cost comparisons

#### For Oraseas EE (Super Admin)

1. **Managing All Suppliers**
   - View all supplier relationships
   - Approve new supplier registrations
   - Monitor supplier performance across customers

2. **Supplier Onboarding**
   - Create supplier organizations
   - Assign parent relationships
   - Set up initial users and permissions

## Organization Dashboard and Analytics

### Key Metrics Display

Your organization dashboard shows:

#### Inventory Overview
- Total parts in all warehouses
- Low stock alerts
- Parts value summary
- Recent inventory movements

#### Activity Summary
- Recent orders and deliveries
- User activity levels
- Machine usage statistics
- Transaction volume

#### Performance Indicators
- Order fulfillment rates
- Inventory turnover
- Cost trends
- Usage patterns

### Customizing Dashboard Views

1. **Widget Configuration**
   - Add/remove dashboard widgets
   - Resize and reposition elements
   - Set refresh intervals
   - Configure alert thresholds

2. **Report Scheduling**
   - Set up automated reports
   - Configure email delivery
   - Choose report formats
   - Set frequency and recipients

## Organization Settings and Preferences

### System Preferences

1. **Default Settings**
   - Default warehouse for new inventory
   - Standard units of measure
   - Currency and number formats
   - Time zone settings

2. **Notification Settings**
   - Low stock alerts
   - Order status updates
   - User activity notifications
   - System maintenance alerts

3. **Security Settings**
   - Password policy requirements
   - Session timeout preferences
   - Two-factor authentication options
   - IP address restrictions

### Business Rules Configuration

1. **Inventory Rules**
   - Minimum stock levels
   - Reorder point calculations
   - Automatic reorder triggers
   - Stock adjustment approval limits

2. **Order Management Rules**
   - Order approval workflows
   - Spending limits by user role
   - Preferred supplier rankings
   - Emergency order procedures

3. **User Management Rules**
   - User invitation policies
   - Role assignment restrictions
   - Account deactivation procedures
   - Access review schedules

## Multi-Warehouse Management

### Warehouse Overview

1. **Viewing All Warehouses**
   - Go to **Warehouses** in main navigation
   - See list of all organization warehouses
   - View status, location, and capacity
   - Check inventory distribution

2. **Warehouse Performance**
   - Inventory levels by warehouse
   - Transaction volume
   - Space utilization
   - Cost per warehouse

### Creating New Warehouses

1. **Basic Setup**
   - Navigate to **Warehouses** → **Add New**
   - Enter warehouse name and location
   - Set capacity and operational details
   - Assign responsible users

2. **Configuration Options**
   - Physical address and contact info
   - Operating hours and schedules
   - Special handling requirements
   - Integration with external systems

### Managing Warehouse Operations

1. **Inventory Distribution**
   - View stock levels across warehouses
   - Transfer inventory between locations
   - Balance stock based on demand
   - Optimize storage efficiency

2. **Operational Controls**
   - Activate/deactivate warehouses
   - Set operational status
   - Manage access permissions
   - Configure alerts and monitoring

## Reporting and Analytics

### Standard Reports

1. **Inventory Reports**
   - Current stock levels by warehouse
   - Inventory valuation
   - Stock movement history
   - Low stock and reorder reports

2. **Activity Reports**
   - User activity summaries
   - Transaction histories
   - Order fulfillment metrics
   - Machine usage statistics

3. **Financial Reports**
   - Parts cost analysis
   - Spending by category
   - Supplier cost comparisons
   - Budget vs. actual reports

### Custom Report Builder

1. **Creating Custom Reports**
   - Select data sources and fields
   - Apply filters and grouping
   - Choose visualization types
   - Set formatting options

2. **Report Scheduling**
   - Set automated generation
   - Configure delivery methods
   - Manage recipient lists
   - Archive and retention settings

## Compliance and Audit

### Audit Trail Management

1. **Viewing Audit Logs**
   - Access **Settings** → **Audit Logs**
   - Filter by user, action, or date
   - Export logs for compliance
   - Monitor security events

2. **Compliance Reporting**
   - Generate compliance reports
   - Track regulatory requirements
   - Document control procedures
   - Maintain audit evidence

### Data Management

1. **Data Retention Policies**
   - Configure retention periods
   - Set archival procedures
   - Manage data deletion
   - Ensure compliance requirements

2. **Backup and Recovery**
   - Monitor backup status
   - Test recovery procedures
   - Document recovery plans
   - Coordinate with IT support

## Troubleshooting Common Issues

### Organization Setup Problems

**Issue**: Cannot update organization information
- **Solution**: Check admin permissions and field restrictions
- **Prevention**: Understand which fields are editable vs. system-controlled

**Issue**: Supplier relationships not working
- **Solution**: Verify parent organization assignments and permissions
- **Prevention**: Follow proper supplier onboarding procedures

### Performance Issues

**Issue**: Dashboard loading slowly
- **Solution**: Reduce widget complexity and data ranges
- **Prevention**: Optimize dashboard configuration and refresh intervals

**Issue**: Reports taking too long to generate
- **Solution**: Narrow date ranges and reduce data complexity
- **Prevention**: Use scheduled reports for large datasets

## Best Practices

### Organization Management
- Keep organization information current and accurate
- Regularly review and update supplier relationships
- Monitor dashboard metrics for operational insights
- Maintain proper documentation of procedures

### Security and Compliance
- Regularly review user access and permissions
- Monitor audit logs for unusual activity
- Keep security settings current with best practices
- Document all configuration changes

### Performance Optimization
- Optimize dashboard widgets for your needs
- Use scheduled reports for regular information
- Archive old data according to retention policies
- Monitor system performance and usage patterns

---

**Need Help?** Contact your super administrator or refer to the [System Administration Guide](admin-guides/system-setup.md) for advanced configuration options.