# Net Cleaning Records - Implementation Plan

## Feature Overview

The Net Cleaning Records feature enables aquaculture operations to track and manage net cleaning activities across farm sites. This includes managing farm sites, individual nets/cages, and detailed cleaning event records.

## Business Context

**Purpose:** Track net cleaning operations for aquaculture farms using AutoBoss net cleaning machines.

**Key Activities:**
- Define farm sites and cage/pen structures
- Record net specifications (dimensions, materials)
- Log cleaning events with operational details
- Track cleaning modes, depths, duration, and operators
- Generate cleaning history and analytics

## Data Model

### 1. Farm Sites
Represents physical aquaculture farm locations within an organization.

**Table: `farm_sites`**
```sql
- id (UUID, PK)
- organization_id (UUID, FK -> organizations)
- name (VARCHAR, required) - e.g., "North Bay Farm"
- location (VARCHAR, optional) - GPS coordinates or address
- description (TEXT, optional)
- active (BOOLEAN, default: true)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### 2. Nets/Cages
Individual nets or cages within a farm site.

**Table: `nets`**
```sql
- id (UUID, PK)
- farm_site_id (UUID, FK -> farm_sites)
- name (VARCHAR, required) - e.g., "Pen A1", "Cage 12"
- diameter (DECIMAL, optional) - in meters
- vertical_depth (DECIMAL, optional) - in meters
- cone_depth (DECIMAL, optional) - in meters
- mesh_size (VARCHAR, optional) - e.g., "22mm", "28mm"
- material (VARCHAR, optional) - e.g., "Nylon", "Polyethylene"
- notes (TEXT, optional)
- active (BOOLEAN, default: true)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### 3. Cleaning Records
Individual cleaning event records.

