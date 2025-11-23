# Parts, Warehouses & Inventory System - Current Implementation

## Overview

ABParts uses a **warehouse-based inventory management system** where parts are tracked at specific warehouse locations. The system supports multi-organization operations with proper access controls and comprehensive transaction auditing.

---

## Core Concepts

### 1. **Parts** (`parts` table)
Parts are the items being tracked in the system.

**Key Fields:**
- `part_number` - Unique identifier (e.g., "AB-001")
- `name` - Part name (supports multilingual text)
- `part_type` - Either `CONSUMABLE` or `BULK_MATERIAL`
- `is_proprietary` - Boolean (true for BossAqua parts)
- `unit_of_measure` - How the part is measured (pieces, liters, kg, etc.)
- `manufacturer_part_number` - External reference
- `image_urls` - Array of image URLs

**Business Rules:**
- Parts are global entities (not organization-specific)
- Can be used across multiple organizations
- Support decimal quantities (precision: 10, scale: 3)

---

### 2. **Warehouses** (`warehouses` table)
Physical storage locations within organizations.

**Key Fields:**
- `organization_id` - Which organization owns this warehouse
- `name` - Warehouse name (unique per organization)
- `location` - Physical address/description
- `is_active` - Whether warehouse is operational

**Business Rules:**
- Each warehouse belongs to ONE organization
- Warehouse names must be unique within an organization
- Organizations can have multiple warehouses
- Maximum 150 warehouses across all organizations

**Unique Constraint:**
```sql
UNIQUE (organization_id, name)
```

---

### 3. **Inventory** (`inventory` table)
The actual stock levels - tracks how many of each part are in each warehouse.

**Key Fields:**
- `warehouse_id` - Which warehouse
- `part_id` - Which part
- `current_stock` - Current quantity (DECIMAL 10,3)
- `minimum_stock_recommendation` - Reorder threshold
- `unit_of_measure` - Must match part's UOM
- `last_updated` - When stock was last changed

**Business Rules:**
- One inventory record per warehouse-part combination
- Stock levels are automatically updated by database triggers when transactions occur
- Supports decimal quantities (e.g., 2.5 liters, 10.25 kg)
- Negative stock is prevented by validation

**Unique Constraint:**
```sql
UNIQUE (warehouse_id, part_id)
```

---

## How Inventory Works

### Stock Movement Flow

```
1. CREATION (New stock arrives)
   └─> Increases inventory in destination warehouse
   
2. TRANSFER (Move between warehouses)
   └─> Decreases source warehouse
   └─> Increases destination warehouse
   
3. CONSUMPTION (Part used in machine)
   └─> Decreases warehouse stock
   └─> Creates part_usage record
   
4. ADJUSTMENT (Manual correction)
   └─> Increases or decreases stock
   └─> Requires reason code
```

### Automatic Inventory Updates

The system uses **PostgreSQL database triggers** to automatically update inventory when transactions are created:

**Trigger:** `trigger_update_inventory_on_transaction`
- Fires AFTER INSERT on `transactions` table
- Automatically adjusts `inventory.current_stock`
- Ensures data consistency
- No manual inventory updates needed in application code

---

## Key Operations

### 1. **View Inventory**

**By Warehouse:**
```
GET /inventory/warehouse/{warehouse_id}
```
Returns all parts in a specific warehouse with current stock levels.

**By Organization (Aggregated):**
```
GET /inventory/organization/{organization_id}/aggregated
```
Returns total stock for each part across ALL warehouses in the organization.

**By Organization (Detailed):**
```
GET /inventory/organization/{organization_id}/by-warehouse
```
Returns all inventory items across all warehouses (not aggregated).

---

### 2. **Transfer Inventory Between Warehouses**

```
POST /inventory/transfer
{
  "from_warehouse_id": "uuid",
  "to_warehouse_id": "uuid",
  "part_id": "uuid",
  "quantity": 10.5
}
```

**What Happens:**
1. Validates source warehouse has sufficient stock
2. Creates a TRANSFER transaction record
3. Database trigger automatically:
   - Decreases stock in source warehouse
   - Increases stock in destination warehouse (creates inventory record if needed)
4. Returns success with transaction details

**Validations:**
- Source and destination must be different
- Quantity must be positive
- Sufficient stock must exist
- User must have access to both warehouses
- Quantity precision max 3 decimal places

---

### 3. **Stock Adjustments**

Manual corrections to inventory (e.g., after physical count).

**Reasons:**
- `STOCKTAKE_DISCREPANCY` - Physical count differs from system
- `DAMAGED_GOODS` - Items damaged/unusable
- `FOUND_STOCK` - Discovered uncounted stock
- `INITIAL_STOCK_ENTRY` - First-time entry
- `RETURN_TO_VENDOR` - Returned to supplier
- `CUSTOMER_RETURN_RESALABLE` - Customer returned, can resell
- `CUSTOMER_RETURN_DAMAGED` - Customer returned, damaged
- `OTHER` - Other reasons (requires notes)

