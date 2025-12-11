# ABParts Business Model Realignment Design

## Overview

This design document provides a comprehensive analysis of the required changes to align the ABParts system with the detailed business requirements. The approach prioritizes minimal-impact extensions to the existing architecture while ensuring full business requirement compliance.

## Architecture

The current ABParts system follows a three-tier architecture:
- **Frontend**: React SPA with role-based UI components
- **Backend**: FastAPI with SQLAlchemy ORM and PostgreSQL
- **Database**: PostgreSQL with enum-based business rules

The realignment will extend this architecture with:
- Enhanced organizational hierarchy management
- Country-based localization support
- Multilingual data handling
- Advanced role-based access control
- Service management framework (future)

## Components and Interfaces

### Database Model Extensions

#### 1. Organization Model Enhancements
**Current State**: Basic organization types and hierarchy support exists
**Required Changes**:
- Add `country` field with enum constraint ['GR', 'KSA', 'ES', 'CY', 'OM']
- Enhance supplier-customer relationship validation
- Add default organization seeding for Oraseas EE and BossAqua

#### 2. Parts Model Enhancements  
**Current State**: Basic part information with type classification
**Required Changes**:
- Extend `name` field to support multilingual compound strings
- Add `manufacturer` field (separate from is_proprietary flag)
- Add `part_code` field for AutoBoss-specific codes
- Add `serial_number` field (optional)
- Extend `image_urls` array to support up to 4 images
- Ensure `part_type` enum supports both CONSUMABLE and BULK_MATERIAL

#### 3. Machine Model Enhancements
**Current State**: Basic machine registration with customer relationship
**Required Changes**:
- Add `model_type` enum with ['V3.1B', 'V4.0'] values
- Enhance `name` field for customer customization
- Add machine hours tracking relationship
- Add service history relationship (future enhancement)

#### 4. New Models Required

##### MachineHours Model
```
- id: UUID (PK)
- machine_id: UUID (FK to machines)
- recorded_by_user_id: UUID (FK to users)  
- hours_value: DECIMAL
- recorded_date: DATETIME
- notes: TEXT (optional)
```

##### ServiceRecommendation Model (Future)
```
- id: UUID (PK)
- service_type: ENUM ['50h', '250h', '500h', '750h', 'custom']
- checklist_items: JSONB
- required_parts: JSONB
- created_by_user_id: UUID (FK to users)
```

### Backend API Extensions

#### 1. Organization Management API
**New Endpoints**:
- `GET /organizations/countries` - List supported countries
- `POST /organizations/initialize-defaults` - Seed default organizations
- `GET /organizations/{id}/suppliers` - Get organization-specific suppliers
- `PUT /organizations/{id}/activate` - Toggle supplier active status

#### 2. Parts Management API  
**Enhanced Endpoints**:
- `GET /parts` - Add multilingual name search
- `POST /parts` - Enhanced validation for new fields
- `PUT /parts/{id}` - Support multilingual updates

#### 3. Machine Management API
**New Endpoints**:
- `POST /machines/{id}/hours` - Record machine hours
- `GET /machines/{id}/hours` - Get machine hours history
- `GET /machines/{id}/service-recommendations` - Get service suggestions

#### 4. Transaction API Extensions
**Enhanced Endpoints**:
- `POST /transactions/machine-sale` - Record machine ownership transfer
- `POST /transactions/part-order` - Two-phase order recording
- `POST /transactions/part-usage` - Machine part consumption

### Role-Based Access Control Enhancements

#### Permission Matrix Extensions
```
Resource Type: Organizations
- superadmin: CRUD all organizations
- admin: READ own org, UPDATE own org, CREATE suppliers under own org
- user: READ own org

Resource Type: Parts  
- superadmin: CRUD all parts
- admin: READ all parts
- user: READ all parts

Resource Type: Machines
- superadmin: CRUD all machines, transfer ownership
- admin: READ own org machines, UPDATE machine names
- user: READ own org machines, record hours/usage

Resource Type: Warehouses
- superadmin: CRUD all warehouses  
- admin: CRUD own org warehouses
- user: READ own org warehouses, perform transactions
```