**Table: `net_cleaning_records`**
```sql
- id (UUID, PK)
- net_id (UUID, FK -> nets)
- machine_id (UUID, FK -> machines, optional)
- operator_name (VARCHAR, required)
- cleaning_mode (INTEGER, required) - 1, 2, or 3
- depth_1 (DECIMAL, optional) - first depth in meters
- depth_2 (DECIMAL, optional) - second depth in meters
- depth_3 (DECIMAL, optional) - third depth in meters
- start_time (TIMESTAMP, required)
- end_time (TIMESTAMP, required)
- duration_minutes (INTEGER, computed)
- notes (TEXT, optional)
- created_by (UUID, FK -> users)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

**Constraints:**
- `end_time` must be after `start_time`
- `cleaning_mode` must be 1, 2, or 3
- `duration_minutes` = (end_time - start_time) in minutes

## Implementation Phases

### Phase 1: Backend Foundation (Database & Models)

#### 1.1 Database Migration
**File:** `backend/alembic/versions/XXXX_add_net_cleaning_tables.py`

Create migration for three new tables with proper relationships and constraints.

#### 1.2 SQLAlchemy Models
**File:** `backend/app/models.py`

Add three new model classes:
- `FarmSite` - with relationship to Organization
- `Net` - with relationship to FarmSite
- `NetCleaningRecord` - with relationships to Net, Machine, and User

#### 1.3 Pydantic Schemas
**File:** `backend/app/schemas/net_cleaning.py` (new file)

Create schemas for:
- `FarmSiteBase`, `FarmSiteCreate`, `FarmSiteUpdate`, `FarmSiteResponse`
- `NetBase`, `NetCreate`, `NetUpdate`, `NetResponse`
- `NetCleaningRecordBase`, `NetCleaningRecordCreate`, `NetCleaningRecordUpdate`, `NetCleaningRecordResponse`
- Include nested relationships in response schemas

### Phase 2: Backend API (CRUD & Endpoints)

#### 2.1 CRUD Operations
**Files:**
- `backend/app/crud/farm_sites.py` (new)
- `backend/app/crud/nets.py` (new)
- `backend/app/crud/net_cleaning_records.py` (new)

Implement standard CRUD operations with:
- Organization-scoped queries
- Filtering and pagination
- Soft delete support (active flag)
- Validation logic

#### 2.2 API Routers
**Files:**
- `backend/app/routers/farm_sites.py` (new)
- `backend/app/routers/nets.py` (new)
- `backend/app/routers/net_cleaning_records.py` (new)

**Endpoints:**

**Farm Sites:**
- `GET /farm-sites` - List all sites (org-scoped, paginated)
- `GET /farm-sites/{id}` - Get site details with nets
- `POST /farm-sites` - Create new site
- `PUT /farm-sites/{id}` - Update site
- `DELETE /farm-sites/{id}` - Soft delete site

**Nets:**
- `GET /nets` - List all nets (org-scoped, paginated)
- `GET /nets?farm_site_id={id}` - Filter by farm site
- `GET /nets/{id}` - Get net details with cleaning history
- `POST /nets` - Create new net
- `PUT /nets/{id}` - Update net
- `DELETE /nets/{id}` - Soft delete net

**Cleaning Records:**
- `GET /net-cleaning-records` - List all records (org-scoped, paginated)
- `GET /net-cleaning-records?net_id={id}` - Filter by net
- `GET /net-cleaning-records?start_date={date}&end_date={date}` - Date range filter
- `GET /net-cleaning-records/{id}` - Get record details
- `POST /net-cleaning-records` - Create new record
- `PUT /net-cleaning-records/{id}` - Update record
- `DELETE /net-cleaning-records/{id}` - Delete record

#### 2.3 Business Logic
- Validate cleaning mode (1, 2, or 3)
- Calculate duration automatically
- Validate depth values based on mode
- Ensure end_time > start_time
- Organization-scoped access control

### Phase 3: Frontend Services

#### 3.1 API Service Layer
**Files:**
- `frontend/src/services/farmSitesService.js` (new)
- `frontend/src/services/netsService.js` (new)
- `frontend/src/services/netCleaningRecordsService.js` (new)

Implement service functions for all API endpoints with proper error handling.

### Phase 4: Frontend Components

#### 4.1 Farm Sites Management
**File:** `frontend/src/pages/FarmSites.js` (new)

Features:
- List view with search and filters
- Create/Edit modal form
- View site details with nets list
- Delete confirmation
- Active/inactive toggle

**File:** `frontend/src/components/FarmSiteForm.js` (new)
- Form fields: name, location, description
- Validation
- Organization auto-assigned from context

#### 4.2 Nets Management
**File:** `frontend/src/pages/Nets.js` (new)

Features:
- List view grouped by farm site
- Filter by farm site dropdown
- Create/Edit modal form
- View net details with cleaning history
- Delete confirmation

**File:** `frontend/src/components/NetForm.js` (new)
- Form fields: name, farm site selector, dimensions, mesh size, material, notes
- Validation for numeric fields
- Optional fields clearly marked

#### 4.3 Cleaning Records
**File:** `frontend/src/pages/NetCleaningRecords.js` (new)

Features:
- List view with filters (date range, farm site, net, operator)
- Create/Edit modal form
- Calendar view option
- Export to CSV functionality
- Summary statistics (total cleanings, average duration)

**File:** `frontend/src/components/NetCleaningRecordForm.js` (new)
- Farm site selector (cascades to net selector)
- Net selector (filtered by farm site)
- Machine selector (optional, from existing machines)
- Operator name input
- Cleaning mode selector (1, 2, 3)
- Dynamic depth fields based on mode:
  - Mode 1: depth_1 only
  - Mode 2: depth_1, depth_2
  - Mode 3: depth_1, depth_2, depth_3
- Start time and end time pickers
- Duration auto-calculated and displayed
- Notes textarea
- Validation

**File:** `frontend/src/components/NetCleaningRecordDetails.js` (new)
- Display all record details
- Show related net and farm site info
- Show machine info if linked
- Edit and delete actions

#### 4.4 Dashboard Integration
**File:** `frontend/src/components/NetCleaningDashboard.js` (new)

Widgets:
- Recent cleaning activities
- Cleanings by farm site (chart)
- Cleanings by mode (chart)
- Average cleaning duration
- Most active operators
- Nets due for cleaning (based on last cleaning date)

### Phase 5: Navigation & Routing

#### 5.1 Update App Routing
**File:** `frontend/src/App.js`

Add routes:
```javascript
<Route path="/farm-sites" element={<FarmSites />} />
<Route path="/nets" element={<Nets />} />
<Route path="/net-cleaning-records" element={<NetCleaningRecords />} />
```

#### 5.2 Update Navigation Menu
**File:** `frontend/src/components/Layout.js`

Add new menu section "Net Cleaning" with:
- Farm Sites
- Nets
- Cleaning Records

### Phase 6: Localization

#### 6.1 Translation Keys
**File:** `add_net_cleaning_translations.py` (new)

Add translation keys for all languages:
- Farm sites labels and messages
- Nets labels and messages
- Cleaning records labels and messages
- Validation messages
- Success/error messages

Translation scopes:
- `net_cleaning.farm_sites.*`
- `net_cleaning.nets.*`
- `net_cleaning.cleaning_records.*`

### Phase 7: Permissions & Access Control

#### 7.1 Permission Rules
- **View:** All authenticated users in organization
- **Create/Edit Farm Sites:** Admin and Super Admin only
- **Create/Edit Nets:** Admin and Super Admin only
- **Create/Edit Cleaning Records:** All users (operators need to log their work)
- **Delete:** Admin and Super Admin only

#### 7.2 Update Permissions Utility
**File:** `frontend/src/utils/permissions.js`

Add permission checks for net cleaning features.

### Phase 8: Testing & Validation

#### 8.1 Backend Tests
**Files:**
- `backend/tests/test_farm_sites.py` (new)
- `backend/tests/test_nets.py` (new)
- `backend/tests/test_net_cleaning_records.py` (new)

Test:
- CRUD operations
- Validation logic
- Organization scoping
- Relationships
- Edge cases

#### 8.2 Frontend Tests
Test critical user flows:
- Creating farm site and nets
- Recording cleaning event
- Filtering and searching
- Form validation

#### 8.3 Integration Testing
**File:** `test_net_cleaning_workflow.py` (new)

End-to-end workflow:
1. Create farm site
2. Create nets in site
3. Record cleaning events
4. Query and filter records
5. Generate reports

### Phase 9: Documentation

#### 9.1 User Manual
**File:** `docs/NET_CLEANING_USER_GUIDE.md` (new)

Include:
- Feature overview
- How to set up farm sites and nets
- How to record cleaning events
- How to view cleaning history
- Best practices

#### 9.2 API Documentation
Update OpenAPI docs with new endpoints (auto-generated by FastAPI).

#### 9.3 Developer Documentation
**File:** `docs/NET_CLEANING_TECHNICAL_DOCS.md` (new)

Include:
- Data model relationships
- API endpoint details
- Frontend component architecture
- Extension points

## Database Relationships Diagram

```
organizations (existing)
    ↓ (1:many)
