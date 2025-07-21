# ABParts API Documentation

**Version:** 2.0.0  
**Last Updated:** January 2025  
**Base URL:** `http://localhost:8000` (Development)  
**Production URL:** `https://api.yourdomain.com`  

---

## 📋 **API Overview**

The ABParts API is a comprehensive RESTful API built with FastAPI, providing complete inventory and order management capabilities for the AutoBoss parts distribution ecosystem. The API has been fully aligned with the business model and features automatic OpenAPI documentation, JWT authentication, and role-based access control.

### **Business Model Integration**
The API now properly represents the AutoBoss parts ecosystem:
- **Oraseas EE**: Primary distributor and app owner (singleton organization)
- **BossAqua**: Manufacturer of AutoBoss machines and proprietary parts (singleton organization)
- **Customers**: Organizations that purchase AutoBoss machines and need parts (max 100)
- **Suppliers**: Third-party suppliers serving customers or Oraseas EE

### **Key Features**
- **RESTful Design:** Standard HTTP methods and status codes
- **JWT Authentication:** Secure token-based authentication with 8-hour expiration
- **Role-Based Access:** Three-tier permission system (user, admin, super_admin)
- **Organization Scoping:** Data access limited to user's organization (except super_admin)
- **Warehouse-Based Inventory:** Multi-warehouse support with real-time tracking
- **Transaction Audit Trail:** Complete tracking of all parts movements
- **Business Rule Enforcement:** Automatic validation of business constraints
- **Comprehensive Validation:** Pydantic schema validation
- **Auto-Generated Docs:** OpenAPI/Swagger documentation at `/docs`

### **Scale Requirements**
The API is designed to efficiently handle:
- Maximum 100 customer organizations
- Maximum 200 total users across all organizations
- Maximum 200 different parts in catalog
- Maximum 150 AutoBoss machines deployed
- Maximum 150 warehouses across all organizations
- Maximum 7,500 transactions per year (50 per machine)

---

## 🔐 **Authentication**

### **Authentication Flow**
1. **Login:** POST `/token` with username/password
2. **Receive JWT Token:** Use token in Authorization header
3. **Access Protected Endpoints:** Include `Authorization: Bearer <token>`

### **Token Management**
- **Expiration:** 8 hours
- **Refresh:** Re-authenticate when token expires
- **Security:** Automatic session cleanup and monitoring

```bash
# Login Example
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=password"

# Use Token
curl -X GET "http://localhost:8000/users/me/" \
  -H "Authorization: Bearer <your-jwt-token>"
```

---

## 👥 **User Roles & Permissions**

### **Role Hierarchy**
1. **super_admin:** Full system access across all organizations (Oraseas EE only)
2. **admin:** Full access within their organization (can manage users, warehouses, inventory)
3. **user:** Limited access within their organization (can order parts, record usage, view inventory)

### **Permission Matrix**
| Permission | User | Admin | Super Admin |
|------------|------|-------|-------------|
| View own organization data | ✅ | ✅ | ✅ |
| View all organizations data | ❌ | ❌ | ✅ |
| Order parts | ✅ | ✅ | ✅ |
| Record part usage | ✅ | ✅ | ✅ |
| Check inventories | ✅ | ✅ | ✅ |
| Create/edit warehouses | ❌ | ✅ | ✅ |
| Manage suppliers | ❌ | ✅ | ✅ |
| Adjust inventories | ❌ | ✅ | ✅ |
| Register machines | ❌ | ❌ | ✅ |
| Invite users | ❌ | ✅ | ✅ |
| Manage users | ❌ | ✅ | ✅ |
| View audit logs | ❌ | ✅ | ✅ |

### **Permission Scoping**
- **Organization-Based:** Users can only access data from their organization
- **Role-Based:** Different endpoints require different permission levels
- **Super Admin Override:** Super admins can access cross-organization data
- **Business Rule Enforcement:** System enforces singleton constraints for Oraseas EE and BossAqua

---

## 📚 **API Modules**

