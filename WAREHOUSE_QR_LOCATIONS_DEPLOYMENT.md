# Warehouse QR Location System - Deployment Guide

## Feature Summary

This deployment adds the Warehouse QR Location System, enabling:
- Shelf location management within warehouses
- QR code label generation (PDF) for physical shelves
- Mobile QR scanning to identify parts at a location
- Reverse lookup ("Where is this part?")
- Order pick lists sorted by location for efficient fulfillment

---

## Pre-Deployment Checklist

- [ ] All code merged to the deployment branch
- [ ] Backend Python syntax verified (all files pass `py_compile`)
- [ ] Frontend builds successfully (`npm run build` — exit code 0)
- [ ] New Python dependencies added to `requirements.txt`:
  - `reportlab==4.0.7` (PDF generation)
  - `qrcode[pil]==7.4.2` (QR code generation)
- [ ] New frontend dependency in `package.json`:
  - `html5-qrcode: ^2.3.8` (camera QR scanning)
- [ ] Migration file exists: `backend/alembic/versions/warehouse_locations_001_add_location_tables.py`
- [ ] Router registered in `backend/app/main.py`
- [ ] Backup production database before migration

---

## Deployment Steps

### 1. Backup Database

```bash
# SSH into production server
ssh your-server

# Backup the database
docker-compose -f docker-compose.prod.yml exec db pg_dump -U abparts_user abparts_prod > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Pull Latest Code

```bash
cd /path/to/abparts
git pull origin main  # or your deployment branch
```

### 3. Rebuild Docker Images

```bash
# Rebuild backend (installs new Python packages: qrcode, reportlab)
docker-compose -f docker-compose.prod.yml build api

# Rebuild frontend (installs html5-qrcode, builds React app)
docker-compose -f docker-compose.prod.yml build web
```

### 4. Run Database Migration

```bash
# Run the warehouse locations migration
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

This creates:
- `warehouse_locations` table (id, warehouse_id, location_code, description, created_at, updated_at)
- `inventory_locations` junction table (id, inventory_id, location_id, created_at)
- Unique constraint on (warehouse_id, location_code)
- Indexes on warehouse_id, location_code, inventory_id, location_id

### 5. Restart Services

```bash
# Restart all services with new images
docker-compose -f docker-compose.prod.yml up -d

# Verify services are healthy
docker-compose -f docker-compose.prod.yml ps
```

### 6. Verify Deployment

```bash
# Check API is responding
curl -s http://localhost:8000/docs | head -5

# Check migration was applied
docker-compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "\dt warehouse_locations"
docker-compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "\dt inventory_locations"

# Check API logs for errors
docker-compose -f docker-compose.prod.yml logs --tail=50 api
```

---

## Post-Deployment Verification (Manual Test Flow)

### Test 1: Create Locations

1. Log in as a warehouse admin
2. Navigate to a warehouse → "Locations" tab
3. Create locations: "A1", "A2", "B1", "B2", "C1"
4. Verify locations appear in the grid view
5. Verify color coding: gray for empty locations

### Test 2: Assign Parts to Locations

1. Navigate to a part's inventory view
2. Set location to "A1"
3. Assign another part to "A1" (shared bin)
4. Assign a part to "B1"
5. Verify location shows in parts list
6. Navigate to location "A1" → verify both parts appear
7. Test bulk assignment: select multiple parts → assign to "C1"

### Test 3: Print QR Labels

1. Go to Location Management page
2. Select locations A1, A2, B1 using checkboxes
3. Click "Print Labels"
4. Verify PDF downloads with QR codes
5. Verify each label shows: QR code + location code text
6. Test "Print All" option
7. Verify QR codes encode correct URLs: `https://abparts.oraseas.com/locate/{warehouse_id}/{location_code}`

### Test 4: QR Scanner (Mobile)

1. Open app on mobile phone
2. Tap "Scan" button
3. Grant camera permission
4. Point camera at a printed QR label
5. Verify it navigates to the location detail page
6. Verify parts at that location are displayed with photos and quantities
7. Verify result appears within ~1 second of scan

