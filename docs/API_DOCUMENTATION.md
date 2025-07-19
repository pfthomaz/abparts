# ABParts API Documentation

**Version:** 0.1.0  
**Last Updated:** January 18, 2025  
**Base URL:** `http://localhost:8000` (Development)  

---

## 📋 **API Overview**

The ABParts API is a comprehensive RESTful API built with FastAPI, providing complete inventory and order management capabilities. The API features automatic OpenAPI documentation, JWT authentication, and role-based access control.

### **Key Features**
- **RESTful Design:** Standard HTTP methods and status codes
- **JWT Authentication:** Secure token-based authentication
- **Role-Based Access:** Three-tier permission system
- **Organization Scoping:** Data access limited to user's organization
- **Comprehensive Validation:** Pydantic schema validation
- **Auto-Generated Docs:** OpenAPI/Swagger documentation at `/docs`

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
1. **super_admin:** Full system access across all organizations
2. **admin:** Full access within their organization
3. **user:** Limited access within their organization

### **Permission Scoping**
- **Organization-Based:** Users can only access data from their organization
- **Role-Based:** Different endpoints require different permission levels
- **Super Admin Override:** Super admins can access cross-organization data

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
GET    /organizations/          # List organizations
POST   /organizations/          # Create organization
GET    /organizations/{org_id}  # Get organization details
PUT    /organizations/{org_id}  # Update organization
DELETE /organizations/{org_id}  # Delete organization
GET    /organizations/hierarchy # Get organization hierarchy
```

#### **Organization Types**
- **oraseas_ee:** Primary distributor (singleton)
- **bossaqua:** Manufacturer (singleton)
- **customer:** Customer organizations
- **supplier:** External suppliers

### **3. Warehouse Management**

#### **Warehouse Endpoints**
```
GET    /warehouses/             # List warehouses
POST   /warehouses/             # Create warehouse
GET    /warehouses/{warehouse_id} # Get warehouse details
PUT    /warehouses/{warehouse_id} # Update warehouse
DELETE /warehouses/{warehouse_id} # Delete warehouse
POST   /warehouses/{warehouse_id}/activate   # Activate warehouse
POST   /warehouses/{warehouse_id}/deactivate # Deactivate warehouse
```

### **4. Parts Management**

#### **Parts Endpoints**
```
GET    /parts/                  # List parts
POST   /parts/                  # Create part
GET    /parts/{part_id}         # Get part details
PUT    /parts/{part_id}         # Update part
DELETE /parts/{part_id}         # Delete part
GET    /parts/search            # Search parts
GET    /parts/{part_id}/inventory # Get part inventory across warehouses
```

#### **Part Types**
- **consumable:** Standard consumable parts
- **bulk_material:** Bulk materials with decimal quantities

### **5. Inventory Management**

#### **Inventory Endpoints**
```
GET    /inventory/              # List inventory items
POST   /inventory/              # Create inventory record
GET    /inventory/{inventory_id} # Get inventory details
PUT    /inventory/{inventory_id} # Update inventory
DELETE /inventory/{inventory_id} # Delete inventory
POST   /inventory/transfer      # Transfer between warehouses
GET    /inventory/low-stock     # Get low stock alerts
```

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
GET    /sessions/               # List active sessions
DELETE /sessions/{session_id}   # Terminate session
POST   /sessions/cleanup        # Cleanup expired sessions
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
  "parent_organization_id": "uuid-of-parent",
  "contact_email": "contact@customer.com",
  "contact_phone": "+1-555-0123",
  "address": "123 Business St, City, State 12345"
}

// Response
{
  "id": "uuid-generated",
  "name": "Customer Corp",
  "organization_type": "customer",
  "parent_organization_id": "uuid-of-parent",
  "contact_email": "contact@customer.com",
  "contact_phone": "+1-555-0123",
  "address": "123 Business St, City, State 12345",
  "is_active": true,
  "created_at": "2025-01-18T10:00:00Z",
  "updated_at": "2025-01-18T10:00:00Z"
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

### **Version 0.1.0 (January 2025)**
- ✅ Complete backend API implementation
- ✅ Business model alignment
- ✅ Comprehensive security system
- ✅ Inventory workflow management
- ✅ Order processing system
- ✅ Analytics and reporting

---

**For the most up-to-date API documentation, visit the interactive Swagger UI at `/docs` when the application is running.**