### **1. Authentication & User Management**

#### **Authentication Endpoints**
```
POST   /token                    # Login and get JWT token
GET    /users/me/               # Get current user info
```

#### **User Management Endpoints**
```
GET    /users/                  # List users (organization-scoped)
POST   /users/                  # Create new user
GET    /users/{user_id}         # Get user details
PUT    /users/{user_id}         # Update user
DELETE /users/{user_id}         # Delete user
POST   /users/invite            # Send user invitation
POST   /users/accept-invitation # Accept invitation
PUT    /users/change-password   # Change password
POST   /users/reset-password    # Request password reset
```

### **2. Organization Management**

#### **Organization Endpoints**
```
GET    /organizations/                    # List organizations (organization-scoped)
POST   /organizations/                    # Create organization (super_admin only)
GET    /organizations/{org_id}            # Get organization details
PUT    /organizations/{org_id}            # Update organization
DELETE /organizations/{org_id}            # Delete organization (super_admin only)
GET    /organizations/hierarchy           # Get organization hierarchy
GET    /organizations/types               # Get available organization types
POST   /organizations/{org_id}/activate   # Activate organization
POST   /organizations/{org_id}/deactivate # Deactivate organization
```

#### **Organization Types & Business Rules**
- **oraseas_ee:** Primary distributor and app owner (singleton - only one allowed)
- **bossaqua:** Manufacturer of AutoBoss machines and proprietary parts (singleton - only one allowed)
- **customer:** Customer organizations that purchase AutoBoss machines (max 100)
- **supplier:** External suppliers that must have a parent organization (Oraseas EE or Customer)

#### **Organization Hierarchy**
```
Oraseas EE (root)
├── Customer Organization 1
│   └── Supplier A (serves Customer 1)
├── Customer Organization 2
└── Supplier B (serves Oraseas EE)

BossAqua (independent root)
```

### **3. Warehouse Management**

#### **Warehouse Endpoints**
```
GET    /warehouses/                        # List warehouses (organization-scoped)
POST   /warehouses/                        # Create warehouse (admin+ only)
GET    /warehouses/{warehouse_id}          # Get warehouse details
PUT    /warehouses/{warehouse_id}          # Update warehouse (admin+ only)
DELETE /warehouses/{warehouse_id}          # Delete warehouse (admin+ only)
POST   /warehouses/{warehouse_id}/activate # Activate warehouse (admin+ only)
POST   /warehouses/{warehouse_id}/deactivate # Deactivate warehouse (admin+ only)
GET    /warehouses/{warehouse_id}/inventory # Get warehouse inventory
GET    /warehouses/{warehouse_id}/utilization # Get warehouse utilization metrics
```

#### **Warehouse Business Rules**
- Each organization can have multiple warehouses (except suppliers)
- Warehouse names must be unique within an organization
- Only active warehouses can receive inventory
- Warehouse deletion requires empty inventory or admin override

### **4. Parts Management**

#### **Parts Endpoints**
```
GET    /parts/                           # List parts with filtering
POST   /parts/                           # Create part (super_admin only)
GET    /parts/{part_id}                  # Get part details
PUT    /parts/{part_id}                  # Update part (super_admin only)
DELETE /parts/{part_id}                  # Delete part (super_admin only)
GET    /parts/search                     # Advanced parts search
GET    /parts/{part_id}/inventory        # Get part inventory across all warehouses
GET    /parts/{part_id}/usage-history    # Get part usage history
GET    /parts/{part_id}/compatibility    # Get machine compatibility
GET    /parts/proprietary                # List proprietary (BossAqua) parts
GET    /parts/low-stock                  # Get low stock parts
```

#### **Part Types & Classification**
- **consumable:** Standard consumable parts (tracked in whole units)
- **bulk_material:** Bulk materials with decimal quantities (e.g., 6.7 liters of oil)

#### **Part Origin**
- **proprietary:** Parts manufactured by BossAqua (is_proprietary = true)
- **general:** Parts from other suppliers (is_proprietary = false)

