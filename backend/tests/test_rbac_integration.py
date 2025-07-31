"""
Integration tests for role-based access control in ABParts.
Tests organizational data isolation and permission enforcement.
"""

import pytest
import uuid
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import (
    Organization, User, Part, Warehouse, Inventory, Machine, MachineHours,
    OrganizationType, UserRole, UserStatus, PartType, MachineModelType, MachineStatus
)


class TestOrganizationalDataIsolation:
    """Test that users can only access data from their own organization."""
    
    def test_organization_data_isolation(self, client: TestClient, auth_headers, test_organizations, test_users):
        """Test that users can only see organizations they have access to."""
        # Super admin should see all organizations
        response = client.get("/organizations/", headers=auth_headers["super_admin"])
        assert response.status_code == 200
        super_admin_orgs = response.json()
        assert len(super_admin_orgs) >= 4  # Should see all test organizations
        
        # Customer admin should only see their own organization and its suppliers
        response = client.get("/organizations/", headers=auth_headers["customer_admin"])
        assert response.status_code == 200
        customer_admin_orgs = response.json()
        
        # Customer admin should see their own organization
        customer_org_ids = [org["id"] for org in customer_admin_orgs]
        assert test_organizations["customer1"].id in [uuid.UUID(org_id) for org_id in customer_org_ids]
        
        # Customer admin should not see other customer organizations
        assert test_organizations["customer2"].id not in [uuid.UUID(org_id) for org_id in customer_org_ids]
    
    def test_user_data_isolation(self, client: TestClient, auth_headers, test_organizations, test_users):
        """Test that users can only see users from their own organization."""
        # Super admin should see all users
        response = client.get("/users/", headers=auth_headers["super_admin"])
        assert response.status_code == 200
        super_admin_users = response.json()
        assert len(super_admin_users) >= 5  # Should see all test users
        
        # Customer admin should only see users from their organization
        response = client.get("/users/", headers=auth_headers["customer_admin"])
        assert response.status_code == 200
        customer_admin_users = response.json()
        
        # All returned users should belong to the same organization as the requesting admin
        customer_org_id = str(test_organizations["customer1"].id)
        for user in customer_admin_users:
            assert user["organization_id"] == customer_org_id
        
        # Should not see users from other organizations
        customer2_org_id = str(test_organizations["customer2"].id)
        for user in customer_admin_users:
            assert user["organization_id"] != customer2_org_id
    
    def test_warehouse_data_isolation(self, client: TestClient, auth_headers, test_warehouses, test_organizations):
        """Test that users can only see warehouses from their own organization."""
        # Super admin should see all warehouses
        response = client.get("/warehouses/", headers=auth_headers["super_admin"])
        assert response.status_code == 200
        super_admin_warehouses = response.json()
        assert len(super_admin_warehouses) >= 4  # Should see all test warehouses
        
        # Customer admin should only see warehouses from their organization
        response = client.get("/warehouses/", headers=auth_headers["customer_admin"])
        assert response.status_code == 200
        customer_admin_warehouses = response.json()
        
        # All returned warehouses should belong to the same organization as the requesting admin
        customer_org_id = str(test_organizations["customer1"].id)
        for warehouse in customer_admin_warehouses:
            assert warehouse["organization_id"] == customer_org_id
    
    def test_machine_data_isolation(self, client: TestClient, auth_headers, test_machines, test_organizations):
        """Test that users can only see machines from their own organization."""
        # Super admin should see all machines
        response = client.get("/machines/", headers=auth_headers["super_admin"])
        assert response.status_code == 200
        super_admin_machines = response.json()
        assert len(super_admin_machines) >= 3  # Should see all test machines
        
        # Customer admin should only see machines from their organization
        response = client.get("/machines/", headers=auth_headers["customer_admin"])
        assert response.status_code == 200
        customer_admin_machines = response.json()
        
        # All returned machines should belong to the same organization as the requesting admin
        customer_org_id = str(test_organizations["customer1"].id)
        for machine in customer_admin_machines:
            assert machine["customer_organization_id"] == customer_org_id
        
        # Should see 2 machines for customer1
        assert len(customer_admin_machines) == 2
    
    def test_inventory_data_isolation(self, client: TestClient, auth_headers, test_inventory, test_warehouses, test_organizations):
        """Test that users can only see inventory from their own organization's warehouses."""
        # Super admin should see all inventory
        response = client.get("/inventory/", headers=auth_headers["super_admin"])
        assert response.status_code == 200
        super_admin_inventory = response.json()
        assert len(super_admin_inventory) >= 4  # Should see all test inventory
        
        # Customer admin should only see inventory from their organization's warehouses
        response = client.get("/inventory/", headers=auth_headers["customer_admin"])
        assert response.status_code == 200
        customer_admin_inventory = response.json()
        
        # All returned inventory should belong to warehouses in the same organization
        customer_warehouse_ids = [
            str(warehouse.id) for warehouse in test_warehouses.values() 
            if warehouse.organization_id == test_organizations["customer1"].id
        ]
        
        for inventory in customer_admin_inventory:
            assert inventory["warehouse_id"] in customer_warehouse_ids


