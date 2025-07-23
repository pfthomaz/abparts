"""
Unit tests for new organization CRUD functions.
Tests the get_potential_parent_organizations and validate_organization_data functions.
"""

import pytest
import uuid
from sqlalchemy.orm import Session
from app import models
from app.models import OrganizationType
from app.crud.organizations import (
    get_potential_parent_organizations,
    validate_organization_data,
    create_organization
)
from app.schemas.organization import OrganizationCreate


class TestGetPotentialParentOrganizations:
    """Test cases for get_potential_parent_organizations function"""
    
    def test_supplier_potential_parents_returns_customer_and_oraseas(self, db_session: Session):
        """Test that suppliers can have customer and oraseas_ee organizations as parents"""
        # Create test organizations
        customer_org = models.Organization(
            id=uuid.uuid4(),
            name="Test Customer",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        oraseas_org = models.Organization(
            id=uuid.uuid4(),
            name="Oraseas EE",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        bossaqua_org = models.Organization(
            id=uuid.uuid4(),
            name="BossAqua",
            organization_type=OrganizationType.bossaqua,
            is_active=True
        )
        
        db_session.add_all([customer_org, oraseas_org, bossaqua_org])
        db_session.commit()
        
        # Get potential parents for supplier
        potential_parents = get_potential_parent_organizations(db_session, OrganizationType.supplier)
        
        # Should return customer and oraseas_ee, but not bossaqua
        assert len(potential_parents) == 2
        parent_types = [org.organization_type for org in potential_parents]
        assert OrganizationType.customer in parent_types
        assert OrganizationType.oraseas_ee in parent_types
        assert OrganizationType.bossaqua not in parent_types
    
    def test_supplier_potential_parents_excludes_inactive(self, db_session: Session):
        """Test that inactive organizations are not returned as potential parents"""
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
        
        # Get potential parents for supplier
        potential_parents = get_potential_parent_organizations(db_session, OrganizationType.supplier)
        
        # Should only return active customer
        assert len(potential_parents) == 1
        assert potential_parents[0].name == "Active Customer"
        assert potential_parents[0].is_active is True
    
    def test_non_supplier_types_return_empty_list(self, db_session: Session):
        """Test that non-supplier organization types return empty potential parents list"""
        # Create test organizations
        customer_org = models.Organization(
            id=uuid.uuid4(),
            name="Test Customer",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(customer_org)
        db_session.commit()
        
        # Test each non-supplier type
        for org_type in [OrganizationType.customer, OrganizationType.oraseas_ee, OrganizationType.bossaqua]:
            potential_parents = get_potential_parent_organizations(db_session, org_type)
            assert potential_parents == []
    
    def test_potential_parents_ordered_by_name(self, db_session: Session):
        """Test that potential parents are returned ordered by name"""
        # Create organizations with names that will test ordering
        zebra_customer = models.Organization(
            id=uuid.uuid4(),
            name="Zebra Customer",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        alpha_customer = models.Organization(
            id=uuid.uuid4(),
            name="Alpha Customer",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        
        db_session.add_all([zebra_customer, alpha_customer])
        db_session.commit()
        
        # Get potential parents for supplier
        potential_parents = get_potential_parent_organizations(db_session, OrganizationType.supplier)
        
        # Should be ordered alphabetically
        assert len(potential_parents) == 2
        assert potential_parents[0].name == "Alpha Customer"
        assert potential_parents[1].name == "Zebra Customer"


class TestValidateOrganizationData:
    """Test cases for validate_organization_data function"""
    
    def test_valid_customer_organization(self, db_session: Session):
        """Test validation of a valid customer organization"""
        org_data = {
            "name": "Test Customer",
            "organization_type": OrganizationType.customer,
            "is_active": True
        }
        
        result = validate_organization_data(db_session, org_data)
        
        assert result["valid"] is True
        assert result["errors"] == []
    
    def test_valid_supplier_with_parent(self, db_session: Session):
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
        
        org_data = {
            "name": "Test Supplier",
            "organization_type": OrganizationType.supplier,
            "parent_organization_id": parent_org.id,
            "is_active": True
        }
        
        result = validate_organization_data(db_session, org_data)
        
        assert result["valid"] is True
        assert result["errors"] == []
    
    def test_supplier_without_parent_fails(self, db_session: Session):
        """Test that supplier without parent fails validation"""
        org_data = {
            "name": "Test Supplier",
            "organization_type": OrganizationType.supplier,
            "is_active": True
        }
        
        result = validate_organization_data(db_session, org_data)
        
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert result["errors"][0]["field"] == "parent_organization_id"
        assert "must have a parent organization" in result["errors"][0]["message"]
    
    def test_singleton_organization_duplicate_fails(self, db_session: Session):
        """Test that creating duplicate singleton organizations fails validation"""
        # Create existing Oraseas EE organization
        existing_oraseas = models.Organization(
            id=uuid.uuid4(),
            name="Existing Oraseas EE",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        db_session.add(existing_oraseas)
        db_session.commit()
        
        # Try to validate another Oraseas EE organization
        org_data = {
            "name": "New Oraseas EE",
            "organization_type": OrganizationType.oraseas_ee,
            "is_active": True
        }
        
        result = validate_organization_data(db_session, org_data)
        
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert result["errors"][0]["field"] == "organization_type"
        assert "Only one oraseas_ee organization is allowed" in result["errors"][0]["message"]
    
    def test_singleton_organization_update_allowed(self, db_session: Session):
        """Test that updating existing singleton organization is allowed"""
        # Create existing Oraseas EE organization
        existing_oraseas = models.Organization(
            id=uuid.uuid4(),
            name="Existing Oraseas EE",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        db_session.add(existing_oraseas)
        db_session.commit()
        
        # Validate updating the same organization
        org_data = {
            "name": "Updated Oraseas EE",
            "organization_type": OrganizationType.oraseas_ee,
            "is_active": True
        }
        
        result = validate_organization_data(db_session, org_data, existing_oraseas.id)
        
        assert result["valid"] is True
        assert result["errors"] == []
    
    def test_invalid_parent_organization_fails(self, db_session: Session):
        """Test that invalid parent organization ID fails validation"""
        non_existent_id = uuid.uuid4()
        
        org_data = {
            "name": "Test Supplier",
            "organization_type": OrganizationType.supplier,
            "parent_organization_id": non_existent_id,
            "is_active": True
        }
        
        result = validate_organization_data(db_session, org_data)
        
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert result["errors"][0]["field"] == "parent_organization_id"
        assert "Parent organization not found" in result["errors"][0]["message"]
    
    def test_inactive_parent_organization_fails(self, db_session: Session):
        """Test that inactive parent organization fails validation"""
        # Create inactive parent organization
        inactive_parent = models.Organization(
            id=uuid.uuid4(),
            name="Inactive Parent",
            organization_type=OrganizationType.customer,
            is_active=False
        )
        db_session.add(inactive_parent)
        db_session.commit()
        
        org_data = {
            "name": "Test Supplier",
            "organization_type": OrganizationType.supplier,
            "parent_organization_id": inactive_parent.id,
            "is_active": True
        }
        
        result = validate_organization_data(db_session, org_data)
        
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert result["errors"][0]["field"] == "parent_organization_id"
        assert "Cannot assign inactive parent organization" in result["errors"][0]["message"]
    
    def test_self_parent_fails(self, db_session: Session):
        """Test that organization cannot be its own parent"""
        # Create an existing organization first
        existing_org = models.Organization(
            id=uuid.uuid4(),
            name="Existing Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(existing_org)
        db_session.commit()
        
        org_data = {
            "name": "Test Organization",
            "organization_type": OrganizationType.supplier,
            "parent_organization_id": existing_org.id,
            "is_active": True
        }
        
        result = validate_organization_data(db_session, org_data, existing_org.id)
        
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert result["errors"][0]["field"] == "parent_organization_id"
        assert "cannot be its own parent" in result["errors"][0]["message"]
    
    def test_circular_reference_fails(self, db_session: Session):
        """Test that circular references are prevented"""
        # Create organization hierarchy: A -> B -> C
        org_a = models.Organization(
            id=uuid.uuid4(),
            name="Organization A",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        org_b = models.Organization(
            id=uuid.uuid4(),
            name="Organization B",
            organization_type=OrganizationType.supplier,
            parent_organization_id=org_a.id,
            is_active=True
        )
        org_c = models.Organization(
            id=uuid.uuid4(),
            name="Organization C",
            organization_type=OrganizationType.supplier,
            parent_organization_id=org_b.id,
            is_active=True
        )
        
        db_session.add_all([org_a, org_b, org_c])
        db_session.commit()
        
        # Try to make A a child of C (would create cycle: A -> B -> C -> A)
        org_data = {
            "name": "Organization A",
            "organization_type": OrganizationType.supplier,
            "parent_organization_id": org_c.id,
            "is_active": True
        }
        
        result = validate_organization_data(db_session, org_data, org_a.id)
        
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert result["errors"][0]["field"] == "parent_organization_id"
        assert "circular reference" in result["errors"][0]["message"]
    
    def test_empty_name_fails(self, db_session: Session):
        """Test that empty organization name fails validation"""
        org_data = {
            "name": "",
            "organization_type": OrganizationType.customer,
            "is_active": True
        }
        
        result = validate_organization_data(db_session, org_data)
        
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert result["errors"][0]["field"] == "name"
        assert "Organization name is required" in result["errors"][0]["message"]
    
    def test_whitespace_only_name_fails(self, db_session: Session):
        """Test that whitespace-only organization name fails validation"""
        org_data = {
            "name": "   ",
            "organization_type": OrganizationType.customer,
            "is_active": True
        }
        
        result = validate_organization_data(db_session, org_data)
        
        assert result["valid"] is False
        assert len(result["errors"]) == 1
        assert result["errors"][0]["field"] == "name"
        assert "Organization name is required" in result["errors"][0]["message"]
    
    def test_multiple_validation_errors(self, db_session: Session):
        """Test that multiple validation errors are returned"""
        org_data = {
            "name": "",  # Empty name
            "organization_type": OrganizationType.supplier,  # Supplier without parent
            "is_active": True
        }
        
        result = validate_organization_data(db_session, org_data)
        
        assert result["valid"] is False
        assert len(result["errors"]) == 2
        
        # Check that both errors are present
        error_fields = [error["field"] for error in result["errors"]]
        assert "name" in error_fields
        assert "parent_organization_id" in error_fields
    
    def test_invalid_uuid_format_fails(self, db_session: Session):
        """Test that invalid UUID format for parent ID fails validation"""
        org_data = {
            "name": "Test Supplier",
            "organization_type": OrganizationType.supplier,
            "parent_organization_id": "invalid-uuid-format",
            "is_active": True
        }
        
        result = validate_organization_data(db_session, org_data)
        
        assert result["valid"] is False
        # Should have at least one error about invalid UUID format
        error_messages = [error["message"] for error in result["errors"]]
        assert any("Invalid parent organization ID format" in msg for msg in error_messages)
        # Check that the field is parent_organization_id for the UUID format error
        uuid_format_errors = [error for error in result["errors"] if "Invalid parent organization ID format" in error["message"]]
        assert len(uuid_format_errors) == 1
        assert uuid_format_errors[0]["field"] == "parent_organization_id"
    
    def test_validation_with_pydantic_model(self, db_session: Session):
        """Test validation works with Pydantic model input"""
        # Create parent organization
        parent_org = models.Organization(
            id=uuid.uuid4(),
            name="Parent Customer",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(parent_org)
        db_session.commit()
        
        # Create Pydantic model
        org_create = OrganizationCreate(
            name="Test Supplier",
            organization_type="supplier",
            parent_organization_id=parent_org.id,
            is_active=True
        )
        
        result = validate_organization_data(db_session, org_create)
        
        assert result["valid"] is True
        assert result["errors"] == []


# Test fixtures are provided by conftest.py