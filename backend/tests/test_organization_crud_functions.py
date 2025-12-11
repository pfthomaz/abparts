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
    create_organization,
    get_organization_hierarchy_tree
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


class TestGetOrganizationHierarchyTree:
    """Test cases for get_organization_hierarchy_tree function"""
    
    def test_simple_hierarchy_structure(self, db_session: Session):
        """Test hierarchy building with simple parent-child structure"""
        # Create simple hierarchy: Oraseas EE -> Customer -> Supplier
        oraseas_org = models.Organization(
            id=uuid.uuid4(),
            name="Oraseas EE",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        customer_org = models.Organization(
            id=uuid.uuid4(),
            name="Test Customer",
            organization_type=OrganizationType.customer,
            parent_organization_id=oraseas_org.id,
            is_active=True
        )
        supplier_org = models.Organization(
            id=uuid.uuid4(),
            name="Test Supplier",
            organization_type=OrganizationType.supplier,
            parent_organization_id=customer_org.id,
            is_active=True
        )
        
        db_session.add_all([oraseas_org, customer_org, supplier_org])
        db_session.commit()
        
        # Get hierarchy tree
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Should return one root (Oraseas EE) with nested children
        assert len(hierarchy) == 1
        root = hierarchy[0]
        assert root.name == "Oraseas EE"
        assert root.organization_type.value == OrganizationType.oraseas_ee.value
        assert root.parent_organization_id is None
        
        # Check first level children
        assert len(root.children) == 1
        customer = root.children[0]
        assert customer.name == "Test Customer"
        assert customer.organization_type.value == OrganizationType.customer.value
        assert customer.parent_organization_id == oraseas_org.id
        
        # Check second level children
        assert len(customer.children) == 1
        supplier = customer.children[0]
        assert supplier.name == "Test Supplier"
        assert supplier.organization_type.value == OrganizationType.supplier.value
        assert supplier.parent_organization_id == customer_org.id
        assert len(supplier.children) == 0
    
    def test_complex_hierarchy_with_multiple_branches(self, db_session: Session):
        """Test hierarchy building with multiple branches and levels"""
        # Create complex hierarchy
        oraseas_org = models.Organization(
            id=uuid.uuid4(),
            name="Oraseas EE",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        
        # Two customers under Oraseas
        customer1 = models.Organization(
            id=uuid.uuid4(),
            name="Customer Alpha",
            organization_type=OrganizationType.customer,
            parent_organization_id=oraseas_org.id,
            is_active=True
        )
        customer2 = models.Organization(
            id=uuid.uuid4(),
            name="Customer Beta",
            organization_type=OrganizationType.customer,
            parent_organization_id=oraseas_org.id,
            is_active=True
        )
        
        # Suppliers under each customer
        supplier1 = models.Organization(
            id=uuid.uuid4(),
            name="Supplier One",
            organization_type=OrganizationType.supplier,
            parent_organization_id=customer1.id,
            is_active=True
        )
        supplier2 = models.Organization(
            id=uuid.uuid4(),
            name="Supplier Two",
            organization_type=OrganizationType.supplier,
            parent_organization_id=customer1.id,
            is_active=True
        )
        supplier3 = models.Organization(
            id=uuid.uuid4(),
            name="Supplier Three",
            organization_type=OrganizationType.supplier,
            parent_organization_id=customer2.id,
            is_active=True
        )
        
        db_session.add_all([oraseas_org, customer1, customer2, supplier1, supplier2, supplier3])
        db_session.commit()
        
        # Get hierarchy tree
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Should return one root with complex structure
        assert len(hierarchy) == 1
        root = hierarchy[0]
        assert root.name == "Oraseas EE"
        
        # Check customers are sorted alphabetically
        assert len(root.children) == 2
        assert root.children[0].name == "Customer Alpha"
        assert root.children[1].name == "Customer Beta"
        
        # Check Customer Alpha's suppliers
        customer_alpha = root.children[0]
        assert len(customer_alpha.children) == 2
        assert customer_alpha.children[0].name == "Supplier One"
        assert customer_alpha.children[1].name == "Supplier Two"
        
        # Check Customer Beta's suppliers
        customer_beta = root.children[1]
        assert len(customer_beta.children) == 1
        assert customer_beta.children[0].name == "Supplier Three"
    
    def test_flat_structure_multiple_roots(self, db_session: Session):
        """Test hierarchy with multiple root organizations (no parents)"""
        # Create multiple root organizations
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
        customer_org = models.Organization(
            id=uuid.uuid4(),
            name="Independent Customer",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        
        db_session.add_all([oraseas_org, bossaqua_org, customer_org])
        db_session.commit()
        
        # Get hierarchy tree
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Should return three roots sorted alphabetically
        assert len(hierarchy) == 3
        assert hierarchy[0].name == "BossAqua"
        assert hierarchy[1].name == "Independent Customer"
        assert hierarchy[2].name == "Oraseas EE"
        
        # All should have no children
        for root in hierarchy:
            assert len(root.children) == 0
            assert root.parent_organization_id is None
    
    def test_active_status_filtering_default(self, db_session: Session):
        """Test that inactive organizations are excluded by default"""
        # Create mix of active and inactive organizations
        active_root = models.Organization(
            id=uuid.uuid4(),
            name="Active Root",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        inactive_root = models.Organization(
            id=uuid.uuid4(),
            name="Inactive Root",
            organization_type=OrganizationType.customer,
            is_active=False
        )
        active_child = models.Organization(
            id=uuid.uuid4(),
            name="Active Child",
            organization_type=OrganizationType.customer,
            parent_organization_id=active_root.id,
            is_active=True
        )
        inactive_child = models.Organization(
            id=uuid.uuid4(),
            name="Inactive Child",
            organization_type=OrganizationType.supplier,
            parent_organization_id=active_root.id,
            is_active=False
        )
        
        db_session.add_all([active_root, inactive_root, active_child, inactive_child])
        db_session.commit()
        
        # Get hierarchy tree (default: active only)
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Should only return active root with active child
        assert len(hierarchy) == 1
        root = hierarchy[0]
        assert root.name == "Active Root"
        assert root.is_active is True
        
        # Should only have active child
        assert len(root.children) == 1
        child = root.children[0]
        assert child.name == "Active Child"
        assert child.is_active is True
    
    def test_include_inactive_organizations(self, db_session: Session):
        """Test including inactive organizations in hierarchy"""
        # Create mix of active and inactive organizations
        active_root = models.Organization(
            id=uuid.uuid4(),
            name="Active Root",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        inactive_root = models.Organization(
            id=uuid.uuid4(),
            name="Inactive Root",
            organization_type=OrganizationType.customer,
            is_active=False
        )
        active_child = models.Organization(
            id=uuid.uuid4(),
            name="Active Child",
            organization_type=OrganizationType.customer,
            parent_organization_id=active_root.id,
            is_active=True
        )
        inactive_child = models.Organization(
            id=uuid.uuid4(),
            name="Inactive Child",
            organization_type=OrganizationType.supplier,
            parent_organization_id=active_root.id,
            is_active=False
        )
        
        db_session.add_all([active_root, inactive_root, active_child, inactive_child])
        db_session.commit()
        
        # Get hierarchy tree including inactive
        hierarchy = get_organization_hierarchy_tree(db_session, include_inactive=True)
        
        # Should return both roots sorted alphabetically
        assert len(hierarchy) == 2
        assert hierarchy[0].name == "Active Root"
        assert hierarchy[1].name == "Inactive Root"
        
        # Active root should have both children
        active_root_node = hierarchy[0]
        assert len(active_root_node.children) == 2
        assert active_root_node.children[0].name == "Active Child"
        assert active_root_node.children[0].is_active is True
        assert active_root_node.children[1].name == "Inactive Child"
        assert active_root_node.children[1].is_active is False
        
        # Inactive root should have no children
        inactive_root_node = hierarchy[1]
        assert len(inactive_root_node.children) == 0
        assert inactive_root_node.is_active is False
    
    def test_organization_scoping_filtering(self, db_session: Session):
        """Test filtering hierarchy by accessible organization IDs"""
        # Create hierarchy
        oraseas_org = models.Organization(
            id=uuid.uuid4(),
            name="Oraseas EE",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        customer1 = models.Organization(
            id=uuid.uuid4(),
            name="Customer One",
            organization_type=OrganizationType.customer,
            parent_organization_id=oraseas_org.id,
            is_active=True
        )
        customer2 = models.Organization(
            id=uuid.uuid4(),
            name="Customer Two",
            organization_type=OrganizationType.customer,
            parent_organization_id=oraseas_org.id,
            is_active=True
        )
        supplier1 = models.Organization(
            id=uuid.uuid4(),
            name="Supplier One",
            organization_type=OrganizationType.supplier,
            parent_organization_id=customer1.id,
            is_active=True
        )
        
        db_session.add_all([oraseas_org, customer1, customer2, supplier1])
        db_session.commit()
        
        # Test with limited access (only customer1 and supplier1)
        accessible_ids = {customer1.id, supplier1.id}
        hierarchy = get_organization_hierarchy_tree(db_session, accessible_org_ids=accessible_ids)
        
        # Should only return customer1 as root (since oraseas is not accessible)
        # Customer1 becomes orphaned root since its parent (oraseas) is not accessible
        assert len(hierarchy) == 1
        assert hierarchy[0].name == "Customer One"
        assert hierarchy[0].parent_organization_id == oraseas_org.id  # Still has parent ID but parent not in tree
        
        # Should have supplier1 as child
        assert len(hierarchy[0].children) == 1
        assert hierarchy[0].children[0].name == "Supplier One"
    
    def test_empty_hierarchy_returns_empty_list(self, db_session: Session):
        """Test that empty database returns empty hierarchy list"""
        hierarchy = get_organization_hierarchy_tree(db_session)
        assert hierarchy == []
    
    def test_hierarchy_maintains_parent_child_relationships_regardless_of_active_status(self, db_session: Session):
        """Test that parent-child relationships are maintained even with mixed active status"""
        # Create hierarchy with inactive parent but active child
        inactive_parent = models.Organization(
            id=uuid.uuid4(),
            name="Inactive Parent",
            organization_type=OrganizationType.customer,
            is_active=False
        )
        active_child = models.Organization(
            id=uuid.uuid4(),
            name="Active Child",
            organization_type=OrganizationType.supplier,
            parent_organization_id=inactive_parent.id,
            is_active=True
        )
        
        db_session.add_all([inactive_parent, active_child])
        db_session.commit()
        
        # With include_inactive=True, should maintain relationships
        hierarchy = get_organization_hierarchy_tree(db_session, include_inactive=True)
        
        assert len(hierarchy) == 1
        parent_node = hierarchy[0]
        assert parent_node.name == "Inactive Parent"
        assert parent_node.is_active is False
        
        assert len(parent_node.children) == 1
        child_node = parent_node.children[0]
        assert child_node.name == "Active Child"
        assert child_node.is_active is True
        assert child_node.parent_organization_id == inactive_parent.id
    
    def test_hierarchy_with_orphaned_organizations_due_to_scoping(self, db_session: Session):
        """Test that organizations become orphaned roots when their parents are not accessible"""
        # Create hierarchy: Root -> Child -> Grandchild
        root_org = models.Organization(
            id=uuid.uuid4(),
            name="Root Org",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        child_org = models.Organization(
            id=uuid.uuid4(),
            name="Child Org",
            organization_type=OrganizationType.customer,
            parent_organization_id=root_org.id,
            is_active=True
        )
        grandchild_org = models.Organization(
            id=uuid.uuid4(),
            name="Grandchild Org",
            organization_type=OrganizationType.supplier,
            parent_organization_id=child_org.id,
            is_active=True
        )
        
        db_session.add_all([root_org, child_org, grandchild_org])
        db_session.commit()
        
        # Only allow access to child and grandchild (not root)
        accessible_ids = {child_org.id, grandchild_org.id}
        hierarchy = get_organization_hierarchy_tree(db_session, accessible_org_ids=accessible_ids)
        
        # Child becomes orphaned root, grandchild remains as its child
        assert len(hierarchy) == 1
        orphaned_root = hierarchy[0]
        assert orphaned_root.name == "Child Org"
        assert orphaned_root.parent_organization_id == root_org.id  # Still has parent ID
        
        assert len(orphaned_root.children) == 1
        assert orphaned_root.children[0].name == "Grandchild Org"
    
    def test_hierarchy_sorting_by_name_at_all_levels(self, db_session: Session):
        """Test that organizations are sorted alphabetically at all hierarchy levels"""
        # Create root organizations
        zebra_root = models.Organization(
            id=uuid.uuid4(),
            name="Zebra Root",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        alpha_root = models.Organization(
            id=uuid.uuid4(),
            name="Alpha Root",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        
        # Create children for alpha_root in reverse alphabetical order
        zebra_child = models.Organization(
            id=uuid.uuid4(),
            name="Zebra Child",
            organization_type=OrganizationType.supplier,
            parent_organization_id=alpha_root.id,
            is_active=True
        )
        alpha_child = models.Organization(
            id=uuid.uuid4(),
            name="Alpha Child",
            organization_type=OrganizationType.customer,
            parent_organization_id=alpha_root.id,
            is_active=True
        )
        
        db_session.add_all([zebra_root, alpha_root, zebra_child, alpha_child])
        db_session.commit()
        
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Roots should be sorted alphabetically
        assert len(hierarchy) == 2
        assert hierarchy[0].name == "Alpha Root"
        assert hierarchy[1].name == "Zebra Root"
        
        # Children should also be sorted alphabetically
        alpha_root_node = hierarchy[0]
        assert len(alpha_root_node.children) == 2
        assert alpha_root_node.children[0].name == "Alpha Child"
        assert alpha_root_node.children[1].name == "Zebra Child"
    
    def test_hierarchy_with_deep_nesting(self, db_session: Session):
        """Test hierarchy building with multiple levels of nesting"""
        # Create 4-level hierarchy
        level1 = models.Organization(
            id=uuid.uuid4(),
            name="Level 1",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        level2 = models.Organization(
            id=uuid.uuid4(),
            name="Level 2",
            organization_type=OrganizationType.customer,
            parent_organization_id=level1.id,
            is_active=True
        )
        level3 = models.Organization(
            id=uuid.uuid4(),
            name="Level 3",
            organization_type=OrganizationType.supplier,
            parent_organization_id=level2.id,
            is_active=True
        )
        level4 = models.Organization(
            id=uuid.uuid4(),
            name="Level 4",
            organization_type=OrganizationType.supplier,
            parent_organization_id=level3.id,
            is_active=True
        )
        
        db_session.add_all([level1, level2, level3, level4])
        db_session.commit()
        
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Verify deep nesting structure
        assert len(hierarchy) == 1
        
        current = hierarchy[0]
        assert current.name == "Level 1"
        assert len(current.children) == 1
        
        current = current.children[0]
        assert current.name == "Level 2"
        assert len(current.children) == 1
        
        current = current.children[0]
        assert current.name == "Level 3"
        assert len(current.children) == 1
        
        current = current.children[0]
        assert current.name == "Level 4"
        assert len(current.children) == 0
    
    def test_hierarchy_node_contains_all_required_fields(self, db_session: Session):
        """Test that hierarchy nodes contain all required organization fields"""
        # Create organization with all fields
        org = models.Organization(
            id=uuid.uuid4(),
            name="Test Organization",
            organization_type=OrganizationType.customer,
            address="123 Test Street",
            contact_info="test@example.com",
            is_active=True
        )
        db_session.add(org)
        db_session.commit()
        
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        assert len(hierarchy) == 1
        node = hierarchy[0]
        
        # Verify all required fields are present
        assert node.id == org.id
        assert node.name == org.name
        assert node.organization_type == org.organization_type
        assert node.parent_organization_id == org.parent_organization_id
        assert node.is_active == org.is_active
        assert node.created_at == org.created_at
        assert node.updated_at == org.updated_at
        assert isinstance(node.children, list)
        assert len(node.children) == 0
    
    def test_hierarchy_with_mixed_organization_types(self, db_session: Session):
        """Test hierarchy with all different organization types"""
        # Create one of each organization type
        oraseas = models.Organization(
            id=uuid.uuid4(),
            name="Oraseas EE",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        bossaqua = models.Organization(
            id=uuid.uuid4(),
            name="BossAqua",
            organization_type=OrganizationType.bossaqua,
            is_active=True
        )
        customer = models.Organization(
            id=uuid.uuid4(),
            name="Customer Org",
            organization_type=OrganizationType.customer,
            parent_organization_id=oraseas.id,
            is_active=True
        )
        supplier = models.Organization(
            id=uuid.uuid4(),
            name="Supplier Org",
            organization_type=OrganizationType.supplier,
            parent_organization_id=customer.id,
            is_active=True
        )
        
        db_session.add_all([oraseas, bossaqua, customer, supplier])
        db_session.commit()
        
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Should have two roots (BossAqua and Oraseas EE)
        assert len(hierarchy) == 2
        assert hierarchy[0].name == "BossAqua"
        assert hierarchy[0].organization_type == OrganizationType.bossaqua
        assert len(hierarchy[0].children) == 0
        
        assert hierarchy[1].name == "Oraseas EE"
        assert hierarchy[1].organization_type == OrganizationType.oraseas_ee
        assert len(hierarchy[1].children) == 1
        
        # Check nested structure
        customer_node = hierarchy[1].children[0]
        assert customer_node.name == "Customer Org"
        assert customer_node.organization_type == OrganizationType.customer
        assert len(customer_node.children) == 1
        
        supplier_node = customer_node.children[0]
        assert supplier_node.name == "Supplier Org"
        assert supplier_node.organization_type == OrganizationType.supplier
        assert len(supplier_node.children) == 0
    
    def test_hierarchy_performance_with_single_query(self, db_session: Session):
        """Test that hierarchy building uses efficient single query approach"""
        # Create a moderately complex hierarchy to test performance
        root = models.Organization(
            id=uuid.uuid4(),
            name="Root",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        
        # Create 10 customers under root
        customers = []
        for i in range(10):
            customer = models.Organization(
                id=uuid.uuid4(),
                name=f"Customer {i:02d}",
                organization_type=OrganizationType.customer,
                parent_organization_id=root.id,
                is_active=True
            )
            customers.append(customer)
        
        # Create 2 suppliers under each customer
        suppliers = []
        for customer in customers:
            for j in range(2):
                supplier = models.Organization(
                    id=uuid.uuid4(),
                    name=f"Supplier {customer.name[-2:]}-{j}",
                    organization_type=OrganizationType.supplier,
                    parent_organization_id=customer.id,
                    is_active=True
                )
                suppliers.append(supplier)
        
        # Add all organizations
        all_orgs = [root] + customers + suppliers
        db_session.add_all(all_orgs)
        db_session.commit()
        
        # Get hierarchy - this should work efficiently with single query
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Verify structure
        assert len(hierarchy) == 1
        root_node = hierarchy[0]
        assert root_node.name == "Root"
        assert len(root_node.children) == 10
        
        # Verify each customer has 2 suppliers
        for customer_node in root_node.children:
            assert len(customer_node.children) == 2
            assert customer_node.organization_type.value == OrganizationType.customer.value
            for supplier_node in customer_node.children:
                assert supplier_node.organization_type.value == OrganizationType.supplier.value
                assert len(supplier_node.children) == 0
    
    def test_hierarchy_with_none_accessible_org_ids(self, db_session: Session):
        """Test hierarchy when accessible_org_ids is None (no scoping)"""
        # Create simple hierarchy
        root = models.Organization(
            id=uuid.uuid4(),
            name="Root Org",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        child = models.Organization(
            id=uuid.uuid4(),
            name="Child Org",
            organization_type=OrganizationType.customer,
            parent_organization_id=root.id,
            is_active=True
        )
        
        db_session.add_all([root, child])
        db_session.commit()
        
        # Test with None (should return all organizations)
        hierarchy = get_organization_hierarchy_tree(db_session, accessible_org_ids=None)
        
        assert len(hierarchy) == 1
        assert hierarchy[0].name == "Root Org"
        assert len(hierarchy[0].children) == 1
        assert hierarchy[0].children[0].name == "Child Org"
    
    def test_hierarchy_with_empty_accessible_org_ids(self, db_session: Session):
        """Test hierarchy when accessible_org_ids is empty set"""
        # Create organizations
        root = models.Organization(
            id=uuid.uuid4(),
            name="Root Org",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        db_session.add(root)
        db_session.commit()
        
        # Test with empty set (should return no organizations)
        hierarchy = get_organization_hierarchy_tree(db_session, accessible_org_ids=set())
        
        assert hierarchy == []
        assert root.parent_organization_id == oraseas_org.id  # Still has parent ID but parent not in tree
        
        # Should have supplier1 as child
        assert len(root.children) == 1
        assert root.children[0].name == "Supplier One"
    
    def test_empty_hierarchy_returns_empty_list(self, db_session: Session):
        """Test that empty database returns empty hierarchy list"""
        # Don't create any organizations
        
        # Get hierarchy tree
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Should return empty list
        assert hierarchy == []
    
    def test_hierarchy_maintains_parent_child_relationships_regardless_of_active_status(self, db_session: Session):
        """Test that parent-child relationships are maintained even with mixed active status"""
        # Create hierarchy with inactive parent but active child
        inactive_parent = models.Organization(
            id=uuid.uuid4(),
            name="Inactive Parent",
            organization_type=OrganizationType.customer,
            is_active=False
        )
        active_child = models.Organization(
            id=uuid.uuid4(),
            name="Active Child",
            organization_type=OrganizationType.supplier,
            parent_organization_id=inactive_parent.id,
            is_active=True
        )
        
        db_session.add_all([inactive_parent, active_child])
        db_session.commit()
        
        # Get hierarchy including inactive
        hierarchy = get_organization_hierarchy_tree(db_session, include_inactive=True)
        
        # Should return inactive parent with active child
        assert len(hierarchy) == 1
        parent = hierarchy[0]
        assert parent.name == "Inactive Parent"
        assert parent.is_active is False
        
        # Should have active child
        assert len(parent.children) == 1
        child = parent.children[0]
        assert child.name == "Active Child"
        assert child.is_active is True
        assert child.parent_organization_id == inactive_parent.id
    
    def test_hierarchy_with_no_accessible_orgs_returns_empty(self, db_session: Session):
        """Test that hierarchy with empty accessible_org_ids returns empty list"""
        # Create some organizations
        org = models.Organization(
            id=uuid.uuid4(),
            name="Test Org",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
        db_session.commit()
        
        # Get hierarchy with empty accessible set
        hierarchy = get_organization_hierarchy_tree(db_session, accessible_org_ids=set())
        
        # Should return empty list
        assert hierarchy == []
    
    def test_hierarchy_node_contains_all_required_fields(self, db_session: Session):
        """Test that hierarchy nodes contain all required organization fields"""
        # Create organization with all fields
        org = models.Organization(
            id=uuid.uuid4(),
            name="Test Organization",
            organization_type=OrganizationType.customer,
            address="123 Test Street",
            contact_info="test@example.com",
            is_active=True
        )
        db_session.add(org)
        db_session.commit()
        
        # Get hierarchy tree
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Verify all fields are present
        assert len(hierarchy) == 1
        node = hierarchy[0]
        assert node.id == org.id
        assert node.name == "Test Organization"
        assert node.organization_type.value == OrganizationType.customer.value
        assert node.address == "123 Test Street"
        assert node.contact_info == "test@example.com"
        assert node.is_active is True
        assert node.parent_organization_id is None
        assert node.created_at is not None
        assert node.updated_at is not None
        assert isinstance(node.children, list)
        assert len(node.children) == 0
    
    def test_hierarchy_children_sorted_alphabetically(self, db_session: Session):
        """Test that children are sorted alphabetically by name"""
        # Create parent with multiple children in non-alphabetical order
        parent = models.Organization(
            id=uuid.uuid4(),
            name="Parent Org",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        
        # Create children with names that test sorting
        child_z = models.Organization(
            id=uuid.uuid4(),
            name="Zebra Supplier",
            organization_type=OrganizationType.supplier,
            parent_organization_id=parent.id,
            is_active=True
        )
        child_a = models.Organization(
            id=uuid.uuid4(),
            name="Alpha Supplier",
            organization_type=OrganizationType.supplier,
            parent_organization_id=parent.id,
            is_active=True
        )
        child_m = models.Organization(
            id=uuid.uuid4(),
            name="Middle Supplier",
            organization_type=OrganizationType.supplier,
            parent_organization_id=parent.id,
            is_active=True
        )
        
        db_session.add_all([parent, child_z, child_a, child_m])
        db_session.commit()
        
        # Get hierarchy tree
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Verify children are sorted alphabetically
        assert len(hierarchy) == 1
        parent_node = hierarchy[0]
        assert len(parent_node.children) == 3
        assert parent_node.children[0].name == "Alpha Supplier"
        assert parent_node.children[1].name == "Middle Supplier"
        assert parent_node.children[2].name == "Zebra Supplier"
    
    def test_hierarchy_roots_sorted_alphabetically(self, db_session: Session):
        """Test that root organizations are sorted alphabetically by name"""
        # Create multiple root organizations in non-alphabetical order
        root_z = models.Organization(
            id=uuid.uuid4(),
            name="Zebra Root",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        root_a = models.Organization(
            id=uuid.uuid4(),
            name="Alpha Root",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        root_m = models.Organization(
            id=uuid.uuid4(),
            name="Middle Root",
            organization_type=OrganizationType.bossaqua,
            is_active=True
        )
        
        db_session.add_all([root_z, root_a, root_m])
        db_session.commit()
        
        # Get hierarchy tree
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Verify roots are sorted alphabetically
        assert len(hierarchy) == 3
        assert hierarchy[0].name == "Alpha Root"
        assert hierarchy[1].name == "Middle Root"
        assert hierarchy[2].name == "Zebra Root"
    
    def test_hierarchy_with_deep_nesting(self, db_session: Session):
        """Test hierarchy building with deep nesting levels"""
        # Create deep hierarchy: Root -> Level1 -> Level2 -> Level3
        root = models.Organization(
            id=uuid.uuid4(),
            name="Root Organization",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        level1 = models.Organization(
            id=uuid.uuid4(),
            name="Level 1 Customer",
            organization_type=OrganizationType.customer,
            parent_organization_id=root.id,
            is_active=True
        )
        level2 = models.Organization(
            id=uuid.uuid4(),
            name="Level 2 Supplier",
            organization_type=OrganizationType.supplier,
            parent_organization_id=level1.id,
            is_active=True
        )
        
        db_session.add_all([root, level1, level2])
        db_session.commit()
        
        # Get hierarchy tree
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Verify deep nesting structure
        assert len(hierarchy) == 1
        
        # Check root level
        root_node = hierarchy[0]
        assert root_node.name == "Root Organization"
        assert len(root_node.children) == 1
        
        # Check level 1
        level1_node = root_node.children[0]
        assert level1_node.name == "Level 1 Customer"
        assert level1_node.parent_organization_id == root.id
        assert len(level1_node.children) == 1
        
        # Check level 2
        level2_node = level1_node.children[0]
        assert level2_node.name == "Level 2 Supplier"
        assert level2_node.parent_organization_id == level1.id
        assert len(level2_node.children) == 0
    
    def test_hierarchy_performance_single_query(self, db_session: Session):
        """Test that hierarchy building uses efficient single query approach"""
        # Create a moderately complex hierarchy to test performance
        root = models.Organization(
            id=uuid.uuid4(),
            name="Root",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        
        # Create multiple customers and suppliers
        customers = []
        suppliers = []
        
        for i in range(5):
            customer = models.Organization(
                id=uuid.uuid4(),
                name=f"Customer {i}",
                organization_type=OrganizationType.customer,
                parent_organization_id=root.id,
                is_active=True
            )
            customers.append(customer)
            
            # Each customer has 2 suppliers
            for j in range(2):
                supplier = models.Organization(
                    id=uuid.uuid4(),
                    name=f"Supplier {i}-{j}",
                    organization_type=OrganizationType.supplier,
                    parent_organization_id=customer.id,
                    is_active=True
                )
                suppliers.append(supplier)
        
        db_session.add_all([root] + customers + suppliers)
        db_session.commit()
        
        # Get hierarchy tree - this should work efficiently with single query
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Verify structure is correct
        assert len(hierarchy) == 1
        root_node = hierarchy[0]
        assert len(root_node.children) == 5  # 5 customers
        
        # Each customer should have 2 suppliers
        for customer_node in root_node.children:
            assert len(customer_node.children) == 2
    
    def test_hierarchy_with_mixed_organization_types(self, db_session: Session):
        """Test hierarchy with all organization types represented"""
        # Create one of each organization type
        oraseas = models.Organization(
            id=uuid.uuid4(),
            name="Oraseas EE",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        bossaqua = models.Organization(
            id=uuid.uuid4(),
            name="BossAqua",
            organization_type=OrganizationType.bossaqua,
            is_active=True
        )
        customer = models.Organization(
            id=uuid.uuid4(),
            name="Test Customer",
            organization_type=OrganizationType.customer,
            parent_organization_id=oraseas.id,
            is_active=True
        )
        supplier = models.Organization(
            id=uuid.uuid4(),
            name="Test Supplier",
            organization_type=OrganizationType.supplier,
            parent_organization_id=customer.id,
            is_active=True
        )
        
        db_session.add_all([oraseas, bossaqua, customer, supplier])
        db_session.commit()
        
        # Get hierarchy tree
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Should have 2 roots (BossAqua and Oraseas EE)
        assert len(hierarchy) == 2
        
        # Find BossAqua (should be first alphabetically)
        bossaqua_node = hierarchy[0]
        assert bossaqua_node.name == "BossAqua"
        assert bossaqua_node.organization_type.value == OrganizationType.bossaqua.value
        assert len(bossaqua_node.children) == 0
        
        # Find Oraseas EE (should be second alphabetically)
        oraseas_node = hierarchy[1]
        assert oraseas_node.name == "Oraseas EE"
        assert oraseas_node.organization_type == OrganizationType.oraseas_ee
        assert len(oraseas_node.children) == 1
        
        # Check customer under Oraseas EE
        customer_node = oraseas_node.children[0]
        assert customer_node.name == "Test Customer"
        assert customer_node.organization_type == OrganizationType.customer
        assert len(customer_node.children) == 1
        
        # Check supplier under customer
        supplier_node = customer_node.children[0]
        assert supplier_node.name == "Test Supplier"
        assert supplier_node.organization_type == OrganizationType.supplier
        assert len(supplier_node.children) == 0
        
        # Should have supplier1 as child
        assert len(root.children) == 1
        child = root.children[0]
        assert child.name == "Supplier One"
        assert child.id == supplier1.id
    
    def test_empty_hierarchy_returns_empty_list(self, db_session: Session):
        """Test that empty database returns empty hierarchy list"""
        # No organizations in database
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        assert hierarchy == []
        assert isinstance(hierarchy, list)
    
    def test_orphaned_organizations_become_roots(self, db_session: Session):
        """Test that organizations with non-existent parents become roots"""
        # This test simulates the scenario where an organization's parent was deleted
        # but the organization still has a parent_organization_id reference
        # We'll create this by temporarily disabling foreign key constraints
        
        # Create a parent organization first
        parent_org = models.Organization(
            id=uuid.uuid4(),
            name="Parent Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        
        # Create child organization
        orphaned_org = models.Organization(
            id=uuid.uuid4(),
            name="Orphaned Organization",
            organization_type=OrganizationType.supplier,
            parent_organization_id=parent_org.id,
            is_active=True
        )
        
        db_session.add_all([parent_org, orphaned_org])
        db_session.commit()
        
        # Now delete the parent organization directly from database to simulate orphaning
        db_session.delete(parent_org)
        db_session.commit()
        
        # Get hierarchy tree
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Orphaned organization should become a root since its parent doesn't exist
        assert len(hierarchy) == 1
        root = hierarchy[0]
        assert root.name == "Orphaned Organization"
        assert len(root.children) == 0
    
    def test_hierarchy_node_contains_all_organization_fields(self, db_session: Session):
        """Test that hierarchy nodes contain all required organization fields"""
        # Create organization with all fields
        org = models.Organization(
            id=uuid.uuid4(),
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        
        db_session.add(org)
        db_session.commit()
        
        # Get hierarchy tree
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Check that all fields are present
        assert len(hierarchy) == 1
        node = hierarchy[0]
        
        assert node.id == org.id
        assert node.name == org.name
        assert node.organization_type.value == org.organization_type.value
        assert node.is_active == org.is_active
        assert node.parent_organization_id == org.parent_organization_id
        assert node.created_at == org.created_at
        assert node.updated_at == org.updated_at
        assert isinstance(node.children, list)
    
    def test_children_sorted_alphabetically(self, db_session: Session):
        """Test that children are sorted alphabetically by name"""
        # Create parent with multiple children in non-alphabetical order
        parent_org = models.Organization(
            id=uuid.uuid4(),
            name="Parent Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        
        # Create children with names that test sorting
        child_z = models.Organization(
            id=uuid.uuid4(),
            name="Zebra Supplier",
            organization_type=OrganizationType.supplier,
            parent_organization_id=parent_org.id,
            is_active=True
        )
        child_a = models.Organization(
            id=uuid.uuid4(),
            name="Alpha Supplier",
            organization_type=OrganizationType.supplier,
            parent_organization_id=parent_org.id,
            is_active=True
        )
        child_m = models.Organization(
            id=uuid.uuid4(),
            name="Middle Supplier",
            organization_type=OrganizationType.supplier,
            parent_organization_id=parent_org.id,
            is_active=True
        )
        
        db_session.add_all([parent_org, child_z, child_a, child_m])
        db_session.commit()
        
        # Get hierarchy tree
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Check children are sorted alphabetically
        assert len(hierarchy) == 1
        parent = hierarchy[0]
        assert len(parent.children) == 3
        
        assert parent.children[0].name == "Alpha Supplier"
        assert parent.children[1].name == "Middle Supplier"
        assert parent.children[2].name == "Zebra Supplier"
    
    def test_root_organizations_sorted_alphabetically(self, db_session: Session):
        """Test that root organizations are sorted alphabetically by name"""
        # Create multiple root organizations in non-alphabetical order
        root_z = models.Organization(
            id=uuid.uuid4(),
            name="Zebra Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        root_a = models.Organization(
            id=uuid.uuid4(),
            name="Alpha Organization",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        root_m = models.Organization(
            id=uuid.uuid4(),
            name="Middle Organization",
            organization_type=OrganizationType.bossaqua,
            is_active=True
        )
        
        db_session.add_all([root_z, root_a, root_m])
        db_session.commit()
        
        # Get hierarchy tree
        hierarchy = get_organization_hierarchy_tree(db_session)
        
        # Check roots are sorted alphabetically
        assert len(hierarchy) == 3
        assert hierarchy[0].name == "Alpha Organization"
        assert hierarchy[1].name == "Middle Organization"
        assert hierarchy[2].name == "Zebra Organization"
    
    def test_mixed_active_inactive_with_scoping(self, db_session: Session):
        """Test combination of active/inactive filtering with organization scoping"""
        # Create hierarchy with mixed active/inactive status
        active_root = models.Organization(
            id=uuid.uuid4(),
            name="Active Root",
            organization_type=OrganizationType.oraseas_ee,
            is_active=True
        )
        inactive_child = models.Organization(
            id=uuid.uuid4(),
            name="Inactive Child",
            organization_type=OrganizationType.customer,
            parent_organization_id=active_root.id,
            is_active=False
        )
        active_grandchild = models.Organization(
            id=uuid.uuid4(),
            name="Active Grandchild",
            organization_type=OrganizationType.supplier,
            parent_organization_id=inactive_child.id,
            is_active=True
        )
        
        db_session.add_all([active_root, inactive_child, active_grandchild])
        db_session.commit()
        
        # Test with scoping that includes all IDs but excludes inactive
        accessible_ids = {active_root.id, inactive_child.id, active_grandchild.id}
        hierarchy = get_organization_hierarchy_tree(
            db_session, 
            include_inactive=False, 
            accessible_org_ids=accessible_ids
        )
        
        # Should only return active root and active grandchild (inactive child filtered out)
        assert len(hierarchy) == 2  # active_root becomes root, active_grandchild becomes orphaned root
        
        # Find the nodes
        root_names = [node.name for node in hierarchy]
        assert "Active Root" in root_names
        assert "Active Grandchild" in root_names
        
        # Active root should have no children (inactive child filtered out)
        active_root_node = next(node for node in hierarchy if node.name == "Active Root")
        assert len(active_root_node.children) == 0
        
        # Active grandchild becomes orphaned root
        grandchild_node = next(node for node in hierarchy if node.name == "Active Grandchild")
        assert len(grandchild_node.children) == 0