
# Warehouse QR Location System - Implementation Tasks

## Phase 1: Backend - Location Model & API

- [x] 1. Create database migration for warehouse_locations table
  - Add `warehouse_locations` table (id, warehouse_id, location_code, description, created_at, updated_at)
  - Add `inventory_locations` junction table (id, inventory_id, location_id, created_at)
  - Add unique constraint on (warehouse_id, location_code)
  - _Requirements: 1.1, 1.2, 1.5_

- [x] 2. Create SQLAlchemy models for locations
  - Add WarehouseLocation model to models.py
  - Add InventoryLocation model to models.py
  - Add relationships to existing Warehouse and Inventory models
  - _Requirements: 1.1, 1.3, 1.4_

- [x] 3. Create Pydantic schemas for locations
  - WarehouseLocationCreate, WarehouseLocationUpdate, WarehouseLocationResponse
  - InventoryLocationAssign (assign part to location)
  - LocationWithParts (location + list of parts at that location)
  - _Requirements: 1, 2_

- [x] 4. Create CRUD operations for locations
  - Create `backend/app/crud/warehouse_locations.py`
  - CRUD for locations (create, read, update, delete)
  - Assign/unassign parts to locations
  - Get parts by location, get location by part
  - _Requirements: 1, 2_

- [x] 5. Create API router for locations
  - Create `backend/app/routers/warehouse_locations.py`
  - GET /warehouses/{id}/locations - list locations for a warehouse
  - POST /warehouses/{id}/locations - create location
  - PUT /warehouse-locations/{id} - update location
  - DELETE /warehouse-locations/{id} - delete location
  - POST /warehouse-locations/{id}/assign - assign part(s) to location
  - GET /warehouse-locations/{id}/parts - get parts at location
  - GET /locate/{warehouse_id}/{location_code} - public lookup endpoint (for QR)
  - _Requirements: 1, 2, 4, 5_

## Phase 2: Frontend - Location Management

- [x] 6. Create Location Management page
  - Create `frontend/src/pages/WarehouseLocations.js`
  - List all locations in a warehouse (grid/card view)
  - Show location code, description, number of parts
  - Color coding: green (has parts), gray (empty)
  - Add/edit/delete locations
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 7. Add location assignment to inventory
  - Add "Location" field/dropdown to part inventory views
  - Allow setting location when viewing a part's stock
  - Show location in parts list table
  - Bulk assign: select multiple parts → assign location
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 8. Add routing and navigation
  - Add WarehouseLocations to App.js routes
  - Add "Locations" tab/link in warehouse detail view
  - Add "Scan" button to mobile navigation
  - _Requirements: 7_

## Phase 3: QR Code Generation & Labels

- [x] 9. Create QR code generation service (backend)
  - Install `qrcode` and `reportlab` Python packages
  - Create `backend/app/services/qr_label_service.py`
  - Generate QR code image for a location URL
  - Generate PDF with QR labels (configurable layout for A4 sticker sheets)
  - _Requirements: 3.1, 3.2, 3.4_

- [x] 10. Create label generation API endpoint
  - POST /warehouses/{id}/locations/labels - generate PDF for selected locations
  - GET /warehouses/{id}/locations/labels/all - generate PDF for all locations
  - Return PDF file for download
  - _Requirements: 3.4, 3.5_

- [x] 11. Create label generation UI
  - "Print Labels" button on Location Management page
  - Select which locations to print (checkboxes)
  - "Print All" option
  - Preview label layout
  - Download PDF button
  - _Requirements: 3.1, 3.5_

## Phase 4: QR Scanner (Mobile)

- [x] 12. Install QR scanning library
  - Add `html5-qrcode` to frontend dependencies
  - Create QR scanner wrapper component
  - Handle camera permissions
  - _Requirements: 4.1, 4.2_

- [x] 13. Create Scanner page/modal
  - Create `frontend/src/components/QRScanner.js`
  - Full-screen camera view with scan overlay
  - Auto-detect QR code from camera feed
  - Parse scanned URL to extract warehouse_id and location_code
  - _Requirements: 4.1, 4.2, 4.4_

- [x] 14. Create Location Detail view (scan result)
  - Create `frontend/src/pages/LocationDetail.js`
  - Route: `/locate/{warehouse_id}/{location_code}`
  - Shows: location code, all parts at this location with photos and quantities
  - Big, clear, mobile-friendly cards for each part
  - _Requirements: 4.3, 4.5_

- [x] 15. Add "Find Part" feature
  - Search box on warehouse/inventory page
  - Type part name → shows location code prominently
  - "📍 Where is this?" button on each part card
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

## Phase 5: Order Pick List

- [x] 16. Create Pick List component
  - Create `frontend/src/components/OrderPickList.js`
  - Takes an order → shows items with locations
  - Sort by location code for efficient walking
  - Checkbox to mark items as picked
  - Progress bar (3/7 picked)
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 17. Add Pick List to order detail
  - "Start Picking" button on order detail page
  - Opens pick list view (mobile-optimized)
  - Optional: scan QR to confirm location
  - Celebration animation when all items picked
  - _Requirements: 6.1, 6.6_

## Phase 6: Polish & Translations

- [x] 18. Add translations for all new UI
  - Location management strings
  - Scanner strings
  - Pick list strings
  - All 6 languages
  - _Requirements: All_

- [x] 19. Mobile optimization
  - Test scanner on iOS and Android
  - Ensure pick list works well on small screens
  - Large touch targets for picking checkboxes
  - _Requirements: 4, 6_

- [x] 20. Deploy and test
  - Run migration on production
  - Deploy frontend + backend
  - Test full flow: create locations → assign parts → print labels → scan → pick order
  - _Requirements: All_

## Estimated Timeline

- **Phase 1** (Backend): 2-3 days
- **Phase 2** (Location UI): 2-3 days
- **Phase 3** (QR Labels): 2 days
- **Phase 4** (Scanner): 2-3 days
- **Phase 5** (Pick List): 2-3 days
- **Phase 6** (Polish): 1-2 days

**Total**: ~2 weeks

## Dependencies

- `qrcode` Python package (QR generation)
- `reportlab` Python package (PDF generation)
- `html5-qrcode` npm package (camera QR scanning)
- `qrcode.react` npm package (QR display in UI)

## Branch

```bash
git checkout -b warehouse-qr-locations
```
