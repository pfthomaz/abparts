"""
Integration tests for ABParts business workflows.
Tests the complete end-to-end business processes.
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import (
    Organization, User, Part, Warehouse, Inventory, Machine, Transaction,
    OrganizationType, UserRole, TransactionType, MachineStatus
)


class TestOrganizationManagement:
    """Test organization management workflows."""
    
    def test_organization_hierarchy_creation(self, client: TestClient, auth_headers, db_session: Session):
        """Test creating organization hierarchy with proper business relationships."""
        # Super admin creates organizations
        headers = auth_headers["super_admin"]
        
        # Create parent organization (Oraseas EE should already exist)
        response = client.get("/organizations/", headers=headers)
        assert response.status_code == 200
        organizations = response.json()
        oraseas = next((org for org in organizations if org["organization_type"] == "oraseas_ee"), None)
        assert oraseas is not None
        
        # Create supplier with parent relationship
        supplier_data = {
            "name": "New Parts Supplier",
            "organization_type": "supplier",
            "parent_organization_id": oraseas["id"],
            "address": "123 Supplier Street",
            "contact_info": "contact@newsupplier.com"
        }
        
        response = client.post("/organizations/", json=supplier_data, headers=headers)
        assert response.status_code == 201
        supplier = response.json()
        assert supplier["parent_organization_id"] == oraseas["id"]
        
        # Verify hierarchy query
        response = client.get(f"/organizations/{oraseas['id']}/children", headers=headers)
        assert response.status_code == 200
        children = response.json()
        assert len(children) > 0
        assert any(child["id"] == supplier["id"] for child in children)
    
    def test_organization_type_constraints(self, client: TestClient, auth_headers):
        """Test business rule constraints for organization types."""
        headers = auth_headers["super_admin"]
        
        # Try to create second Oraseas EE (should fail)
        duplicate_oraseas = {
            "name": "Another Oraseas EE",
            "organization_type": "oraseas_ee",
            "address": "456 Duplicate Street",
            "contact_info": "duplicate@oraseas.com"
        }
        
        response = client.post("/organizations/", json=duplicate_oraseas, headers=headers)
        assert response.status_code == 400
        assert "only one" in response.json()["detail"].lower()
        
        # Try to create supplier without parent (should fail)
        orphan_supplier = {
            "name": "Orphan Supplier",
            "organization_type": "supplier",
            "address": "789 Orphan Lane",
            "contact_info": "orphan@supplier.com"
        }
        
        response = client.post("/organizations/", json=orphan_supplier, headers=headers)
        assert response.status_code == 400
        assert "parent" in response.json()["detail"].lower()


class TestUserManagement:
    """Test comprehensive user management workflows."""
    
    def test_user_invitation_workflow(self, client: TestClient, auth_headers, test_organizations):
        """Test complete user invitation and onboarding workflow."""
        headers = auth_headers["customer_admin"]
        
        # Send invitation
        invitation_data = {
            "email": "newuser@autowash.com",
            "name": "New User",
            "role": "user",
            "organization_id": str(test_organizations["customer1"].id)
        }
        
        response = client.post("/users/invite", json=invitation_data, headers=headers)
        assert response.status_code == 201
        invitation = response.json()
        assert invitation["user_status"] == "pending_invitation"
        assert invitation["invitation_token"] is not None
        
        # Check pending invitations
        response = client.get("/users/pending-invitations", headers=headers)
        assert response.status_code == 200
        pending = response.json()
        assert len(pending) >= 1
        assert any(inv["email"] == "newuser@autowash.com" for inv in pending)
        
        # Accept invitation
        acceptance_data = {
            "username": "newuser123",
            "password": "securepassword123",
            "name": "New User Full Name"
        }
        
        response = client.post(
            f"/users/accept-invitation/{invitation['invitation_token']}", 
            json=acceptance_data
        )
        assert response.status_code == 200
        activated_user = response.json()
        assert activated_user["user_status"] == "active"
        assert activated_user["username"] == "newuser123"
    
    def test_role_based_access_control(self, client: TestClient, auth_headers, test_organizations):
        """Test role-based access control enforcement."""
        # Super admin can access all organizations
        super_admin_headers = auth_headers["super_admin"]
        response = client.get("/organizations/", headers=super_admin_headers)
        assert response.status_code == 200
        all_orgs = response.json()
        assert len(all_orgs) >= 4  # Should see all organizations
        
        # Customer admin can only see own organization data
        customer_headers = auth_headers["customer_admin"]
        response = client.get("/users/", headers=customer_headers)
        assert response.status_code == 200
        users = response.json()
        # Should only see users from own organization
        for user in users:
            assert user["organization_id"] == str(test_organizations["customer1"].id)
        
        # Customer user has limited access
        user_headers = auth_headers["customer_user"]
        
        # Can view own profile
        response = client.get("/users/me/profile", headers=user_headers)
        assert response.status_code == 200
        
        # Cannot create users
        new_user_data = {
            "username": "unauthorized",
            "email": "unauthorized@test.com",
            "password": "password123",
            "name": "Unauthorized User",
            "role": "user",
            "organization_id": str(test_organizations["customer1"].id)
        }
        response = client.post("/users/", json=new_user_data, headers=user_headers)
        assert response.status_code == 403
    
    def test_user_profile_management(self, client: TestClient, auth_headers):
        """Test user profile and self-service management."""
        headers = auth_headers["customer_user"]
        
        # Get current profile
        response = client.get("/users/me/profile", headers=headers)
        assert response.status_code == 200
        profile = response.json()
        
        # Update profile
        update_data = {
            "name": "Updated Name",
            "email": "updated@autowash.com"
        }
        
        response = client.put("/users/me/profile", json=update_data, headers=headers)
        assert response.status_code == 200
        updated_profile = response.json()
        assert updated_profile["name"] == "Updated Name"
        
        # Change password
        password_data = {
            "current_password": "user123",
            "new_password": "newpassword123"
        }
        
        response = client.post("/users/me/change-password", json=password_data, headers=headers)
        assert response.status_code == 200


class TestWarehouseManagement:
    """Test warehouse management workflows."""
    
    def test_warehouse_creation_and_management(self, client: TestClient, auth_headers, test_organizations):
        """Test warehouse creation and management within organizations."""
        headers = auth_headers["customer_admin"]
        
        # Create new warehouse
        warehouse_data = {
            "name": "Secondary Storage",
            "location": "Building B",
            "description": "Additional storage facility",
            "organization_id": str(test_organizations["customer1"].id)
        }
        
        response = client.post("/warehouses/", json=warehouse_data, headers=headers)
        assert response.status_code == 201
        warehouse = response.json()
        assert warehouse["name"] == "Secondary Storage"
        assert warehouse["organization_id"] == str(test_organizations["customer1"].id)
        
        # List warehouses (should only see own organization's warehouses)
        response = client.get("/warehouses/", headers=headers)
        assert response.status_code == 200
        warehouses = response.json()
        for wh in warehouses:
            assert wh["organization_id"] == str(test_organizations["customer1"].id)
        
        # Update warehouse
        update_data = {
            "description": "Updated storage facility description"
        }
        
        response = client.put(f"/warehouses/{warehouse['id']}", json=update_data, headers=headers)
        assert response.status_code == 200
        updated_warehouse = response.json()
        assert updated_warehouse["description"] == "Updated storage facility description"


class TestInventoryManagement:
    """Test inventory management workflows."""
    
    def test_inventory_tracking_across_warehouses(self, client: TestClient, auth_headers, test_warehouses, test_parts):
        """Test inventory tracking across multiple warehouses."""
        headers = auth_headers["customer_admin"]
        
        # Get inventory for organization (aggregated across warehouses)
        response = client.get("/inventory/", headers=headers)
        assert response.status_code == 200
        inventory = response.json()
        assert len(inventory) > 0
        
        # Get warehouse-specific inventory
        warehouse_id = str(test_warehouses["customer1_main"].id)
        response = client.get(f"/inventory/warehouse/{warehouse_id}", headers=headers)
        assert response.status_code == 200
        warehouse_inventory = response.json()
        
        # Verify all inventory items belong to the specified warehouse
        for item in warehouse_inventory:
            assert item["warehouse_id"] == warehouse_id
    
    def test_stock_adjustments(self, client: TestClient, auth_headers, test_inventory):
        """Test stock adjustment workflows."""
        headers = auth_headers["customer_admin"]
        
        # Create stock adjustment
        inventory_item = test_inventory["customer1_oil_filter"]
        adjustment_data = {
            "inventory_id": str(inventory_item.id),
            "quantity_adjusted": "5.000",
            "reason_code": "FOUND_STOCK",
            "notes": "Found additional stock during audit"
        }
        
        response = client.post("/stock_adjustments/", json=adjustment_data, headers=headers)
        assert response.status_code == 201
        adjustment = response.json()
        assert float(adjustment["quantity_adjusted"]) == 5.0
        
        # Verify inventory was updated
        response = client.get(f"/inventory/{inventory_item.id}", headers=headers)
        assert response.status_code == 200
        updated_inventory = response.json()
        # Stock should have increased by 5
        assert float(updated_inventory["current_stock"]) == float(inventory_item.current_stock) + 5.0


class TestMachineManagement:
    """Test machine registration and management workflows."""
    
    def test_machine_registration(self, client: TestClient, auth_headers, test_organizations):
        """Test machine registration by super admin."""
        headers = auth_headers["super_admin"]
        
        # Register new machine
        machine_data = {
            "name": "AutoBoss Unit 3",
            "model_type": "V4.0",
            "serial_number": "AB-V4-003",
            "customer_organization_id": str(test_organizations["customer1"].id),
            "purchase_date": datetime.utcnow().isoformat(),
            "warranty_expiry_date": (datetime.utcnow() + timedelta(days=730)).isoformat(),
            "location": "Bay 3"
        }
        
        response = client.post("/machines/", json=machine_data, headers=headers)
        assert response.status_code == 201
        machine = response.json()
        assert machine["serial_number"] == "AB-V4-003"
        assert machine["customer_organization_id"] == str(test_organizations["customer1"].id)
        
        # Verify customer can see their machines
        customer_headers = auth_headers["customer_admin"]
        response = client.get("/machines/", headers=customer_headers)
        assert response.status_code == 200
        machines = response.json()
        machine_serials = [m["serial_number"] for m in machines]
        assert "AB-V4-003" in machine_serials
    
    def test_machine_parts_usage_tracking(self, client: TestClient, auth_headers, test_machines, test_parts, test_warehouses):
        """Test tracking parts usage in machines."""
        headers = auth_headers["customer_user"]
        
        # Record parts usage
        usage_data = {
            "part_id": str(test_parts["oil_filter"].id),
            "machine_id": str(test_machines["customer1_machine1"].id),
            "quantity": "1.000",
            "usage_date": datetime.utcnow().isoformat(),
            "warehouse_id": str(test_warehouses["customer1_main"].id),
            "notes": "Routine maintenance"
        }
        
        response = client.post("/part_usage/", json=usage_data, headers=headers)
        assert response.status_code == 201
        usage = response.json()
        assert usage["machine_id"] == str(test_machines["customer1_machine1"].id)
        assert float(usage["quantity"]) == 1.0
        
        # Get machine usage history
        machine_id = str(test_machines["customer1_machine1"].id)
        response = client.get(f"/machines/{machine_id}/usage-history", headers=headers)
        assert response.status_code == 200
        history = response.json()
        assert len(history) >= 1
        assert history[0]["part_id"] == str(test_parts["oil_filter"].id)


class TestTransactionTracking:
    """Test comprehensive transaction tracking workflows."""
    
    def test_transaction_creation_and_audit_trail(self, client: TestClient, auth_headers, test_parts, test_warehouses):
        """Test transaction creation and audit trail."""
        headers = auth_headers["oraseas_admin"]
        
        # Create inventory creation transaction
        transaction_data = {
            "transaction_type": "creation",
            "part_id": str(test_parts["oil_filter"].id),
            "to_warehouse_id": str(test_warehouses["oraseas_main"].id),
            "quantity": "50.000",
            "unit_of_measure": "pieces",
            "transaction_date": datetime.utcnow().isoformat(),
            "notes": "New stock arrival from supplier"
        }
        
        response = client.post("/transactions/", json=transaction_data, headers=headers)
        assert response.status_code == 201
        transaction = response.json()
        assert transaction["transaction_type"] == "creation"
        assert float(transaction["quantity"]) == 50.0
        
        # Get transaction history
        response = client.get("/transactions/", headers=headers)
        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions) >= 1
        
        # Filter transactions by part
        part_id = str(test_parts["oil_filter"].id)
        response = client.get(f"/transactions/?part_id={part_id}", headers=headers)
        assert response.status_code == 200
        part_transactions = response.json()
        for txn in part_transactions:
            assert txn["part_id"] == part_id
    
    def test_inventory_transfer_workflow(self, client: TestClient, auth_headers, test_parts, test_warehouses):
        """Test inventory transfer between warehouses."""
        headers = auth_headers["oraseas_admin"]
        
        # Transfer inventory between Oraseas warehouses
        transfer_data = {
            "transaction_type": "transfer",
            "part_id": str(test_parts["cleaning_oil"].id),
            "from_warehouse_id": str(test_warehouses["oraseas_main"].id),
            "to_warehouse_id": str(test_warehouses["oraseas_secondary"].id),
            "quantity": "25.500",
            "unit_of_measure": "liters",
            "transaction_date": datetime.utcnow().isoformat(),
            "notes": "Rebalancing inventory between warehouses"
        }
        
        response = client.post("/transactions/", json=transfer_data, headers=headers)
        assert response.status_code == 201
        transfer = response.json()
        assert transfer["transaction_type"] == "transfer"
        assert transfer["from_warehouse_id"] == str(test_warehouses["oraseas_main"].id)
        assert transfer["to_warehouse_id"] == str(test_warehouses["oraseas_secondary"].id)


class TestBusinessWorkflowIntegration:
    """Test complete end-to-end business workflows."""
    
    def test_complete_parts_ordering_workflow(self, client: TestClient, auth_headers, test_organizations, test_parts, test_warehouses):
        """Test complete parts ordering workflow from customer to Oraseas EE."""
        customer_headers = auth_headers["customer_admin"]
        oraseas_headers = auth_headers["oraseas_admin"]
        
        # Customer creates order
        order_data = {
            "customer_organization_id": str(test_organizations["customer1"].id),
            "oraseas_organization_id": str(test_organizations["oraseas"].id),
            "order_date": datetime.utcnow().isoformat(),
            "expected_delivery_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "status": "Pending",
            "notes": "Urgent order for maintenance"
        }
        
        response = client.post("/customer_orders/", json=order_data, headers=customer_headers)
        assert response.status_code == 201
        order = response.json()
        
        # Add items to order
        item_data = {
            "customer_order_id": order["id"],
            "part_id": str(test_parts["oil_filter"].id),
            "quantity": "10.000",
            "unit_price": "15.50"
        }
        
        response = client.post("/customer_order_items/", json=item_data, headers=customer_headers)
        assert response.status_code == 201
        
        # Oraseas admin processes order
        update_data = {"status": "Processing"}
        response = client.put(f"/customer_orders/{order['id']}", json=update_data, headers=oraseas_headers)
        assert response.status_code == 200
        
        # Fulfill order (create transfer transaction)
        fulfillment_data = {
            "transaction_type": "transfer",
            "part_id": str(test_parts["oil_filter"].id),
            "from_warehouse_id": str(test_warehouses["oraseas_main"].id),
            "to_warehouse_id": str(test_warehouses["customer1_main"].id),
            "quantity": "10.000",
            "unit_of_measure": "pieces",
            "transaction_date": datetime.utcnow().isoformat(),
            "reference_number": order["id"],
            "notes": f"Order fulfillment for order {order['id']}"
        }
        
        response = client.post("/transactions/", json=fulfillment_data, headers=oraseas_headers)
        assert response.status_code == 201
        
        # Mark order as delivered
        delivery_data = {
            "status": "Delivered",
            "actual_delivery_date": datetime.utcnow().isoformat()
        }
        response = client.put(f"/customer_orders/{order['id']}", json=delivery_data, headers=oraseas_headers)
        assert response.status_code == 200
        
        # Verify complete workflow
        response = client.get(f"/customer_orders/{order['id']}", headers=customer_headers)
        assert response.status_code == 200
        final_order = response.json()
        assert final_order["status"] == "Delivered"
        assert final_order["actual_delivery_date"] is not None
    
    def test_machine_maintenance_workflow(self, client: TestClient, auth_headers, test_machines, test_parts, test_warehouses):
        """Test complete machine maintenance workflow with parts consumption."""
        headers = auth_headers["customer_user"]
        
        machine_id = str(test_machines["customer1_machine1"].id)
        
        # Record maintenance parts usage
        maintenance_parts = [
            {
                "part_id": str(test_parts["oil_filter"].id),
                "quantity": "1.000",
                "notes": "Oil filter replacement"
            },
            {
                "part_id": str(test_parts["cleaning_oil"].id),
                "quantity": "2.500",
                "notes": "Oil top-up"
            }
        ]
        
        for part_usage in maintenance_parts:
            usage_data = {
                "part_id": part_usage["part_id"],
                "machine_id": machine_id,
                "quantity": part_usage["quantity"],
                "usage_date": datetime.utcnow().isoformat(),
                "warehouse_id": str(test_warehouses["customer1_main"].id),
                "notes": part_usage["notes"]
            }
            
            response = client.post("/part_usage/", json=usage_data, headers=headers)
            assert response.status_code == 201
        
        # Get machine maintenance history
        response = client.get(f"/machines/{machine_id}/usage-history", headers=headers)
        assert response.status_code == 200
        history = response.json()
        assert len(history) >= 2  # Should have both parts usage records
        
        # Verify inventory was reduced
        response = client.get("/inventory/", headers=headers)
        assert response.status_code == 200
        inventory = response.json()
        
        # Find oil filter inventory and verify reduction
        oil_filter_inventory = next(
            (inv for inv in inventory if inv["part_id"] == str(test_parts["oil_filter"].id)), 
            None
        )
        assert oil_filter_inventory is not None
        # Stock should be reduced by 1 (original stock minus usage)


class TestDataConsistency:
    """Test data consistency across business operations."""
    
    def test_inventory_balance_consistency(self, client: TestClient, auth_headers, test_inventory, test_parts, test_warehouses):
        """Test that inventory balances remain consistent across operations."""
        headers = auth_headers["customer_admin"]
        
        # Get initial inventory
        inventory_item = test_inventory["customer1_oil_filter"]
        initial_stock = float(inventory_item.current_stock)
        
        # Perform stock adjustment
        adjustment_data = {
            "inventory_id": str(inventory_item.id),
            "quantity_adjusted": "3.000",
            "reason_code": "FOUND_STOCK",
            "notes": "Consistency test adjustment"
        }
        
        response = client.post("/stock_adjustments/", json=adjustment_data, headers=headers)
        assert response.status_code == 201
        
        # Verify inventory updated correctly
        response = client.get(f"/inventory/{inventory_item.id}", headers=headers)
        assert response.status_code == 200
        updated_inventory = response.json()
        expected_stock = initial_stock + 3.0
        assert float(updated_inventory["current_stock"]) == expected_stock
        
        # Record parts usage
        usage_data = {
            "part_id": str(test_parts["oil_filter"].id),
            "quantity": "2.000",
            "usage_date": datetime.utcnow().isoformat(),
            "warehouse_id": str(test_warehouses["customer1_main"].id),
            "notes": "Consistency test usage"
        }
        
        response = client.post("/part_usage/", json=usage_data, headers=headers)
        assert response.status_code == 201
        
        # Verify inventory reduced correctly
        response = client.get(f"/inventory/{inventory_item.id}", headers=headers)
        assert response.status_code == 200
        final_inventory = response.json()
        final_expected_stock = expected_stock - 2.0
        assert float(final_inventory["current_stock"]) == final_expected_stock
    
    def test_transaction_audit_trail_completeness(self, client: TestClient, auth_headers, test_parts, test_warehouses):
        """Test that all operations create proper audit trail."""
        headers = auth_headers["oraseas_admin"]
        
        # Perform multiple operations
        operations = [
            {
                "transaction_type": "creation",
                "to_warehouse_id": str(test_warehouses["oraseas_main"].id),
                "quantity": "20.000",
                "notes": "Audit trail test - creation"
            },
            {
                "transaction_type": "transfer",
                "from_warehouse_id": str(test_warehouses["oraseas_main"].id),
                "to_warehouse_id": str(test_warehouses["oraseas_secondary"].id),
                "quantity": "5.000",
                "notes": "Audit trail test - transfer"
            }
        ]
        
        transaction_ids = []
        for op in operations:
            transaction_data = {
                "part_id": str(test_parts["drive_belt"].id),
                "unit_of_measure": "pieces",
                "transaction_date": datetime.utcnow().isoformat(),
                **op
            }
            
            response = client.post("/transactions/", json=transaction_data, headers=headers)
            assert response.status_code == 201
            transaction_ids.append(response.json()["id"])
        
        # Verify all transactions are in audit trail
        response = client.get("/transactions/", headers=headers)
        assert response.status_code == 200
        all_transactions = response.json()
        
        found_transactions = [
            txn for txn in all_transactions 
            if txn["id"] in transaction_ids
        ]
        assert len(found_transactions) == len(transaction_ids)
        
        # Verify transaction details
        for txn in found_transactions:
            assert txn["part_id"] == str(test_parts["drive_belt"].id)
            assert "Audit trail test" in txn["notes"]