farm_sites
    ↓ (1:many)
nets
    ↓ (1:many)
net_cleaning_records
    ↓ (many:1)
machines (existing, optional)
users (existing)
```

## API Endpoint Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/farm-sites` | List farm sites |
| POST | `/farm-sites` | Create farm site |
| GET | `/farm-sites/{id}` | Get farm site details |
| PUT | `/farm-sites/{id}` | Update farm site |
| DELETE | `/farm-sites/{id}` | Delete farm site |
| GET | `/nets` | List nets |
| POST | `/nets` | Create net |
| GET | `/nets/{id}` | Get net details |
| PUT | `/nets/{id}` | Update net |
| DELETE | `/nets/{id}` | Delete net |
| GET | `/net-cleaning-records` | List cleaning records |
| POST | `/net-cleaning-records` | Create cleaning record |
| GET | `/net-cleaning-records/{id}` | Get record details |
| PUT | `/net-cleaning-records/{id}` | Update record |
| DELETE | `/net-cleaning-records/{id}` | Delete record |
| GET | `/net-cleaning-records/stats` | Get cleaning statistics |

## UI Component Hierarchy

```
FarmSites (Page)
├── FarmSitesList
├── FarmSiteForm (Modal)
└── FarmSiteDetails (Modal)
    └── NetsList (embedded)

Nets (Page)
├── NetsList
├── NetForm (Modal)
└── NetDetails (Modal)
    └── CleaningRecordsList (embedded)

NetCleaningRecords (Page)
├── CleaningRecordsFilters
├── CleaningRecordsList
├── CleaningRecordsCalendar (toggle view)
├── NetCleaningRecordForm (Modal)
└── NetCleaningRecordDetails (Modal)

Dashboard (existing, enhanced)
└── NetCleaningDashboard (new widget)
```

