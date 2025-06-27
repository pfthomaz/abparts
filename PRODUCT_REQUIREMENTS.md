# Product Requirements Document: ABParts App - Phase 2 Enhancements

## 1. Introduction

This document outlines the product requirements for the next phase of development for the ABParts application. The goal is to enhance core inventory and order management capabilities, introduce robust reporting, and improve user experience by incorporating industry best practices. This phase aims to transform ABParts into a more comprehensive and efficient solution for Oraseas EE and its customers.

**Overall Goals:**

*   Increase operational efficiency for inventory and order fulfillment processes.
*   Provide better visibility and data-driven insights into stock levels, sales, and supplier performance.
*   Enhance user satisfaction through improved workflows and proactive notifications.
*   Lay the groundwork for future integrations and scalability.

## 2. Target User Personas

*   **Oraseas Admin (Olivia):** Oversees all operations, manages system settings, users, and high-level business strategy. Needs comprehensive visibility and control.
*   **Oraseas Inventory Manager (Ian):** Responsible for day-to-day inventory control, stock accuracy, receiving, and supplier order management. Needs efficient tools for stock operations and reporting.
*   **Oraseas Sales/Order Processor (Sarah):** Manages customer orders, quotes, and fulfillment. Needs clear order tracking and customer communication tools.
*   **Customer Admin (Chris - e.g., Autoboss Admin):** Manages their organization's users, places orders, tracks their inventory (if managed by Oraseas), and records part usage. Needs self-service capabilities and clear visibility into their interactions with Oraseas EE.
*   **Customer User (Charlie - e.g., Autoboss Technician):** Places orders, records part usage. Needs simple and efficient ways to perform these tasks.

## 3. Feature Areas & User Stories

### 3.1 Core Inventory Management

#### 3.1.1 Advanced Stock Adjustments
*   **US-INV001: Manually Adjust Stock Levels with Reason Codes**
    *   **As an** Oraseas Inventory Manager (Ian),
    *   **I want to** be able to manually adjust stock levels (increase or decrease quantity) for a specific part at a specific location,
    *   **So that** I can correct discrepancies found during audits, account for damages, or record found stock.
    *   **Acceptance Criteria:**
        *   Form allows selection of part and location.
        *   User can input positive or negative adjustment quantity.
        *   A predefined list of reason codes (e.g., "Stocktake Discrepancy," "Damaged Goods," "Found Stock," "Initial Stock Entry," "Return to Vendor") must be selectable.
        *   An optional notes field is available for further details.
        *   All adjustments are logged in an audit trail (see US-ADM001).
        *   Current stock level for the part is updated immediately.

#### 3.1.2 Stock Locations & Transfers (Future Foundation - Basic Location Now)
*   *(Assumption: `organizations` can act as distinct stock locations. For this phase, we enhance clarity around this.)*
*   **US-INV002: View Stock by Organization/Location**
    *   **As an** Oraseas Admin (Olivia) or Inventory Manager (Ian),
    *   **I want to** clearly see stock levels for each part broken down by the organization (acting as a location, e.g., "Oraseas Warehouse," "Autoboss Inc - Consignment"),
    *   **So that** I can understand where my inventory is physically located.
    *   **Acceptance Criteria:**
        *   Inventory views clearly display the organization/location associated with each stock record.
        *   Filtering inventory by organization/location is possible.
*   *(True multi-location stock transfers within a single organization are deferred to a later phase, but this clarifies current capability.)*

#### 3.1.3 Cycle Counting / Stocktaking (Simplified)
*   **US-INV003: Generate Stocktake Worksheet**
    *   **As an** Oraseas Inventory Manager (Ian),
    *   **I want to** generate a list of parts with their current system stock levels for a specific organization/location,
    *   **So that** I can print it and use it for physical stock counting.
    *   **Acceptance Criteria:**
        *   Ability to select an organization/location.
        *   Option to filter by part category or supplier (if part categories/suppliers are added).
        *   Generated list includes Part Number, Part Name, System Quantity, and a blank field for "Counted Quantity."
        *   List can be exported to CSV/PDF.