class TestRoleBasedPermissions:
    """Test role-based permission enforcement."""
    
    def test_super_admin_permissions(self, client: TestClient, auth_headers, test_organizations):
        """Test super admin permissions across all resources."""
        headers = auth_headers["super_admin"]
        
        # Super admin can create organizations
        new_org_data = {
            "name": "Super Admin Test Org",
            "organization_type": "customer",
            "country": "GR",
            "address": "123 Super Admin Street",
            "contact_info": "superadmin@test.com"
        }
        response = client.post("/organizations/", json=new_org_data, headers=headers)
        assert response.status_code == 201
        
        # Super admin can create users in any organization
        new_user_data = {
            "username": "superadmin_created_user",
            "email": "superadmin_user@test.com",
            "password": "securepassword123",
            "name": "Super Admin Created User",
            "role": "user",
            "organization_id": str(test_organizations["customer1"].id)
        }
        response = client.post("/users/", json=new_user_data, headers=headers)
        assert response.status_code == 201
        
        # Super admin can create parts
        new_part_data = {
            "part_number": "SA-TEST-001",
            "name": "Super Admin Test Part",
            "description": "A test part created by super admin",
            "part_type": "CONSUMABLE",
            "is_proprietary": False,
            "unit_of_measure": "pieces",
            "manufacturer": "Test Manufacturer"
        }
        response = client.post("/parts/", json=new_part_data, headers=headers)
        assert response.status_code == 201
        
        # Super admin can create machines
        new_machine_data = {
            "name": "Super Admin Test Machine",
            "model_type": "V4.0",
            "serial_number": "SA-TEST-MACHINE-001",
            "customer_organization_id": str(test_organizations["customer1"].id),
            "status": "active"
        }
        response = client.post("/machines/", json=new_machine_data, headers=headers)
        assert response.status_code == 201
    
    def test_admin_permissions(self, client: TestClient, auth_headers, test_organizations, test_users):
        """Test admin permissions within their organization."""
        headers = auth_headers["customer_admin"]
        
        # Admin can create users in their own organization
        new_user_data = {
            "username": "admin_created_user",
            "email": "admin_user@test.com",
            "password": "securepassword123",
            "name": "Admin Created User",
            "role": "user",
            "organization_id": str(test_organizations["customer1"].id)
        }
        response = client.post("/users/", json=new_user_data, headers=headers)
        assert response.status_code == 201
        
        # Admin cannot create users in other organizations
        new_user_other_org_data = {
            "username": "admin_created_user_other_org",
            "email": "admin_user_other@test.com",
            "password": "securepassword123",
            "name": "Admin Created User Other Org",
            "role": "user",
            "organization_id": str(test_organizations["customer2"].id)
        }
        response = client.post("/users/", json=new_user_other_org_data, headers=headers)
        assert response.status_code == 403  # Forbidden
        
        # Admin can create warehouses in their own organization
        new_warehouse_data = {
            "name": "Admin Test Warehouse",
            "organization_id": str(test_organizations["customer1"].id),
            "location": "Admin Test Location",
            "description": "A test warehouse created by admin"
        }
        response = client.post("/warehouses/", json=new_warehouse_data, headers=headers)
        assert response.status_code == 201
        
        # Admin cannot create warehouses in other organizations
        new_warehouse_other_org_data = {
            "name": "Admin Test Warehouse Other Org",
            "organization_id": str(test_organizations["customer2"].id),
            "location": "Admin Test Location Other Org",
            "description": "A test warehouse in other org"
        }
        response = client.post("/warehouses/", json=new_warehouse_other_org_data, headers=headers)
        assert response.status_code == 403  # Forbidden
        
        # Admin cannot create parts (only super admin can)
        new_part_data = {
            "part_number": "ADMIN-TEST-001",
            "name": "Admin Test Part",
            "description": "A test part created by admin",
            "part_type": "CONSUMABLE",
            "is_proprietary": False,
            "unit_of_measure": "pieces"
        }
        response = client.post("/parts/", json=new_part_data, headers=headers)
        assert response.status_code == 403  # Forbidden
        
        # Admin cannot create machines (only super admin can)
        new_machine_data = {
            "name": "Admin Test Machine",
            "model_type": "V4.0",
            "serial_number": "ADMIN-TEST-MACHINE-001",
            "customer_organization_id": str(test_organizations["customer1"].id),
            "status": "active"
        }
        response = client.post("/machines/", json=new_machine_data, headers=headers)
        assert response.status_code == 403  # Forbidden
    
    def test_user_permissions(self, client: TestClient, auth_headers, test_organizations):
        """Test regular user permissions (read-only with limited transaction capabilities)."""
        headers = auth_headers["customer_user"]
        
        # User can read parts
        response = client.get("/parts/", headers=headers)
        assert response.status_code == 200
        
        # User can read machines from their organization
        response = client.get("/machines/", headers=headers)
        assert response.status_code == 200
        
        # User can read warehouses from their organization
        response = client.get("/warehouses/", headers=headers)
        assert response.status_code == 200
        
        # User cannot create organizations
        new_org_data = {
            "name": "User Test Org",
            "organization_type": "customer",
            "address": "123 User Street",
            "contact_info": "user@test.com"
        }
        response = client.post("/organizations/", json=new_org_data, headers=headers)
        assert response.status_code == 403  # Forbidden
        
        # User cannot create other users
        new_user_data = {
            "username": "user_created_user",
            "email": "user_user@test.com",
            "password": "securepassword123",
            "name": "User Created User",
            "role": "user",
            "organization_id": str(test_organizations["customer1"].id)
        }
        response = client.post("/users/", json=new_user_data, headers=headers)
        assert response.status_code == 403  # Forbidden
        
        # User cannot create parts
        new_part_data = {
            "part_number": "USER-TEST-001",
            "name": "User Test Part",
            "description": "A test part created by user",
            "part_type": "CONSUMABLE",
            "is_proprietary": False,
            "unit_of_measure": "pieces"
        }
        response = client.post("/parts/", json=new_part_data, headers=headers)
        assert response.status_code == 403  # Forbidden
        
        # User cannot create machines
        new_machine_data = {
            "name": "User Test Machine",
            "model_type": "V4.0",
            "serial_number": "USER-TEST-MACHINE-001",
            "customer_organization_id": str(test_organizations["customer1"].id),
            "status": "active"
        }
        response = client.post("/machines/", json=new_machine_data, headers=headers)
        assert response.status_code == 403  # Forbidden
        
        # User cannot create warehouses
        new_warehouse_data = {
            "name": "User Test Warehouse",
            "organization_id": str(test_organizations["customer1"].id),
            "location": "User Test Location",
            "description": "A test warehouse created by user"
        }
        response = client.post("/warehouses/", json=new_warehouse_data, headers=headers)
        assert response.status_code == 403  # Forbidden


