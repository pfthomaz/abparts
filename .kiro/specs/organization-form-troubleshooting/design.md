# Design Document

## Overview

This design addresses the current issues preventing organization creation and editing in the ABParts application. The solution involves systematically diagnosing and fixing connectivity, configuration, and integration issues between the frontend and backend. The approach will identify the root cause and implement targeted fixes while ensuring all organization management functionality works correctly.

## Architecture

The organization form functionality relies on several interconnected components:

1. **Frontend Organization Form** - React component handling user input and validation
2. **Organizations Service** - Frontend service layer for API communication
3. **API Client** - Generic HTTP client with authentication and error handling
4. **Backend API Endpoints** - FastAPI endpoints for organization CRUD operations
5. **Docker Environment** - Containerized development environment with proper networking

## Components and Interfaces

### Diagnostic Components

#### 1. Service Connectivity Test
- **Purpose**: Verify backend API is accessible from frontend
- **Location**: Development environment testing
- **Tests**: Basic connectivity, CORS headers, authentication flow

#### 2. API Endpoint Validation
- **Purpose**: Ensure all organization endpoints respond correctly
- **Location**: Backend API testing
- **Tests**: CRUD operations, validation endpoints, permission checks

#### 3. Frontend Integration Test
- **Purpose**: Verify frontend can successfully interact with backend
- **Location**: Frontend service layer testing
- **Tests**: Form submission, error handling, data flow

### Fix Components

#### 1. Environment Configuration
- **Location**: Docker Compose and environment files
- **Purpose**: Ensure proper API URL configuration and service networking
- **Changes**: Align frontend API URL with backend service configuration

#### 2. CORS Configuration
- **Location**: Backend FastAPI CORS middleware
- **Purpose**: Ensure frontend can make cross-origin requests
- **Changes**: Verify CORS origins include frontend URL

#### 3. Authentication Flow
- **Location**: Frontend API client and backend auth middleware
- **Purpose**: Ensure authentication tokens are properly handled
- **Changes**: Verify token inclusion and validation

#### 4. Error Handling
- **Location**: Frontend organization form and service layer
- **Purpose**: Provide clear feedback when operations fail
- **Changes**: Improve error message display and handling

## Data Models

### Diagnostic Response Format
```json
{
  "test_name": "string",
  "status": "success|failure",
  "details": "string",
  "error": "string|null"
}
```

### API Error Response Format
```json
{
  "detail": "string|array",
  "status_code": "number",
  "timestamp": "string"
}
```

## Error Handling

### Connectivity Issues
- **Network Errors**: Check Docker service networking and port configuration
- **CORS Errors**: Verify CORS middleware configuration and allowed origins
- **Timeout Errors**: Check service health and response times

### API Issues
- **Authentication Errors**: Verify token generation and validation
- **Permission Errors**: Check user roles and endpoint permissions
- **Validation Errors**: Verify request data format and business rules

### Frontend Issues
- **Form Submission Errors**: Check form data serialization and API calls
- **State Management Errors**: Verify React state updates and error handling
- **UI Display Errors**: Check error message rendering and user feedback

## Testing Strategy

### Phase 1: Diagnostic Testing
1. **Service Health Check**: Verify all Docker services are running
2. **API Connectivity Test**: Test basic API endpoints from frontend
3. **Authentication Test**: Verify login flow and token handling
4. **CORS Test**: Check cross-origin request handling

### Phase 2: API Endpoint Testing
1. **Organization CRUD**: Test create, read, update, delete operations
2. **Validation Endpoint**: Test organization data validation
3. **Potential Parents**: Test parent organization retrieval
4. **Permission Testing**: Test with different user roles

### Phase 3: Frontend Integration Testing
1. **Form Rendering**: Verify organization form displays correctly
2. **Form Submission**: Test successful organization creation/update
3. **Error Handling**: Test error display and user feedback
4. **State Updates**: Verify organization list updates after operations

### Phase 4: End-to-End Testing
1. **Complete Flow**: Test full organization creation workflow
2. **Edit Flow**: Test organization editing workflow
3. **Permission Flow**: Test with different user permission levels
4. **Error Scenarios**: Test various error conditions and recovery

## Implementation Approach

### Phase 1: Environment Diagnosis
1. Check Docker service status and networking
2. Verify API URL configuration alignment
3. Test basic API connectivity
4. Check CORS configuration

### Phase 2: API Verification
1. Test organization endpoints directly
2. Verify authentication and permissions
3. Check validation logic
4. Test error responses

### Phase 3: Frontend Integration
1. Test organization service API calls
2. Verify form data handling
3. Check error message display
4. Test state management

### Phase 4: Issue Resolution
1. Fix identified configuration issues
2. Update error handling as needed
3. Improve user feedback
4. Verify complete functionality

## Configuration Requirements

### Docker Environment
- All services (api, web, db, redis) must be running
- Network connectivity between frontend and backend containers
- Proper port mapping for external access

### API Configuration
- Correct CORS origins including frontend URL
- Proper authentication middleware configuration
- Database connectivity and migrations applied

### Frontend Configuration
- API base URL matching backend service
- Proper error handling in API client
- Authentication token management

## Business Rules Validation

The solution must maintain all existing business rules:

1. **Organization Types**: Proper validation of organization type constraints
2. **Singleton Organizations**: Enforcement of single Oraseas EE and BossAqua
3. **Parent Relationships**: Proper validation of supplier parent requirements
4. **Permissions**: Role-based access control for organization management
5. **Data Integrity**: Proper validation of all organization fields

## Success Criteria

The implementation will be considered successful when:

1. **Organization Creation**: Users can successfully create new organizations
2. **Organization Editing**: Users can successfully edit existing organizations
3. **Error Handling**: Clear error messages are displayed for validation failures
4. **Permission Enforcement**: Proper access control is maintained
5. **Data Consistency**: All organization operations maintain data integrity