"""
Unit tests for organization business rule validation.
Tests the specific business rules for organization creation and updates.
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import OrganizationType
from app.crud.organizations import create_organization, validate_organization_data
from app.schemas import OrganizationCreate


class TestOrganizationBusinessRules:
    """Test organization business rule validation."""
    
    def test_singleton_organization_validation(self, db_session: Session):
        """Test that only one Oraseas EE and BossAqua organization can exist."""
        # Create first Oraseas EE organization
        oraseas_data = OrganizationCreate(
            name="Oraseas EE",
            organization_type="oraseas_ee",
            country="GR"
        )
        
        first_oraseas = create_organization(db_session, oraseas_data)
        assert first_oraseas.organization_type == OrganizationType.oraseas_ee
        
        # Try to create second Oraseas EE organization (should fail)
        duplicate_oraseas_data = OrganizationCreate(
            name="Another Oraseas EE",
            organization_type="oraseas_ee",
            country="ES"
        )
        
        with pytest.raises(ValueError) as exc_info:
            create_organization(db_session, duplicate_oraseas_data)
        
        assert "only one oraseas_ee organization is allowed" in str(exc_info.value).lower()
        
        # Create first BossAqua organization
        bossaqua_data = OrganizationCreate(
            name="BossAqua",
            organization_type="bossaqua",
            country="GR"
        )
        
        first_bossaqua = create_organization(db_session, bossaqua_data)
        assert first_bossaqua.organization_type == OrganizationType.bossaqua
        
        # Try to create second BossAqua organization (should fail)
        duplicate_bossaqua_data = OrganizationCreate(
            name="Another BossAqua",
            organization_type="bossaqua",
            country="CY"
        )
        
        with pytest.raises(ValueError) as exc_info:
            create_organization(db_session, duplicate_bossaqua_data)
        
        assert "only one bossaqua organization is allowed" in str(exc_info.value).lower()
    
    def test_supplier_parent_requirement(self, db_session: Session):
        """Test that supplier organizations must have a parent."""
        # Try to create supplier without parent (should fail)
        orphan_supplier_data = OrganizationCreate(
            name="Orphan Supplier",
            organization_type="supplier",
            country="GR"
        )
        
        with pytest.raises(ValueError) as exc_info:
            create_organization(db_session, orphan_supplier_data)
        
        assert "supplier organizations must have a parent organization" in str(exc_info.value).lower()
        
        # Create a customer organization first
        customer_data = OrganizationCreate(
            name="Test Customer",
            organization_type="customer",
            country="KSA"
        )
        
        customer = create_organization(db_session, customer_data)
        
        # Now create supplier with parent (should succeed)
        supplier_data = OrganizationCreate(
            name="Valid Supplier",
            organization_type="supplier",
            parent_organization_id=customer.id,
            country="ES"
        )
        
        supplier = create_organization(db_session, supplier_data)
        assert supplier.organization_type == OrganizationType.supplier
        assert supplier.parent_organization_id == customer.id
    
    def test_validation_function_consistency(self, db_session: Session):
        """Test that the validation function returns consistent results with create_organization."""
        # Test singleton validation
        oraseas_data = {
            "name": "Oraseas EE",
            "organization_type": "oraseas_ee",
            "country": "GR"
        }
        
        # First organization should validate successfully
        validation_result = validate_organization_data(db_session, oraseas_data)
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
        
        # Create the organization
        create_organization(db_session, OrganizationCreate(**oraseas_data))
        
        # Second organization should fail validation
        duplicate_data = {
            "name": "Another Oraseas EE",
            "organization_type": "oraseas_ee",
            "country": "ES"
        }
        
        validation_result = validate_organization_data(db_session, duplicate_data)
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
        assert any("only one oraseas_ee organization is allowed" in error["message"].lower() 
                  for error in validation_result["errors"])
    
    def test_invalid_organization_type_handling(self, db_session: Session):
        """Test handling of invalid organization types."""
        # Test with invalid string type
        invalid_data = {
            "name": "Invalid Org",
            "organization_type": "invalid_type",
            "country": "GR"
        }
        
        with pytest.raises(ValueError) as exc_info:
            create_organization(db_session, OrganizationCreate(**invalid_data))
        
        # The error should be caught during Pydantic validation, not in our CRUD function
        # But if it somehow gets through, our CRUD should handle it
        assert "invalid" in str(exc_info.value).lower()
    
    def test_customer_organization_creates_default_warehouse(self, db_session: Session):
        """Test that customer organizations automatically get a default warehouse."""
        customer_data = OrganizationCreate(
            name="Test Customer with Warehouse",
            organization_type="customer",
            country="OM"
        )
        
        customer = create_organization(db_session, customer_data)
        
        # Check that a warehouse was created
        assert len(customer.warehouses) == 1
        warehouse = customer.warehouses[0]
        assert warehouse.name == customer.name
        assert warehouse.organization_id == customer.id
        assert warehouse.is_active is True


class TestOrganizationAPIBusinessRules:
    """Test organization business rules through the API."""
    
    def test_api_singleton_validation(self, client: TestClient, auth_headers):
        """Test singleton validation through the API."""
        headers = auth_headers["super_admin"]
        
        # Note: Oraseas EE already exists from conftest fixtures
        # Try to create duplicate Oraseas EE (should fail)
        duplicate_data = {
            "name": "Another Oraseas EE",
            "organization_type": "oraseas_ee",
            "country": "ES",
            "address": "Spain Office",
            "contact_info": "spain@oraseas.com"
        }
        
        response = client.post("/organizations/", json=duplicate_data, headers=headers)
        assert response.status_code == 400
        assert "only one" in response.json()["detail"].lower()
        
        # Try to create duplicate BossAqua (should also fail since it exists from fixtures)
        duplicate_bossaqua = {
            "name": "Another BossAqua",
            "organization_type": "bossaqua",
            "country": "CY",
            "address": "Cyprus Office",
            "contact_info": "cyprus@bossaqua.com"
        }
        
        response = client.post("/organizations/", json=duplicate_bossaqua, headers=headers)
        assert response.status_code == 400
        assert "only one" in response.json()["detail"].lower()
    
    def test_api_supplier_parent_validation(self, client: TestClient, auth_headers):
        """Test supplier parent requirement through the API."""
        headers = auth_headers["super_admin"]
        
        # Try to create supplier without parent
        orphan_supplier = {
            "name": "Orphan Supplier",
            "organization_type": "supplier",
            "country": "GR",
            "address": "Supplier Street",
            "contact_info": "supplier@example.com"
        }
        
        response = client.post("/organizations/", json=orphan_supplier, headers=headers)
        assert response.status_code == 400
        assert "parent" in response.json()["detail"].lower()
    
    def test_api_validation_endpoint(self, client: TestClient, auth_headers):
        """Test the validation endpoint."""
        headers = auth_headers["super_admin"]
        
        # Test valid data
        valid_data = {
            "name": "Valid Organization",
            "organization_type": "customer",
            "country": "KSA"
        }
        
        response = client.post("/organizations/validate", json=valid_data, headers=headers)
        assert response.status_code == 200
        validation_result = response.json()
        assert validation_result["valid"] is True
        
        # Test invalid data (supplier without parent)
        invalid_data = {
            "name": "Invalid Supplier",
            "organization_type": "supplier",
            "country": "ES"
        }
        
        response = client.post("/organizations/validate", json=invalid_data, headers=headers)
        assert response.status_code == 400
        assert "parent" in response.json()["detail"].lower()