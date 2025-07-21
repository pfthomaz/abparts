# Part Ordering Workflow

This guide covers the complete part ordering process in ABParts, from initial request through receipt and inventory update.

## Overview

The part ordering workflow in ABParts supports the business model where:
- **Customers** order parts from Oraseas EE (primary distributor) or their own suppliers
- **Oraseas EE** manages distribution and can order from BossAqua or suppliers
- **All transactions** are tracked with complete audit trails
- **Inventory updates** happen automatically when parts are received

## Workflow Participants

### Customer Organizations
- **Users**: Can create part requests and receive parts
- **Admins**: Can approve orders, manage suppliers, and handle complex orders

### Oraseas EE (Primary Distributor)
- **Super Admins**: Can fulfill customer orders and manage system-wide inventory

### Suppliers
- **External Process**: Suppliers fulfill orders through external systems
- **System Integration**: Order status updates tracked in ABParts

## Complete Ordering Process

### Phase 1: Order Creation

#### Step 1: Identify Parts Needed

1. **Check Current Inventory**
   - Navigate to **Inventory** → **Current Stock**
   - Filter by warehouse and part type
   - Identify low stock items
   - Check minimum stock recommendations

2. **Review Machine Requirements**
   - Go to **Machines** → Select machine
   - Review maintenance schedule
   - Check parts usage history
   - Identify upcoming maintenance needs

3. **Consult Parts Catalog**
   - Browse **Parts** → **Catalog**
   - Search by part number or description
   - Verify part specifications
   - Check proprietary vs. general parts

#### Step 2: Create Order Request

1. **Start New Order**
   - Navigate to **Orders** → **Create New Order**
   - Select order type: "Parts Request"

2. **Order Header Information**
   - **Supplier Selection**: Choose from approved suppliers
     - Oraseas EE (primary distributor)
     - Organization's approved suppliers
   - **Delivery Warehouse**: Select destination warehouse
   - **Priority Level**: Normal, Urgent, Emergency
   - **Expected Delivery Date**: When parts are needed

3. **Add Parts to Order**
   - **Search Parts**: Use catalog search or browse
   - **Select Quantities**: Enter required amounts
     - Whole numbers for consumables
     - Decimal quantities for bulk materials
   - **Verify Specifications**: Confirm part details
   - **Add Notes**: Special requirements or instructions

4. **Order Review and Submission**
   - Review all order details
   - Verify total cost (if available)
   - Add order notes and special instructions
   - Submit order for processing

### Phase 2: Order Processing

#### Step 3: Order Approval (If Required)

1. **Automatic Approval Criteria**
   - Orders under approval threshold
   - Standard parts from approved suppliers
   - Regular users within spending limits

2. **Manual Approval Required**
   - High-value orders above threshold
   - New or non-standard parts
   - Emergency orders outside normal process
   - Orders from new suppliers

3. **Approval Process**
   - Admin receives approval notification
   - Reviews order details and justification
   - Approves, rejects, or requests modifications
   - System notifies requester of decision

#### Step 4: Supplier Communication

1. **For Oraseas EE Orders**
   - Order automatically routed to Oraseas EE
   - Super admin reviews and processes
   - Inventory allocation from Oraseas EE warehouses
   - Shipping arrangement and tracking

2. **For External Supplier Orders**
   - Order details exported/communicated to supplier
   - Purchase order generated (if integrated)
   - Supplier confirmation and delivery schedule
   - Tracking information provided

### Phase 3: Order Fulfillment

#### Step 5: Order Status Tracking

1. **Order Status Updates**
   ```
   Order Status Flow:
   Requested → Approved → Processing → Shipped → Delivered → Received
   ```

2. **Status Notifications**
   - Email notifications for status changes
   - Dashboard alerts for urgent orders
   - Mobile notifications (if available)
   - Escalation for overdue orders

3. **Tracking Information**
   - Estimated delivery dates
   - Shipping carrier and tracking numbers
   - Delivery confirmation requirements
   - Contact information for issues

#### Step 6: Parts Receipt

1. **Delivery Notification**
   - System notification of expected delivery
   - Preparation of receiving area
   - Assignment of receiving personnel
   - Receiving documentation ready

2. **Physical Receipt Process**
   - **Verify Delivery**: Check against order details
   - **Inspect Parts**: Quality and condition check
   - **Count Quantities**: Verify amounts received
   - **Document Issues**: Note any discrepancies

3. **System Receipt Recording**
   - Navigate to **Orders** → Select order
   - Click **Record Receipt**
   - Enter actual quantities received
   - Note any discrepancies or issues
   - Update order status to "Received"

### Phase 4: Inventory Update

#### Step 7: Automatic Inventory Processing

1. **Inventory Increase**
   - System automatically increases warehouse inventory
   - Quantities added based on receipt recording
   - Unit of measure consistency verified
   - Inventory value updated (if cost tracking enabled)

