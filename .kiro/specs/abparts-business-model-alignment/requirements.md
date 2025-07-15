# Requirements Document: ABParts Business Model Alignment

## Introduction

This document outlines the requirements to align the ABParts application with the actual business model of Oraseas EE's AutoBoss parts distribution system. The current implementation has some architectural misalignments that need to be corrected to properly represent the business relationships and workflows.

## Business Context Summary

ABParts manages the AutoBoss net cleaner parts ecosystem with these key players:
- **Oraseas EE**: App owner and primary distributor
- **BossAqua**: Manufacturer of AutoBoss machines and proprietary parts
- **Customers**: Organizations that buy AutoBoss machines and need parts
- **Suppliers**: Third-party suppliers serving customers or Oraseas EE

The system tracks parts flow from creation (manufacturer/suppliers) → distribution (Oraseas EE) → customers → consumption (in machines).

## Scale Requirements

The application must be designed to support:
- **Maximum 100 customer organizations**
- **Maximum 200 total users** across all organizations
- **Maximum 200 different parts** in the catalog
- **Maximum 150 AutoBoss machines** deployed across customers
- **Maximum 150 warehouses** across all organizations
- **Maximum 50 transactions per year per machine** (7,500 total transactions/year)

These numbers inform database design, indexing strategy, caching requirements, and performance optimization decisions.

## Requirements

### Requirement 1: Organization Type Management

**User Story:** As a super admin, I want to properly categorize organizations by their business role, so that the system enforces correct business relationships and permissions.

#### Acceptance Criteria

1. WHEN creating an organization THEN the system SHALL require selection of organization type from: "Oraseas EE", "BossAqua", "Customer", "Supplier"
2. WHEN an organization type is "Oraseas EE" THEN there SHALL be only one such organization in the system
3. WHEN an organization type is "BossAqua" THEN there SHALL be only one such organization in the system
4. IF organization type is "Supplier" THEN the system SHALL require association with either Oraseas EE or a Customer organization
5. WHEN displaying organizations THEN the system SHALL clearly indicate the organization type and relationships

### Requirement 2: Comprehensive User Management System

**User Story:** As a super admin, I want to manage the complete user lifecycle with proper role-based access control, so that the system maintains security while enabling efficient user administration.

#### Acceptance Criteria

1. WHEN creating users THEN the system SHALL support three role types: "user", "admin", "super_admin"
2. WHEN a user role is "super_admin" THEN they SHALL be associated with Oraseas EE organization only
3. WHEN a user role is "super_admin" THEN they SHALL have access to all organizations' data
4. WHEN a user role is "admin" or "user" THEN they SHALL only access data from their own organization
5. WHEN an organization is created THEN it SHALL require at least one admin user
6. IF a user role is "user" THEN they SHALL be able to: order parts, receive parts, check inventories, record part usage
7. IF a user role is "admin" THEN they SHALL be able to: perform all user actions, create/edit warehouses, manage suppliers, adjust inventories, register machines

### Requirement 2A: User Invitation and Onboarding System

**User Story:** As an admin, I want to invite new users to join my organization, so that I can efficiently onboard team members without sharing passwords.

#### Acceptance Criteria

1. WHEN inviting a user THEN the system SHALL send an email invitation with a secure registration link
2. WHEN a user receives an invitation THEN they SHALL be able to set their own password and complete profile
3. WHEN an invitation is sent THEN it SHALL expire after 7 days for security
4. WHEN an invitation expires THEN admins SHALL be able to resend invitations
5. WHEN a user accepts an invitation THEN their account SHALL be automatically activated
6. IF an invitation is for a super_admin role THEN only existing super_admins SHALL be able to send it

### Requirement 2B: User Profile and Self-Service Management

**User Story:** As a user, I want to manage my own profile and account settings, so that I can keep my information current and secure.

#### Acceptance Criteria

1. WHEN accessing my profile THEN I SHALL be able to update my name, email, and contact information
2. WHEN changing my password THEN I SHALL be required to provide my current password
3. WHEN updating my email THEN I SHALL receive a verification email to confirm the change
4. WHEN viewing my profile THEN I SHALL see my role, organization, and account status
5. WHEN I am inactive THEN I SHALL not be able to log in or access the system
6. IF I forget my password THEN I SHALL be able to request a password reset via email