## Form Validation Rules

### Farm Site Form
- Name: Required, max 200 chars
- Location: Optional, max 500 chars
- Description: Optional, max 2000 chars

### Net Form
- Name: Required, max 200 chars
- Farm Site: Required (dropdown)
- Diameter: Optional, positive decimal
- Vertical Depth: Optional, positive decimal
- Cone Depth: Optional, positive decimal
- Mesh Size: Optional, max 50 chars
- Material: Optional, max 100 chars
- Notes: Optional, max 2000 chars

### Cleaning Record Form
- Net: Required (dropdown, filtered by farm site)
- Machine: Optional (dropdown)
- Operator Name: Required, max 200 chars
- Cleaning Mode: Required (1, 2, or 3)
- Depth 1: Required if mode >= 1, positive decimal
- Depth 2: Required if mode >= 2, positive decimal
- Depth 3: Required if mode = 3, positive decimal
- Start Time: Required, datetime
- End Time: Required, datetime, must be after start time
- Notes: Optional, max 2000 chars

## Estimated Effort

| Phase | Estimated Time |
|-------|----------------|
| Phase 1: Backend Foundation | 4-6 hours |
| Phase 2: Backend API | 6-8 hours |
| Phase 3: Frontend Services | 2-3 hours |
| Phase 4: Frontend Components | 12-16 hours |
| Phase 5: Navigation & Routing | 1-2 hours |
| Phase 6: Localization | 3-4 hours |
| Phase 7: Permissions | 2-3 hours |
| Phase 8: Testing | 6-8 hours |
| Phase 9: Documentation | 3-4 hours |
| **Total** | **39-54 hours** |

## Dependencies

- Existing authentication system
- Existing organization management
- Existing machine management (optional link)
- Localization system
- Permissions system

## Future Enhancements (Out of Scope)

- Photo attachments for cleaning records
- Maintenance scheduling based on cleaning frequency
- Mobile app for field data entry
- QR codes for nets
- Integration with machine sensors for automatic logging
- Predictive maintenance alerts
- Weather data integration
- Water quality tracking
- Net condition assessment scoring

## Success Criteria

- [ ] Users can create and manage farm sites
- [ ] Users can create and manage nets with specifications
- [ ] Users can record cleaning events with all required details
- [ ] Cleaning records are properly validated
- [ ] Users can filter and search cleaning history
- [ ] Dashboard shows cleaning statistics
- [ ] All features are localized in supported languages
- [ ] Permissions are properly enforced
- [ ] API endpoints are documented
- [ ] User manual is complete

## Deployment Checklist

- [ ] Run database migration
- [ ] Test on development environment
- [ ] Verify all translations
- [ ] Test permissions for different user roles
- [ ] Review API documentation
- [ ] Deploy to production
- [ ] Train users on new features
- [ ] Monitor for issues

---

**Created:** January 18, 2026
**Branch:** `feature/net-cleaning-records`
**Status:** Planning Phase