#### **Unit of Measure Support**
- **Pieces:** Standard countable items (filters, belts, etc.)
- **Liters:** Liquid measurements (oils, chemicals)
- **Kilograms:** Weight measurements (bulk materials)
- **Meters:** Length measurements (cables, hoses)

### **5. Inventory Management**

#### **Inventory Endpoints**
```
GET    /inventory/                       # List inventory items (warehouse-scoped)
POST   /inventory/                       # Create inventory record (admin+ only)
GET    /inventory/{inventory_id}         # Get inventory details
PUT    /inventory/{inventory_id}         # Update inventory (admin+ only)
DELETE /inventory/{inventory_id}         # Delete inventory (admin+ only)
POST   /inventory/transfer               # Transfer between warehouses (admin+ only)
GET    /inventory/low-stock              # Get low stock alerts
GET    /inventory/valuation              # Get inventory valuation
GET    /inventory/movements              # Get inventory movement history
POST   /inventory/bulk-update            # Bulk inventory updates (admin+ only)
GET    /inventory/reconciliation         # Get reconciliation reports
```

#### **Inventory Business Rules**
- Inventory is warehouse-specific (not organization-specific)
- Stock levels calculated from transaction history
- Negative inventory allowed with warnings (configurable)
- Decimal quantities supported for bulk materials
- Automatic reorder suggestions based on usage patterns

### **6. Inventory Workflows**

#### **Stocktake Management**
```
GET    /inventory-workflows/stocktakes/           # List stocktakes
POST   /inventory-workflows/stocktakes/           # Create stocktake
GET    /inventory-workflows/stocktakes/{id}       # Get stocktake details
PUT    /inventory-workflows/stocktakes/{id}       # Update stocktake
DELETE /inventory-workflows/stocktakes/{id}       # Delete stocktake
POST   /inventory-workflows/stocktakes/{id}/complete # Complete stocktake
```

#### **Stocktake Items**
```
GET    /inventory-workflows/stocktakes/{id}/items # Get stocktake items
PUT    /inventory-workflows/stocktake-items/{id}  # Update item count
PUT    /inventory-workflows/stocktakes/{id}/items/batch # Batch update items
```

#### **Inventory Adjustments**
```
GET    /inventory-workflows/adjustments/         # List adjustments
POST   /inventory-workflows/adjustments/         # Create adjustment
POST   /inventory-workflows/adjustments/batch    # Batch adjustments
```

#### **Inventory Alerts**
```
GET    /inventory-workflows/alerts/              # List alerts
POST   /inventory-workflows/alerts/              # Create alert
PUT    /inventory-workflows/alerts/{id}          # Update alert
POST   /inventory-workflows/alerts/generate      # Generate alerts
```

### **7. Order Management**

#### **Part Order Endpoints**
```
GET    /part-orders/            # List orders
POST   /part-orders/            # Create order
GET    /part-orders/{order_id}  # Get order details
PUT    /part-orders/{order_id}  # Update order
DELETE /part-orders/{order_id}  # Delete order
POST   /part-orders/{order_id}/approve   # Approve order
POST   /part-orders/{order_id}/fulfill   # Fulfill order
POST   /part-orders/batch       # Create batch order
```

#### **Order Items**
```
POST   /part-orders/{order_id}/items     # Add order item
PUT    /part-orders/items/{item_id}      # Update order item
DELETE /part-orders/items/{item_id}      # Remove order item
```

### **8. Machine Management**

#### **Machine Endpoints**
```
GET    /machines/               # List machines
POST   /machines/               # Register machine (super_admin only)
GET    /machines/{machine_id}   # Get machine details
PUT    /machines/{machine_id}   # Update machine
DELETE /machines/{machine_id}   # Delete machine
GET    /machines/{machine_id}/usage # Get machine usage history
```

### **9. Transaction Tracking**

#### **Transaction Endpoints**
```
GET    /transactions/           # List transactions
GET    /transactions/{transaction_id} # Get transaction details
POST   /transactions/reverse    # Reverse transaction
GET    /transactions/audit      # Get audit trail
```

