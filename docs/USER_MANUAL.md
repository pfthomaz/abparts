# ABParts User Manual

**Version 1.0 | AutoBoss Parts Inventory & Order Management System**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard](#dashboard)
3. [Organizations](#organizations)
4. [Users](#users)
5. [Parts Catalog](#parts-catalog)
6. [Warehouses](#warehouses)
7. [Inventory Management](#inventory-management)
8. [Orders](#orders)
9. [Machines](#machines)
10. [Reports](#reports)

---

## Getting Started

### Logging In

1. Navigate to the ABParts application URL
2. Enter your username and password
3. Click "Login"

**[SCREENSHOT: Login screen]**

### User Roles

ABParts has three user roles with different permissions:

- **Super Admin** (Oraseas EE): Full system access, manages all organizations
- **Admin**: Manages their organization's data, users, and operations
- **User**: Can view data, place orders, and record machine hours

---

## Dashboard

The Dashboard provides an at-a-glance view of your organization's key metrics:

**[SCREENSHOT: Dashboard overview]**

### Key Metrics Displayed

- **Inventory Status**: Current stock levels and low stock alerts
- **Recent Orders**: Latest customer and supplier orders
- **Machine Status**: Active machines and maintenance alerts
- **Quick Actions**: Shortcuts to common tasks

### Navigation

Use the sidebar menu to access different sections:
- Dashboard
- Organizations (Super Admin only)
- Users
- Parts
- Warehouses
- Inventory
- Orders
- Machines
- Stock Adjustments
- Reports

---

## Organizations

*Available to: Super Admin*

### Viewing Organizations

**[SCREENSHOT: Organizations list]**

Organizations represent the different entities in the system:
- **Oraseas EE**: The main distributor
- **BossAqua**: The manufacturer
- **Customer Organizations**: Companies that purchase parts

### Organization Details

Each organization has:
- Name and type
- Contact information
- Logo (optional)
- Associated users and warehouses

### Adding a New Organization

1. Click "Add Organization"
2. Fill in organization details:
   - Name
   - Organization Type (Customer, Supplier, etc.)
   - Contact information
3. Upload logo (optional)
4. Click "Create"

**[SCREENSHOT: Add Organization form]**

---

## Users

*Available to: Admin and Super Admin*

### User Management

**[SCREENSHOT: Users list]**

### Adding a New User

1. Click "Add User"
2. Enter user details:
   - Name
   - Username
   - Email
   - Password
   - Role (User or Admin)
   - Organization
3. Click "Create User"

**[SCREENSHOT: Add User form]**

### Editing Users

1. Click the "Edit" button next to a user
2. Update the information
3. Click "Update User"

### User Roles Explained

- **User**: Can view parts, place orders, record machine hours
- **Admin**: Can manage users, warehouses, inventory, and orders for their organization
- **Super Admin**: Full system access (Oraseas EE only)

---

## Parts Catalog

*Available to: All users*

### Viewing Parts

**[SCREENSHOT: Parts catalog]**

The parts catalog shows all available AutoBoss parts with:
- Part number and name
- Description
- Category
- Unit of measure (pieces, liters, kg)
- Current stock levels

### Searching for Parts

Use the search bar to find parts by:
- Part number
- Part name
- Description
- Category

**[SCREENSHOT: Parts search]**

### Part Details

Click on a part to view:
- Full specifications
- Stock levels across warehouses
- Recent transactions
- Usage history

**[SCREENSHOT: Part details view]**

---

## Warehouses

*Available to: Admin and Super Admin*

### Warehouse Management

**[SCREENSHOT: Warehouses list]**

Warehouses are storage locations for parts inventory.

### Adding a Warehouse

1. Click "Add Warehouse"
2. Enter warehouse details:
   - Name
   - Location
   - Organization
3. Click "Create Warehouse"

**[SCREENSHOT: Add Warehouse form]**

### Warehouse Inventory View

Click on a warehouse to see:
- All parts stored in that warehouse
- Current stock levels
- Low stock alerts
- Recent transactions

**[SCREENSHOT: Warehouse inventory view]**

---

## Inventory Management

*Available to: Admin and Super Admin*

### Viewing Inventory

**[SCREENSHOT: Inventory overview]**

The inventory view shows:
- Current stock levels for all parts
- Warehouse locations
- Low stock warnings
- Recommended reorder quantities

### Stock Adjustments

Use stock adjustments to correct inventory levels or record stock changes.

**[SCREENSHOT: Stock Adjustments page]**

#### Creating a Stock Adjustment

1. Navigate to "Stock Adjustments"
2. Click "Create Stock Adjustment"
3. Select:
   - Warehouse
   - Part
   - Adjustment type (Addition, Removal, Correction, Damage, etc.)
   - Quantity
   - Reason
4. Click "Create Adjustment"

**[SCREENSHOT: Create Stock Adjustment form]**

### Inventory Transfers

Transfer parts between warehouses:

1. Go to Warehouses
2. Click "Transfer Inventory"
3. Select:
   - From warehouse
   - To warehouse
   - Part and quantity
4. Add notes (optional)
5. Click "Transfer"

**[SCREENSHOT: Inventory Transfer form]**

---

## Orders

*Available to: All users (view/create), Admin (manage)*

### Order Types

ABParts handles two types of orders:

1. **Customer Orders**: Orders placed by customers to Oraseas EE
2. **Supplier Orders**: Orders placed by Oraseas EE to suppliers

**[SCREENSHOT: Orders page with both tabs]**

### Placing a Customer Order

1. Navigate to "Orders"
2. Click "Add Customer Order"
3. Fill in order details:
   - Customer organization (auto-filled for non-admin users)
   - Order date
   - Expected delivery date
4. Add order items:
   - Select part
   - Enter quantity
   - Enter unit price (optional)
   - Click "Add Item"
5. Add notes (optional)
6. Click "Create Order"

**[SCREENSHOT: Create Customer Order form]**

### Placing a Supplier Order

*Admin only*

1. Navigate to "Orders" → "Supplier Orders" tab
2. Click "Add Supplier Order"
3. Fill in order details:
   - Supplier name
   - Order date
   - Expected delivery date
4. Add order items
5. Click "Create Order"

**[SCREENSHOT: Create Supplier Order form]**

### Order Status Workflow

Orders progress through these statuses:

**Customer Orders:**
- **Pending**: Order placed, awaiting processing
- **Shipped**: Order shipped by Oraseas EE
- **Delivered**: Order received by customer
- **Cancelled**: Order cancelled

**Supplier Orders:**
- **Requested**: Order placed with supplier
- **Confirmed**: Supplier confirmed the order
- **Shipped**: Supplier shipped the order
- **Received**: Order received by Oraseas EE
- **Cancelled**: Order cancelled

### Managing Orders (Admin)

**[SCREENSHOT: Order list with Edit/Delete buttons]**

#### Editing an Order

1. Click "Edit" next to an order (only Pending orders can be edited)
2. Modify order details or items
3. Click "Update Order"

#### Deleting an Order

1. Click "Delete" next to an order (only Pending/Requested orders can be deleted)
2. Confirm deletion
3. Order is removed from the system

### Order Calendar View

View orders on a calendar to track delivery dates:

1. Click "Calendar View" on the Orders page
2. Orders are displayed by expected delivery date
3. Click on an order to view details

**[SCREENSHOT: Order Calendar View]**

### Shipping Orders (Oraseas EE Admin)

1. Find the order in "Pending" status
2. Click "Ship Order"
3. Enter:
   - Shipped date
   - Tracking number (optional)
   - Notes
4. Click "Ship"

**[SCREENSHOT: Ship Order modal]**

### Confirming Receipt (Customer Admin)

1. Find the order in "Shipped" status
2. Click "Confirm Receipt"
3. Enter:
   - Actual delivery date
   - Receiving warehouse
   - Notes
4. Click "Confirm Receipt"

The system automatically updates inventory in the selected warehouse.

**[SCREENSHOT: Confirm Receipt modal]**

---

## Machines

*Available to: All users*

### Machine Management

**[SCREENSHOT: Machines list]**

Track AutoBoss machines deployed at customer locations.

### Registering a Machine

1. Navigate to "Machines"
2. Click "Add Machine"
3. Enter machine details:
   - Serial number
   - Model
   - Installation date
   - Location
   - Organization
4. Click "Register Machine"

**[SCREENSHOT: Add Machine form]**

### Recording Machine Hours

Users can record operating hours for machines:

**[SCREENSHOT: Machine hours recording]**

#### Quick Hour Recording

1. Find the machine in the list
2. Click the "Record Hours" button
3. Enter current hour meter reading
4. Click "Save"

#### Detailed Hour Recording

1. Click on a machine to view details
2. Click "Record Hours"
3. Enter:
   - Current hour meter reading
   - Date
   - Notes (optional)
4. Click "Record"

### Machine Hour History

View the complete history of hour recordings for each machine:

**[SCREENSHOT: Machine hour history]**

### Maintenance Reminders

The system shows maintenance reminders based on:
- Hours since last maintenance
- Time since last maintenance
- Recommended maintenance intervals

**[SCREENSHOT: Maintenance reminder notification]**

---

## Reports

*Available to: Admin and Super Admin*

### Available Reports

**[SCREENSHOT: Reports page]**

#### Inventory Reports

- Current stock levels by warehouse
- Low stock alerts
- Stock movement history
- Inventory valuation

#### Order Reports

- Order history by date range
- Order status summary
- Customer order patterns
- Supplier performance

#### Machine Reports

- Machine utilization
- Maintenance history
- Hour meter readings
- Machine performance metrics

### Generating a Report

1. Navigate to "Reports"
2. Select report type
3. Choose filters:
   - Date range
   - Organization
   - Warehouse
   - Part category
4. Click "Generate Report"
5. Export to PDF or Excel (if available)

**[SCREENSHOT: Report generation interface]**

---

## Tips & Best Practices

### For All Users

- **Keep information current**: Update machine hours regularly
- **Use search**: Use the search function to quickly find parts
- **Check notifications**: Review alerts for low stock and maintenance reminders

### For Admins

- **Review orders daily**: Process pending orders promptly
- **Monitor inventory**: Check low stock alerts and reorder as needed
- **Maintain user accounts**: Keep user information up to date
- **Regular stock checks**: Perform periodic physical inventory counts and adjust as needed

### For Super Admins

- **User management**: Regularly review user access and permissions
- **System monitoring**: Check system health and performance
- **Data integrity**: Ensure organizations and warehouses are properly configured

---

## Troubleshooting

### Common Issues

**Can't log in**
- Verify username and password
- Check with your administrator if account is active
- Clear browser cache and try again

**Can't see certain features**
- Check your user role - some features are role-restricted
- Contact your administrator for permission changes

**Order not updating inventory**
- Ensure order status is "Delivered" or "Received"
- Verify receiving warehouse is selected
- Check with administrator if issue persists

**Parts not showing in search**
- Check spelling and part number
- Try searching by category
- Verify part exists in the system

---

## Support

For technical support or questions:

- **Email**: support@oraseas.com
- **Phone**: [Contact Number]
- **System Administrator**: [Admin Name/Contact]

---

## Appendix

### Keyboard Shortcuts

- `Ctrl/Cmd + K`: Quick search
- `Esc`: Close modal dialogs
- `Tab`: Navigate between form fields

### Part Categories

- Filters
- Chemicals
- Consumables
- Spare Parts
- Accessories

### Unit of Measure

- **pieces**: Countable items (filters, parts)
- **liters**: Liquids (chemicals, cleaning solutions)
- **kg**: Weight-based items (powder, granules)

---

**Document Version**: 1.0  
**Last Updated**: December 2025  
**For**: ABParts Inventory Management System