### Requirement 2C: Advanced User Administration

**User Story:** As an admin, I want comprehensive user management capabilities, so that I can effectively manage my organization's users.

#### Acceptance Criteria

1. WHEN viewing users THEN I SHALL see users from my organization only (except super_admins who see all)
2. WHEN searching users THEN I SHALL be able to filter by role, status, and search by name/email
3. WHEN deactivating a user THEN their active sessions SHALL be terminated immediately
4. WHEN reactivating a user THEN they SHALL receive a notification email
5. WHEN deleting a user THEN the system SHALL prevent deletion if they have associated transactions
6. IF a user has been inactive for 90 days THEN the system SHALL flag them for review
7. WHEN managing users THEN I SHALL see audit logs of user management actions

### Requirement 2D: Session and Security Management

**User Story:** As a system administrator, I want robust session and security management, so that user access is properly controlled and monitored.

#### Acceptance Criteria

1. WHEN a user logs in THEN the system SHALL create a session with 8-hour expiration
2. WHEN a session expires THEN the user SHALL be automatically logged out
3. WHEN detecting suspicious login activity THEN the system SHALL require additional verification
4. WHEN a user fails login 5 times THEN their account SHALL be temporarily locked for 15 minutes
5. WHEN a user changes their password THEN all other sessions SHALL be terminated
6. IF a user is deactivated THEN all their active sessions SHALL be immediately terminated
7. WHEN viewing security logs THEN admins SHALL see login attempts, session activity, and security events

### Requirement 3: Warehouse Management System

**User Story:** As an admin, I want to manage multiple warehouses for my organization, so that I can track inventory across different physical locations.

#### Acceptance Criteria

1. WHEN managing warehouses THEN all organization types except suppliers SHALL be able to have multiple warehouses
2. WHEN creating a warehouse THEN it SHALL be associated with exactly one organization
3. WHEN viewing warehouses THEN users SHALL only see warehouses from their own organization (except super_admins)
4. WHEN a part is added to a warehouse THEN the inventory for that part in that warehouse SHALL increase
5. WHEN a part is sold or consumed from a warehouse THEN the inventory for that part in that warehouse SHALL decrease

### Requirement 4: Enhanced Parts Classification

**User Story:** As a super admin, I want to properly classify parts by type and origin, so that the system handles different part behaviors correctly.

#### Acceptance Criteria

1. WHEN creating parts THEN the system SHALL support two part types: "consumable" and "bulk_material"
2. WHEN a part type is "consumable" THEN inventory SHALL be tracked in whole units
3. WHEN a part type is "bulk_material" THEN inventory SHALL support decimal quantities (e.g., 6.7 liters)
4. WHEN creating parts THEN the system SHALL indicate if parts are "proprietary" (from BossAqua) or "general" (from other suppliers)
5. WHEN displaying parts THEN the system SHALL show part type, origin, and current inventory across all warehouses

### Requirement 5: Machine Registration and Management

**User Story:** As a super admin, I want to register machine sales to customers, so that the system tracks which machines are deployed where.

#### Acceptance Criteria

1. WHEN registering a new machine THEN only super_admin users SHALL be able to perform this action
2. WHEN creating a machine THEN it SHALL be assigned to a customer organization
3. WHEN creating a machine THEN it SHALL have a unique serial number across all machines
4. WHEN creating a machine THEN it SHALL specify the model type (V3.1B or V4.0)
5. WHEN a machine is registered THEN it represents a sale from Oraseas EE to the customer

### Requirement 6: Part Transaction Workflow - Machine Sales

**User Story:** As a super admin, I want to record machine sales to customers, so that the system tracks machine deployment and ownership.

#### Acceptance Criteria

1. WHEN recording a machine sale THEN the system SHALL create a new machine record associated with the customer
2. WHEN a machine sale is recorded THEN the system SHALL log the transaction with sale date and customer details
3. WHEN viewing machine sales THEN super_admins SHALL see all sales across all customers
4. WHEN viewing machines THEN customer users SHALL only see machines owned by their organization