*   **US-INV004: Record Stocktake Results**
    *   **As an** Oraseas Inventory Manager (Ian),
    *   **I want to** input counted quantities from a physical stocktake and have the system show discrepancies,
    *   **So that** I can identify variances and make necessary adjustments.
    *   **Acceptance Criteria:**
        *   Interface to input counted quantities against the generated stocktake list (or by part lookup).
        *   System displays variance (System Qty vs. Counted Qty).
        *   Option to automatically create stock adjustments (using US-INV001 with a "Stocktake Adjustment" reason code) for items with variances.

#### 3.1.4 Enhanced Part Information
*   **US-INV005: Track Multiple Suppliers per Part**
    *   **As an** Oraseas Inventory Manager (Ian),
    *   **I want to** associate multiple suppliers with a single part, including their specific part numbers and costs,
    *   **So that** I can make informed purchasing decisions and track supplier options.
    *   **Acceptance Criteria:**
        *   Parts model allows a one-to-many relationship with a new "Part Supplier" entity.
        *   "Part Supplier" entity includes Supplier (from Organizations), Supplier Part Number, Cost Price, Lead Time.
        *   Ability to designate a "Preferred Supplier" for a part.
*   **US-INV006: Define Part Categories**
    *   **As an** Oraseas Admin (Olivia),
    *   **I want to** create and assign categories to parts (e.g., "Filters," "Sensors," "Mechanical"),
    *   **So that** parts can be better organized for browsing, reporting, and stocktaking.
    *   **Acceptance Criteria:**
        *   CRUD functionality for Part Categories.
        *   Parts can be assigned to a category.
        *   Ability to filter parts lists by category.

### 3.2 Order Management

#### 3.2.1 Enhanced Order Statuses & Fulfillment
*   **US-ORD001: Detailed Customer Order Statuses**
    *   **As an** Oraseas Sales/Order Processor (Sarah),
    *   **I want to** manage customer orders through a more detailed set of statuses (e.g., "Pending Confirmation," "Awaiting Payment," "Confirmed," "Picking," "Packed," "Shipped," "Delivered," "Cancelled"),
    *   **So that** I can accurately track the order fulfillment lifecycle.
    *   **Acceptance Criteria:**
        *   Order status field updated to reflect new, configurable statuses.
        *   Transitions between statuses are logical (e.g., cannot go from "Pending Confirmation" to "Delivered" directly).
        *   Status changes are logged in an audit trail.
*   **US-ORD002: Generate Pick Lists for Customer Orders**
    *   **As an** Oraseas Inventory Manager (Ian),
    *   **I want to** generate a pick list for a "Confirmed" or "Picking" customer order, showing parts, quantities, and Oraseas warehouse locations (if applicable),
    *   **So that** warehouse staff can efficiently gather items for shipment.
    *   **Acceptance Criteria:**
        *   Pick list includes Order ID, Customer, Part Number, Part Name, Quantity to Pick, (Future: Bin Location).
        *   Can be printed or viewed on a mobile-friendly interface.
*   **US-ORD003: Record Shipment Details**
    *   **As an** Oraseas Sales/Order Processor (Sarah),
    *   **I want to** record shipment details (tracking number, carrier, shipment date) when a customer order is "Shipped,"
    *   **So that** the customer and internal team can track the delivery.
    *   **Acceptance Criteria:**
        *   Fields for Carrier, Tracking Number, Shipment Date added to Customer Order.
        *   These details are visible on the order view.

#### 3.2.2 Partial Shipments and Backorders
*   **US-ORD004: Handle Partial Shipments for Customer Orders**
    *   **As an** Oraseas Sales/Order Processor (Sarah),
    *   **I want to** be able to ship available items on a customer order and mark the remaining items as backordered if stock is insufficient,
    *   **So that** customers receive available parts sooner and backorders are tracked.
    *   **Acceptance Criteria:**
        *   When processing a shipment, user can specify quantities shipped per line item.
        *   If shipped quantity < ordered quantity, the remainder is marked as "Backordered Quantity."
        *   Order status can reflect "Partially Shipped."
        *   Inventory is reduced only for shipped quantities.
        *   A separate view/report for backordered items is available.
