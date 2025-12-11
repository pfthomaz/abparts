# Requirements Document

## Introduction

The organization creation form in the ABParts application is currently failing due to a critical backend/frontend misalignment. The frontend is attempting to call `/organizations/potential-parents` and `/organizations/validate` endpoints that don't exist in the backend, causing the form to fail when users try to create new organizations. This represents a broader misalignment between the frontend expectations and backend implementation that must be addressed without breaking existing functionality.

## Requirements

### Requirement 1

**User Story:** As a super admin, I want to create new organizations through the web interface, so that I can manage the organization hierarchy effectively.

#### Acceptance Criteria

1. WHEN I click "Add Organization" THEN the system SHALL display a functional organization creation form
2. WHEN I select "Supplier" as organization type THEN the system SHALL load and display available parent organizations
3. WHEN I submit valid organization data THEN the system SHALL create the organization successfully
4. WHEN I submit invalid organization data THEN the system SHALL display clear validation error messages

### Requirement 2

**User Story:** As a super admin creating a supplier organization, I want to see available parent organizations in a dropdown, so that I can properly establish the organization hierarchy.

#### Acceptance Criteria

1. WHEN I select "Supplier" organization type THEN the system SHALL call the potential parents API endpoint
2. WHEN the potential parents API is called THEN the system SHALL return organizations that can be parents for suppliers
3. WHEN potential parents are loaded THEN the system SHALL populate the parent organization dropdown
4. WHEN no potential parents exist THEN the system SHALL display an appropriate message

### Requirement 3

**User Story:** As a super admin, I want real-time validation feedback when creating organizations, so that I can fix errors before submitting the form.

#### Acceptance Criteria

1. WHEN I enter organization data THEN the system SHALL validate the data in real-time
2. WHEN validation fails THEN the system SHALL display specific error messages
3. WHEN I attempt to create a singleton organization that already exists THEN the system SHALL prevent creation with a clear error message
4. WHEN I attempt to create a supplier without a parent THEN the system SHALL prevent creation with a clear error message

### Requirement 4

**User Story:** As a developer, I want to ensure backend/frontend alignment, so that no existing functionality is broken during the fix.

#### Acceptance Criteria

1. WHEN implementing missing endpoints THEN the system SHALL maintain all existing API functionality
2. WHEN adding new endpoints THEN the system SHALL follow existing patterns and conventions
3. WHEN testing the fix THEN the system SHALL verify that existing organization operations still work
4. WHEN reviewing the codebase THEN the system SHALL identify and document any other potential misalignments