### Requirement 7: Part Transaction Workflow - Part Orders and Fulfillment

**User Story:** As a customer user/admin, I want to order parts from Oraseas EE or my suppliers, so that I can maintain my AutoBoss machines.

#### Acceptance Criteria

1. WHEN ordering parts THEN customer users SHALL be able to create part requests specifying supplier (Oraseas EE or own suppliers)
2. WHEN a part request is created THEN it SHALL have status "Requested"
3. WHEN parts are received THEN the user SHALL update the request with arrival date and change status to "Received"
4. IF the supplier is Oraseas EE THEN the transaction SHALL represent a transfer from Oraseas EE warehouse to customer warehouse
5. WHEN parts are received THEN the destination warehouse inventory SHALL increase by the received quantity
6. IF the supplier is Oraseas EE THEN the Oraseas EE warehouse inventory SHALL decrease by the transferred quantity

### Requirement 8: Part Transaction Workflow - Part Usage Tracking

**User Story:** As a customer user/admin, I want to record part usage in machines, so that the system tracks maintenance history and inventory consumption.

#### Acceptance Criteria

1. WHEN recording part usage THEN users SHALL specify the machine, part, quantity used, and usage date
2. WHEN part usage is recorded THEN the warehouse inventory SHALL decrease by the used quantity
3. WHEN part usage is recorded THEN the system SHALL create a usage history record linked to the specific machine
4. IF the part type is "bulk_material" THEN the system SHALL accept decimal quantities for usage
5. WHEN viewing part usage THEN users SHALL see usage history for their organization's machines only

### Requirement 9: Inventory Tracking and Reporting

**User Story:** As an admin, I want to view accurate inventory reports, so that I can make informed decisions about stock levels and reordering.

#### Acceptance Criteria

1. WHEN viewing inventory THEN the system SHALL show current stock as balance of all ins and outs for each part in each warehouse
2. WHEN BossAqua adds parts THEN it SHALL be recorded as inventory adjustment (creation)
3. WHEN non-Oraseas suppliers supply parts THEN it SHALL be recorded as inventory adjustment (creation)
4. WHEN parts are sold between organizations THEN it SHALL be recorded as inventory transfer
5. WHEN parts are consumed in machines THEN it SHALL be recorded as inventory consumption
6. WHEN generating inventory reports THEN users SHALL only see inventory for their organization's warehouses

### Requirement 10: Data Access and Security Model

**User Story:** As a system administrator, I want to ensure data access follows business hierarchy, so that sensitive business information is properly protected.

#### Acceptance Criteria

1. WHEN super_admin users access data THEN they SHALL see all organizations, warehouses, machines, and transactions
2. WHEN admin/user roles access data THEN they SHALL only see data from their own organization
3. WHEN customers view suppliers THEN they SHALL only see suppliers associated with their organization or Oraseas EE
4. WHEN viewing transactions THEN users SHALL only see transactions involving their organization
5. WHEN BossAqua users access the system THEN they SHALL manage their inventory and view transactions with Oraseas EE only

## Data Model Implications

### Required Model Changes

1. **Organizations Table**: Add `organization_type` enum field, add `parent_organization_id` for supplier relationships
2. **Users Table**: Update role enum to `user`, `admin`, `super_admin`
3. **Warehouses Table**: New entity to manage multiple warehouses per organization
4. **Parts Table**: Add `part_type` enum (`consumable`, `bulk_material`), enhance `is_proprietary` logic
5. **Inventory Table**: Link to warehouse instead of organization directly, support decimal quantities
6. **Machines Table**: Add proper customer relationship tracking
7. **Transactions Table**: New entity to track all part movements (creation, transfer, consumption)

### Business Rule Enforcement

1. Singleton constraints for Oraseas EE and BossAqua organizations
2. Cascade permissions based on user roles and organization hierarchy
3. Inventory balance calculations based on transaction history
4. Supplier-organization relationship validation
5. Machine ownership and access control validation

This requirements document provides the foundation for aligning the ABParts system with the actual business model and ensuring proper data relationships and access control.