class TestSupplierVisibilityRestrictions:
    """Test supplier visibility restrictions within organizations."""
    
    def test_supplier_organization_scoping(self, client: TestClient, auth_headers, test_organizations, db_session: Session):
        """Test that suppliers are only visible to their parent organization."""
        # Create suppliers for different parent organizations
        supplier1_data = {
            "name": "Customer1 Supplier",
            "organization_type": "supplier",
            "parent_organization_id": str(test_organizations["customer1"].id),
            "address": "123 Supplier1 Street",
            "contact_info": "supplier1@test.com"
        }
        response = client.post("/organizations/", json=supplier1_data, headers=auth_headers["super_admin"])
        assert response.status_code == 201
        supplier1 = response.json()
        
        supplier2_data = {
            "name": "Customer2 Supplier",
            "organization_type": "supplier",
            "parent_organization_id": str(test_organizations["customer2"].id),
            "address": "123 Supplier2 Street",
            "contact_info": "supplier2@test.com"
        }
        response = client.post("/organizations/", json=supplier2_data, headers=auth_headers["super_admin"])
        assert response.status_code == 201
        supplier2 = response.json()
        
        # Customer1 admin should only see suppliers belonging to customer1
        response = client.get(f"/organizations/{test_organizations['customer1'].id}/suppliers", 
                            headers=auth_headers["customer_admin"])
        assert response.status_code == 200
        customer1_suppliers = response.json()
        
        supplier_names = [s["name"] for s in customer1_suppliers]
        assert "Customer1 Supplier" in supplier_names
        assert "Customer2 Supplier" not in supplier_names
        
        # Customer2 admin should only see suppliers belonging to customer2
        response = client.get(f"/organizations/{test_organizations['customer2'].id}/suppliers", 
                            headers=auth_headers["customer2_admin"])
        assert response.status_code == 200
        customer2_suppliers = response.json()
        
        supplier_names = [s["name"] for s in customer2_suppliers]
        assert "Customer2 Supplier" in supplier_names
        assert "Customer1 Supplier" not in supplier_names
    
    def test_supplier_activation_permissions(self, client: TestClient, auth_headers, test_organizations):
        """Test supplier activation/deactivation permissions."""
        # Create a supplier for customer1
        supplier_data = {
            "name": "Test Supplier for Activation",
            "organization_type": "supplier",
            "parent_organization_id": str(test_organizations["customer1"].id),
            "address": "123 Activation Test Street",
            "contact_info": "activation@test.com"
        }
        response = client.post("/organizations/", json=supplier_data, headers=auth_headers["super_admin"])
        assert response.status_code == 201
        supplier = response.json()
        
        # Customer1 admin should be able to activate/deactivate their own suppliers
        response = client.put(f"/organizations/{supplier['id']}/activate", 
                            json={"is_active": False}, 
                            headers=auth_headers["customer_admin"])
        assert response.status_code == 200
        
        # Customer2 admin should not be able to activate/deactivate customer1's suppliers
        response = client.put(f"/organizations/{supplier['id']}/activate", 
                            json={"is_active": True}, 
                            headers=auth_headers["customer2_admin"])
        assert response.status_code == 403  # Forbidden