#### Organizational Data Isolation
- Implement middleware for automatic organization filtering
- Add organization_id validation to all data access operations
- Create organization-scoped query helpers
- Implement supplier visibility restrictions

## Data Models

### Enhanced Organization Schema
```sql
ALTER TABLE organizations 
ADD COLUMN country VARCHAR(3) CHECK (country IN ('GR', 'KSA', 'ES', 'CY', 'OM'));

-- Add constraint for supplier parent requirement
ALTER TABLE organizations 
ADD CONSTRAINT supplier_parent_required 
CHECK (organization_type != 'supplier' OR parent_organization_id IS NOT NULL);
```

### Enhanced Parts Schema  
```sql
ALTER TABLE parts
ADD COLUMN manufacturer VARCHAR(255),
ADD COLUMN part_code VARCHAR(100),
ADD COLUMN serial_number VARCHAR(255);

-- Update name field to support longer multilingual strings
ALTER TABLE parts ALTER COLUMN name TYPE TEXT;
```

### New MachineHours Schema
```sql
CREATE TABLE machine_hours (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    machine_id UUID NOT NULL REFERENCES machines(id),
    recorded_by_user_id UUID NOT NULL REFERENCES users(id),
    hours_value DECIMAL(10,2) NOT NULL,
    recorded_date TIMESTAMP WITH TIME ZONE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Error Handling

### Business Rule Validation
- Country selection validation with user-friendly error messages
- Organizational hierarchy validation (suppliers must have parents)
- Machine model validation against supported types
- Multilingual name format validation
- Inventory transaction validation against organizational boundaries

### Permission-Based Error Handling
- Clear error messages for organizational access violations
- Role-specific error messages for unauthorized operations
- Graceful handling of cross-organizational data access attempts

## Testing Strategy

### Unit Testing Extensions
- Organization country validation tests
- Multilingual parts name handling tests  
- Machine hours recording validation tests
- Role-based permission enforcement tests
- Organizational data isolation tests

### Integration Testing
- End-to-end organization creation with default warehouse
- Machine sale transaction flow testing
- Part order two-phase recording testing
- Cross-organizational access prevention testing

### User Acceptance Testing
- Role-based UI visibility testing
- Multilingual data display testing
- Dashboard functionality across different user types
- Mobile responsiveness for field operations
##
 Frontend UI and User Experience Design

### Dashboard Layout Redesign

#### Three-Column Dashboard Structure
The main dashboard will feature three primary areas as specified:

**1. Entities Column**
- Organizations box: Shows organization type and active suppliers count
- Users box: Displays user count and pending invitations  
- Warehouses box: Shows total parts in stock across all warehouses
- Machines box: Displays machine count and service alerts
- Parts box: Shows total parts catalog and low stock alerts

**2. Actions Column**  
- Order Parts: Quick access to part ordering workflow
- Use Parts: Machine part consumption recording
- Record Hours: Machine hours logging
- Adjust Inventory: Stock level adjustments
- Register Machine: New machine registration (superadmin only)

**3. Reports Column**
- Inventory Reports: Current stock levels and movements
- Machine Reports: Hours tracking and service schedules  
- Transaction Reports: Order history and usage patterns
- Organization Reports: Multi-org analytics (superadmin only)

#### Role-Based UI Customization

**Superadmin Dashboard**
- Full access to all three columns
- Additional admin tools section
- Cross-organizational analytics
- System configuration options

**Admin Dashboard**  
- Organization-scoped entity management
- Supplier and warehouse creation tools
- User management within organization
- Organization-specific reports

**User Dashboard**
- Read-only entities with transaction capabilities
- Simplified action buttons for common tasks
- Personal transaction history
- Machine-specific quick actions

### Navigation and User Flow Enhancements

#### Organizational Context Switching
- Header displays current organization context
- Superadmin gets organization selector dropdown
- Clear visual indicators for organizational boundaries
- Breadcrumb navigation showing organizational hierarchy

#### Multilingual Support Implementation
- Language selector in user profile
- Part names display in preferred language with fallback
- Country-specific date/number formatting
- RTL support for Arabic regions (KSA, OM)

#### Mobile-Responsive Design
- Touch-friendly dashboard boxes for field operations
- Simplified mobile navigation for warehouse operations
- Offline capability for machine hours recording
- Camera integration for part photo capture

### Component Architecture Changes

#### Enhanced Organization Components
- OrganizationSelector: Dropdown with country flags
- SupplierManager: Organization-scoped supplier CRUD
- OrganizationHierarchy: Visual tree representation

#### New Machine Management Components  
- MachineHoursRecorder: Simple hours input with validation
- MachineServiceAlert: Service due notifications
- MachineTransferWizard: Ownership transfer workflow

#### Enhanced Parts Components
- MultilingualPartName: Compound string display/edit
- PartPhotoGallery: Up to 4 image management
- PartCategoryBadge: Visual consumable/bulk indicators

#### New Transaction Components
- TwoPhaseOrderWizard: Request → Receipt workflow
- PartUsageRecorder: Machine part consumption
- InventoryTransactionLog: Audit trail display

### User Experience Improvements

#### Onboarding and Training
- Role-specific guided tours
- Interactive tutorials for complex workflows
- Contextual help system
- Video tutorials for mobile operations

#### Performance Optimizations
- Lazy loading for large parts catalogs
- Infinite scroll for transaction histories
- Cached organization data for faster switching
- Optimistic UI updates for common operations

#### Accessibility Enhancements
- WCAG 2.1 AA compliance
- Keyboard navigation for all functions
- Screen reader support for complex data tables
- High contrast mode for industrial environments

## System Settings and Configuration

### Administrative Configuration Panel

#### Organization Management Settings
- Default country selection for new organizations
- Automatic warehouse creation rules
- Supplier approval workflows
- Organization deactivation policies

#### Parts Management Settings  
- Multilingual name format templates
- Photo upload size and format restrictions
- Part categorization rules
- Inventory threshold configurations

#### User Management Settings
- Role assignment rules and restrictions
- Password policy configuration
- Session timeout settings
- Multi-factor authentication options

#### Localization Settings
- Supported language configurations
- Regional format preferences
- Currency display options
- Time zone management

### Workflow Configuration

#### Machine Service Workflows
- Service interval definitions (50h, 250h, etc.)
- Checklist template management
- Required parts specifications
- Service notification rules

#### Inventory Management Workflows
- Automatic reorder point calculations
- Stock adjustment approval processes
- Inter-warehouse transfer rules
- Inventory audit scheduling

#### Order Management Workflows
- Two-phase order approval processes
- Supplier selection rules
- Delivery tracking integration
- Order fulfillment notifications

## Migration and Deployment Strategy

### Database Migration Plan
1. Add new columns to existing tables (non-breaking)
2. Create new tables for machine hours and service management
3. Populate default organizations (Oraseas EE, BossAqua)
4. Migrate existing data to new schema constraints
5. Add new indexes for performance optimization

### API Versioning Strategy
- Maintain backward compatibility for existing endpoints
- Add new endpoints with /v2/ prefix where needed
- Deprecation notices for endpoints requiring changes
- Gradual migration timeline for breaking changes

### Frontend Deployment Strategy
- Feature flags for new dashboard layout
- Progressive rollout by organization type
- A/B testing for UI improvements
- Rollback capabilities for critical issues

### Training and Documentation
- Updated user manuals for each role type
- API documentation updates
- Video tutorials for new workflows
- Change management communication plan