### **10. Dashboard & Analytics**

#### **Dashboard Endpoints**
```
GET    /dashboard/metrics       # Get dashboard metrics
GET    /dashboard/low-stock     # Get low stock summary
GET    /dashboard/orders        # Get order summary
GET    /dashboard/inventory-value # Get inventory valuation
```

### **11. Session Management**

#### **Session Endpoints**
```
GET    /sessions/                    # List active sessions (own sessions or admin)
DELETE /sessions/{session_id}        # Terminate session
POST   /sessions/cleanup             # Cleanup expired sessions (admin+ only)
GET    /sessions/security-events     # Get security events (admin+ only)
POST   /sessions/terminate-all       # Terminate all user sessions (admin+ only)
```

### **12. Predictive Maintenance**

#### **Predictive Maintenance Endpoints**
```
GET    /predictive-maintenance/predictions          # Get maintenance predictions
POST   /predictive-maintenance/predictions          # Create prediction
GET    /predictive-maintenance/recommendations      # Get maintenance recommendations
POST   /predictive-maintenance/recommendations      # Create recommendation
PUT    /predictive-maintenance/recommendations/{id} # Update recommendation
```

### **13. Monitoring & Health**

#### **Monitoring Endpoints**
```
GET    /health                      # System health check
GET    /monitoring/metrics          # System metrics
GET    /monitoring/performance      # Performance metrics
GET    /monitoring/database         # Database health
GET    /monitoring/cache            # Cache status
```

### **14. Inventory Workflows**

#### **Stocktake Management**
```
GET    /inventory-workflows/stocktakes/           # List stocktakes
POST   /inventory-workflows/stocktakes/           # Create stocktake (admin+ only)
GET    /inventory-workflows/stocktakes/{id}       # Get stocktake details
PUT    /inventory-workflows/stocktakes/{id}       # Update stocktake (admin+ only)
DELETE /inventory-workflows/stocktakes/{id}       # Delete stocktake (admin+ only)
POST   /inventory-workflows/stocktakes/{id}/complete # Complete stocktake (admin+ only)
GET    /inventory-workflows/stocktakes/{id}/items # Get stocktake items
PUT    /inventory-workflows/stocktake-items/{id}  # Update item count
PUT    /inventory-workflows/stocktakes/{id}/items/batch # Batch update items (admin+ only)
```

#### **Inventory Adjustments**
```
GET    /inventory-workflows/adjustments/         # List adjustments
POST   /inventory-workflows/adjustments/         # Create adjustment (admin+ only)
POST   /inventory-workflows/adjustments/batch    # Batch adjustments (admin+ only)
GET    /inventory-workflows/adjustments/{id}     # Get adjustment details
```

#### **Inventory Alerts**
```
GET    /inventory-workflows/alerts/              # List alerts
POST   /inventory-workflows/alerts/              # Create alert (admin+ only)
PUT    /inventory-workflows/alerts/{id}          # Update alert (admin+ only)
POST   /inventory-workflows/alerts/generate      # Generate alerts (system)
DELETE /inventory-workflows/alerts/{id}          # Delete alert (admin+ only)
```

---

## 📊 **Request/Response Examples**

### **Authentication**
```json
// POST /token
{
  "username": "admin@example.com",
  "password": "password"
}

// Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 28800
}
```

### **Create Organization**
```json
// POST /organizations/
{
  "name": "Customer Corp",
  "organization_type": "customer",
  "parent_organization_id": "uuid-of-oraseas-ee",
  "address": "123 Business St, City, State 12345",
  "contact_info": "Contact: John Doe, Phone: +1-555-0123, Email: contact@customer.com"
}

// Response
{
  "id": "uuid-generated",
  "name": "Customer Corp",
  "organization_type": "customer",
  "parent_organization_id": "uuid-of-oraseas-ee",
  "address": "123 Business St, City, State 12345",
  "contact_info": "Contact: John Doe, Phone: +1-555-0123, Email: contact@customer.com",
  "is_active": true,
  "created_at": "2025-01-18T10:00:00Z",
  "updated_at": "2025-01-18T10:00:00Z",
  "parent_organization": {
    "id": "uuid-of-oraseas-ee",
    "name": "Oraseas EE",
    "organization_type": "oraseas_ee"
  },
  "child_organizations": [],
  "warehouses_count": 0,
  "users_count": 0,
  "machines_count": 0
}
```