2. **Transaction Recording**
   - Complete transaction record created
   - Links order, supplier, warehouse, and parts
   - Audit trail with user, date, and details
   - Integration with financial systems (if applicable)

#### Step 8: Order Completion

1. **Final Order Processing**
   - Order status updated to "Complete"
   - Final cost reconciliation (if applicable)
   - Supplier performance metrics updated
   - Order archived for historical reference

2. **Post-Receipt Activities**
   - Parts put away in designated locations
   - Inventory location records updated
   - Quality control processes (if required)
   - Documentation filed and archived

## Special Order Types

### Emergency Orders

#### Characteristics
- **Urgent Need**: Critical machine downtime
- **Expedited Processing**: Skip normal approval delays
- **Premium Costs**: May incur rush charges
- **Special Handling**: Direct delivery, after-hours receipt

#### Process Modifications
1. **Immediate Approval**: Auto-approval for emergency orders
2. **Direct Communication**: Phone/email to supplier
3. **Expedited Shipping**: Express delivery options
4. **After-Hours Receipt**: Special receiving procedures

### Bulk Material Orders

#### Special Considerations
- **Quantity Precision**: Decimal quantities supported
- **Storage Requirements**: Tank capacity, handling equipment
- **Delivery Methods**: Bulk delivery, pumping, containers
- **Measurement Verification**: Accurate quantity confirmation

#### Process Adaptations
1. **Storage Verification**: Confirm adequate tank/container space
2. **Delivery Coordination**: Schedule bulk delivery logistics
3. **Measurement Recording**: Precise quantity documentation
4. **Quality Testing**: Sample testing if required

### Proprietary Parts Orders

#### BossAqua Parts Process
- **Supplier**: Must order through Oraseas EE
- **Availability**: Limited to BossAqua production schedule
- **Lead Times**: Longer delivery times typical
- **Pricing**: Fixed pricing from manufacturer

#### Special Handling
1. **Supplier Restriction**: Only Oraseas EE can supply
2. **Lead Time Planning**: Extended delivery schedules
3. **Quality Assurance**: Factory quality standards
4. **Warranty Tracking**: Manufacturer warranty coverage

## Order Management Tools

### Order Dashboard

#### Key Metrics Display
- **Open Orders**: Current orders in process
- **Overdue Orders**: Orders past expected delivery
- **Recent Receipts**: Recently completed orders
- **Spending Summary**: Order values and budgets

#### Quick Actions
- **Create New Order**: Fast order creation
- **Check Order Status**: Quick status lookup
- **Receive Parts**: Rapid receipt processing
- **Contact Supplier**: Direct communication links

### Reporting and Analytics

#### Standard Reports
1. **Order History**: Complete order records
2. **Supplier Performance**: Delivery times, quality metrics
3. **Spending Analysis**: Costs by category, supplier
4. **Lead Time Analysis**: Delivery performance trends

#### Custom Analytics
1. **Demand Forecasting**: Predict future part needs
2. **Supplier Comparison**: Evaluate supplier options
3. **Cost Optimization**: Identify savings opportunities
4. **Process Efficiency**: Workflow performance metrics

## Troubleshooting Common Issues

### Order Creation Problems

**Issue**: Cannot find required parts in catalog
- **Solution**: Contact admin to add parts or verify part numbers
- **Prevention**: Regular catalog updates and part standardization

**Issue**: Supplier not available for selection
- **Solution**: Verify supplier is approved and active
- **Prevention**: Maintain current supplier relationships

### Order Processing Delays

**Issue**: Order stuck in approval process
- **Solution**: Contact approving admin, provide justification
- **Prevention**: Follow approval guidelines, plan ahead

**Issue**: Supplier not responding to order
- **Solution**: Contact supplier directly, escalate to admin
- **Prevention**: Maintain good supplier relationships

### Receipt and Inventory Issues

**Issue**: Received quantities don't match order
- **Solution**: Document discrepancy, contact supplier
- **Prevention**: Clear order specifications, quality suppliers

**Issue**: Parts not updating in inventory
- **Solution**: Verify receipt recording, check system status
- **Prevention**: Proper receipt procedures, system training

## Best Practices

### Order Planning
- **Forecast Needs**: Plan orders based on usage patterns
- **Batch Orders**: Combine multiple needs into single orders
- **Lead Time Management**: Order with adequate lead time
- **Emergency Reserves**: Maintain safety stock for critical parts

### Supplier Management
- **Relationship Building**: Maintain good supplier relationships
- **Performance Monitoring**: Track supplier delivery and quality
- **Backup Suppliers**: Have alternative suppliers identified
- **Communication**: Clear, timely communication with suppliers

### Process Efficiency
- **Standardization**: Use consistent ordering procedures
- **Documentation**: Maintain complete order records
- **Training**: Ensure staff understand ordering process
- **Continuous Improvement**: Regular process review and optimization

---

**Need Help?** Contact your organization administrator or refer to the [User Management Guide](../user-management.md) for role-specific capabilities.