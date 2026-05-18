# Warehouse QR Location System - Requirements

## Introduction

The Oraseas warehouse has spare parts stored on shelves but lacks a system connecting physical locations to the app. Currently only experienced staff can find parts. This feature adds shelf location tracking with QR codes so anyone can locate and pick parts.

## Key Constraints

- Start with Oraseas warehouse, design for any organization to use
- Up to 10 shelf positions (Oraseas), up to 50 for customers
- Multiple parts can share a bin/location
- QR codes printed on standard A4 sticker label sheets (format TBD)
- Mobile-first scanning experience (phone camera)
- Must feel simple and fun, not bureaucratic

## Requirements

### Requirement 1: Shelf Location Model

**User Story:** As a warehouse admin, I want to define shelf locations in my warehouse so parts can be assigned to specific positions.

**Acceptance Criteria:**
1. Each warehouse can have locations defined with a simple code (e.g., "A1", "B3", "C2-top")
2. Locations have: code, description (optional), warehouse_id
3. A part's inventory record can be linked to one or more locations
4. Multiple parts can share the same location (shared bin)
5. Location codes are unique within a warehouse

### Requirement 2: Assign Parts to Locations

**User Story:** As a warehouse admin, I want to assign parts to shelf locations so the system knows where everything is stored.

**Acceptance Criteria:**
1. When viewing a part's inventory, I can set/change its location
2. When viewing a location, I can see all parts stored there
3. Bulk assignment: select multiple parts and assign to same location
4. Location is shown on the parts list and inventory views

### Requirement 3: QR Code Generation

**User Story:** As a warehouse admin, I want to generate QR code labels for my shelf locations so I can print and stick them on shelves.

**Acceptance Criteria:**
1. Generate QR codes for selected locations
2. QR encodes a URL: `https://abparts.oraseas.com/locate/{warehouse_id}/{location_code}`
3. Label includes: QR code + location code (large text) + part name(s) if assigned
4. Generate PDF formatted for A4 sticker label sheets (layout configurable later)
5. Can generate labels for individual locations or batch (all locations in a warehouse)

### Requirement 4: QR Scanner (Mobile)

**User Story:** As a warehouse worker, I want to scan a QR code with my phone and instantly see what's in that location.

**Acceptance Criteria:**
1. "Scan" button accessible from warehouse/inventory pages
2. Opens phone camera for QR scanning
3. After scan: shows location details with all parts stored there (name, photo, quantity)
4. Works on mobile browsers (no app install required)
5. Fast - result appears within 1 second of scan

### Requirement 5: Find Part (Reverse Lookup)

**User Story:** As a warehouse worker, I want to search for a part and see where it's stored.

**Acceptance Criteria:**
1. Search/filter parts by name or SKU
2. Results show the shelf location prominently
3. "Where is this?" button on any part → shows location code
4. Works from mobile

### Requirement 6: Order Pick List

**User Story:** As a warehouse worker fulfilling an order, I want a pick list showing where each item is located so I can efficiently gather all parts.

**Acceptance Criteria:**
1. From an order, generate a "Pick List" view
2. Shows each order line with: part name, quantity needed, location code
3. Items sorted by location for efficient walking path
4. Worker can mark items as "picked" (checkbox)
5. Visual progress indicator (3/7 items picked)
6. Optional: scan QR to confirm correct location when picking

### Requirement 7: Location Management UI

**User Story:** As a warehouse admin, I want a simple page to manage my warehouse locations.

**Acceptance Criteria:**
1. List all locations in a warehouse with their assigned parts
2. Add/edit/delete locations
3. Visual grid or list view of the warehouse layout
4. Show empty locations vs occupied ones
5. Quick stats: total locations, occupied, empty

## Data Model

```
warehouse_locations:
  - id (UUID)
  - warehouse_id (FK → warehouses)
  - location_code (string, e.g., "A1", "B3-top")
  - description (optional string)
  - created_at, updated_at

inventory_locations (junction table):
  - id (UUID)
  - inventory_id (FK → inventory)
  - location_id (FK → warehouse_locations)
  - created_at
```

## UI Priorities

1. **Scan & Find** - The primary mobile interaction
2. **Pick List** - The "fun" order fulfillment flow
3. **Location Management** - Admin setup (done once)
4. **Label Printing** - Generate PDFs for physical labels

## Non-Goals (for now)

- Barcode support (QR only)
- Automated inventory counting
- Warehouse floor plan/map visualization
- Integration with external WMS systems
- Real-time location tracking
