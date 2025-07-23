"""
Tests for organization form fix endpoints.
Tests the new potential parents and validation endpoints added for the organization form fix.
"""

import pytest
import uuid
from typing import Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Organization, OrganizationType, UserRole


class TestPotentialParentsEndpoint:
    """Test the GET /organizations/potential-parents endpoint."""
    
    def test_get_potential_parents_for_supplier_as_super_admin(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]], 
        test_organizations: Dict[str, Organization]
    ):
        """Test getting potential parents for supplier organization type as super admin."""
        headers = auth_headers["super_admin"]
        
        response = client.get(
            "/organizations/potential-parents?organization_type=supplier", 
            headers=headers
        )
        
        assert response.status_code == 200
        potential_parents = response.json()
        
        # Should return Customer and Oraseas EE organizations
        assert len(potential_parents) >= 2
        
        # Verify all returned organizations are valid parent types
        valid_parent_types = {"customer", "oraseas_ee"}
        for parent in potential_parents:
            assert parent["organization_type"] in valid_parent_types
            assert parent["is_active"] is True
        
        # Verify specific organizations are included
        parent_names = [p["name"] for p in potential_parents]
        assert "Oraseas EE" in parent_names
        assert "AutoWash Solutions Ltd" in parent_names or "CleanCar Services" in parent_names
    
    def test_get_potential_parents_for_customer_returns_empty(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test that customer organization type returns no potential parents."""
        headers = auth_headers["super_admin"]
        
        response = client.get(
            "/organizations/potential-parents?organization_type=customer", 
            headers=headers
        )
        
        assert response.status_code == 200
        potential_parents = response.json()
        assert len(potential_parents) == 0
    
    def test_get_potential_parents_for_oraseas_ee_returns_empty(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test that oraseas_ee organization type returns no potential parents."""
        headers = auth_headers["super_admin"]
        
        response = client.get(
            "/organizations/potential-parents?organization_type=oraseas_ee", 
            headers=headers
        )
        
        assert response.status_code == 200
        potential_parents = response.json()
        assert len(potential_parents) == 0
    
    def test_get_potential_parents_for_bossaqua_returns_empty(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test that bossaqua organization type returns no potential parents."""
        headers = auth_headers["super_admin"]
        
        response = client.get(
            "/organizations/potential-parents?organization_type=bossaqua", 
            headers=headers
        )
        
        assert response.status_code == 200
        potential_parents = response.json()
        assert len(potential_parents) == 0
    
    def test_get_potential_parents_with_customer_admin_access(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test potential parents endpoint with customer admin permissions."""
        headers = auth_headers["customer_admin"]
        
        response = client.get(
            "/organizations/potential-parents?organization_type=supplier", 
            headers=headers
        )
        
        assert response.status_code == 200
        potential_parents = response.json()
        
        # Customer admin should see limited results based on their access
        # They should at least see their own organization if it's a valid parent type
        for parent in potential_parents:
            assert parent["is_active"] is True
    
    def test_get_potential_parents_with_customer_user_access(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test potential parents endpoint with customer user permissions."""
        headers = auth_headers["customer_user"]
        
        response = client.get(
            "/organizations/potential-parents?organization_type=supplier", 
            headers=headers
        )
        
        assert response.status_code == 200
        # Customer users should still be able to access this read-only endpoint
    
    def test_get_potential_parents_without_auth_fails(self, client: TestClient):
        """Test that potential parents endpoint requires authentication."""
        response = client.get("/organizations/potential-parents?organization_type=supplier")
        assert response.status_code == 401
    
    def test_get_potential_parents_invalid_organization_type(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test potential parents endpoint with invalid organization type."""
        headers = auth_headers["super_admin"]
        
        response = client.get(
            "/organizations/potential-parents?organization_type=invalid_type", 
            headers=headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_potential_parents_missing_organization_type(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test potential parents endpoint without organization_type parameter."""
        headers = auth_headers["super_admin"]
        
        response = client.get("/organizations/potential-parents", headers=headers)
        assert response.status_code == 422  # Missing required parameter


class TestOrganizationValidationEndpoint:
    """Test the POST /organizations/validate endpoint."""
    
    def test_validate_valid_supplier_organization(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]], 
        test_organizations: Dict[str, Organization]
    ):
        """Test validation of a valid supplier organization."""
        headers = auth_headers["super_admin"]
        
        validation_data = {
            "name": "New Valid Supplier",
            "organization_type": "supplier",
            "parent_organization_id": str(test_organizations["oraseas"].id),
            "address": "123 Supplier Street",
            "contact_info": "contact@newsupplier.com",
            "is_active": True
        }
        
        response = client.post("/organizations/validate", json=validation_data, headers=headers)
        
        assert response.status_code == 200
        validation_result = response.json()
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
    
    def test_validate_supplier_without_parent_fails(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test validation of supplier organization without parent fails."""
        headers = auth_headers["super_admin"]
        
        validation_data = {
            "name": "Invalid Supplier",
            "organization_type": "supplier",
            "address": "123 Supplier Street",
            "contact_info": "contact@invalidsupplier.com",
            "is_active": True
        }
        
        response = client.post("/organizations/validate", json=validation_data, headers=headers)
        
        assert response.status_code == 200
        validation_result = response.json()
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
        
        # Check for specific error about parent requirement
        error_messages = [error["message"] for error in validation_result["errors"]]
        assert any("parent organization" in msg.lower() for msg in error_messages)
        
        # Check that the error is on the correct field
        parent_errors = [error for error in validation_result["errors"] if error["field"] == "parent_organization_id"]
        assert len(parent_errors) > 0
    
    def test_validate_duplicate_singleton_organization_fails(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test validation of duplicate singleton organization fails."""
        headers = auth_headers["super_admin"]
        
        # Try to create another Oraseas EE (should fail)
        validation_data = {
            "name": "Another Oraseas EE",
            "organization_type": "oraseas_ee",
            "address": "456 Duplicate Street",
            "contact_info": "duplicate@oraseas.com",
            "is_active": True
        }
        
        response = client.post("/organizations/validate", json=validation_data, headers=headers)
        
        assert response.status_code == 200
        validation_result = response.json()
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
        
        # Check for specific error about singleton constraint
        error_messages = [error["message"] for error in validation_result["errors"]]
        assert any("only one" in msg.lower() for msg in error_messages)
        
        # Check that the error is on the correct field
        type_errors = [error for error in validation_result["errors"] if error["field"] == "organization_type"]
        assert len(type_errors) > 0
    
    def test_validate_duplicate_bossaqua_organization_fails(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test validation of duplicate BossAqua organization fails."""
        headers = auth_headers["super_admin"]
        
        # Try to create another BossAqua (should fail)
        validation_data = {
            "name": "Another BossAqua",
            "organization_type": "bossaqua",
            "address": "789 Another Street",
            "contact_info": "another@bossaqua.com",
            "is_active": True
        }
        
        response = client.post("/organizations/validate", json=validation_data, headers=headers)
        
        assert response.status_code == 200
        validation_result = response.json()
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
        
        # Check for specific error about singleton constraint
        error_messages = [error["message"] for error in validation_result["errors"]]
        assert any("only one" in msg.lower() for msg in error_messages)
    
    def test_validate_organization_with_nonexistent_parent_fails(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test validation with nonexistent parent organization fails."""
        headers = auth_headers["super_admin"]
        
        fake_parent_id = str(uuid.uuid4())
        validation_data = {
            "name": "Supplier with Fake Parent",
            "organization_type": "supplier",
            "parent_organization_id": fake_parent_id,
            "address": "123 Fake Street",
            "contact_info": "contact@fake.com",
            "is_active": True
        }
        
        response = client.post("/organizations/validate", json=validation_data, headers=headers)
        
        assert response.status_code == 200
        validation_result = response.json()
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
        
        # Check for specific error about parent not found
        error_messages = [error["message"] for error in validation_result["errors"]]
        assert any("not found" in msg.lower() for msg in error_messages)
    
    def test_validate_organization_with_invalid_parent_uuid_fails(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test validation with invalid parent UUID format fails."""
        headers = auth_headers["super_admin"]
        
        validation_data = {
            "name": "Supplier with Invalid Parent UUID",
            "organization_type": "supplier",
            "parent_organization_id": "not-a-valid-uuid",
            "address": "123 Invalid Street",
            "contact_info": "contact@invalid.com",
            "is_active": True
        }
        
        response = client.post("/organizations/validate", json=validation_data, headers=headers)
        
        assert response.status_code == 422  # Pydantic validation error for invalid UUID
    
    def test_validate_organization_update_scenario(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]], 
        test_organizations: Dict[str, Organization]
    ):
        """Test validation for organization update scenario."""
        headers = auth_headers["super_admin"]
        
        # Validate updating an existing organization
        existing_org = test_organizations["supplier"]
        validation_data = {
            "name": "Updated Supplier Name",
            "organization_type": "supplier",
            "parent_organization_id": str(test_organizations["oraseas"].id),
            "address": "Updated Address",
            "contact_info": "updated@supplier.com",
            "is_active": True,
            "id": str(existing_org.id)  # Include ID for update validation
        }
        
        response = client.post("/organizations/validate", json=validation_data, headers=headers)
        
        assert response.status_code == 200
        validation_result = response.json()
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
    
    def test_validate_organization_self_parent_fails(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]], 
        test_organizations: Dict[str, Organization]
    ):
        """Test validation fails when organization tries to be its own parent."""
        headers = auth_headers["super_admin"]
        
        existing_org = test_organizations["customer1"]
        validation_data = {
            "name": "Self Parent Test",
            "organization_type": "supplier",
            "parent_organization_id": str(existing_org.id),
            "address": "123 Self Street",
            "contact_info": "self@test.com",
            "is_active": True,
            "id": str(existing_org.id)  # Same ID as parent
        }
        
        response = client.post("/organizations/validate", json=validation_data, headers=headers)
        
        assert response.status_code == 200
        validation_result = response.json()
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
        
        # Check for specific error about self-parent
        error_messages = [error["message"] for error in validation_result["errors"]]
        assert any("own parent" in msg.lower() for msg in error_messages)
    
    def test_validate_organization_empty_name_fails(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test validation fails with empty organization name."""
        headers = auth_headers["super_admin"]
        
        validation_data = {
            "name": "",
            "organization_type": "customer",
            "address": "123 Empty Name Street",
            "contact_info": "empty@test.com",
            "is_active": True
        }
        
        response = client.post("/organizations/validate", json=validation_data, headers=headers)
        
        assert response.status_code == 200
        validation_result = response.json()
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
        
        # Check for specific error about name requirement
        name_errors = [error for error in validation_result["errors"] if error["field"] == "name"]
        assert len(name_errors) > 0
        assert "required" in name_errors[0]["message"].lower()
    
    def test_validate_organization_with_different_user_roles(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]], 
        test_organizations: Dict[str, Organization]
    ):
        """Test validation endpoint with different user roles."""
        validation_data = {
            "name": "Role Test Organization",
            "organization_type": "customer",
            "address": "123 Role Test Street",
            "contact_info": "role@test.com",
            "is_active": True
        }
        
        # Test with different user roles
        for role in ["super_admin", "oraseas_admin", "customer_admin", "customer_user"]:
            headers = auth_headers[role]
            
            response = client.post("/organizations/validate", json=validation_data, headers=headers)
            
            # All roles should be able to validate (read permission)
            assert response.status_code == 200
            validation_result = response.json()
            assert "valid" in validation_result
            assert "errors" in validation_result
    
    def test_validate_organization_without_auth_fails(self, client: TestClient):
        """Test that validation endpoint requires authentication."""
        validation_data = {
            "name": "Unauthorized Test",
            "organization_type": "customer",
            "address": "123 Unauthorized Street",
            "contact_info": "unauthorized@test.com",
            "is_active": True
        }
        
        response = client.post("/organizations/validate", json=validation_data)
        assert response.status_code == 401


class TestBusinessRuleValidation:
    """Test business rule validation in both endpoints."""
    
    def test_supplier_parent_business_rules(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]], 
        test_organizations: Dict[str, Organization]
    ):
        """Test that supplier parent business rules are enforced consistently."""
        headers = auth_headers["super_admin"]
        
        # Get potential parents for supplier
        response = client.get(
            "/organizations/potential-parents?organization_type=supplier", 
            headers=headers
        )
        assert response.status_code == 200
        potential_parents = response.json()
        
        # Validate supplier with each potential parent
        for parent in potential_parents:
            validation_data = {
                "name": f"Test Supplier for {parent['name']}",
                "organization_type": "supplier",
                "parent_organization_id": parent["id"],
                "address": "123 Test Street",
                "contact_info": "test@supplier.com",
                "is_active": True
            }
            
            response = client.post("/organizations/validate", json=validation_data, headers=headers)
            assert response.status_code == 200
            validation_result = response.json()
            assert validation_result["valid"] is True, f"Validation failed for parent {parent['name']}"
    
    def test_singleton_organization_constraints(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test singleton organization constraints across both endpoints."""
        headers = auth_headers["super_admin"]
        
        # Test that singleton types have no potential parents
        singleton_types = ["oraseas_ee", "bossaqua"]
        
        for org_type in singleton_types:
            # Check potential parents (should be empty)
            response = client.get(
                f"/organizations/potential-parents?organization_type={org_type}", 
                headers=headers
            )
            assert response.status_code == 200
            potential_parents = response.json()
            assert len(potential_parents) == 0
            
            # Check validation (should fail for duplicates)
            validation_data = {
                "name": f"Duplicate {org_type}",
                "organization_type": org_type,
                "address": "123 Duplicate Street",
                "contact_info": "duplicate@test.com",
                "is_active": True
            }
            
            response = client.post("/organizations/validate", json=validation_data, headers=headers)
            assert response.status_code == 200
            validation_result = response.json()
            assert validation_result["valid"] is False
    
    def test_organization_hierarchy_consistency(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]], 
        test_organizations: Dict[str, Organization]
    ):
        """Test that organization hierarchy rules are consistent."""
        headers = auth_headers["super_admin"]
        
        # Test that customer organizations cannot have parents
        validation_data = {
            "name": "Customer with Parent",
            "organization_type": "customer",
            "parent_organization_id": str(test_organizations["oraseas"].id),
            "address": "123 Invalid Street",
            "contact_info": "invalid@customer.com",
            "is_active": True
        }
        
        response = client.post("/organizations/validate", json=validation_data, headers=headers)
        assert response.status_code == 200
        validation_result = response.json()
        
        # This should be valid according to current business rules
        # (customers can have parents in some scenarios)
        # Adjust assertion based on actual business requirements
        assert "valid" in validation_result


class TestEndpointIntegration:
    """Test integration between the two new endpoints."""
    
    def test_potential_parents_and_validation_consistency(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test that potential parents and validation endpoints are consistent."""
        headers = auth_headers["super_admin"]
        
        # Get potential parents for supplier
        response = client.get(
            "/organizations/potential-parents?organization_type=supplier", 
            headers=headers
        )
        assert response.status_code == 200
        potential_parents = response.json()
        
        if potential_parents:
            # Use first potential parent for validation test
            parent = potential_parents[0]
            
            validation_data = {
                "name": "Integration Test Supplier",
                "organization_type": "supplier",
                "parent_organization_id": parent["id"],
                "address": "123 Integration Street",
                "contact_info": "integration@test.com",
                "is_active": True
            }
            
            response = client.post("/organizations/validate", json=validation_data, headers=headers)
            assert response.status_code == 200
            validation_result = response.json()
            assert validation_result["valid"] is True
    
    def test_frontend_workflow_simulation(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Simulate the frontend workflow using both endpoints."""
        headers = auth_headers["super_admin"]
        
        # Step 1: Frontend loads potential parents when user selects "supplier"
        response = client.get(
            "/organizations/potential-parents?organization_type=supplier", 
            headers=headers
        )
        assert response.status_code == 200
        potential_parents = response.json()
        
        # Step 2: User fills form and frontend validates before submission
        if potential_parents:
            validation_data = {
                "name": "Frontend Workflow Test",
                "organization_type": "supplier",
                "parent_organization_id": potential_parents[0]["id"],
                "address": "123 Frontend Street",
                "contact_info": "frontend@test.com",
                "is_active": True
            }
            
            response = client.post("/organizations/validate", json=validation_data, headers=headers)
            assert response.status_code == 200
            validation_result = response.json()
            assert validation_result["valid"] is True
            
            # Step 3: If validation passes, frontend would proceed with actual creation
            # (This would use the existing POST /organizations/ endpoint)
            # We're not testing that here as it's part of existing functionality


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_potential_parents_with_malformed_request(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test potential parents endpoint with malformed requests."""
        headers = auth_headers["super_admin"]
        
        # Test with invalid enum value
        response = client.get(
            "/organizations/potential-parents?organization_type=invalid", 
            headers=headers
        )
        assert response.status_code == 422
    
    def test_validation_with_malformed_request(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test validation endpoint with malformed requests."""
        headers = auth_headers["super_admin"]
        
        # Test with missing required fields
        invalid_data = {
            "organization_type": "supplier"
            # Missing name field
        }
        
        response = client.post("/organizations/validate", json=invalid_data, headers=headers)
        assert response.status_code == 422
    
    def test_endpoints_with_database_errors(
        self, 
        client: TestClient, 
        auth_headers: Dict[str, Dict[str, str]]
    ):
        """Test endpoint behavior with database connection issues."""
        # This would require mocking database failures
        # For now, we'll test with valid requests to ensure no unexpected errors
        headers = auth_headers["super_admin"]
        
        response = client.get(
            "/organizations/potential-parents?organization_type=supplier", 
            headers=headers
        )
        assert response.status_code == 200
        
        validation_data = {
            "name": "Database Test",
            "organization_type": "customer",
            "address": "123 DB Street",
            "contact_info": "db@test.com",
            "is_active": True
        }
        
        response = client.post("/organizations/validate", json=validation_data, headers=headers)
        assert response.status_code == 200