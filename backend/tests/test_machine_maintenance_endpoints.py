"""
Test machine maintenance API endpoints functionality.
Tests maintenance-related endpoints with error handling and response validation.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from fastapi import status
from fastapi.testclient import TestClient

from app import models, schemas


class TestMachineMaintenanceEndpoints:
    """Test machine maintenance API endpoints functionality."""

    def test_get_machine_maintenance_history_success(self, client: TestClient, auth_headers, test_machines):
        """Test successful retrieval of machine maintenance history."""
        machine_id = test_machines["customer1_machine1"].id
        response = client.get(f"/machines/{machine_id}/maintenance", headers=auth_headers["super_admin"])
        
        assert response.status_code == status.HTTP_200_OK
        maintenance_history = response.json()
        assert isinstance(maintenance_history, list)
        
        # Even if empty, should return a list with proper structure
        for record in maintenance_history:
            if record:  # If there are records
                assert "machine_name" in record
                assert "machine_serial_number" in record
                assert "performed_by_username" in record

    def test_get_machine_maintenance_history_organization_access(self, client: TestClient, auth_headers, test_machines):
        """Test that users can only access maintenance history for their organization's machines."""
        # Customer admin trying to access another customer's machine maintenance
        machine_id = test_machines["customer2_machine1"].id
        response = client.get(f"/machines/{machine_id}/maintenance", headers=auth_headers["customer_admin"])
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        error = response.json()
        assert "Not authorized to view this machine's maintenance history" in str(error["detail"])

    def test_get_machine_maintenance_history_machine_not_found(self, client: TestClient, auth_headers):
        """Test maintenance history retrieval for non-existent machine."""
        non_existent_id = uuid.uuid4()
        response = client.get(f"/machines/{non_existent_id}/maintenance", headers=auth_headers["super_admin"])
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        error = response.json()
        assert "Machine not found" in str(error["detail"])

    def test_get_machine_maintenance_history_pagination(self, client: TestClient, auth_headers, test_machines):
        """Test maintenance history pagination parameters."""
        machine_id = test_machines["customer1_machine1"].id
        
        # Test with valid pagination
        response = client.get(f"/machines/{machine_id}/maintenance?skip=0&limit=5", headers=auth_headers["super_admin"])
        assert response.status_code == status.HTTP_200_OK
        
        # Test with invalid pagination (should be handled gracefully)
        response = client.get(f"/machines/{machine_id}/maintenance?skip=-1&limit=0", headers=auth_headers["super_admin"])
        assert response.status_code == status.HTTP_200_OK

    def test_create_machine_maintenance_success(self, client: TestClient, auth_headers, test_machines, test_users):
        """Test successful maintenance record creation."""
        machine_id = test_machines["customer1_machine1"].id
        maintenance_data = {
            "machine_id": str(machine_id),
            "maintenance_date": datetime.utcnow().isoformat(),
            "maintenance_type": "routine",
            "description": "Regular maintenance check",
            "notes": "All systems functioning normally",
            "performed_by_user_id": str(test_users["customer_admin"].id)
        }
        
        response = client.post(f"/machines/{machine_id}/maintenance", json=maintenance_data, headers=auth_headers["customer_admin"])
        
        assert response.status_code == status.HTTP_201_CREATED
        maintenance = response.json()
        assert maintenance["machine_id"] == str(machine_id)
        assert maintenance["maintenance_type"] == maintenance_data["maintenance_type"]
        assert maintenance["description"] == maintenance_data["description"]
        assert maintenance["notes"] == maintenance_data["notes"]

    def test_create_machine_maintenance_auto_user_assignment(self, client: TestClient, auth_headers, test_machines):
        """Test that maintenance record automatically assigns current user if not specified."""
        machine_id = test_machines["customer1_machine1"].id
        maintenance_data = {
            "machine_id": str(machine_id),
            "maintenance_date": datetime.utcnow().isoformat(),
            "maintenance_type": "emergency",
            "description": "Emergency repair"
        }
        
        response = client.post(f"/machines/{machine_id}/maintenance", json=maintenance_data, headers=auth_headers["customer_admin"])
        
        assert response.status_code == status.HTTP_201_CREATED
        maintenance = response.json()
        assert maintenance["performed_by_user_id"] is not None

    def test_create_machine_maintenance_machine_not_found(self, client: TestClient, auth_headers):
        """Test maintenance creation for non-existent machine."""
        non_existent_id = uuid.uuid4()
        maintenance_data = {
            "machine_id": str(non_existent_id),
            "maintenance_date": datetime.utcnow().isoformat(),
            "maintenance_type": "routine",
            "description": "Test maintenance"
        }
        
        response = client.post(f"/machines/{non_existent_id}/maintenance", json=maintenance_data, headers=auth_headers["super_admin"])
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        error = response.json()
        assert "Machine not found" in str(error["detail"])

    def test_create_machine_maintenance_organization_access(self, client: TestClient, auth_headers, test_machines):
        """Test that users can only create maintenance records for their organization's machines."""
        # Customer admin trying to create maintenance for another customer's machine
        machine_id = test_machines["customer2_machine1"].id
        maintenance_data = {
            "machine_id": str(machine_id),
            "maintenance_date": datetime.utcnow().isoformat(),
            "maintenance_type": "routine",
            "description": "Unauthorized maintenance"
        }
        
        response = client.post(f"/machines/{machine_id}/maintenance", json=maintenance_data, headers=auth_headers["customer_admin"])
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        error = response.json()
        assert "Not authorized to create maintenance records for this machine" in str(error["detail"])

    def test_create_machine_maintenance_missing_required_fields(self, client: TestClient, auth_headers, test_machines):
        """Test maintenance creation with missing required fields."""
        machine_id = test_machines["customer1_machine1"].id
        
        # Missing maintenance_type
        maintenance_data = {
            "machine_id": str(machine_id),
            "maintenance_date": datetime.utcnow().isoformat(),
            "description": "Test maintenance"
        }
        
        response = client.post(f"/machines/{machine_id}/maintenance", json=maintenance_data, headers=auth_headers["customer_admin"])
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing description
        maintenance_data = {
            "machine_id": str(machine_id),
            "maintenance_date": datetime.utcnow().isoformat(),
            "maintenance_type": "routine"
        }
        
        response = client.post(f"/machines/{machine_id}/maintenance", json=maintenance_data, headers=auth_headers["customer_admin"])
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_add_part_to_maintenance_success(self, client: TestClient, auth_headers, test_machines, test_parts, test_users, db_session):
        """Test successful addition of part to maintenance record."""
        machine_id = test_machines["customer1_machine1"].id
        
        # First create a maintenance record
        maintenance_data = {
            "machine_id": str(machine_id),
            "maintenance_date": datetime.utcnow().isoformat(),
            "maintenance_type": "repair",
            "description": "Part replacement",
            "performed_by_user_id": str(test_users["customer_admin"].id)
        }
        
        maintenance_response = client.post(f"/machines/{machine_id}/maintenance", json=maintenance_data, headers=auth_headers["customer_admin"])
        assert maintenance_response.status_code == status.HTTP_201_CREATED
        maintenance = maintenance_response.json()
        maintenance_id = maintenance["id"]
        
        # Now add a part to the maintenance record
        part_usage_data = {
            "part_id": str(test_parts["oil_filter"].id),
            "quantity": 2.0,
            "notes": "Replaced oil filter"
        }
        
        response = client.post(f"/machines/{machine_id}/maintenance/{maintenance_id}/parts", json=part_usage_data, headers=auth_headers["customer_admin"])
        
        assert response.status_code == status.HTTP_201_CREATED
        part_usage = response.json()
        assert part_usage["part_id"] == str(test_parts["oil_filter"].id)
        assert part_usage["quantity"] == part_usage_data["quantity"]
        assert part_usage["notes"] == part_usage_data["notes"]

    def test_add_part_to_maintenance_invalid_ids(self, client: TestClient, auth_headers):
        """Test adding part to maintenance with invalid IDs."""
        machine_id = uuid.uuid4()
        maintenance_id = uuid.uuid4()
        part_usage_data = {
            "part_id": str(uuid.uuid4()),
            "quantity": 1.0
        }
        
        response = client.post(f"/machines/{machine_id}/maintenance/{maintenance_id}/parts", json=part_usage_data, headers=auth_headers["super_admin"])
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        error = response.json()
        assert "Machine not found" in str(error["detail"])

    def test_maintenance_endpoints_authentication_required(self, client: TestClient, test_machines):
        """Test that authentication is required for maintenance endpoints."""
        machine_id = test_machines["customer1_machine1"].id
        
        # Test without authentication header
        response = client.get(f"/machines/{machine_id}/maintenance")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = client.post(f"/machines/{machine_id}/maintenance", json={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_maintenance_error_response_structure(self, client: TestClient, auth_headers):
        """Test that maintenance error responses have proper structure."""
        non_existent_id = uuid.uuid4()
        response = client.get(f"/machines/{non_existent_id}/maintenance", headers=auth_headers["super_admin"])
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        error = response.json()
        
        # Check error response structure
        assert "detail" in error
        if isinstance(error["detail"], dict):
            assert "timestamp" in error["detail"]
            assert "resource" in error["detail"]
            assert error["detail"]["resource"] == "machine"

    def test_maintenance_date_handling(self, client: TestClient, auth_headers, test_machines, test_users):
        """Test proper handling of maintenance dates in different formats."""
        machine_id = test_machines["customer1_machine1"].id
        
        # Test with ISO format
        maintenance_data = {
            "machine_id": str(machine_id),
            "maintenance_date": "2024-01-15T10:30:00Z",
            "maintenance_type": "routine",
            "description": "ISO date test",
            "performed_by_user_id": str(test_users["customer_admin"].id)
        }
        
        response = client.post(f"/machines/{machine_id}/maintenance", json=maintenance_data, headers=auth_headers["customer_admin"])
        assert response.status_code == status.HTTP_201_CREATED
        
        # Test with current datetime
        maintenance_data["maintenance_date"] = datetime.utcnow().isoformat()
        maintenance_data["description"] = "Current date test"
        
        response = client.post(f"/machines/{machine_id}/maintenance", json=maintenance_data, headers=auth_headers["customer_admin"])
        assert response.status_code == status.HTTP_201_CREATED

    def test_maintenance_type_validation(self, client: TestClient, auth_headers, test_machines, test_users):
        """Test validation of maintenance type values."""
        machine_id = test_machines["customer1_machine1"].id
        
        valid_types = ["routine", "emergency", "repair", "inspection", "upgrade"]
        
        for maintenance_type in valid_types:
            maintenance_data = {
                "machine_id": str(machine_id),
                "maintenance_date": datetime.utcnow().isoformat(),
                "maintenance_type": maintenance_type,
                "description": f"Test {maintenance_type} maintenance",
                "performed_by_user_id": str(test_users["customer_admin"].id)
            }
            
            response = client.post(f"/machines/{machine_id}/maintenance", json=maintenance_data, headers=auth_headers["customer_admin"])
            assert response.status_code == status.HTTP_201_CREATED
            
            maintenance = response.json()
            assert maintenance["maintenance_type"] == maintenance_type

    def test_maintenance_quantity_validation(self, client: TestClient, auth_headers, test_machines, test_parts, test_users, db_session):
        """Test validation of part quantities in maintenance records."""
        machine_id = test_machines["customer1_machine1"].id
        
        # Create maintenance record first
        maintenance_data = {
            "machine_id": str(machine_id),
            "maintenance_date": datetime.utcnow().isoformat(),
            "maintenance_type": "repair",
            "description": "Quantity validation test",
            "performed_by_user_id": str(test_users["customer_admin"].id)
        }
        
        maintenance_response = client.post(f"/machines/{machine_id}/maintenance", json=maintenance_data, headers=auth_headers["customer_admin"])
        maintenance_id = maintenance_response.json()["id"]
        
        # Test with valid decimal quantity
        part_usage_data = {
            "part_id": str(test_parts["cleaning_oil"].id),
            "quantity": 2.5,
            "notes": "Used 2.5 liters"
        }
        
        response = client.post(f"/machines/{machine_id}/maintenance/{maintenance_id}/parts", json=part_usage_data, headers=auth_headers["customer_admin"])
        assert response.status_code == status.HTTP_201_CREATED
        
        part_usage = response.json()
        assert float(part_usage["quantity"]) == 2.5

    def test_maintenance_notes_handling(self, client: TestClient, auth_headers, test_machines, test_users):
        """Test handling of maintenance notes including special characters and long text."""
        machine_id = test_machines["customer1_machine1"].id
        
        # Test with special characters and long text
        long_notes = "This is a very long maintenance note with special characters: !@#$%^&*()_+-=[]{}|;':\",./<>? " * 10
        
        maintenance_data = {
            "machine_id": str(machine_id),
            "maintenance_date": datetime.utcnow().isoformat(),
            "maintenance_type": "routine",
            "description": "Notes handling test",
            "notes": long_notes,
            "performed_by_user_id": str(test_users["customer_admin"].id)
        }
        
        response = client.post(f"/machines/{machine_id}/maintenance", json=maintenance_data, headers=auth_headers["customer_admin"])
        assert response.status_code == status.HTTP_201_CREATED
        
        maintenance = response.json()
        assert maintenance["notes"] == long_notes