*   **US-ORD005: Fulfill Backorders**
    *   **As an** Oraseas Sales/Order Processor (Sarah),
    *   **I want to** be notified or easily identify when stock becomes available for backordered items,
    *   **So that** I can prioritize their fulfillment.
    *   **Acceptance Criteria:**
        *   System highlights or provides a list of backorders that can now be fulfilled based on current stock.
        *   Ability to create a new shipment for backordered items.

#### 3.2.3 Return Merchandise Authorization (RMA)
*   **US-ORD006: Initiate a Customer Return (RMA)**
    *   **As an** Oraseas Sales/Order Processor (Sarah),
    *   **I want to** initiate a return request for a customer, referencing the original customer order/item, and specify reason for return,
    *   **So that** customer returns are properly tracked and processed.
    *   **Acceptance Criteria:**
        *   New "RMA" or "Return Request" entity linked to Customer Order Item and Customer.
        *   Fields for Return Reason, Requested Action (Refund, Replacement), Return Status (e.g., "Pending Approval," "Approved," "Received," "Processed").
        *   Unique RMA number generated.
*   **US-ORD007: Process a Received Return**
    *   **As an** Oraseas Inventory Manager (Ian),
    *   **I want to** mark an RMA as "Received" and inspect the returned part,
    *   **So that** I can decide whether to return it to stock, scrap it, or refurbish it.
    *   **Acceptance Criteria:**
        *   Ability to update RMA status to "Received."
        *   Option to trigger a stock adjustment (using US-INV001) to add the item back to inventory if in good condition (e.g., reason "Customer Return - Resalable").
        *   Link to process refund or replacement (latter may trigger new order).

#### 3.2.4 Quotation Management
*   **US-ORD008: Create and Send Customer Quotations**
    *   **As an** Oraseas Sales/Order Processor (Sarah),
    *   **I want to** create a quotation for parts for a customer, including prices and validity period, and send it via email (or as PDF),
    *   **So that** customers can review and approve pricing before an order is placed.
    *   **Acceptance Criteria:**
        *   New "Quotation" entity similar to Customer Order but with status (Draft, Sent, Accepted, Expired).
        *   Ability to add line items with prices.
        *   Option to convert an "Accepted" quotation into a Customer Order.
        *   Generate a PDF version of the quotation.

### 3.3 Reporting and Analytics

*   **US-REP001: Inventory Valuation Report**
    *   **As an** Oraseas Admin (Olivia),
    *   **I want to** generate a report showing the total value of current inventory, based on part cost (from preferred supplier or average cost),
    *   **So that** I can understand the financial value of my stock.
    *   **Acceptance Criteria:**
        *   Report lists parts, quantity on hand, unit cost, and total value per part.
        *   Summary total for all inventory.
        *   Filterable by organization/location and part category.
*   **US-REP002: Stock Aging Report**
    *   **As an** Oraseas Inventory Manager (Ian),
    *   **I want to** see how long inventory items have been in stock (e.g., 0-30 days, 31-60 days, 60-90 days, 90+ days),
    *   **So that** I can identify slow-moving or potentially obsolete stock.
    *   **Acceptance Criteria:**
        *   Report requires tracking of stock receipt dates (needs enhancement to inventory model or via purchase order receipts).
        *   Displays parts grouped by aging buckets.
*   **US-REP003: Sales Report by Part/Customer**
    *   **As an** Oraseas Admin (Olivia) or Sales Processor (Sarah),
    *   **I want to** generate sales reports showing quantity sold and revenue by part and by customer over a selected period,
    *   **So that** I can identify top-selling parts and key customers.
    *   **Acceptance Criteria:**
        *   Filterable by date range, customer, part.
        *   Displays Part Number, Part Name, Quantity Sold, Total Revenue.
        *   Summaries and drill-down capabilities.