### **Create User with Invitation**
```json
// POST /users/invite
{
  "email": "newuser@customer.com",
  "name": "Jane Smith",
  "role": "admin",
  "organization_id": "uuid-of-customer-org"
}

// Response
{
  "id": "uuid-generated",
  "email": "newuser@customer.com",
  "name": "Jane Smith",
  "role": "admin",
  "user_status": "pending_invitation",
  "organization_id": "uuid-of-customer-org",
  "invitation_token": "secure-token-generated",
  "invitation_expires_at": "2025-01-25T10:00:00Z",
  "invited_by_user_id": "uuid-of-inviting-user",
  "created_at": "2025-01-18T10:00:00Z"
}
```

### **Create Warehouse**
```json
// POST /warehouses/
{
  "name": "Main Warehouse",
  "location": "Building A, Floor 1",
  "description": "Primary storage facility for consumable parts"
}

// Response
{
  "id": "uuid-generated",
  "organization_id": "uuid-of-current-org",
  "name": "Main Warehouse",
  "location": "Building A, Floor 1", 
  "description": "Primary storage facility for consumable parts",
  "is_active": true,
  "created_at": "2025-01-18T10:00:00Z",
  "updated_at": "2025-01-18T10:00:00Z",
  "organization": {
    "id": "uuid-of-current-org",
    "name": "Customer Corp",
    "organization_type": "customer"
  },
  "inventory_items_count": 0
}
```

### **Create Part**
```json
// POST /parts/
{
  "part_number": "AB-FILTER-001",
  "name": "AutoBoss Air Filter",
  "description": "High-efficiency air filter for AutoBoss V4.0 machines",
  "part_type": "consumable",
  "is_proprietary": true,
  "unit_of_measure": "pieces",
  "manufacturer_part_number": "BA-AF-4001",
  "image_urls": ["https://example.com/images/filter001.jpg"]
}

// Response
{
  "id": "uuid-generated",
  "part_number": "AB-FILTER-001",
  "name": "AutoBoss Air Filter",
  "description": "High-efficiency air filter for AutoBoss V4.0 machines",
  "part_type": "consumable",
  "is_proprietary": true,
  "unit_of_measure": "pieces",
  "manufacturer_part_number": "BA-AF-4001",
  "manufacturer_delivery_time_days": null,
  "local_supplier_delivery_time_days": null,
  "image_urls": ["https://example.com/images/filter001.jpg"],
  "created_at": "2025-01-18T10:00:00Z",
  "updated_at": "2025-01-18T10:00:00Z",
  "total_inventory": 0,
  "low_stock_warehouses": []
}
```

### **Record Transaction**
```json
// POST /transactions/
{
  "transaction_type": "consumption",
  "part_id": "uuid-of-part",
  "from_warehouse_id": "uuid-of-warehouse",
  "machine_id": "uuid-of-machine",
  "quantity": 2.5,
  "unit_of_measure": "liters",
  "transaction_date": "2025-01-18T14:30:00Z",
  "notes": "Routine maintenance - oil change"
}

// Response
{
  "id": "uuid-generated",
  "transaction_type": "consumption",
  "part_id": "uuid-of-part",
  "from_warehouse_id": "uuid-of-warehouse",
  "to_warehouse_id": null,
  "machine_id": "uuid-of-machine",
  "quantity": 2.5,
  "unit_of_measure": "liters",
  "performed_by_user_id": "uuid-of-current-user",
  "transaction_date": "2025-01-18T14:30:00Z",
  "notes": "Routine maintenance - oil change",
  "reference_number": "TXN-20250118-001",
  "requires_approval": false,
  "approval_status": null,
  "created_at": "2025-01-18T14:30:00Z",
  "part": {
    "part_number": "AB-OIL-001",
    "name": "AutoBoss Engine Oil",
    "unit_of_measure": "liters"
  },
  "machine": {
    "name": "Machine #001",
    "serial_number": "AB-V40-001"
  }
}
```

