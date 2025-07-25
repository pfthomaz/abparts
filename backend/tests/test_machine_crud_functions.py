"""
Test machine CRUD functions with enhanced error handling and comprehensive functionality testing.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError, OperationalError, TimeoutError
from fastapi import HTTPException

from app.crud import machines
from app import models, schemas


class TestMachineCRUDFunctionality:
    """Test machine CRUD operations functionality."""

    def test_get_machine_success(self, db_session, test_machines):
        """Test successful machine retrieval."""
        machine = test_machines["customer1_machine1"]
        result = machines.get_machine(db_session, machine.id)
        
        assert result is not None
        assert result.id == machine.id
        assert result.name == machine.name
        assert result.serial_number == machine.serial_number
        assert result.status == machine.status

    def test_get_machines_success(self, db_session, test_machines):
        """Test successful machines list retrieval."""
        result = machines.get_machines(db_session, skip=0, limit=10)
        
        assert isinstance(result, list)
        assert len(result) >= 3  # We have 3 test machines
        
        # Verify machine objects have expected attributes
        machine = result[0]
        assert hasattr(machine, 'id')
        assert hasattr(machine, 'name')
        assert hasattr(machine, 'serial_number')
        assert hasattr(machine, 'status')

    def test_get_machines_with_organization_filter(self, db_session, test_machines, test_organizations):
        """Test machines retrieval filtered by organization."""
        customer1_org_id = test_organizations["customer1"].id
        result = machines.get_machines(db_session, skip=0, limit=10, organization_id=customer1_org_id)
        
        assert isinstance(result, list)
        # All returned machines should belong to customer1
        for machine in result:
            assert machine.customer_organization_id == customer1_org_id

    def test_create_machine_success(self, db_session, test_organizations):
        """Test successful machine creation."""
        machine_data = schemas.MachineCreate(
            customer_organization_id=test_organizations["customer1"].id,
            model_type="V4.1",
            name="Test Machine Creation",
            serial_number=f"TEST-CREATE-{uuid.uuid4().hex[:8]}",
            status=models.MachineStatus.active,
            location="Test Bay",
            notes="Created for testing"
        )
        
        result = machines.create_machine(db_session, machine_data)
        
        assert result is not None
        assert result.name == machine_data.name
        assert result.model_type == machine_data.model_type
        assert result.serial_number == machine_data.serial_number
        assert result.status == machine_data.status
        assert result.location == machine_data.location
        assert result.notes == machine_data.notes

    def test_create_machine_with_enum_status(self, db_session, test_organizations):
        """Test machine creation with different enum status values."""
        test_statuses = [
            models.MachineStatus.active,
            models.MachineStatus.inactive,
            models.MachineStatus.maintenance,
            models.MachineStatus.decommissioned
        ]
        
        for status in test_statuses:
            machine_data = schemas.MachineCreate(
                customer_organization_id=test_organizations["customer1"].id,
                model_type="V4.0",
                name=f"Test Machine {status.value}",
                serial_number=f"TEST-{status.value.upper()}-{uuid.uuid4().hex[:8]}",
                status=status
            )
            
            result = machines.create_machine(db_session, machine_data)
            assert result.status == status

    def test_update_machine_success(self, db_session, test_machines):
        """Test successful machine update."""
        machine = test_machines["customer1_machine1"]
        update_data = schemas.MachineUpdate(
            name="Updated Machine Name",
            status=models.MachineStatus.maintenance,
            location="Updated Location",
            notes="Updated for testing"
        )
        
        result = machines.update_machine(db_session, machine.id, update_data)
        
        assert result is not None
        assert result.name == update_data.name
        assert result.status == update_data.status
        assert result.location == update_data.location
        assert result.notes == update_data.notes

    def test_update_machine_partial_update(self, db_session, test_machines):
        """Test machine update with only some fields."""
        machine = test_machines["customer1_machine1"]
        original_name = machine.name
        
        update_data = schemas.MachineUpdate(status=models.MachineStatus.inactive)
        result = machines.update_machine(db_session, machine.id, update_data)
        
        assert result is not None
        assert result.status == models.MachineStatus.inactive
        assert result.name == original_name  # Should remain unchanged

    def test_delete_machine_success(self, db_session, test_machines):
        """Test successful machine deletion."""
        machine = test_machines["customer1_machine2"]
        machine_id = machine.id
        
        result = machines.delete_machine(db_session, machine_id)
        
        assert result is not None
        assert "message" in result
        assert "deleted successfully" in result["message"]
        
        # Verify machine is deleted
        deleted_machine = machines.get_machine(db_session, machine_id)
        assert deleted_machine is None

    def test_transfer_machine_success(self, db_session, test_machines, test_organizations):
        """Test successful machine transfer."""
        machine = test_machines["customer1_machine1"]
        transfer_data = schemas.MachineTransferRequest(
            machine_id=machine.id,
            new_customer_organization_id=test_organizations["customer2"].id,
            transfer_date=datetime.utcnow(),
            transfer_notes="Test transfer operation"
        )
        
        result = machines.transfer_machine(db_session, transfer_data)
        
        assert result is not None
        assert result.customer_organization_id == test_organizations["customer2"].id
        assert "Test transfer operation" in result.notes

    def test_get_machine_maintenance_history_success(self, db_session, test_machines):
        """Test successful maintenance history retrieval."""
        machine = test_machines["customer1_machine1"]
        
        result = machines.get_machine_maintenance_history(db_session, machine.id, skip=0, limit=10)
        
        assert isinstance(result, list)
        # Even if empty, should return a list
        for maintenance_record in result:
            assert "machine_name" in maintenance_record
            assert "machine_serial_number" in maintenance_record

    def test_create_machine_maintenance_success(self, db_session, test_machines, test_users):
        """Test successful maintenance record creation."""
        machine = test_machines["customer1_machine1"]
        user = test_users["customer_admin"]
        
        maintenance_data = schemas.MaintenanceCreate(
            machine_id=machine.id,
            maintenance_date=datetime.utcnow(),
            maintenance_type="routine",
            performed_by_user_id=user.id,
            description="Test maintenance record",
            notes="Created for testing"
        )
        
        result = machines.create_machine_maintenance(db_session, maintenance_data)
        
        assert result is not None
        assert result.machine_id == machine.id
        assert result.performed_by_user_id == user.id
        assert result.description == maintenance_data.description


class TestMachineCRUDErrorHandling:
    """Test enhanced error handling in machine CRUD operations."""

    def test_get_machine_with_none_id(self, db_session):
        """Test get_machine handles None machine_id gracefully."""
        result = machines.get_machine(db_session, None)
        assert result is None

    def test_get_machine_with_database_error(self, db_session):
        """Test get_machine handles database errors."""
        machine_id = uuid.uuid4()
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.side_effect = SQLAlchemyError("Database connection failed")
            
            with pytest.raises(HTTPException) as exc_info:
                machines.get_machine(db_session, machine_id)
            
            assert exc_info.value.status_code == 500
            assert "Database error occurred while retrieving machine" in str(exc_info.value.detail)

    def test_get_machine_with_timeout_error(self, db_session):
        """Test get_machine handles database timeout errors."""
        machine_id = uuid.uuid4()
        
        with patch.object(db_session, 'query') as mock_query:
            mock_query.side_effect = TimeoutError("Database timeout")
            
            with pytest.raises(HTTPException) as exc_info:
                machines.get_machine(db_session, machine_id)
            
            assert exc_info.value.status_code == 503
            assert "Database service temporarily unavailable" in str(exc_info.value.detail)

    def test_get_machines_with_invalid_parameters(self, db_session):
        """Test get_machines handles invalid parameters gracefully."""
        # Mock the query chain to return an empty list
        db_session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        db_session.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        
        # Test with negative skip
        result = machines.get_machines(db_session, skip=-5, limit=10)
        assert isinstance(result, list)
        
        # Test with invalid limit
        result = machines.get_machines(db_session, skip=0, limit=0)
        assert isinstance(result, list)

    def test_create_machine_with_missing_organization_id(self, db_session):
        """Test create_machine handles missing organization ID."""
        # Create a mock machine data object that bypasses Pydantic validation
        machine_data = Mock()
        machine_data.customer_organization_id = None
        machine_data.model_type = "V3.1B"
        machine_data.name = "Test Machine"
        machine_data.serial_number = "TEST123"
        machine_data.dict.return_value = {
            "customer_organization_id": None,
            "model_type": "V3.1B",
            "name": "Test Machine",
            "serial_number": "TEST123"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            machines.create_machine(db_session, machine_data)
        
        assert exc_info.value.status_code == 400
        assert "Customer organization ID is required" in str(exc_info.value.detail)

    def test_create_machine_with_empty_serial_number(self, db_session):
        """Test create_machine handles empty serial number."""
        machine_data = schemas.MachineCreate(
            customer_organization_id=uuid.uuid4(),
            model_type="V3.1B",
            name="Test Machine",
            serial_number=""
        )
        
        with pytest.raises(HTTPException) as exc_info:
            machines.create_machine(db_session, machine_data)
        
        assert exc_info.value.status_code == 400
        assert "Serial number is required" in str(exc_info.value.detail)

    def test_create_machine_with_nonexistent_organization(self, db_session):
        """Test create_machine handles nonexistent organization."""
        machine_data = schemas.MachineCreate(
            customer_organization_id=uuid.uuid4(),
            model_type="V3.1B",
            name="Test Machine",
            serial_number="TEST123"
        )
        
        # Mock organization query to return None
        with patch.object(db_session, 'query') as mock_query:
            mock_filter = Mock()
            mock_filter.first.return_value = None
            mock_query.return_value.filter.return_value = mock_filter
            
            with pytest.raises(HTTPException) as exc_info:
                machines.create_machine(db_session, machine_data)
            
            assert exc_info.value.status_code == 400
            assert "Organization ID not found" in str(exc_info.value.detail)

    def test_create_machine_with_invalid_status_enum(self, db_session):
        """Test create_machine handles invalid status enum values."""
        # Create a mock machine data object that bypasses Pydantic validation
        machine_data = Mock()
        machine_data.customer_organization_id = uuid.uuid4()
        machine_data.model_type = "V3.1B"
        machine_data.name = "Test Machine"
        machine_data.serial_number = "TEST123"
        machine_data.dict.return_value = {
            "customer_organization_id": machine_data.customer_organization_id,
            "model_type": "V3.1B",
            "name": "Test Machine",
            "serial_number": "TEST123",
            "status": "invalid_status"
        }
        
        # Mock organization query to return a customer organization
        mock_org = Mock()
        mock_org.organization_type = models.OrganizationType.customer
        
        with patch.object(db_session, 'query') as mock_query:
            mock_filter = Mock()
            mock_filter.first.return_value = mock_org
            mock_query.return_value.filter.return_value = mock_filter
            
            with pytest.raises(HTTPException) as exc_info:
                machines.create_machine(db_session, machine_data)
            
            assert exc_info.value.status_code == 400
            assert "Invalid machine status" in str(exc_info.value.detail)

    def test_create_machine_with_integrity_error(self, db_session):
        """Test create_machine handles integrity constraint violations."""
        machine_data = schemas.MachineCreate(
            customer_organization_id=uuid.uuid4(),
            model_type="V3.1B",
            name="Test Machine",
            serial_number="DUPLICATE123"
        )
        
        # Mock organization query to return a customer organization
        mock_org = Mock()
        mock_org.organization_type = models.OrganizationType.customer
        
        with patch.object(db_session, 'query') as mock_query:
            mock_filter = Mock()
            mock_filter.first.return_value = mock_org
            mock_query.return_value.filter.return_value = mock_filter
            
            # Mock add/commit to raise IntegrityError
            from psycopg2.errors import UniqueViolation
            mock_unique_error = Mock()
            mock_unique_error.orig = UniqueViolation("duplicate key value violates unique constraint")
            
            with patch.object(db_session, 'commit') as mock_commit:
                mock_commit.side_effect = IntegrityError("statement", "params", mock_unique_error.orig)
                
                with pytest.raises(HTTPException) as exc_info:
                    machines.create_machine(db_session, machine_data)
                
                assert exc_info.value.status_code == 409
                assert "Machine data violates uniqueness constraint" in str(exc_info.value.detail)

    def test_update_machine_with_none_id(self, db_session):
        """Test update_machine handles None machine_id."""
        machine_update = schemas.MachineUpdate(name="Updated Name")
        
        with pytest.raises(HTTPException) as exc_info:
            machines.update_machine(db_session, None, machine_update)
        
        assert exc_info.value.status_code == 400
        assert "Machine ID is required" in str(exc_info.value.detail)

    def test_update_machine_with_empty_update_data(self, db_session):
        """Test update_machine handles empty update data gracefully."""
        machine_id = uuid.uuid4()
        machine_update = schemas.MachineUpdate()
        
        # Mock machine query to return a machine
        mock_machine = Mock()
        mock_machine.id = machine_id
        
        with patch.object(db_session, 'query') as mock_query:
            mock_filter = Mock()
            mock_filter.first.return_value = mock_machine
            mock_query.return_value.filter.return_value = mock_filter
            
            result = machines.update_machine(db_session, machine_id, machine_update)
            assert result == mock_machine

    def test_update_machine_not_found(self, db_session):
        """Test update_machine handles non-existent machine."""
        machine_id = uuid.uuid4()
        machine_update = schemas.MachineUpdate(name="Updated Name")
        
        # Mock machine query to return None
        with patch.object(db_session, 'query') as mock_query:
            mock_filter = Mock()
            mock_filter.first.return_value = None
            mock_query.return_value.filter.return_value = mock_filter
            
            result = machines.update_machine(db_session, machine_id, machine_update)
            assert result is None

    def test_delete_machine_with_none_id(self, db_session):
        """Test delete_machine handles None machine_id."""
        with pytest.raises(HTTPException) as exc_info:
            machines.delete_machine(db_session, None)
        
        assert exc_info.value.status_code == 400
        assert "Machine ID is required" in str(exc_info.value.detail)

    def test_delete_machine_not_found(self, db_session):
        """Test delete_machine handles non-existent machine."""
        machine_id = uuid.uuid4()
        
        # Mock machine query to return None
        with patch.object(db_session, 'query') as mock_query:
            mock_filter = Mock()
            mock_filter.first.return_value = None
            mock_query.return_value.filter.return_value = mock_filter
            
            result = machines.delete_machine(db_session, machine_id)
            assert result is None

    def test_delete_machine_with_foreign_key_constraint(self, db_session):
        """Test delete_machine handles foreign key constraint violations."""
        machine_id = uuid.uuid4()
        
        # Mock machine query to return a machine
        mock_machine = Mock()
        mock_machine.id = machine_id
        
        with patch.object(db_session, 'query') as mock_query:
            mock_filter = Mock()
            mock_filter.first.return_value = mock_machine
            mock_query.return_value.filter.return_value = mock_filter
            
            # Mock delete to raise IntegrityError with foreign key violation
            from psycopg2.errors import ForeignKeyViolation
            mock_fk_error = Mock()
            mock_fk_error.orig = ForeignKeyViolation("foreign key constraint violation")
            
            with patch.object(db_session, 'delete') as mock_delete:
                mock_delete.side_effect = IntegrityError("statement", "params", mock_fk_error.orig)
                
                with pytest.raises(HTTPException) as exc_info:
                    machines.delete_machine(db_session, machine_id)
                
                assert exc_info.value.status_code == 400
                assert "Cannot delete machine due to existing dependent records" in str(exc_info.value.detail)

    def test_get_machine_maintenance_history_with_invalid_params(self, db_session):
        """Test get_machine_maintenance_history handles invalid parameters."""
        machine_id = uuid.uuid4()
        
        # Mock machine query to return a machine
        mock_machine = Mock()
        mock_machine.id = machine_id
        mock_machine.name = "Test Machine"
        mock_machine.serial_number = "TEST123"
        
        with patch.object(db_session, 'query') as mock_query:
            mock_filter = Mock()
            mock_filter.first.return_value = mock_machine
            mock_query.return_value.filter.return_value = mock_filter
            
            # Mock the maintenance query to return empty results
            mock_maintenance_query = Mock()
            mock_maintenance_query.outerjoin.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
            mock_query.side_effect = [mock_filter, mock_maintenance_query]
            
            # Test with negative skip and invalid limit
            result = machines.get_machine_maintenance_history(db_session, machine_id, skip=-5, limit=0)
            assert isinstance(result, list)

    def test_get_machine_maintenance_history_machine_not_found(self, db_session):
        """Test get_machine_maintenance_history handles non-existent machine."""
        machine_id = uuid.uuid4()
        
        # Mock machine query to return None
        with patch.object(db_session, 'query') as mock_query:
            mock_filter = Mock()
            mock_filter.first.return_value = None
            mock_query.return_value.filter.return_value = mock_filter
            
            with pytest.raises(HTTPException) as exc_info:
                machines.get_machine_maintenance_history(db_session, machine_id)
            
            assert exc_info.value.status_code == 404
            assert "Machine not found" in str(exc_info.value.detail)

    def test_transfer_machine_with_missing_ids(self, db_session):
        """Test transfer_machine handles missing IDs."""
        # Create a mock transfer request that bypasses Pydantic validation
        transfer_request = Mock()
        transfer_request.machine_id = None
        transfer_request.new_customer_organization_id = uuid.uuid4()
        transfer_request.transfer_date = datetime.now()
        transfer_request.transfer_notes = "Test transfer"
        
        with pytest.raises(HTTPException) as exc_info:
            machines.transfer_machine(db_session, transfer_request)
        
        assert exc_info.value.status_code == 400
        assert "Machine ID is required" in str(exc_info.value.detail)

    def test_transfer_machine_not_found(self, db_session):
        """Test transfer_machine handles non-existent machine."""
        transfer_request = Mock()
        transfer_request.machine_id = uuid.uuid4()
        transfer_request.new_customer_organization_id = uuid.uuid4()
        transfer_request.transfer_date = datetime.now()
        transfer_request.transfer_notes = "Test transfer"
        
        # Mock machine query to return None
        with patch.object(db_session, 'query') as mock_query:
            mock_filter = Mock()
            mock_filter.first.return_value = None
            mock_query.return_value.filter.return_value = mock_filter
            
            with pytest.raises(HTTPException) as exc_info:
                machines.transfer_machine(db_session, transfer_request)
            
            assert exc_info.value.status_code == 404
            assert "Machine not found" in str(exc_info.value.detail)

    def test_create_machine_maintenance_missing_machine(self, db_session):
        """Test create_machine_maintenance handles non-existent machine."""
        maintenance_data = Mock()
        maintenance_data.machine_id = uuid.uuid4()
        maintenance_data.performed_by_user_id = uuid.uuid4()
        
        # Mock machine query to return None
        with patch.object(db_session, 'query') as mock_query:
            mock_filter = Mock()
            mock_filter.first.return_value = None
            mock_query.return_value.filter.return_value = mock_filter
            
            with pytest.raises(HTTPException) as exc_info:
                machines.create_machine_maintenance(db_session, maintenance_data)
            
            assert exc_info.value.status_code == 404
            assert "Machine not found" in str(exc_info.value.detail)

    def test_safe_enum_conversion_valid_values(self):
        """Test safe_enum_conversion with valid enum values."""
        from app.crud.machines import safe_enum_conversion
        
        # Test with enum instance
        result = safe_enum_conversion(models.MachineStatus, models.MachineStatus.active, "status")
        assert result == models.MachineStatus.active
        
        # Test with string values
        result = safe_enum_conversion(models.MachineStatus, "active", "status")
        assert result == models.MachineStatus.active
        
        result = safe_enum_conversion(models.MachineStatus, "MAINTENANCE", "status")
        assert result == models.MachineStatus.maintenance
        
        # Test with None
        result = safe_enum_conversion(models.MachineStatus, None, "status")
        assert result is None

    def test_safe_enum_conversion_invalid_values(self):
        """Test safe_enum_conversion with invalid enum values."""
        from app.crud.machines import safe_enum_conversion
        
        with pytest.raises(HTTPException) as exc_info:
            safe_enum_conversion(models.MachineStatus, "invalid_status", "status")
        
        assert exc_info.value.status_code == 400
        assert "Invalid status" in str(exc_info.value.detail)
        assert "active" in str(exc_info.value.detail)  # Should list valid values


@pytest.fixture
def db_session():
    """Mock database session for testing."""
    return Mock()