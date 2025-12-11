# Design Document

## Overview

The user reactivation fix addresses the inconsistency between the `is_active` boolean field and the `user_status` enum field in the User model. The current implementation only updates `is_active` during reactivation, leaving `user_status` as "inactive", which causes display and logic issues throughout the application.

## Architecture

The fix involves updating the existing CRUD function `set_user_active_status` to properly synchronize both status fields, ensuring data consistency across the application. This approach maintains backward compatibility while fixing the underlying issue.

## Components and Interfaces

### Backend Components

**Modified CRUD Function:**
- `crud/users.py::set_user_active_status()` - Enhanced to update both `is_active` and `user_status` fields synchronously

**Existing API Endpoint:**
- `routers/users.py::/users/{user_id}/reactivate` - No changes needed, will benefit from improved CRUD function

**Database Model:**
- `models.py::User` - No schema changes required, both fields already exist

### Frontend Components

**Existing Components:**
- `services/userService.js::reactivateUser()` - No changes needed
- `pages/UsersPage.js::handleReactivate()` - No changes needed, already has proper error handling

## Data Models

### User Status Synchronization Logic

```python
# Status field synchronization rules:
if is_active == True:
    user_status = UserStatus.active
elif is_active == False:
    user_status = UserStatus.inactive
```

### Status Field Relationships

| is_active | user_status | Valid State | Description |
|-----------|-------------|-------------|-------------|
| True      | active      | ✅ Valid    | Active user |
| False     | inactive    | ✅ Valid    | Inactive user |
| True      | inactive    | ❌ Invalid  | Inconsistent state (current bug) |
| False     | active      | ❌ Invalid  | Inconsistent state |

## Error Handling

### CRUD Level Error Handling
- Return `None` if user not found (existing behavior)
- Database transaction rollback on commit failures
- Proper exception propagation to API layer

### API Level Error Handling
- 404 for user not found
- 403 for insufficient permissions (existing)
- 500 for database errors with generic message

### Frontend Error Handling
- Display specific error messages from API responses
- Maintain existing error state management
- Refresh user list on successful reactivation

## Testing Strategy

### Unit Tests
- Test `set_user_active_status` with both `True` and `False` values
- Verify both `is_active` and `user_status` are updated correctly
- Test error conditions (user not found, database errors)

### Integration Tests
- Test full reactivation flow from API endpoint
- Verify proper error responses for various failure scenarios
- Test permission checks for cross-organization reactivation

### Frontend Tests
- Test error message display for failed reactivations
- Test successful reactivation UI updates
- Test loading states during reactivation operations

## Implementation Approach

### Phase 1: Fix CRUD Function
1. Update `set_user_active_status` to synchronize both status fields
2. Add proper error handling and transaction management
3. Maintain backward compatibility

### Phase 2: Testing
1. Add unit tests for the updated CRUD function
2. Test existing API endpoints to ensure they work correctly
3. Verify frontend behavior with the fixed backend

### Phase 3: Validation
1. Test the fix with the actual failing scenario
2. Verify user status consistency across the application
3. Ensure no regressions in existing functionality

## Security Considerations

- No changes to existing permission checks
- Maintain organization-scoped access controls
- Preserve audit logging capabilities (if using advanced endpoint)

## Performance Impact

- Minimal performance impact (one additional field update)
- No additional database queries required
- Maintains existing transaction boundaries