### **Create Stocktake**
```json
// POST /inventory-workflows/stocktakes/
{
  "warehouse_id": "uuid-of-warehouse",
  "scheduled_date": "2025-01-20T09:00:00Z",
  "notes": "Monthly inventory count"
}

// Response
{
  "id": "uuid-generated",
  "warehouse_id": "uuid-of-warehouse",
  "scheduled_date": "2025-01-20T09:00:00Z",
  "status": "planned",
  "notes": "Monthly inventory count",
  "scheduled_by_user_id": "uuid-of-user",
  "warehouse_name": "Main Warehouse",
  "organization_name": "Customer Corp",
  "total_items": 150,
  "items_counted": 0,
  "discrepancy_count": 0,
  "created_at": "2025-01-18T10:00:00Z"
}
```

---

## 📊 **Data Models**

### **Organization Model**
```json
{
  "id": "uuid",
  "name": "string (unique)",
  "organization_type": "oraseas_ee | bossaqua | customer | supplier",
  "parent_organization_id": "uuid | null",
  "address": "string | null",
  "contact_info": "string | null",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "parent_organization": "Organization | null",
  "child_organizations": "Organization[]",
  "warehouses_count": "integer",
  "users_count": "integer",
  "machines_count": "integer"
}
```

### **User Model**
```json
{
  "id": "uuid",
  "organization_id": "uuid",
  "username": "string (unique)",
  "email": "string (unique)",
  "name": "string",
  "role": "user | admin | super_admin",
  "user_status": "active | inactive | pending_invitation | locked",
  "failed_login_attempts": "integer",
  "locked_until": "datetime | null",
  "last_login": "datetime | null",
  "invitation_token": "string | null",
  "invitation_expires_at": "datetime | null",
  "invited_by_user_id": "uuid | null",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "organization": "Organization"
}
```

### **Warehouse Model**
```json
{
  "id": "uuid",
  "organization_id": "uuid",
  "name": "string",
  "location": "string | null",
  "description": "string | null",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "organization": "Organization",
  "inventory_items_count": "integer"
}
```

### **Part Model**
```json
{
  "id": "uuid",
  "part_number": "string (unique)",
  "name": "string",
  "description": "string | null",
  "part_type": "consumable | bulk_material",
  "is_proprietary": "boolean",
  "unit_of_measure": "string",
  "manufacturer_part_number": "string | null",
  "manufacturer_delivery_time_days": "integer | null",
  "local_supplier_delivery_time_days": "integer | null",
  "image_urls": "string[]",
  "created_at": "datetime",
  "updated_at": "datetime",
  "total_inventory": "decimal",
  "low_stock_warehouses": "Warehouse[]"
}
```

### **Inventory Model**
```json
{
  "id": "uuid",
  "warehouse_id": "uuid",
  "part_id": "uuid",
  "current_stock": "decimal",
  "minimum_stock_recommendation": "decimal",
  "unit_of_measure": "string",
  "reorder_threshold_set_by": "string | null",
  "last_recommendation_update": "datetime | null",
  "last_updated": "datetime",
  "created_at": "datetime",
  "warehouse": "Warehouse",
  "part": "Part"
}
```

### **Machine Model**
```json
{
  "id": "uuid",
  "customer_organization_id": "uuid",
  "model_type": "string",
  "name": "string",
  "serial_number": "string (unique)",
  "purchase_date": "datetime | null",
  "warranty_expiry_date": "datetime | null",
  "status": "active | inactive | maintenance | decommissioned",
  "last_maintenance_date": "datetime | null",
  "next_maintenance_date": "datetime | null",
  "location": "string | null",
  "notes": "string | null",
  "created_at": "datetime",
  "updated_at": "datetime",
  "customer_organization": "Organization"
}
```