### Test 5: Find Part (Reverse Lookup)

1. Use the search/filter on warehouse page
2. Type a part name
3. Verify location code is shown prominently in results
4. Click "Where is this?" button on a part card
5. Verify it shows the location code

### Test 6: Order Pick List

1. Navigate to an existing order with multiple items
2. Click "Start Picking"
3. Verify pick list shows items sorted by location code
4. Verify each item shows: part name, quantity needed, location
5. Mark items as picked using checkboxes
6. Verify progress bar updates (e.g., "3/7 picked")
7. Pick all items → verify celebration animation

---

## New API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/warehouses/{id}/locations` | List locations for a warehouse |
| POST | `/warehouses/{id}/locations` | Create a new location |
| PUT | `/warehouse-locations/{id}` | Update a location |
| DELETE | `/warehouse-locations/{id}` | Delete a location |
| POST | `/warehouse-locations/{id}/assign` | Assign part(s) to location |
| GET | `/warehouse-locations/{id}/parts` | Get parts at a location |
| GET | `/locate/{warehouse_id}/{location_code}` | Public lookup (for QR) |
| POST | `/warehouses/{id}/locations/labels` | Generate PDF for selected locations |
| GET | `/warehouses/{id}/locations/labels/all` | Generate PDF for all locations |

---

## New Frontend Routes

| Route | Page | Description |
|-------|------|-------------|
| `/warehouses/:id/locations` | WarehouseLocations | Location management |
| `/locate/:warehouseId/:locationCode` | LocationDetail | QR scan result page |

---

## Files Added/Modified

### Backend (New Files)
- `backend/app/routers/warehouse_locations.py` — API endpoints
- `backend/app/crud/warehouse_locations.py` — Database operations
- `backend/app/services/qr_label_service.py` — QR code & PDF generation
- `backend/alembic/versions/warehouse_locations_001_add_location_tables.py` — Migration

### Backend (Modified)
- `backend/app/models.py` — Added WarehouseLocation, InventoryLocation models
- `backend/app/schemas.py` — Added location-related Pydantic schemas
- `backend/app/main.py` — Registered warehouse_locations router
- `backend/requirements.txt` — Added qrcode, reportlab

### Frontend (New Files)
- `frontend/src/pages/WarehouseLocations.js` — Location management page
- `frontend/src/pages/LocationDetail.js` — QR scan result page
- `frontend/src/components/QRScanner.js` — Camera QR scanner
- `frontend/src/components/OrderPickList.js` — Order pick list component

### Frontend (Modified)
- `frontend/src/App.js` — Added routes
- `frontend/package.json` — Added html5-qrcode dependency

---

## Rollback Instructions

If issues are found after deployment:

### 1. Rollback Database Migration

```bash
# Revert the warehouse locations migration
docker-compose -f docker-compose.prod.yml exec api alembic downgrade add_machine_dates
```

This drops both `inventory_locations` and `warehouse_locations` tables.

### 2. Restore Previous Code

```bash
# Revert to previous commit
git checkout <previous-commit-hash>

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build api web
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Restore Database (if needed)

```bash
# Only if data corruption occurred
docker-compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod < backup_YYYYMMDD_HHMMSS.sql
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Migration fails with "relation already exists" | Table may already exist from a manual run. Check with `\dt` and drop if needed, then re-run. |
| QR scanner not working on mobile | Ensure HTTPS is configured (camera requires secure context). Check browser permissions. |
| PDF labels not generating | Verify `reportlab` and `qrcode` packages are installed in the container. Check API logs. |
| Frontend shows blank page | Check browser console for JS errors. Verify build completed without errors. |
| Location not found after scan | Verify the QR URL format matches the route pattern. Check the `locate` endpoint. |

---

## Notes

- The QR scanner requires HTTPS in production (browser camera API requirement)
- Labels are formatted for A4 sticker sheets — layout can be adjusted in `qr_label_service.py`
- The system supports up to 50 locations per warehouse
- Multiple parts can share the same location (shared bin concept)
- Location codes must be unique within a warehouse
