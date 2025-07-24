# Requirements Document

## Introduction

The user reactivation functionality in ABParts currently has a bug where reactivating a user only updates the `is_active` field but not the `user_status` field, creating an inconsistent state. This leads to "Failed to reactivate user" errors and users appearing as inactive even after reactivation attempts. The system needs to properly synchronize both status fields during reactivation operations.

## Requirements

### Requirement 1

**User Story:** As an admin, I want to successfully reactivate inactive users so that they can regain access to the system

#### Acceptance Criteria

1. WHEN an admin clicks the "Reactivate" button for an inactive user THEN the system SHALL update both `is_active=True` and `user_status=active`
2. WHEN a user is successfully reactivated THEN the system SHALL display the user with "Active" status in the user list
3. WHEN reactivation fails THEN the system SHALL display a clear error message explaining the failure reason

### Requirement 2

**User Story:** As a system administrator, I want consistent user status representation so that the system maintains data integrity

#### Acceptance Criteria

1. WHEN a user's status is changed THEN the system SHALL ensure `is_active` and `user_status` fields are synchronized
2. IF `user_status=active` THEN `is_active` SHALL be `True`
3. IF `user_status=inactive` THEN `is_active` SHALL be `False`

### Requirement 3

**User Story:** As an admin, I want proper error handling during reactivation so that I understand what went wrong

#### Acceptance Criteria

1. WHEN reactivation fails due to user not found THEN the system SHALL return a 404 error with "User not found" message
2. WHEN reactivation fails due to insufficient permissions THEN the system SHALL return a 403 error with appropriate message
3. WHEN reactivation fails due to database errors THEN the system SHALL return a 500 error with generic error message
4. WHEN any reactivation error occurs THEN the frontend SHALL display the error message to the admin