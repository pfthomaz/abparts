# Requirements Document

## Introduction

The frontend Organizations page is failing to load the hierarchy view because it's calling a `/organizations/hierarchy` API endpoint that doesn't exist in the backend. The frontend expects to receive a complete organization hierarchy structure with nested children, but the current backend only provides individual organization hierarchy queries and root organization queries. This feature will implement the missing API endpoint to provide the complete organization hierarchy data structure that the frontend requires.

## Requirements

### Requirement 1

**User Story:** As a user viewing the Organizations page, I want to see organizations displayed in a hierarchical tree structure, so that I can understand the parent-child relationships between organizations.

#### Acceptance Criteria

1. WHEN a user switches to hierarchy view THEN the system SHALL fetch the complete organization hierarchy from the `/organizations/hierarchy` endpoint
2. WHEN the hierarchy endpoint is called THEN the system SHALL return an array of root organizations with nested children
3. WHEN the hierarchy data is received THEN each organization node SHALL include all organization properties plus a `children` array
4. WHEN an organization has child organizations THEN the `children` array SHALL contain the complete child organization data with their own nested children

### Requirement 2

**User Story:** As a developer integrating with the organization hierarchy API, I want the endpoint to respect user permissions and organization scoping, so that users only see organizations they have access to.

#### Acceptance Criteria

1. WHEN a user calls the hierarchy endpoint THEN the system SHALL apply organization-scoped filtering based on the user's permissions
2. WHEN a user has limited organization access THEN the hierarchy SHALL only include organizations the user can view
3. WHEN a super admin calls the endpoint THEN the system SHALL return the complete hierarchy of all organizations
4. WHEN a regular user calls the endpoint THEN the system SHALL return only their organization and its children/parents as appropriate

### Requirement 3

**User Story:** As a user managing organizations, I want to optionally include inactive organizations in the hierarchy view, so that I can see the complete organizational structure including deactivated entities.

#### Acceptance Criteria

1. WHEN the hierarchy endpoint is called without parameters THEN the system SHALL return only active organizations by default
2. WHEN the hierarchy endpoint is called with `include_inactive=true` THEN the system SHALL include both active and inactive organizations
3. WHEN inactive organizations are included THEN they SHALL be clearly marked with their `is_active` status
4. WHEN building the hierarchy THEN the system SHALL maintain parent-child relationships regardless of active status

### Requirement 4

**User Story:** As a system administrator, I want the hierarchy endpoint to handle errors gracefully and provide meaningful error messages, so that I can troubleshoot issues effectively.

#### Acceptance Criteria

1. WHEN the hierarchy endpoint encounters a database error THEN the system SHALL return a 500 status with a descriptive error message
2. WHEN the user lacks permission to view organizations THEN the system SHALL return a 403 status with an appropriate error message
3. WHEN the hierarchy endpoint is called with invalid parameters THEN the system SHALL return a 422 status with validation error details
4. WHEN the hierarchy is empty or no organizations exist THEN the system SHALL return an empty array with 200 status