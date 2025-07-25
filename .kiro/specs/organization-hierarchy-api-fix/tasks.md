# Implementation Plan

- [x] 1. Create organization hierarchy response schema








  - Add `OrganizationHierarchyNode` schema to `backend/app/schemas.py`
  - Include all organization fields plus recursive `children` array
  - Configure Pydantic model for proper serialization
  - _Requirements: 1.3, 1.4_

- [x] 2. Implement CRUD function for hierarchy tree building







  - Add `get_organization_hierarchy_tree` function to `backend/app/crud/organizations.py`
  - Implement single-query approach to fetch all organizations
  - Build parent-child mapping and recursive tree structure
  - Apply organization scoping and active status filtering
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 3.1, 3.2_

- [x] 3. Add hierarchy API endpoint to organizations router







  - Implement `GET /organizations/hierarchy` endpoint in `backend/app/routers/organizations.py`
  - Add query parameter for `include_inactive` with default False
  - Integrate with existing permission system using `require_permission` dependency
  - Apply organization-scoped filtering based on user permissions
  - _Requirements: 1.1, 2.1, 2.3, 3.1_

- [x] 4. Implement comprehensive error handling





  - Add try-catch blocks for database errors with 500 status responses
  - Handle permission errors with 403 status responses
  - Validate query parameters with 422 status for invalid inputs
  - Return empty array with 200 status when no organizations exist
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [-] 5. Write unit tests for CRUD hierarchy function





















  - Create test cases in `backend/tests/test_organizations_crud.py`
  - Test hierarchy building with various organization structures (simple, complex, flat)
  - Test filtering by active status and organization scoping
  - Test empty hierarchy and edge case scenarios
  - _Requirements: 1.2, 1.3, 2.2, 3.2_

- [ ] 6. Write unit tests for hierarchy API endpoint
  - Create test cases in `backend/tests/test_organizations_router.py`
  - Test successful hierarchy retrieval with different user permissions
  - Test query parameter validation and error responses
  - Test permission enforcement for different user roles
  - _Requirements: 2.1, 2.2, 2.3, 4.1, 4.2, 4.3_

- [ ] 7. Test frontend integration with new hierarchy endpoint
  - Verify the Organizations page hierarchy view works with new API
  - Test that hierarchy data structure matches frontend expectations
  - Validate permission-based filtering works correctly in UI
  - Test error handling displays appropriate messages to users
  - _Requirements: 1.1, 1.3, 2.1, 4.4_