### **Transaction Model**
```json
{
  "id": "uuid",
  "transaction_type": "creation | transfer | consumption | adjustment",
  "part_id": "uuid",
  "from_warehouse_id": "uuid | null",
  "to_warehouse_id": "uuid | null",
  "machine_id": "uuid | null",
  "quantity": "decimal",
  "unit_of_measure": "string",
  "performed_by_user_id": "uuid",
  "transaction_date": "datetime",
  "notes": "string | null",
  "reference_number": "string | null",
  "requires_approval": "boolean",
  "approval_status": "pending | approved | rejected | null",
  "created_at": "datetime",
  "part": "Part",
  "from_warehouse": "Warehouse | null",
  "to_warehouse": "Warehouse | null",
  "machine": "Machine | null",
  "performed_by_user": "User"
}
```

### **Business Rule Constraints**

#### **Organization Constraints**
- Only one Oraseas EE organization allowed (singleton)
- Only one BossAqua organization allowed (singleton)
- Supplier organizations must have a parent organization
- Maximum 100 customer organizations

#### **User Constraints**
- Super admins must belong to Oraseas EE organization
- Each organization must have at least one admin user
- Maximum 200 total users across all organizations
- Username and email must be unique across the system

#### **Warehouse Constraints**
- Warehouse names must be unique within an organization
- Maximum 150 warehouses across all organizations
- Only active warehouses can receive inventory

#### **Part Constraints**
- Part numbers must be unique across the system
- Maximum 200 different parts in catalog
- Proprietary parts can only be created by super_admin

#### **Inventory Constraints**
- One inventory record per warehouse-part combination
- Negative inventory allowed with warnings (configurable)
- Stock levels calculated from transaction history

#### **Transaction Constraints**
- All transactions must have a valid performed_by_user
- Consumption transactions must specify from_warehouse
- Transfer transactions must specify both from_warehouse and to_warehouse
- Maximum 7,500 transactions per year (50 per machine)

---

## 🔍 **Query Parameters**

### **Common Query Parameters**
- **skip:** Number of records to skip (pagination)
- **limit:** Maximum number of records to return
- **search:** Search term for filtering
- **sort:** Sort field and direction
- **filter:** Additional filtering options

### **Examples**
```
GET /parts/?skip=0&limit=50&search=filter&sort=name:asc
GET /inventory/?warehouse_id=uuid&low_stock=true
GET /transactions/?start_date=2025-01-01&end_date=2025-01-31
```

---

## ⚠️ **Error Handling**

### **HTTP Status Codes**
- **200:** Success
- **201:** Created
- **400:** Bad Request (validation error)
- **401:** Unauthorized (authentication required)
- **403:** Forbidden (insufficient permissions)
- **404:** Not Found
- **422:** Unprocessable Entity (validation error)
- **500:** Internal Server Error

### **Error Response Format**
```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "field_name": ["Field-specific error message"]
  },
  "context": {
    "additional_info": "value"
  }
}
```

### **Business Rule Error Codes**
- **ORGANIZATION_TYPE_VIOLATION:** Singleton organization constraint violated
- **INSUFFICIENT_INVENTORY:** Not enough stock for requested operation
- **PERMISSION_DENIED:** User lacks required permissions
- **ORGANIZATION_SCOPE_VIOLATION:** Attempting to access data outside organization
- **WAREHOUSE_INACTIVE:** Operation attempted on inactive warehouse
- **INVALID_TRANSACTION_TYPE:** Transaction type not valid for operation
- **USER_ACCOUNT_LOCKED:** User account is temporarily locked
- **INVITATION_EXPIRED:** User invitation has expired
- **DUPLICATE_PART_NUMBER:** Part number already exists
- **MACHINE_NOT_OWNED:** Machine not owned by user's organization
- **SUPPLIER_PARENT_REQUIRED:** Supplier must have parent organization

