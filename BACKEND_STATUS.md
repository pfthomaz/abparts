# Backend Endpoints Status Summary

This document summarizes the current state of the backend API endpoints for each main entity in the ABParts application, based on the codebase and conventions observed.

---

## 1. **Organizations**
- **Endpoints:** Likely include CRUD (Create, Read, Update, Delete) for organizations.
- **Typical Routes:** `/organizations/`, `/organizations/{id}`
- **Purpose:** Manage customer, supplier, and warehouse organizations.
- **Status:** Standard CRUD expected; role-based access likely enforced.

---

## 2. **Users**
- **Endpoints:** User registration, login (`/token`), profile, and possibly user management.
- **Typical Routes:** `/users/`, `/users/{id}`, `/token`
- **Purpose:** Authentication (JWT), user management, role assignment.
- **Status:** JWT-based login implemented; user CRUD likely present.

---

## 3. **Parts**
- **Endpoints:** CRUD for parts catalog.
- **Typical Routes:** `/parts/`, `/parts/{id}`
- **Purpose:** Manage parts metadata, images, and properties.
- **Status:** CRUD expected; image upload/storage may be present.

---

## 4. **Inventory**
- **Endpoints:** CRUD for inventory items, stock adjustments.
- **Typical Routes:** `/inventory/`, `/inventory/{id}`, `/inventory/{inventory_id}/adjustments`
- **Purpose:** Track stock levels, minimum recommendations, and adjustments.
- **Status:** CRUD and stock adjustment endpoints present.

---

## 5. **Machines**
- **Endpoints:** CRUD for machines/assets.
- **Typical Routes:** `/machines/`, `/machines/{id}`
- **Purpose:** Manage machines associated with organizations.
- **Status:** CRUD expected.

---

## 6. **Orders**
- **Entities:** CustomerOrder, SupplierOrder
- **Endpoints:** CRUD for both customer and supplier orders.
- **Typical Routes:** `/customer_orders/`, `/supplier_orders/`, `/orders/{id}`
- **Purpose:** Track order status, items, and fulfillment.
- **Status:** CRUD and status update endpoints likely present.

---

## 7. **Part Usage**
- **Endpoints:** Record and retrieve part usage events.
- **Typical Routes:** `/part_usage/`, `/part_usage/{id}`
- **Purpose:** Track consumption of parts by machines or organizations.
- **Status:** Endpoints for logging and querying usage events.

---

## 8. **Dashboard & Metrics**
- **Endpoints:** Aggregate and summary metrics for dashboard.
- **Typical Routes:** `/dashboard/metrics`, `/dashboard/low_stock_by_organization`
- **Purpose:** Provide summary statistics (total parts, low stock, pending orders, etc.).
- **Status:** Implemented in `crud/dashboard.py` and exposed via dashboard endpoints.

---

## 9. **Authentication**
- **Endpoints:** JWT token issuance and user validation.
- **Typical Routes:** `/token`
- **Purpose:** Secure access to API using JWT; role-based access control.
- **Status:** Implemented; uses password hashing and JWT.

---

## 10. **Other Observations**
- **Role-Based Access:** Many endpoints likely enforce roles (admin, manager, user, etc.).
- **Error Handling:** Standard FastAPI error handling with HTTPException.
- **Async Tasks:** Celery present, but async endpoints/tasks not fully detailed.
- **File Uploads:** Possible for part images, but not confirmed in endpoint summary.

---

**Note:**  
This summary is based on code structure, naming conventions, and observed patterns. For a complete and up-to-date list of endpoints, refer to the FastAPI auto-generated docs at `/docs` when the backend is running.