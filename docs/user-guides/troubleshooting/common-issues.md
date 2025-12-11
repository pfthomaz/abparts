# Common Issues and Solutions

This guide covers the most frequently encountered issues in ABParts and provides step-by-step solutions for users and administrators.

## Login and Access Issues

### Cannot Log In

#### Issue: "Invalid username or password" error

**Possible Causes:**
- Incorrect email address or password
- Account not yet activated
- Account has been deactivated
- Caps Lock is on

**Solutions:**
1. **Verify Credentials**
   - Double-check email address spelling
   - Ensure password is entered correctly
   - Check if Caps Lock is enabled
   - Try typing password in a text editor first

2. **Check Account Status**
   - Look for activation email in inbox/spam
   - Contact your organization administrator
   - Verify you were properly invited to the system

3. **Password Reset**
   - Click "Forgot Password" on login page
   - Check email for reset instructions
   - Follow reset link (valid for 24 hours)
   - Create new password meeting requirements

#### Issue: Account locked after failed login attempts

**Cause:** Too many failed login attempts (5 attempts locks account for 15 minutes)

**Solutions:**
1. **Wait for Automatic Unlock**
   - Account automatically unlocks after 15 minutes
   - Do not continue attempting to log in
   - Wait for the full timeout period

2. **Contact Administrator**
   - Organization admin can unlock immediately
   - Provide your email address and approximate lock time
   - Admin can verify account status and unlock

### Session and Timeout Issues

#### Issue: Frequently logged out of system

**Possible Causes:**
- Session timeout (8-hour maximum)
- Inactivity timeout (2 hours)
- Browser settings clearing cookies
- Multiple active sessions

**Solutions:**
1. **Check Session Settings**
   - Sessions expire after 8 hours maximum
   - Inactivity timeout after 2 hours
   - Save work frequently to avoid data loss

2. **Browser Configuration**
   - Enable cookies for ABParts domain
   - Don't use private/incognito browsing
   - Clear browser cache if experiencing issues
   - Update browser to latest version

3. **Multiple Sessions**
   - You can have multiple sessions active
   - Each browser/device creates separate session
   - Logout from unused sessions to improve performance

## Permission and Access Errors

### "Permission Denied" Messages

#### Issue: Cannot access certain features or data

**Possible Causes:**
- Insufficient role permissions
- Trying to access other organization's data
- Feature not available for your organization type
- Account role changed recently

**Solutions:**
1. **Verify Your Role**
   - Check your role in profile settings
   - Review [User Roles Overview](../user-roles-overview.md)
   - Understand your role's capabilities and limitations

2. **Check Data Scope**
   - You can only access your organization's data
   - Verify you're looking at correct organization
   - Super admins have cross-organization access

3. **Request Additional Access**
   - Contact your organization administrator
   - Explain business need for additional access
   - Provide justification for role change
   - Follow organization's access request procedures

#### Issue: Cannot see expected warehouses or inventory

**Cause:** Organization-scoped data access

**Solutions:**
1. **Verify Organization**
   - Confirm you're viewing your organization's data
   - Check organization name in top navigation
   - Ensure you're not expecting cross-organization access

2. **Check Warehouse Status**
   - Warehouses may be inactive or archived
   - Contact admin to verify warehouse configuration
   - Ensure warehouses are properly assigned to organization

## Inventory and Parts Issues

### Inventory Discrepancies

#### Issue: System inventory doesn't match physical count

**Possible Causes:**
- Unreported transactions
- Data entry errors
- Parts moved without system update
- Timing differences in updates

**Solutions:**
1. **Immediate Actions**
   - Stop all transactions for affected parts
   - Document the discrepancy with photos/notes
   - Notify warehouse supervisor or admin

2. **Investigation Steps**
   - Review recent transaction history
   - Check for pending or incomplete transactions
   - Verify all recent receipts and usage recorded
   - Look for transfer transactions

3. **Resolution Process**
   - Admin performs inventory adjustment
   - Document reason for adjustment
   - Implement controls to prevent recurrence
   - Update procedures if necessary

#### Issue: Cannot find parts in catalog

**Possible Causes:**
- Part not yet added to system
- Incorrect part number or description
- Part assigned to different organization
- Search filters too restrictive

**Solutions:**
1. **Search Techniques**
   - Try partial part numbers or descriptions
   - Remove search filters and browse categories
   - Search by manufacturer or part type
   - Use wildcard characters if supported

2. **Contact Administrator**
   - Request part addition to catalog
   - Provide complete part specifications
   - Include supplier information
   - Verify part compatibility with machines

### Order and Transaction Issues

#### Issue: Order stuck in "Pending" status

**Possible Causes:**
- Awaiting approval (high-value orders)
- Supplier not yet processed order
- System communication issues
- Missing required information

**Solutions:**
1. **Check Order Details**
   - Verify all required information provided
   - Check if order requires approval
   - Review order value against approval thresholds

2. **Contact Relevant Parties**
   - Contact approving administrator if approval needed
   - Reach out to supplier for external orders
   - Check with Oraseas EE for distribution orders