### **Example Business Rule Errors**
```json
// Organization type violation
{
  "detail": "Only one Oraseas EE organization is allowed",
  "error_code": "ORGANIZATION_TYPE_VIOLATION",
  "field_errors": {
    "organization_type": ["Singleton constraint violated"]
  }
}

// Insufficient inventory
{
  "detail": "Cannot consume 5.5L - only 3.2L available",
  "error_code": "INSUFFICIENT_INVENTORY",
  "field_errors": {
    "quantity": ["Exceeds available stock"]
  },
  "context": {
    "available": 3.2,
    "requested": 5.5,
    "unit": "liters",
    "warehouse_id": "uuid-of-warehouse"
  }
}

// Permission denied
{
  "detail": "Admin role required for this operation",
  "error_code": "PERMISSION_DENIED",
  "context": {
    "required_role": "admin",
    "user_role": "user"
  }
}
```

---

## 🚀 **Rate Limiting**

### **Rate Limits**
- **Authentication:** 5 requests per minute per IP
- **General API:** 100 requests per minute per user
- **Bulk Operations:** 10 requests per minute per user

### **Rate Limit Headers**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642694400
```

---

## 📖 **Interactive Documentation**

### **Swagger UI**
- **URL:** `http://localhost:8000/docs`
- **Features:** Interactive API testing, request/response examples
- **Authentication:** Built-in OAuth2 flow for testing

### **ReDoc**
- **URL:** `http://localhost:8000/redoc`
- **Features:** Clean documentation layout, detailed schemas

---

## 🔧 **Development Tools**

### **API Testing**
```bash
# Health Check
curl http://localhost:8000/health

# Get OpenAPI Schema
curl http://localhost:8000/openapi.json
```

### **Database Access**
- **PgAdmin:** `http://localhost:8080`
- **Direct Connection:** `postgresql://abparts_user:password@localhost:5432/abparts_dev`

---

## 📝 **Changelog**

### **Version 2.0.0 (January 2025) - Business Model Alignment**
- ✅ **Complete Business Model Alignment**
  - Organization types with proper hierarchy (Oraseas EE, BossAqua, Customer, Supplier)
  - Singleton constraints for Oraseas EE and BossAqua
  - Parent-child organization relationships
- ✅ **Enhanced User Management System**
  - User invitation and onboarding workflow
  - Role-based permissions (user, admin, super_admin)
  - Session management with 8-hour expiration
  - Account security features (lockout, password reset)
  - Comprehensive audit logging
- ✅ **Warehouse-Based Inventory Management**
  - Multi-warehouse support per organization
  - Warehouse-specific inventory tracking
  - Inventory transfer capabilities
  - Real-time stock calculations
- ✅ **Enhanced Parts Classification**
  - Part types (consumable, bulk_material)
  - Decimal quantity support for bulk materials
  - Proprietary vs general parts classification
  - Unit of measure validation
- ✅ **Comprehensive Transaction Tracking**
  - Complete audit trail for all parts movements
  - Transaction types (creation, transfer, consumption, adjustment)
  - Machine-specific usage tracking
  - Approval workflow for high-value transactions
- ✅ **Machine Registration and Management**
  - Machine ownership tracking
  - Usage history and maintenance records
  - Machine-parts compatibility
- ✅ **Advanced Inventory Workflows**
  - Stocktake management system
  - Inventory adjustment workflows
  - Automated alert generation
  - Low stock recommendations
- ✅ **Analytics and Reporting**
  - Real-time dashboard metrics
  - Inventory valuation
  - Performance analytics
  - Predictive maintenance recommendations

### **Version 1.0.0 (December 2024) - Initial Implementation**
- ✅ Basic backend API implementation
- ✅ User authentication and authorization
- ✅ Basic inventory management
- ✅ Order processing system
- ✅ Initial reporting capabilities

---

**For the most up-to-date API documentation, visit the interactive Swagger UI at `/docs` when the application is running.**