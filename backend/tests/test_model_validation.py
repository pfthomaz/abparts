"""
Unit tests for ABParts model validation and business logic.
Tests all new models and business rule validation for the realignment.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import (
    Organization, User, Part, Warehouse, Inventory, Machine, MachineHours,
    OrganizationType, UserRole, UserStatus, PartType, MachineModelType, MachineStatus
)
from app.auth import get_password_hash


class TestOrganizationModelValidation:
    """Test Organization model validation and business rules."""
    
    def test_organization_country_validation(self, db_session: Session):
        """Test that organization country field accepts valid values."""
        # Test valid countries
        valid_countries = ['GR', 'KSA', 'ES', 'CY', 'OM']
        
        for country in valid_countries:
            org = Organization(
                name=f"Test Org {country}",
                organization_type=OrganizationType.customer,
                country=country,
                address="123 Test Street",
                contact_info="test@example.com"
            )
            db_session.add(org)
            db_session.flush()
            assert org.country == country
            db_session.rollback()
    
    def test_supplier_parent_organization_requirement(self, db_session: Session):
        """Test that supplier organizations must have a parent organization."""
        # Create parent organization first
        parent_org = Organization(
            name="Parent Organization",
            organization_type=OrganizationType.oraseas_ee,
            address="123 Parent Street",
            contact_info="parent@example.com"
        )
        db_session.add(parent_org)
        db_session.flush()
        
        # Test supplier with parent - should succeed
        supplier_with_parent = Organization(
            name="Supplier With Parent",
            organization_type=OrganizationType.supplier,
            parent_organization_id=parent_org.id,
            address="123 Supplier Street",
            contact_info="supplier@example.com"
        )
        db_session.add(supplier_with_parent)
        db_session.flush()
        
        # Validate business rules
        assert supplier_with_parent.validate_business_rules() == True
        
        # Test supplier without parent - should fail validation
        supplier_without_parent = Organization(
            name="Supplier Without Parent",
            organization_type=OrganizationType.supplier,
            address="123 Supplier Street",
            contact_info="supplier2@example.com"
        )
        
        with pytest.raises(ValueError, match="Supplier organizations must have a parent organization"):
            supplier_without_parent.validate_business_rules()
    
    def test_organization_hierarchy_methods(self, db_session: Session):
        """Test organization hierarchy helper methods."""
        # Create parent organization
        parent_org = Organization(
            name="Parent Organization",
            organization_type=OrganizationType.customer,
            address="123 Parent Street",
            contact_info="parent@example.com"
        )
        db_session.add(parent_org)
        db_session.flush()
        
        # Create supplier organizations
        supplier1 = Organization(
            name="Supplier 1",
            organization_type=OrganizationType.supplier,
            parent_organization_id=parent_org.id,
            address="123 Supplier1 Street",
            contact_info="supplier1@example.com",
            is_active=True
        )
        supplier2 = Organization(
            name="Supplier 2",
            organization_type=OrganizationType.supplier,
            parent_organization_id=parent_org.id,
            address="123 Supplier2 Street",
            contact_info="supplier2@example.com",
            is_active=False
        )
        db_session.add_all([supplier1, supplier2])
        db_session.commit()
        
        # Test get_active_suppliers
        active_suppliers = parent_org.get_active_suppliers(db_session)
        assert len(active_suppliers) == 1
        assert active_suppliers[0].name == "Supplier 1"
        
        # Test get_supplier_count
        active_count = parent_org.get_supplier_count(db_session, include_inactive=False)
        total_count = parent_org.get_supplier_count(db_session, include_inactive=True)
        assert active_count == 1
        assert total_count == 2
        
        # Test can_have_suppliers
        assert parent_org.can_have_suppliers() == True
        assert supplier1.can_have_suppliers() == False
    
    def test_organization_type_properties(self, db_session: Session):
        """Test organization type hybrid properties."""
        # Test Oraseas EE
        oraseas = Organization(
            name="Oraseas EE",
            organization_type=OrganizationType.oraseas_ee,
            address="123 Oraseas Street",
            contact_info="info@oraseas.com"
        )
        assert oraseas.is_oraseas_ee == True
        assert oraseas.is_customer == False
        assert oraseas.is_supplier == False
        assert oraseas.is_bossaqua == False
        
        # Test Customer
        customer = Organization(
            name="Customer Org",
            organization_type=OrganizationType.customer,
            address="123 Customer Street",
            contact_info="info@customer.com"
        )
        assert customer.is_customer == True
        assert customer.is_oraseas_ee == False
        
        # Test Supplier
        supplier = Organization(
            name="Supplier Org",
            organization_type=OrganizationType.supplier,
            parent_organization_id=oraseas.id,
            address="123 Supplier Street",
            contact_info="info@supplier.com"
        )
        assert supplier.is_supplier == True
        assert supplier.is_customer == False
        
        # Test BossAqua
        bossaqua = Organization(
            name="BossAqua",
            organization_type=OrganizationType.bossaqua,
            address="123 BossAqua Street",
            contact_info="info@bossaqua.com"
        )
        assert bossaqua.is_bossaqua == True
        assert bossaqua.is_oraseas_ee == False


class TestUserModelValidation:
    """Test User model validation and business rules."""
    
    def test_user_role_properties(self, db_session: Session):
        """Test user role hybrid properties."""
        # Create organization first
        org = Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            address="123 Test Street",
            contact_info="test@example.com"
        )
        db_session.add(org)
        db_session.flush()
        
        # Test super admin
        super_admin = User(
            username="superadmin",
            email="superadmin@example.com",
            password_hash=get_password_hash("password123"),
            name="Super Admin",
            role=UserRole.super_admin,
            user_status=UserStatus.active,
            organization_id=org.id
        )
        assert super_admin.is_super_admin == True
        assert super_admin.is_admin == False
        
        # Test admin
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("password123"),
            name="Admin",
            role=UserRole.admin,
            user_status=UserStatus.active,
            organization_id=org.id
        )
        assert admin.is_admin == True
        assert admin.is_super_admin == False
        
        # Test regular user
        user = User(
            username="user",
            email="user@example.com",
            password_hash=get_password_hash("password123"),
            name="User",
            role=UserRole.user,
            user_status=UserStatus.active,
            organization_id=org.id
        )
        assert user.is_admin == False
        assert user.is_super_admin == False
    
    def test_user_localization_preferences(self, db_session: Session):
        """Test user localization preference fields."""
        # Create organization first
        org = Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            country="GR",
            address="123 Test Street",
            contact_info="test@example.com"
        )
        db_session.add(org)
        db_session.flush()
        
        # Test user with localization preferences
        user = User(
            username="localuser",
            email="localuser@example.com",
            password_hash=get_password_hash("password123"),
            name="Localized User",
            role=UserRole.user,
            user_status=UserStatus.active,
            organization_id=org.id,
            preferred_language="el",
            preferred_country="GR",
            localization_preferences='{"date_format": "DD/MM/YYYY", "currency": "EUR"}'
        )
        db_session.add(user)
        db_session.flush()
        
        assert user.preferred_language == "el"
        assert user.preferred_country == "GR"
        assert user.localization_preferences is not None


class TestMachineModelValidation:
    """Test Machine model validation and business rules."""
    
    def test_machine_model_type_validation(self, db_session: Session):
        """Test machine model type validation."""
        # Create organization first
        org = Organization(
            name="Customer Organization",
            organization_type=OrganizationType.customer,
            address="123 Customer Street",
            contact_info="customer@example.com"
        )
        db_session.add(org)
        db_session.flush()
        
        # Test valid model types
        valid_models = [MachineModelType.V3_1B, MachineModelType.V4_0]
        
        for model_type in valid_models:
            machine = Machine(
                name=f"Test Machine {model_type.value}",
                model_type=model_type,
                serial_number=f"TEST-{model_type.value}-001",
                customer_organization_id=org.id,
                status=MachineStatus.active
            )
            db_session.add(machine)
            db_session.flush()
            
            assert machine.validate_model_type() == True
            db_session.rollback()
    
    def test_machine_ownership_transfer_validation(self, db_session: Session):
        """Test machine ownership transfer business rules."""
        # Create organizations
        oraseas = Organization(
            name="Oraseas EE",
            organization_type=OrganizationType.oraseas_ee,
            address="123 Oraseas Street",
            contact_info="info@oraseas.com"
        )
        customer = Organization(
            name="Customer Org",
            organization_type=OrganizationType.customer,
            address="123 Customer Street",
            contact_info="customer@example.com"
        )
        supplier = Organization(
            name="Supplier Org",
            organization_type=OrganizationType.supplier,
            parent_organization_id=oraseas.id,
            address="123 Supplier Street",
            contact_info="supplier@example.com"
        )
        db_session.add_all([oraseas, customer, supplier])
        db_session.flush()
        
        # Create machine owned by Oraseas EE
        machine = Machine(
            name="Test Machine",
            model_type=MachineModelType.V4_0,
            serial_number="TEST-V4-001",
            customer_organization_id=oraseas.id,
            status=MachineStatus.active
        )
        db_session.add(machine)
        db_session.flush()
        
        # Test valid transfer (Oraseas EE to Customer)
        assert machine.can_transfer_ownership(oraseas, customer) == True
        
        # Test invalid transfers
        with pytest.raises(ValueError, match="Machines can only be transferred from Oraseas EE"):
            machine.can_transfer_ownership(customer, oraseas)
        
        with pytest.raises(ValueError, match="Machines can only be transferred to customer organizations"):
            machine.can_transfer_ownership(oraseas, supplier)
    
    def test_machine_name_editing_permissions(self, db_session: Session):
        """Test machine name editing permission logic."""
        # Create organizations
        org1 = Organization(
            name="Customer Org 1",
            organization_type=OrganizationType.customer,
            address="123 Customer1 Street",
            contact_info="customer1@example.com"
        )
        org2 = Organization(
            name="Customer Org 2",
            organization_type=OrganizationType.customer,
            address="123 Customer2 Street",
            contact_info="customer2@example.com"
        )
        db_session.add_all([org1, org2])
        db_session.flush()
        
        # Create users
        super_admin = User(
            username="superadmin",
            email="superadmin@example.com",
            password_hash=get_password_hash("password123"),
            name="Super Admin",
            role=UserRole.super_admin,
            user_status=UserStatus.active,
            organization_id=org1.id
        )
        admin1 = User(
            username="admin1",
            email="admin1@example.com",
            password_hash=get_password_hash("password123"),
            name="Admin 1",
            role=UserRole.admin,
            user_status=UserStatus.active,
            organization_id=org1.id
        )
        admin2 = User(
            username="admin2",
            email="admin2@example.com",
            password_hash=get_password_hash("password123"),
            name="Admin 2",
            role=UserRole.admin,
            user_status=UserStatus.active,
            organization_id=org2.id
        )
        regular_user = User(
            username="user1",
            email="user1@example.com",
            password_hash=get_password_hash("password123"),
            name="User 1",
            role=UserRole.user,
            user_status=UserStatus.active,
            organization_id=org1.id
        )
        db_session.add_all([super_admin, admin1, admin2, regular_user])
        db_session.flush()
        
        # Create machine in org1
        machine = Machine(
            name="Test Machine",
            model_type=MachineModelType.V4_0,
            serial_number="TEST-V4-001",
            customer_organization_id=org1.id,
            status=MachineStatus.active
        )
        db_session.add(machine)
        db_session.flush()
        
        # Test permissions
        assert machine.can_edit_name(super_admin, org1) == True  # Superadmin can edit any machine
        assert machine.can_edit_name(admin1, org1) == True      # Admin can edit machines in own org
        assert machine.can_edit_name(admin2, org2) == False     # Admin cannot edit machines in other orgs
        assert machine.can_edit_name(regular_user, org1) == False  # Regular users cannot edit machine names
        
        # Test name update
        original_name = machine.name
        machine.update_name("New Machine Name", admin1, org1)
        assert machine.name == "New Machine Name"
        assert "Name changed from" in machine.notes
        
        # Test invalid name update
        with pytest.raises(ValueError, match="User does not have permission"):
            machine.update_name("Another Name", admin2, org2)


class TestMachineHoursValidation:
    """Test MachineHours model validation and business rules."""
    
    def test_hours_value_validation(self, db_session: Session):
        """Test machine hours value validation."""
        # Create test data
        org = Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            address="123 Test Street",
            contact_info="test@example.com"
        )
        db_session.add(org)
        db_session.flush()
        
        user = User(
            username="testuser",
            email="testuser@example.com",
            password_hash=get_password_hash("password123"),
            name="Test User",
            role=UserRole.user,
            user_status=UserStatus.active,
            organization_id=org.id
        )
        db_session.add(user)
        db_session.flush()
        
        machine = Machine(
            name="Test Machine",
            model_type=MachineModelType.V4_0,
            serial_number="TEST-V4-001",
            customer_organization_id=org.id,
            status=MachineStatus.active
        )
        db_session.add(machine)
        db_session.flush()
        
        # Test valid hours value
        valid_hours = MachineHours(
            machine_id=machine.id,
            recorded_by_user_id=user.id,
            hours_value=Decimal("123.50"),
            recorded_date=datetime.now()
        )
        assert valid_hours.validate_hours_value() == True
        
        # Test negative hours value
        negative_hours = MachineHours(
            machine_id=machine.id,
            recorded_by_user_id=user.id,
            hours_value=Decimal("-10.00"),
            recorded_date=datetime.now()
        )
        with pytest.raises(ValueError, match="Hours value cannot be negative"):
            negative_hours.validate_hours_value()
        
        # Test unreasonably high hours value
        high_hours = MachineHours(
            machine_id=machine.id,
            recorded_by_user_id=user.id,
            hours_value=Decimal("100000.00"),
            recorded_date=datetime.now()
        )
        with pytest.raises(ValueError, match="Hours value seems unreasonably high"):
            high_hours.validate_hours_value()
        
        # Test None hours value
        none_hours = MachineHours(
            machine_id=machine.id,
            recorded_by_user_id=user.id,
            hours_value=None,
            recorded_date=datetime.now()
        )
        with pytest.raises(ValueError, match="Hours value cannot be None"):
            none_hours.validate_hours_value()
    
    def test_recorded_date_validation(self, db_session: Session):
        """Test machine hours recorded date validation."""
        # Create test data
        org = Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            address="123 Test Street",
            contact_info="test@example.com"
        )
        db_session.add(org)
        db_session.flush()
        
        user = User(
            username="testuser",
            email="testuser@example.com",
            password_hash=get_password_hash("password123"),
            name="Test User",
            role=UserRole.user,
            user_status=UserStatus.active,
            organization_id=org.id
        )
        db_session.add(user)
        db_session.flush()
        
        machine = Machine(
            name="Test Machine",
            model_type=MachineModelType.V4_0,
            serial_number="TEST-V4-001",
            customer_organization_id=org.id,
            status=MachineStatus.active
        )
        db_session.add(machine)
        db_session.flush()
        
        # Test valid date (current time)
        valid_date_hours = MachineHours(
            machine_id=machine.id,
            recorded_by_user_id=user.id,
            hours_value=Decimal("123.50"),
            recorded_date=datetime.now()
        )
        assert valid_date_hours.validate_recorded_date() == True
        
        # Test future date
        future_date_hours = MachineHours(
            machine_id=machine.id,
            recorded_by_user_id=user.id,
            hours_value=Decimal("123.50"),
            recorded_date=datetime.now() + timedelta(days=1)
        )
        with pytest.raises(ValueError, match="Recorded date cannot be in the future"):
            future_date_hours.validate_recorded_date()
        
        # Test None date
        none_date_hours = MachineHours(
            machine_id=machine.id,
            recorded_by_user_id=user.id,
            hours_value=Decimal("123.50"),
            recorded_date=None
        )
        with pytest.raises(ValueError, match="Recorded date cannot be None"):
            none_date_hours.validate_recorded_date()
    
    def test_hours_recording_permissions(self, db_session: Session):
        """Test machine hours recording permission logic."""
        # Create organizations
        org1 = Organization(
            name="Customer Org 1",
            organization_type=OrganizationType.customer,
            address="123 Customer1 Street",
            contact_info="customer1@example.com"
        )
        org2 = Organization(
            name="Customer Org 2",
            organization_type=OrganizationType.customer,
            address="123 Customer2 Street",
            contact_info="customer2@example.com"
        )
        db_session.add_all([org1, org2])
        db_session.flush()
        
        # Create users
        super_admin = User(
            username="superadmin",
            email="superadmin@example.com",
            password_hash=get_password_hash("password123"),
            name="Super Admin",
            role=UserRole.super_admin,
            user_status=UserStatus.active,
            organization_id=org1.id
        )
        user1 = User(
            username="user1",
            email="user1@example.com",
            password_hash=get_password_hash("password123"),
            name="User 1",
            role=UserRole.user,
            user_status=UserStatus.active,
            organization_id=org1.id
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            password_hash=get_password_hash("password123"),
            name="User 2",
            role=UserRole.user,
            user_status=UserStatus.active,
            organization_id=org2.id
        )
        db_session.add_all([super_admin, user1, user2])
        db_session.flush()
        
        # Create machine in org1
        machine = Machine(
            name="Test Machine",
            model_type=MachineModelType.V4_0,
            serial_number="TEST-V4-001",
            customer_organization_id=org1.id,
            status=MachineStatus.active
        )
        db_session.add(machine)
        db_session.flush()
        
        # Create machine hours record
        machine_hours = MachineHours(
            machine_id=machine.id,
            recorded_by_user_id=user1.id,
            hours_value=Decimal("123.50"),
            recorded_date=datetime.now()
        )
        
        # Test permissions
        assert machine_hours.can_record_hours(super_admin, machine, db_session) == True  # Superadmin can record for any machine
        assert machine_hours.can_record_hours(user1, machine, db_session) == True       # User can record for machines in own org
        assert machine_hours.can_record_hours(user2, machine, db_session) == False      # User cannot record for machines in other orgs
    
    def test_hours_progression_validation(self, db_session: Session):
        """Test machine hours progression validation logic."""
        # Create test data
        org = Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            address="123 Test Street",
            contact_info="test@example.com"
        )
        db_session.add(org)
        db_session.flush()
        
        user = User(
            username="testuser",
            email="testuser@example.com",
            password_hash=get_password_hash("password123"),
            name="Test User",
            role=UserRole.user,
            user_status=UserStatus.active,
            organization_id=org.id
        )
        db_session.add(user)
        db_session.flush()
        
        machine = Machine(
            name="Test Machine",
            model_type=MachineModelType.V4_0,
            serial_number="TEST-V4-001",
            customer_organization_id=org.id,
            status=MachineStatus.active
        )
        db_session.add(machine)
        db_session.flush()
        
        # Create first hours record
        first_hours = MachineHours(
            machine_id=machine.id,
            recorded_by_user_id=user.id,
            hours_value=Decimal("100.00"),
            recorded_date=datetime.now() - timedelta(days=1)
        )
        db_session.add(first_hours)
        db_session.commit()
        
        # Test normal progression (increase)
        second_hours = MachineHours(
            machine_id=machine.id,
            recorded_by_user_id=user.id,
            hours_value=Decimal("150.00"),
            recorded_date=datetime.now()
        )
        # Should not raise an exception
        second_hours.validate_against_previous_records(db_session)
        
        # Test small decrease (should be allowed)
        small_decrease_hours = MachineHours(
            machine_id=machine.id,
            recorded_by_user_id=user.id,
            hours_value=Decimal("90.00"),
            recorded_date=datetime.now()
        )
        # Should not raise an exception
        small_decrease_hours.validate_against_previous_records(db_session)
        
        # Test large decrease (should require explanation)
        large_decrease_hours = MachineHours(
            machine_id=machine.id,
            recorded_by_user_id=user.id,
            hours_value=Decimal("1.00"),  # 99 hour decrease
            recorded_date=datetime.now()
        )
        # Should not raise an exception for 99 hours (under 100 limit)
        large_decrease_hours.validate_against_previous_records(db_session)
        
        # Test very large decrease (should raise exception)
        very_large_decrease_hours = MachineHours(
            machine_id=machine.id,
            recorded_by_user_id=user.id,
            hours_value=Decimal("0.00"),  # 100+ hour decrease
            recorded_date=datetime.now()
        )
        with pytest.raises(ValueError, match="significantly lower than previous record"):
            very_large_decrease_hours.validate_against_previous_records(db_session)


class TestPartModelValidation:
    """Test Part model validation and business rules."""
    
    def test_multilingual_name_support(self, db_session: Session):
        """Test that parts support multilingual names (compound strings)."""
        # Test part with multilingual name
        part = Part(
            part_number="ML-001",
            name="Oil Filter|Φίλτρο Λαδιού|مرشح الزيت|Filtro de Aceite",  # Multilingual compound string
            description="Multilingual oil filter description",
            part_type=PartType.CONSUMABLE,
            is_proprietary=False,
            unit_of_measure="pieces",
            manufacturer="Test Manufacturer",
            part_code="TM-OF-001",
            serial_number="SN-OF-001"
        )
        db_session.add(part)
        db_session.flush()
        
        assert "|" in part.name  # Contains multilingual separator
        assert "Oil Filter" in part.name  # Contains English
        assert "Φίλτρο Λαδιού" in part.name  # Contains Greek
        assert part.manufacturer == "Test Manufacturer"
        assert part.part_code == "TM-OF-001"
        assert part.serial_number == "SN-OF-001"
    
    def test_part_type_validation(self, db_session: Session):
        """Test part type validation for consumable vs bulk material."""
        # Test consumable part
        consumable_part = Part(
            part_number="CONS-001",
            name="Consumable Part",
            description="A consumable part",
            part_type=PartType.CONSUMABLE,
            is_proprietary=False,
            unit_of_measure="pieces"
        )
        db_session.add(consumable_part)
        db_session.flush()
        assert consumable_part.part_type == PartType.CONSUMABLE
        
        # Test bulk material part
        bulk_part = Part(
            part_number="BULK-001",
            name="Bulk Material Part",
            description="A bulk material part",
            part_type=PartType.BULK_MATERIAL,
            is_proprietary=False,
            unit_of_measure="liters"
        )
        db_session.add(bulk_part)
        db_session.flush()
        assert bulk_part.part_type == PartType.BULK_MATERIAL
    
    def test_proprietary_part_classification(self, db_session: Session):
        """Test proprietary vs general part classification."""
        # Test proprietary part (BossAqua)
        proprietary_part = Part(
            part_number="PROP-001",
            name="BossAqua Proprietary Part",
            description="A proprietary BossAqua part",
            part_type=PartType.CONSUMABLE,
            is_proprietary=True,
            unit_of_measure="pieces",
            manufacturer="BossAqua"
        )
        db_session.add(proprietary_part)
        db_session.flush()
        assert proprietary_part.is_proprietary == True
        
        # Test general part
        general_part = Part(
            part_number="GEN-001",
            name="General Part",
            description="A general part from third-party supplier",
            part_type=PartType.CONSUMABLE,
            is_proprietary=False,
            unit_of_measure="pieces",
            manufacturer="Third Party Manufacturer"
        )
        db_session.add(general_part)
        db_session.flush()
        assert general_part.is_proprietary == False