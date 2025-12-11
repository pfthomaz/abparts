# Design Document

## Overview

The machine API endpoints are failing due to database schema inconsistencies and enum handling issues. The primary problems identified are:

1. **Database Schema Mismatch**: The machine model defines fields that don't exist in the database table
2. **Enum Value Mapping**: SQLAlchemy enum handling is not properly configured for the MachineStatus enum
3. **Missing Database Migrations**: Schema changes haven't been properly applied through migrations
4. **Error Handling**: Insufficient error handling for database-related issues

The solution involves fixing the database schema, updating enum handling, and improving error handling across machine endpoints.

## Architecture

### Current Architecture Issues
- Machine model defines fields not present in database table
- SQLAlchemy enum configuration doesn't match database enum values
- Missing proper migration management for schema changes
- Inconsistent error handling across machine endpoints

### Target Architecture
- Synchronized database schema with model definitions
- Proper enum value mapping between Python and database
- Comprehensive error handling with meaningful error messages
- Robust migration system for future schema changes

## Components and Interfaces

### 1. Database Schema Updates

**Component**: Machine table schema
**Interface**: PostgreSQL database table structure

**Changes Required**:
- Ensure all model fields exist in database table
- Verify enum types are properly defined in database
- Add missing columns with appropriate data types and constraints

**Implementation**:
```sql
-- Verify machine table has all required columns
ALTER TABLE machines ADD COLUMN IF NOT EXISTS purchase_date timestamp with time zone;
ALTER TABLE machines ADD COLUMN IF NOT EXISTS warranty_expiry_date timestamp with time zone;
ALTER TABLE machines ADD COLUMN IF NOT EXISTS status machinestatus DEFAULT 'active';
ALTER TABLE machines ADD COLUMN IF NOT EXISTS last_maintenance_date timestamp with time zone;
ALTER TABLE machines ADD COLUMN IF NOT EXISTS next_maintenance_date timestamp with time zone;
ALTER TABLE machines ADD COLUMN IF NOT EXISTS location varchar(255);
ALTER TABLE machines ADD COLUMN IF NOT EXISTS notes text;

-- Ensure enum type exists
CREATE TYPE IF NOT EXISTS machinestatus AS ENUM ('active', 'inactive', 'maintenance', 'decommissioned');
```

### 2. SQLAlchemy Model Updates

**Component**: Machine model enum handling
**Interface**: SQLAlchemy Column definition

**Changes Required**:
- Update enum column definition to use `values_callable`
- Ensure enum values match database enum values
- Add proper default values

**Implementation**:
```python
status = Column(
    Enum(MachineStatus, values_callable=lambda obj: [e.value for e in obj]), 
    nullable=False,
    server_default='active'
)
```

### 3. CRUD Operations Enhancement

**Component**: Machine CRUD functions
**Interface**: Database query and response handling

**Changes Required**:
- Add comprehensive error handling for database operations
- Ensure proper serialization of enum values
- Handle missing or null values gracefully

**Implementation**:
- Wrap database queries in try-catch blocks
- Add specific error handling for enum conversion issues
- Implement proper logging for debugging

### 4. API Endpoint Error Handling

**Component**: Machine router endpoints
**Interface**: FastAPI route handlers

**Changes Required**:
- Add comprehensive error handling middleware
- Return structured error responses
- Log errors with sufficient detail for debugging

## Data Models

### Machine Model Fields
```python
class Machine(Base):
    id: UUID
    customer_organization_id: UUID
    model_type: str
    name: str
    serial_number: str
    purchase_date: Optional[datetime]
    warranty_expiry_date: Optional[datetime]
    status: MachineStatus  # Enum with proper value mapping
    last_maintenance_date: Optional[datetime]
    next_maintenance_date: Optional[datetime]
    location: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### Database Enum Types
```sql
CREATE TYPE machinestatus AS ENUM ('active', 'inactive', 'maintenance', 'decommissioned');
```

### Error Response Model
```python
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str]
    request_id: str
    timestamp: datetime
```

## Error Handling

### Database Connection Errors
- **Detection**: SQLAlchemy connection exceptions
- **Response**: 503 Service Unavailable with retry information
- **Logging**: Full stack trace with connection details

### Schema Mismatch Errors
- **Detection**: Column not found or type mismatch exceptions
- **Response**: 500 Internal Server Error with schema information
- **Logging**: Specific column/type mismatch details

### Enum Value Errors
- **Detection**: Enum value not found exceptions
- **Response**: 422 Unprocessable Entity with valid enum values
- **Logging**: Current value and expected enum values

### Permission Errors
- **Detection**: Authorization failures
- **Response**: 403 Forbidden with permission requirements
- **Logging**: User context and required permissions

## Testing Strategy

### Unit Tests
- Test enum value conversion between Python and database
- Test CRUD operations with various data scenarios
- Test error handling for different failure modes
- Test model serialization and deserialization

### Integration Tests
- Test complete API endpoint flows
- Test database schema compatibility
- Test error responses and status codes
- Test authentication and authorization

### Database Tests
- Verify all model fields exist in database
- Test enum type definitions and constraints
- Test migration scripts for schema updates
- Test data integrity and constraints

### Error Scenario Tests
- Test behavior with missing database columns
- Test enum value mismatch handling
- Test database connection failures
- Test invalid data input handling

## Implementation Steps

### Phase 1: Database Schema Fix
1. Verify current database schema
2. Add missing columns to machines table
3. Create/verify enum types
4. Test schema compatibility with models

### Phase 2: Model and Enum Updates
1. Update SQLAlchemy enum definitions
2. Add proper error handling to CRUD operations
3. Test enum value serialization
4. Verify model-database compatibility

### Phase 3: API Endpoint Enhancement
1. Add comprehensive error handling to routes
2. Implement structured error responses
3. Add request/response logging
4. Test all machine endpoints

### Phase 4: Migration System
1. Create proper migration files for schema changes
2. Test migration scripts in development
3. Document migration procedures
4. Prepare for production deployment

## Monitoring and Maintenance

### Error Monitoring
- Track 500 error rates on machine endpoints
- Monitor database query performance
- Alert on enum conversion failures
- Track schema mismatch incidents

### Performance Monitoring
- Monitor machine endpoint response times
- Track database query execution times
- Monitor memory usage during large queries
- Alert on performance degradation

### Health Checks
- Verify database schema compatibility
- Test enum value mappings
- Validate model serialization
- Check endpoint availability