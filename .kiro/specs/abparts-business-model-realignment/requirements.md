# ABParts Business Model Realignment Requirements

## Introduction

This document outlines the requirements for realigning the ABParts system to match the detailed business model specifications. The goal is to implement minimal-impact changes to support the new business requirements while maintaining compatibility with the existing architecture.

## Requirements

### Requirement 1: Enhanced Organization Management

**User Story:** As a system administrator, I want to manage organizations with proper country support and hierarchical relationships, so that the system accurately reflects the global business structure.

#### Acceptance Criteria

1. WHEN an organization is created THEN the system SHALL support country selection from ['GR', 'KSA', 'ES', 'CY', 'OM']
2. WHEN Oraseas EE and BossAqua organizations are initialized THEN they SHALL be created as default organizations in the database
3. WHEN a customer organization is created THEN the system SHALL automatically create a default warehouse with the same name
4. WHEN a supplier organization is created THEN it SHALL be linked to either a customer organization or Oraseas EE as parent
5. WHEN suppliers are listed in dropdowns THEN only active suppliers SHALL be displayed
6. WHEN an admin views suppliers THEN they SHALL only see suppliers belonging to their organization

### Requirement 2: Role-Based Access Control Enhancement

**User Story:** As a user with specific organizational roles, I want appropriate access permissions, so that I can perform my job functions while maintaining data security.

#### Acceptance Criteria

1. WHEN a superadmin accesses the system THEN they SHALL have full access to all organizations and data
2. WHEN an admin accesses the system THEN they SHALL only access data within their own organization
3. WHEN a regular user accesses the system THEN they SHALL have read access to parts and limited transaction capabilities
4. WHEN a customer organization is created THEN the superadmin SHALL create at least one admin user for that organization
5. WHEN an admin creates suppliers THEN those suppliers SHALL only be visible within their organization
6. WHEN users perform transactions THEN they SHALL only access machines, warehouses, and inventories from their own organization

### Requirement 3: Enhanced Parts Management

**User Story:** As a parts manager, I want comprehensive part information including multilingual names and proper categorization, so that parts can be accurately identified and managed across different regions.

#### Acceptance Criteria

1. WHEN a part is created THEN it SHALL include multilingual name support (compound string format)
2. WHEN a part is categorized THEN it SHALL be marked as either consumable or bulk material
3. WHEN a part is classified THEN it SHALL be flagged as proprietary (BossAqua) or general (other suppliers)
4. WHEN part details are stored THEN they SHALL include manufacturer, part code, serial number (if available), and up to 4 photos
5. WHEN parts are viewed THEN all user types SHALL be able to see all parts
6. WHEN parts are managed THEN only superadmin SHALL be able to create/edit/inactivate parts

### Requirement 4: Machine Registration and Management

**User Story:** As a machine administrator, I want to register and manage AutoBoss machines with proper ownership tracking, so that machine sales and service history can be maintained.

#### Acceptance Criteria

1. WHEN a machine is registered THEN it SHALL support V3.1B and V4.0 models
2. WHEN a machine is created THEN it SHALL have a unique serial number and customizable name
3. WHEN a machine is sold THEN the ownership SHALL transfer from Oraseas EE to the customer organization
4. WHEN machine registration occurs THEN only superadmin SHALL be able to create/edit/inactivate machines
5. WHEN machine names are updated THEN admins SHALL be able to edit names within their own organization

### Requirement 5: Warehouse and Inventory Management

**User Story:** As an inventory manager, I want warehouse-based inventory tracking with proper transaction recording, so that stock levels and movements can be accurately monitored.

#### Acceptance Criteria

1. WHEN organizations are created THEN they SHALL be able to have multiple warehouses (except suppliers)
2. WHEN inventory is managed THEN it SHALL track both consumable parts (discrete quantities) and bulk materials (decimal quantities)
3. WHEN parts are added to warehouses THEN inventory levels SHALL increase accordingly
4. WHEN parts are sold or consumed THEN inventory levels SHALL decrease accordingly
5. WHEN default warehouses are needed THEN Oraseas EE and BossAqua warehouses SHALL be pre-created
6. WHEN customer organizations are created THEN a default warehouse SHALL be automatically created

### Requirement 6: Transaction and Event Management

**User Story:** As a business user, I want to record various business transactions including sales, orders, and part usage, so that complete audit trails and business intelligence can be maintained.

#### Acceptance Criteria

1. WHEN machine sales occur THEN they SHALL be recorded as ownership transfers from Oraseas EE to customers
2. WHEN part orders are placed THEN they SHALL support two-phase recording (request and receipt)
3. WHEN parts are used in machines THEN the transaction SHALL transfer parts from warehouse to machine
4. WHEN part orders are from Oraseas EE THEN they SHALL represent transfers between Oraseas EE and customer warehouses
5. WHEN machine hours are recorded THEN they SHALL store user, date, and value for service timing calculations

### Requirement 7: Service Management (Future Enhancement)

**User Story:** As a service technician, I want to manage machine services with predefined checklists and part usage tracking, so that maintenance can be properly scheduled and documented.

#### Acceptance Criteria

1. WHEN service schedules are defined THEN they SHALL be based on machine hours (50h, 250h, 500h, 750h, etc.)
2. WHEN services are started THEN the system SHALL propose recommended service checklists
3. WHEN service parts are used THEN they SHALL be deducted from warehouse inventory
4. WHEN non-standard parts are serviced THEN users SHALL be able to record them
5. WHEN service recommendations are managed THEN superadmin SHALL define the predefined service lists

### Requirement 8: User Interface Dashboard Design

**User Story:** As a system user, I want an intuitive dashboard with three main areas (Entities, Actions, Reports), so that I can efficiently navigate and perform my daily tasks.

#### Acceptance Criteria

1. WHEN users log in THEN they SHALL see three main areas: Entities, Actions, and Reports
2. WHEN the dashboard displays THEN it SHALL show customized boxes based on user role and organization
3. WHEN entity boxes are clicked THEN they SHALL navigate to detailed views with available actions
4. WHEN warehouse boxes are displayed THEN they SHALL show total parts in stock summary
5. WHEN machine boxes are displayed THEN they SHALL show machine count and latest recorded hours
6. WHEN quick actions are available THEN users SHALL be able to perform common tasks directly from summary views

### Requirement 9: Multilingual and Localization Support

**User Story:** As a global user, I want the system to support multiple languages and regional settings, so that I can work effectively in my local language and format preferences.

#### Acceptance Criteria

1. WHEN part names are stored THEN they SHALL support compound multilingual strings
2. WHEN countries are selected THEN they SHALL be limited to supported regions ['GR', 'KSA', 'ES', 'CY', 'OM']
3. WHEN UI elements are displayed THEN they SHALL adapt to user's regional preferences
4. WHEN data is formatted THEN it SHALL follow regional conventions for dates, numbers, and currencies

### Requirement 10: Data Security and Organizational Isolation

**User Story:** As a security administrator, I want strict organizational data isolation with proper access controls, so that sensitive business information remains protected.

#### Acceptance Criteria

1. WHEN users access data THEN they SHALL only see information from their own organization (except superadmin)
2. WHEN suppliers are managed THEN they SHALL only be visible to their parent organization
3. WHEN transactions are performed THEN they SHALL be validated against organizational permissions
4. WHEN audit trails are maintained THEN they SHALL track all data access and modifications
5. WHEN BossAqua data is accessed THEN only superadmin SHALL have interaction capabilities initially