class TestCrossOrganizationalAccessPrevention:
    """Test prevention of cross-organizational data access."""
    
    def test_cross_org_machine_hours_recording(self, client: TestClient, auth_headers, test_machines, test_organizations):
        """Test that users cannot record hours for machines in other organizations."""
        # Get a machine from customer1
        customer1_machine = test_machines["customer1_machine1"]
        
        # Customer1 user should be able to record hours for customer1 machine
        hours_data = {
            "machine_id": str(customer1_machine.id),
            "hours_value": 123.5,
            "recorded_date": "2024-01-15T10:00:00Z",
            "notes": "Regular maintenance check"
        }
        response = client.post(f"/machines/{customer1_machine.id}/hours", 
                             json=hours_data, 
                             headers=auth_headers["customer_user"])
        assert response.status_code == 201
        
        # Customer2 admin should not be able to record hours for customer1 machine
        response = client.post(f"/machines/{customer1_machine.id}/hours", 
                             json=hours_data, 
                             headers=auth_headers["customer2_admin"])
        assert response.status_code == 403  # Forbidden
    
    def test_cross_org_inventory_access(self, client: TestClient, auth_headers, test_warehouses, test_organizations):
        """Test that users cannot access inventory from other organizations."""
        # Customer1 admin should not be able to access customer2 warehouse inventory
        customer2_warehouse = test_warehouses["customer2_main"]
        
        response = client.get(f"/warehouses/{customer2_warehouse.id}/inventory", 
                            headers=auth_headers["customer_admin"])
        assert response.status_code == 403  # Forbidden
        
        # Customer1 admin should be able to access their own warehouse inventory
        customer1_warehouse = test_warehouses["customer1_main"]
        
        response = client.get(f"/warehouses/{customer1_warehouse.id}/inventory", 
                            headers=auth_headers["customer_admin"])
        assert response.status_code == 200
    
    def test_cross_org_user_management(self, client: TestClient, auth_headers, test_users, test_organizations):
        """Test that admins cannot manage users from other organizations."""
        # Customer1 admin should not be able to update customer2 users
        customer2_user_id = str(test_users["customer2_admin"].id)
        
        update_data = {
            "name": "Updated Name",
            "email": "updated@email.com"
        }
        response = client.put(f"/users/{customer2_user_id}", 
                            json=update_data, 
                            headers=auth_headers["customer_admin"])
        assert response.status_code == 403  # Forbidden
        
        # Customer1 admin should be able to update users in their own organization
        customer1_user_id = str(test_users["customer_user"].id)
        
        response = client.put(f"/users/{customer1_user_id}", 
                            json=update_data, 
                            headers=auth_headers["customer_admin"])
        assert response.status_code == 200


