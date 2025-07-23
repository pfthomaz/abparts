# Design Document

## Overview

This design addresses the critical backend/frontend misalignment in the organization creation form by implementing two missing API endpoints: `/organizations/potential-parents` and `/organizations/validate`. The solution ensures the frontend organization form works correctly while maintaining all existing backend functionality and following established patterns.

## Architecture

The fix involves adding two new endpoints to the existing organizations router without modifying any existing functionality:

1. **GET /organizations/potential-parents** - Returns organizations that can serve as parents for a given organization type
2. **POST /organizations/validate** - Validates organization data before creation/update

Both endpoints will integrate seamlessly with the existing permission system, CRUD operations, and business rule validation.

## Components and Interfaces

### Backend Components

#### 1. Organizations Router Extensions
- **Location**: `backend/app/routers/organizations.py`
- **New Endpoints**:
  - `GET /organizations/potential-parents?organization_type={type}`
  - `POST /organizations/validate`
- **Integration**: Uses existing permission decorators and CRUD functions

#### 2. CRUD Operations Extensions
- **Location**: `backend/app/crud/organizations.py`
- **New Functions**:
  - `get_potential_parent_organizations(db, organization_type)`
  - `validate_organization_data(db, org_data, org_id=None)`
- **Integration**: Leverages existing validation logic from `create_organization` and `update_organization`

#### 3. Schema Extensions
- **Location**: `backend/app/schemas.py`
- **New Schemas**:
  - `OrganizationValidationRequest`
  - `OrganizationValidationResponse`
- **Integration**: Uses existing `OrganizationCreate` and `OrganizationUpdate` schemas

### Frontend Components

#### 1. Organizations Service
- **Location**: `frontend/src/services/organizationsService.js`
- **Status**: Already implemented correctly
- **Verification**: Ensure API calls match new backend endpoints

#### 2. Organization Form
- **Location**: `frontend/src/components/OrganizationForm.js`
- **Status**: Already implemented correctly
- **Verification**: Ensure error handling works with new validation responses

## Data Models

### Potential Parents Response
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Organization Name",
      "organization_type": "customer",
      "is_active": true
    }
  ]
}
```

### Validation Request
```json
{
  "name": "New Organization",
  "organization_type": "supplier",
  "parent_organization_id": "uuid",
  "address": "Optional address",
  "contact_info": "Optional contact",
  "is_active": true,
  "id": "optional-for-updates"
}
```

### Validation Response
```json
{
  "valid": true,
  "errors": []
}
```

Or for validation failures:
```json
{
  "valid": false,
  "errors": [
    {
      "field": "parent_organization_id",
      "message": "Supplier organizations must have a parent organization"
    }
  ]
}
```

## Error Handling

### Backend Error Handling
- **Validation Errors**: Return 400 with detailed error messages
- **Permission Errors**: Return 403 with appropriate messages
- **Not Found Errors**: Return 404 for missing resources
- **Server Errors**: Return 500 with generic error messages

### Frontend Error Handling
- **API Errors**: Display user-friendly error messages in the form
- **Network Errors**: Show connection error messages
- **Validation Errors**: Highlight specific form fields with errors

## Testing Strategy

### Backend Testing
1. **Unit Tests**: Test new CRUD functions with various scenarios
2. **Integration Tests**: Test new API endpoints with different user roles
3. **Validation Tests**: Test business rule validation edge cases
4. **Regression Tests**: Ensure existing organization operations still work

### Frontend Testing
1. **Component Tests**: Test organization form with new API responses
2. **Integration Tests**: Test complete organization creation flow
3. **Error Handling Tests**: Test form behavior with various error responses
4. **Regression Tests**: Ensure existing organization management still works

### End-to-End Testing
1. **Happy Path**: Create organizations of different types successfully
2. **Validation Path**: Test validation errors are displayed correctly
3. **Permission Path**: Test access control works correctly
4. **Edge Cases**: Test singleton constraints and parent relationships

## Implementation Approach

### Phase 1: Backend Implementation
1. Add new CRUD functions for potential parents and validation
2. Add new API endpoints to organizations router
3. Add new schema definitions
4. Test backend functionality

### Phase 2: Frontend Verification
1. Verify existing frontend code works with new endpoints
2. Test error handling and user experience
3. Fix any remaining misalignments

### Phase 3: Integration Testing
1. Test complete organization creation flow
2. Verify all organization types work correctly
3. Test permission and validation scenarios

## Business Rules Validation

The validation endpoint will enforce all existing business rules:

1. **Singleton Organizations**: Only one Oraseas EE and one BossAqua allowed
2. **Supplier Parent Requirement**: Suppliers must have a parent organization
3. **Parent Organization Validation**: Parent must exist and be active
4. **Circular Reference Prevention**: Prevent organization hierarchy cycles
5. **Permission Validation**: Ensure user has rights to create/update organizations

## Potential Parent Logic

The potential parents endpoint will return appropriate parent organizations based on business rules:

- **For Suppliers**: Return active Customer and Oraseas EE organizations
- **For Other Types**: Return empty list (no parent allowed)
- **Permission Filtering**: Only return organizations the user can access

## Backward Compatibility

This implementation maintains full backward compatibility:

- All existing API endpoints remain unchanged
- All existing functionality continues to work
- No breaking changes to data models
- No changes to existing business logic