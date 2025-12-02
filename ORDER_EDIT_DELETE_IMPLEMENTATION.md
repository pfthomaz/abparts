# Order Edit and Delete Implementation

## Overview
Implemented edit and delete functionality for both customer orders and supplier orders with admin-only permissions.

## Backend Changes

### Customer Orders (`backend/app/routers/customer_orders.py`)

#### Updated PUT Endpoint
- **Permission**: Only admins can edit orders
- **Organization Scope**: Admins can edit orders from their organization (customer or Oraseas EE)
- **Super Admins**: Can edit any order

#### New DELETE Endpoint
- **Route**: `DELETE /customer_orders/{order_id}`
- **Permission**: Only admins can delete orders
- **Organization Scope**: Admins can delete orders from their organization
- **Status Restriction**: Can only delete orders in 'Requested' or 'Pending' status
- **Cascade**: Automatically deletes order items and transactions

### Supplier Orders (`backend/app/routers/supplier_orders.py`)

#### Updated PUT Endpoint
- **Permission**: Only admins can edit orders
- **Organization Scope**: Admins can edit orders from their organization
- **Super Admins**: Can edit any order

#### New DELETE Endpoint
- **Route**: `DELETE /supplier_orders/{order_id}`
- **Permission**: Only admins can delete orders
- **Organization Scope**: Admins can delete orders from their organization
- **Status Restriction**: Can only delete orders in 'Requested' or 'Pending' status
- **Cascade**: Automatically deletes order items

## Frontend Changes

### Orders Service (`frontend/src/services/ordersService.js`)

Added two new methods:
- `deleteSupplierOrder(orderId)` - Deletes a supplier order
- `deleteCustomerOrder(orderId)` - Deletes a customer order

## Features

### Edit Orders
- Admins can change:
  - Order dates (order_date, expected_delivery_date)
  - Order items (add/remove/modify quantities)
  - Order status
  - Notes and other metadata

### Delete Orders
- Only orders in 'Requested' or 'Pending' status can be deleted
- Orders that have been shipped, received, or delivered cannot be deleted
- Deletion cascades to order items and related transactions
- Organization-scoped: admins can only delete orders from their organization

## Security
- Admin-only access enforced at the API level
- Organization scoping prevents cross-organization modifications
- Super admins have unrestricted access
- Status checks prevent deletion of fulfilled orders

## Frontend UI Implementation - COMPLETED

### Orders Page (`frontend/src/pages/Orders.js`)

#### New State Variables
- `editingOrder` - Stores the order being edited
- `editOrderType` - Tracks whether editing customer or supplier order
- `showDeleteConfirm` - Controls delete confirmation modal visibility
- `orderToDelete` - Stores the order pending deletion

#### New Helper Functions
- `canEditOrder(order)` - Checks if user is admin
- `canDeleteOrder(order)` - Checks if user is admin and order status is Requested/Pending

#### New Handlers
- `handleEditOrder(order, orderType)` - Opens edit modal with order data
- `handleDeleteOrder(order, orderType)` - Opens delete confirmation
- `confirmDeleteOrder()` - Executes the delete operation
- `cancelDelete()` - Cancels delete operation
- `handleUpdateSupplierOrder(orderData)` - Updates supplier order
- `handleUpdateCustomerOrder(orderData)` - Updates customer order

#### UI Changes
- Added **Edit** button (blue) for admins on both customer and supplier orders
- Added **Delete** button (red) for admins on orders with Requested/Pending status
- Updated order modals to support edit mode with `initialData` and `editMode` props
- Added delete confirmation modal with order details

## Testing Checklist
- [ ] Admin can edit customer order
- [ ] Admin can edit supplier order
- [ ] Admin can delete order in 'Requested' status
- [ ] Admin can delete order in 'Pending' status
- [ ] Admin cannot delete order in 'Shipped' status (button hidden)
- [ ] Admin cannot delete order in 'Received' status (button hidden)
- [ ] Regular user cannot see edit buttons
- [ ] Regular user cannot see delete buttons
- [ ] Edit modal pre-fills with existing order data
- [ ] Delete confirmation shows order details
- [ ] Successful edit refreshes order list
- [ ] Successful delete refreshes order list
- [ ] Error messages display for failed operations

## Notes
- The CustomerOrderForm and SupplierOrderForm components need to support `initialData` and `editMode` props
- If these props are not yet implemented in the form components, they will need to be added
- The forms should pre-populate fields when `initialData` is provided
- The forms should handle both create and update operations based on `editMode`