**Process:**
1. Create `StockAdjustment` record
2. Links to specific `inventory` item
3. Records user who made adjustment
4. Stores reason code and notes
5. Quantity can be positive (increase) or negative (decrease)

---

### 4. **Part Usage (Consumption)**

When a part is used in a machine:

```
POST /part-usage/
{
  "part_id": "uuid",
  "machine_id": "uuid",
  "warehouse_id": "uuid",
  "quantity": 2,
  "usage_date": "2024-11-22T10:30:00Z",
  "notes": "Regular maintenance"
}
```

**What Happens:**
1. Creates `PartUsage` record
2. Creates CONSUMPTION transaction
3. Database trigger decreases warehouse stock
4. Links usage to specific machine
5. Records which user performed the action

---

## Transaction Audit Trail

Every inventory movement creates a `Transaction` record:

**Fields:**
- `transaction_type` - CREATION, TRANSFER, CONSUMPTION, ADJUSTMENT
- `part_id` - Which part moved
- `from_warehouse_id` - Source (null for creation)
- `to_warehouse_id` - Destination (null for consumption)
- `machine_id` - If consumed by machine
- `quantity` - How much moved
- `performed_by_user_id` - Who did it
- `transaction_date` - When it happened
- `notes` - Additional context
- `reference_number` - External reference (e.g., order number)

**Benefits:**
- Complete audit trail
- Can reconstruct inventory history
- Supports compliance requirements
- Enables analytics and reporting

---

## Access Control

### Permission Levels

**Super Admin:**
- Can view/manage inventory across ALL organizations
- Can transfer between any warehouses
- Full system access

**Admin (Organization):**
- Can view/manage inventory in their organization's warehouses only
- Can transfer between their own warehouses
- Cannot access other organizations' inventory

**User (Regular):**
- Can view inventory in their organization
- Can record part usage
- Limited write permissions

### Warehouse Access Check

```python
def check_warehouse_access(user, warehouse_id, db):
    if user.role == "super_admin":
        return True
    
    warehouse = db.query(Warehouse).filter(id == warehouse_id).first()
    return warehouse.organization_id == user.organization_id
```

---

## Analytics & Reporting

### Warehouse Analytics
```
GET /inventory/warehouse/{warehouse_id}/analytics?days=30
```

**Returns:**
- Total inventory value
- Stock levels summary
- Top parts by value
- Movement trends
- Turnover metrics
- Low stock alerts

### Transfer History
```
GET /inventory/transfers?warehouse_id={id}&start_date=2024-01-01
```

**Returns:**
- All transfers involving the warehouse
- Filterable by date range, part, direction
- Shows source/destination details
- Includes user who performed transfer

---

## Database Performance

### Indexes
- `part_number` - Unique index for fast lookups
- `(warehouse_id, part_id)` - Composite unique index on inventory
- `(organization_id, name)` - Composite unique index on warehouses
- Transaction indexes on dates and warehouse IDs

### Caching
- Warehouse analytics are cached (Redis)
- Cache invalidated on inventory changes
- Improves dashboard performance

---

## Current Limitations & Future Enhancements

### Current State
✅ Basic inventory tracking works
✅ Transfers between warehouses functional
✅ Transaction audit trail complete
✅ Multi-organization support
✅ Decimal quantity support

### Known Issues
⚠️ No batch operations (must transfer one part at a time)
⚠️ No inventory reservations (for pending orders)
⚠️ Limited reporting capabilities
⚠️ No automated reorder suggestions
⚠️ No barcode/QR code support

### Potential Improvements
- Batch transfer operations
- Inventory reservations for orders
- Automated low-stock alerts
- Predictive reorder recommendations
- Mobile app for warehouse operations
- Barcode scanning integration
- Advanced analytics dashboard
- Multi-currency support for valuations

---

## Common Workflows

### 1. Receiving New Stock
```
1. Supplier order arrives
2. Update supplier order status to "Delivered"
3. System automatically creates CREATION transactions
4. Inventory in receiving warehouse increases
```

### 2. Fulfilling Customer Order
```
1. Customer places order
2. Admin picks parts from warehouse
3. Creates TRANSFER transaction to "Shipping" warehouse
4. Ships order
5. System creates CONSUMPTION transaction (optional)
```

### 3. Physical Stocktake
```
1. Generate stocktake worksheet: GET /inventory/worksheet/stocktake
2. Count physical stock
3. Compare with system quantities
4. Create stock adjustments for discrepancies
5. Record reason codes and notes
```

### 4. Machine Maintenance
```
1. Technician performs maintenance
2. Records parts used via PartUsageRecorder component
3. System creates CONSUMPTION transactions
4. Inventory decreases automatically
5. Part usage linked to machine for history
```

---

## Summary

The ABParts inventory system is **warehouse-centric** with:
- Parts stored in specific warehouse locations
- Automatic stock updates via database triggers
- Complete transaction audit trail
- Organization-based access control
- Support for decimal quantities
- Real-time analytics and reporting

The architecture is solid for the current scale (max 100 customers, 150 warehouses) and provides a strong foundation for future enhancements.
