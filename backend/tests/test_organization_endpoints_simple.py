"""
Simple integration tests for new organization API endpoints.
Tests the /organizations/potential-parents and /organizations/validate endpoints.
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestNewOrganizationEndpoints:
    """Test cases for new organization endpoints"""
    
    def test_potential_parents_endpoint_exists(self, client: TestClient, auth_headers):
        """Test that potential parents endpoint exists and requires auth"""
        # Test without auth
        response = client.get("/organizations/potential-parents?organization_type=supplier")
        assert response.status_code == 401
        
        # Test with auth
        response = client.get(
            "/organizations/potential-parents?organization_type=supplier",
            headers=auth_headers["super_admin"]
        )
        # Should return 200 (success) or 422 (validation error), not 404
        assert response.status_code in [200, 422]
    
    def test_potential_parents_requires_organization_type(self, client: TestClient, auth_headers):
        """Test that potential parents endpoint requires organization_type parameter"""
        response = client.get(
            "/organizations/potential-parents",
            headers=auth_headers["super_admin"]
        )
        assert response.status_code == 422
    
    def test_potential_parents_invalid_organization_type(self, client: TestClient, auth_headers):
        """Test that invalid organization type returns 422"""
        response = client.get(
            "/organizations/potential-parents?organization_type=invalid_type",
            headers=auth_headers["super_admin"]
        )
        assert response.status_code == 422
    
    def test_potential_parents_valid_organization_types(self, client: TestClient, auth_headers):
        """Test that valid organization types return 200"""
        valid_types = ["supplier", "customer", "oraseas_ee", "bossaqua"]
        
        for org_type in valid_types:
            response = client.get(
                f"/organizations/potential-parents?organization_type={org_type}",
                headers=auth_headers["super_admin"]
            )
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_validate_endpoint_exists(self, client: TestClient, auth_headers):
        """Test that validate endpoint exists and requires auth"""
        validation_data = {
            "name": "Test Organization",
            "organization_type": "customer",
            "is_active": True
        }
        
        # Test without auth
        response = client.post("/organizations/validate", json=validation_data)
        assert response.status_code == 401
        
        # Test with auth
        response = client.post(
            "/organizations/validate",
            json=validation_data,
            headers=auth_headers["super_admin"]
        )
        assert response.status_code == 200
    
    def test_validate_endpoint_response_structure(self, client: TestClient, auth_headers):
        """Test that validate endpoint returns correct response structure"""
        validation_data = {
            "name": "Test Organization",
            "organization_type": "customer",
            "is_active": True
        }
        
        response = client.post(
            "/organizations/validate",
            json=validation_data,
            headers=auth_headers["super_admin"]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "valid" in data
        assert "errors" in data
        assert isinstance(data["valid"], bool)
        assert isinstance(data["errors"], list)
    
    def test_validate_endpoint_invalid_request(self, client: TestClient, auth_headers):
        """Test that validate endpoint handles invalid requests"""
        invalid_data = {
            "name": "Test Organization",
            "organization_type": "invalid_type",  # Invalid enum value
            "is_active": True
        }
        
        response = client.post(
            "/organizations/validate",
            json=invalid_data,
            headers=auth_headers["super_admin"]
        )
        
        assert response.status_code == 422
    
    def test_validate_endpoint_missing_required_fields(self, client: TestClient, auth_headers):
        """Test that validate endpoint handles missing required fields"""
        incomplete_data = {
            "organization_type": "customer"
            # Missing required 'name' field
        }
        
        response = client.post(
            "/organizations/validate",
            json=incomplete_data,
            headers=auth_headers["super_admin"]
        )
        
        assert response.status_code == 422
    
    def test_validate_supplier_without_parent_returns_validation_error(self, client: TestClient, auth_headers):
        """Test that supplier without parent returns validation error"""
        validation_data = {
            "name": "Test Supplier",
            "organization_type": "supplier",  # Supplier without parent
            "is_active": True
        }
        
        response = client.post(
            "/organizations/validate",
            json=validation_data,
            headers=auth_headers["super_admin"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0
        
        # Check that there's an error about parent organization
        error_messages = [error["message"] for error in data["errors"]]
        assert any("parent organization" in msg.lower() for msg in error_messages)


# Test fixtures are provided by conftest.py