class TestBossAquaDataAccessRestrictions:
    """Test BossAqua data access restrictions for non-superadmin users."""
    
    def test_bossaqua_organization_access(self, client: TestClient, auth_headers, test_organizations):
        """Test that only superadmin can interact with BossAqua organization data."""
        bossaqua_org = test_organizations["bossaqua"]
        
        # Super admin should be able to access BossAqua organization
        response = client.get(f"/organizations/{bossaqua_org.id}", 
                            headers=auth_headers["super_admin"])
        assert response.status_code == 200
        
        # Customer admin should not be able to access BossAqua organization details
        response = client.get(f"/organizations/{bossaqua_org.id}", 
                            headers=auth_headers["customer_admin"])
        assert response.status_code == 403  # Forbidden
        
        # Regular user should not be able to access BossAqua organization details
        response = client.get(f"/organizations/{bossaqua_org.id}", 
                            headers=auth_headers["customer_user"])
        assert response.status_code == 403  # Forbidden
    
    def test_bossaqua_proprietary_parts_access(self, client: TestClient, auth_headers, test_parts):
        """Test access to BossAqua proprietary parts."""
        # All users should be able to view proprietary parts (read-only)
        response = client.get("/parts/", headers=auth_headers["customer_user"])
        assert response.status_code == 200
        parts = response.json()
        
        # Should include proprietary parts in the list
        proprietary_parts = [p for p in parts if p.get("is_proprietary", False)]
        assert len(proprietary_parts) > 0
        
        # But only superadmin should be able to modify proprietary parts
        proprietary_part = next((p for p in parts if p.get("is_proprietary", False)), None)
        if proprietary_part:
            update_data = {
                "description": "Updated proprietary part description"
            }
            
            # Super admin can update
            response = client.put(f"/parts/{proprietary_part['id']}", 
                                json=update_data, 
                                headers=auth_headers["super_admin"])
            assert response.status_code == 200
            
            # Customer admin cannot update
            response = client.put(f"/parts/{proprietary_part['id']}", 
                                json=update_data, 
                                headers=auth_headers["customer_admin"])
            assert response.status_code == 403  # Forbidden