*   **US-REP004: Low Stock Report / Reorder Suggestions**
    *   **As an** Oraseas Inventory Manager (Ian),
    *   **I want to** view a report of all parts that are below their minimum stock recommendation or reorder threshold,
    *   **So that** I can proactively create supplier orders.
    *   **Acceptance Criteria:**
        *   Lists parts, current stock, minimum stock, reorder threshold, and suggested reorder quantity (based on a simple formula or preferred supplier batch size initially).
        *   Option to directly initiate a supplier order from this report.

### 3.4 User Experience & Workflow Enhancements

*   **US-UX001: Centralized Dashboard with Actionable KPIs**
    *   **As an** Oraseas Admin (Olivia) or Inventory Manager (Ian),
    *   **I want to** see a dashboard upon login that summarizes key information like low stock items, orders pending shipment, overdue supplier orders, and recent part usage,
    *   **So that** I can quickly identify areas needing attention.
    *   **Acceptance Criteria:**
        *   Dashboard displays configurable widgets/cards for KPIs.
        *   Links from dashboard items to relevant modules/reports.
*   **US-UX002: Advanced Search and Filtering Across Modules**
    *   **As any** user,
    *   **I want to** have robust search (e.g., by part number, name, description, order ID, customer name) and filtering (e.g., by status, date range, category) capabilities on all list views (parts, inventory, orders, etc.),
    *   **So that** I can find information quickly and efficiently.
    *   **Acceptance Criteria:**
        *   Consistent search bar placement.
        *   Multi-criteria filtering options relevant to each module.
*   **US-UX003: System Notifications for Key Events**
    *   **As an** Oraseas Inventory Manager (Ian),
    *   **I want to** receive a system notification (and optionally email) when a part's stock level drops below its reorder threshold,
    *   **So that** I can take timely action to reorder.
    *   **Acceptance Criteria:**
        *   Configurable notification preferences per user (in-app, email).
        *   Notifications for: low stock, new customer order placed, supplier order overdue.
*   **US-UX004: Improved Mobile Responsiveness**
    *   **As any** user accessing the app on a tablet or mobile device,
    *   **I want** the interface to be responsive and usable,
    *   **So that** I can perform essential tasks when not at a desktop.
    *   **Acceptance Criteria:**
        *   All key views and forms adapt to smaller screen sizes.
        *   Touch targets are appropriately sized.
        *   Navigation remains intuitive.

### 3.5 Administrative Features

*   **US-ADM001: Comprehensive Audit Trail**
    *   **As an** Oraseas Admin (Olivia),
    *   **I want** a system-wide audit trail that logs critical actions such as user logins, creation/modification/deletion of key data (parts, orders, inventory adjustments), and role changes,
    *   **So that** I can track system usage, troubleshoot issues, and ensure accountability.
    *   **Acceptance Criteria:**
        *   Audit log includes timestamp, user, action performed, and relevant entity ID.
        *   Ability to view and filter the audit log.
*   **US-ADM002: Granular User Permissions (Foundation)**
    *   **As an** Oraseas Admin (Olivia),
    *   **I want to** have the ability to define more granular permissions beyond the current broad roles (e.g., view-only access to certain modules, specific actions allowed/disallowed),
    *   **So that** I can enforce stricter access control as the team grows or customer needs evolve.
    *   **Acceptance Criteria:**
        *   Backend support for a more flexible permission system (e.g., permission tags associated with roles or users).
        *   Initial implementation might focus on backend changes, with UI for managing these deferred if complex.
        *   Existing roles are mapped to this new permission structure.

## 4. Out of Scope (For This Phase)

*   Full multi-warehouse/bin location management within a single Oraseas organization.
*   Serial number / Batch / Lot tracking for inventory.
*   Advanced demand forecasting models.
*   Direct E-commerce or Accounting software integrations (though foundations like API enhancements can be laid).
*   Barcode generation and scanning functionalities.
*   Kitting/Bill of Materials functionality.

---
This document will serve as the basis for sprint planning and development efforts for ABParts Phase 2.
It will be a living document, subject to review and refinement as development progresses and feedback is gathered.
```
