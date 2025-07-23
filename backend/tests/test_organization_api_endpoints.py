"""
Integration tests for new organization API endpoints.
Tests the /organizations/potential-parents and /organizations/validate endpoints.
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import models
from app.models import OrganizationType


class TestPotentialParentsEndpoint:
    """Test cases for GET /organizations/potential-parents endpoint"""
    
    def test_get_potential_parents_for_supplier(self, client: TestClient, db_session: Session, auth_headers, test_organizations):
        """Test getting potential parents for supplier organization type"""
        # Use existing test organizations from fixtures
        
        # Make API request
        response = client.get(
            "/organizations/potential-parents?organization_type=supplier",
            headers=auth_headers["super_admin"]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return customer and oraseas_ee organizations
        # From test fixtures we have: customer1, customer2, and oraseas
        assert len(data) >= 2  # At least customer and oraseas_ee
        org_types = [org["organization_type"] for org in data]
        assert "customer" in org_types
        assert "oraseas_ee" in org_types
        assert "bossaqua" not in org_types
    
    def test_get_potential_parents_for_customer_returns_empty(self, client: TestClient, db_session: Session, auth_headers):
        """Test that customer organization type returns empty potential parents"""
        # Create test organizations
        customer_org = models.Organization(
            id=uuid.uuid4(),
            name="Test Customer",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(customer_org)
        db_session.commit()
        
        # Make API request
        response = client.get(
            "/organizations/potential-parents?organization_type=customer",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_get_potential_parents_excludes_inactive(self, client: TestClient, db_session: Session, auth_headers):
        """Test that inactive organizations are excluded from potential parents"""
        # Create active and inactive organizations
        active_customer = models.Organization(
            id=uuid.uuid4(),
            name="Active Customer",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        inactive_customer = models.Organization(
            id=uuid.uuid4(),
            name="Inactive Customer",
            organization_type=OrganizationType.customer,
            is_active=False
        )
        
        db_session.add_all([active_customer, inactive_customer])
        db_session.commit()
        
        # Make API request
        response = client.get(
            "/organizations/potential-parents?organization_type=supplier",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only return active customer
        assert len(data) == 1
        assert data[0]["name"] == "Active Customer"
        assert data[0]["is_active"] is True
    
    def test_get_potential_parents_requires_auth(self, client: TestClient, db_session: Session):
        """Test that potential parents endpoint requires authentication"""
        response = client.get("/organizations/potential-parents?organization_type=supplier")
        
        assert response.status_code == 401
    
    def test_get_potential_parents_missing_type_parameter(self, client: TestClient, auth_headers):
        """Test that missing organization_type parameter returns 422"""
        response = client.get("/organizations/potential-parents", headers=auth_headers)
        
        assert response.status_code == 422
    
    def test_get_potential_parents_invalid_type_parameter(self, client: TestClient, auth_headers):
        """Test that invalid organization_type parameter returns 422"""
        response = client.get(
            "/organizations/potential-parents?organization_type=invalid_type",
            headers=auth_headers
        )
        
        assert response.status_code == 422


class TestValidateOrganizationEndpoint:
    """Test cases for POST /organizations/validate endpoint"""
    
    def test_validate_valid_customer_organization(self, client: TestClient, db_session: Session, auth_headers):
        """Test validation of a valid customer organization"""
        validation_data = {
            "name": "Test Customer",
            "organization_type": "customer",
            "is_active": True
        }
        
        response = client.post(
            "/organizations/validate",
            json=validation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["errors"] == []
    
    def test_validate_valid_supplier_with_parent(self, client: TestClient, db_session: Session, auth_headers):
        """Test validation of a valid supplier organization with parent"""
        # Create parent organization
        parent_org = models.Organization(
            id=uuid.uuid4(),
            name="Parent Customer",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(parent_org)
        db_session.commit()
        
        validation_data = {
            "name": "Test Supplier",
            "organization_type": "supplier",
            "parent_organization_id": str(parent_org.id),
            "is_active": True
        }
        
        response = client.post(
            "/organizations/validate",
            json=validation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["errors"] == []
    
    def test_validate_supplier_without_parent_fails(self, client: TestClient, db_session: Session, auth_headers):
        """Test that supplier without parent fails validation"""
        validation_data = {
            "name": "Test Supplier",
            "organization_type": "supplier",
            "is_active": True
        }
        
        response = client.post(
            "/organizations/validate",
            json=validation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) == 1
        assert data["errors"][0]["field"] == "parent_organization_id"
        assert "must have a parent organization" in data["errors"][0]["message"]
    
    def test_validate_singleton_duplicate_fails(self, client: TestClient, db_session: Session, auth_headers):
        """Test that duplicate singleton organization fails validation"""
        # Create existing Oraseas EE organization
        existing_oraseas = models.Organization(
            id=uuid.uuid4(),
            name="Existing Oraseas EE",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        db_session.add(existing_oraseas)
        db_session.commit()
        
        validation_data = {
            "name": "New Oraseas EE",
            "organization_type": "oraseas_ee",
            "is_active": True
        }
        
        response = client.post(
            "/organizations/validate",
            json=validation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) == 1
        assert data["errors"][0]["field"] == "organization_type"
        assert "Only one oraseas_ee organization is allowed" in data["errors"][0]["message"]
    
    def test_validate_update_existing_organization(self, client: TestClient, db_session: Session, auth_headers):
        """Test validation for updating existing organization"""
        # Create existing organization
        existing_org = models.Organization(
            id=uuid.uuid4(),
            name="Existing Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(existing_org)
        db_session.commit()
        
        validation_data = {
            "name": "Updated Organization",
            "organization_type": "customer",
            "is_active": True,
            "id": str(existing_org.id)
        }
        
        response = client.post(
            "/organizations/validate",
            json=validation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["errors"] == []
    
    def test_validate_invalid_parent_organization(self, client: TestClient, db_session: Session, auth_headers):
        """Test validation with invalid parent organization ID"""
        non_existent_id = str(uuid.uuid4())
        
        validation_data = {
            "name": "Test Supplier",
            "organization_type": "supplier",
            "parent_organization_id": non_existent_id,
            "is_active": True
        }
        
        response = client.post(
            "/organizations/validate",
            json=validation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) == 1
        assert data["errors"][0]["field"] == "parent_organization_id"
        assert "Parent organization not found" in data["errors"][0]["message"]
    
    def test_validate_empty_name_fails(self, client: TestClient, db_session: Session, auth_headers):
        """Test that empty organization name fails validation"""
        validation_data = {
            "name": "",
            "organization_type": "customer",
            "is_active": True
        }
        
        response = client.post(
            "/organizations/validate",
            json=validation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) == 1
        assert data["errors"][0]["field"] == "name"
        assert "Organization name is required" in data["errors"][0]["message"]
    
    def test_validate_multiple_errors(self, client: TestClient, db_session: Session, auth_headers):
        """Test that multiple validation errors are returned"""
        validation_data = {
            "name": "",  # Empty name
            "organization_type": "supplier",  # Supplier without parent
            "is_active": True
        }
        
        response = client.post(
            "/organizations/validate",
            json=validation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) == 2
        
        # Check that both errors are present
        error_fields = [error["field"] for error in data["errors"]]
        assert "name" in error_fields
        assert "parent_organization_id" in error_fields
    
    def test_validate_requires_auth(self, client: TestClient, db_session: Session):
        """Test that validate endpoint requires authentication"""
        validation_data = {
            "name": "Test Organization",
            "organization_type": "customer",
            "is_active": True
        }
        
        response = client.post("/organizations/validate", json=validation_data)
        
        assert response.status_code == 401
    
    def test_validate_invalid_request_body(self, client: TestClient, auth_headers):
        """Test that invalid request body returns 422"""
        invalid_data = {
            "name": "Test Organization",
            "organization_type": "invalid_type",  # Invalid enum value
            "is_active": True
        }
        
        response = client.post(
            "/organizations/validate",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_validate_missing_required_fields(self, client: TestClient, auth_headers):
        """Test that missing required fields returns 422"""
        incomplete_data = {
            "organization_type": "customer"
            # Missing required 'name' field
        }
        
        response = client.post(
            "/organizations/validate",
            json=incomplete_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422


# Test fixtures are provided by conftest.py