3. **System Issues**
   - Refresh browser and check status again
   - Log out and back in to refresh session
   - Contact system administrator if persistent

#### Issue: Cannot record parts receipt

**Possible Causes:**
- Order not in correct status for receipt
- Insufficient permissions
- Warehouse not properly configured
- System validation errors

**Solutions:**
1. **Verify Order Status**
   - Order must be in "Shipped" or "Delivered" status
   - Check with supplier on shipment status
   - Update order status if necessary

2. **Check Permissions**
   - Ensure you have receipt recording permissions
   - Verify warehouse access permissions
   - Contact admin if permissions insufficient

3. **Warehouse Configuration**
   - Verify warehouse is active and properly configured
   - Check warehouse capacity and restrictions
   - Ensure warehouse assigned to your organization

## System Performance Issues

### Slow Loading Times

#### Issue: Pages load slowly or time out

**Possible Causes:**
- Network connectivity issues
- High system load
- Large data sets being processed
- Browser performance issues

**Solutions:**
1. **Check Network Connection**
   - Test internet connection speed
   - Try accessing other websites
   - Switch to different network if available
   - Contact IT support for network issues

2. **Browser Optimization**
   - Clear browser cache and cookies
   - Close unnecessary browser tabs
   - Update browser to latest version
   - Try different browser

3. **Reduce Data Load**
   - Use date filters to limit data ranges
   - Apply filters before running reports
   - Break large operations into smaller chunks
   - Contact admin if performance persists

### Data Not Updating

#### Issue: Changes not reflected in system

**Possible Causes:**
- Browser cache showing old data
- Transaction not properly saved
- System synchronization delays
- Network interruption during save

**Solutions:**
1. **Refresh Data**
   - Refresh browser page (F5 or Ctrl+R)
   - Clear browser cache
   - Log out and back in
   - Try different browser

2. **Verify Transaction**
   - Check if transaction appears in history
   - Look for error messages or notifications
   - Verify all required fields completed
   - Re-enter transaction if necessary

3. **System Issues**
   - Wait a few minutes for system synchronization
   - Contact administrator if delays persist
   - Document issue with screenshots
   - Report to technical support if needed

## Mobile and Browser Issues

### Browser Compatibility

#### Issue: Features not working properly in browser

**Supported Browsers:**
- Chrome (recommended)
- Firefox
- Safari
- Edge

**Solutions:**
1. **Update Browser**
   - Use latest version of supported browser
   - Enable JavaScript and cookies
   - Disable browser extensions that might interfere

2. **Browser Settings**
   - Allow pop-ups for ABParts domain
   - Enable local storage
   - Clear cache and cookies
   - Reset browser settings if necessary

### Mobile Access Issues

#### Issue: Difficulty using system on mobile device

**Current Status:** ABParts is optimized for desktop use

**Solutions:**
1. **Desktop Access Recommended**
   - Use desktop or laptop computer when possible
   - Access through tablet in landscape mode
   - Use larger screen for complex operations

2. **Mobile Workarounds**
   - Use mobile browser in desktop mode
   - Zoom interface for better visibility
   - Focus on simple operations (viewing, basic updates)
   - Switch to desktop for complex tasks

## Getting Help

### When to Contact Support

#### Contact Organization Administrator For:
- Permission and access issues
- User account problems
- Organization-specific configuration
- Training and guidance needs

#### Contact Super Administrator For:
- Cross-organization issues
- System-wide problems
- Machine registration issues
- Technical system problems

#### Contact Technical Support For:
- System bugs and errors
- Performance issues
- Data corruption problems
- Integration failures

### How to Report Issues Effectively

#### Information to Provide:
1. **User Information**
   - Your name and email address
   - Organization name
   - User role in system

2. **Issue Details**
   - Exact error message (screenshot if possible)
   - Steps to reproduce the problem
   - When the issue first occurred
   - Frequency of occurrence

3. **System Information**
   - Browser type and version
   - Operating system
   - Network connection type
   - Any recent changes to setup

4. **Business Impact**
   - How the issue affects your work
   - Urgency level
   - Workarounds attempted
   - Other users affected

### Emergency Procedures

#### Critical Issues (System Down, Data Loss)
1. **Immediate Actions**
   - Document the issue with screenshots
   - Note exact time of occurrence
   - Stop related work to prevent further issues

2. **Emergency Contacts**
   - Contact super administrator immediately
   - Use phone/email outside of ABParts system
   - Escalate to technical support if needed

3. **Communication**
   - Notify affected team members
   - Document workarounds being used
   - Keep stakeholders informed of status

## Prevention Best Practices

### User Best Practices
- Save work frequently
- Log out properly when finished
- Keep browser updated
- Report issues promptly
- Follow established procedures

### Administrator Best Practices
- Regular user access reviews
- Monitor system performance
- Maintain current documentation
- Provide user training
- Implement preventive controls

### System Maintenance
- Regular backups
- Performance monitoring
- Security updates
- User feedback collection
- Continuous improvement

---

**Still Need Help?** If your issue isn't covered here, contact your organization administrator or refer to the [Contact Support](contact-support.md) guide for additional assistance options.