# Design Document

## Overview

This design implements a new `/organizations/hierarchy` API endpoint that returns the complete organization hierarchy as a nested tree structure. The endpoint will leverage existing CRUD functions and permission systems while providing the specific data format expected by the frontend Organizations page.

## Architecture

The solution follows the existing ABParts API architecture pattern:

- **Router Layer**: New endpoint in `backend/app/routers/organizations.py`
- **CRUD Layer**: New function in `backend/app/crud/organizations.py` 
- **Schema Layer**: New response schema in `backend/app/schemas.py`
- **Permission Layer**: Integration with existing permission system

## Components and Interfaces

### API Endpoint

**Route**: `GET /organizations/hierarchy`

**Query Parameters**:
- `include_inactive: bool = False` - Include inactive organizations in hierarchy

**Response**: `List[OrganizationHierarchyNode]`

**Authentication**: Requires valid JWT token with organization read permissions

### Data Models

#### OrganizationHierarchyNode Schema

```python
class OrganizationHierarchyNode(BaseModel):
    id: UUID
    name: str
    organization_type: OrganizationTypeEnum
    is_active: bool
    parent_organization_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    children: List['OrganizationHierarchyNode'] = []
    
    class Config:
        from_attributes = True
```

### CRUD Function

#### get_organization_hierarchy_tree

```python
def get_organization_hierarchy_tree(
    db: Session, 
    include_inactive: bool = False,
    accessible_org_ids: Optional[Set[UUID]] = None
) -> List[OrganizationHierarchyNode]:
    """
    Build complete organization hierarchy tree with nested children.
    
    Args:
        db: Database session
        include_inactive: Include inactive organizations
        accessible_org_ids: Set of organization IDs user can access (for scoping)
    
    Returns:
        List of root organization nodes with nested children
    """
```

**Algorithm**:
1. Query all organizations (filtered by active status and accessible IDs)
2. Build parent-child mapping dictionary
3. Identify root organizations (no parent)
4. Recursively build tree structure for each root
5. Return list of root nodes with nested children

### Permission Integration

The endpoint will integrate with the existing permission system:

- Use `require_permission(ResourceType.ORGANIZATION, PermissionType.READ)` dependency
- Apply `OrganizationScopedQueries.get_accessible_organization_ids()` for filtering
- Respect user role-based access (super_admin sees all, others see scoped view)

## Error Handling

### HTTP Status Codes

- **200 OK**: Successful hierarchy retrieval (even if empty)
- **401 Unauthorized**: Invalid or missing authentication token
- **403 Forbidden**: User lacks organization read permissions
- **422 Unprocessable Entity**: Invalid query parameters
- **500 Internal Server Error**: Database or server errors

### Error Response Format

```json
{
  "detail": "Descriptive error message"
}
```

## Testing Strategy

### Unit Tests

1. **CRUD Function Tests** (`test_organizations_crud.py`):
   - Test hierarchy building with various organization structures
   - Test filtering by active status
   - Test organization scoping with different user permissions
   - Test empty hierarchy scenarios
   - Test circular reference prevention

2. **API Endpoint Tests** (`test_organizations_router.py`):
   - Test successful hierarchy retrieval
   - Test permission enforcement
   - Test query parameter validation
   - Test error handling scenarios

### Integration Tests

1. **Frontend Integration**:
   - Verify hierarchy data structure matches frontend expectations
   - Test hierarchy view rendering with real API data
   - Test permission-based hierarchy filtering

### Test Data Scenarios

1. **Simple Hierarchy**: Oraseas EE → Customer → Supplier
2. **Complex Hierarchy**: Multiple levels with branches
3. **Flat Structure**: All root organizations
4. **Mixed Active/Inactive**: Organizations with different statuses
5. **Permission Scoping**: Different user roles seeing different views

## Implementation Notes

### Performance Considerations

- Single database query to fetch all organizations
- In-memory tree building to avoid N+1 queries
- Consider caching for frequently accessed hierarchies

### Backward Compatibility

- New endpoint doesn't affect existing hierarchy endpoints
- Existing `/organizations/hierarchy/roots` and `/organizations/{org_id}/hierarchy` remain unchanged
- Frontend can migrate to new endpoint without breaking changes

### Security Considerations

- Organization scoping prevents unauthorized data access
- Permission checks ensure proper role-based filtering
- Input validation on query parameters

## Database Queries

The implementation will use a single optimized query:

```sql
SELECT * FROM organizations 
WHERE (is_active = true OR :include_inactive = true)
AND id IN (:accessible_org_ids)
ORDER BY name;
```

This avoids multiple database round trips and leverages existing indexes on `is_active` and `id` columns.