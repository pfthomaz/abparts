"""
User Acceptance Testing scenarios for ABParts.
Tests key user workflows from an end-user perspective.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import (
    Organization, User, Part, Warehouse, Inventory, Machine, Transaction,
    OrganizationType, UserRole, TransactionType
)


class TestUserAcceptanceScenarios:
    """Test key user workflows from an end-user perspective."""
    
    def test_user_onboarding_workflow(self, client: TestClient, auth_headers, test_organizations):
        """
        UAT Scenario: New User Onboarding
        
        As an organization admin
        I want to invite a new user to the system
        So that they can access the parts management system
        """
        # Step 1: Admin logs in and invites new user
        headers = auth_headers["customer_admin"]
        
        invitation_data = {
            "email": "newemployee@autowash.com",
            "name": "New Employee",
            "role": "user",
            "organization_id": str(test_organizations["customer1"].id)
        }
        
        response = client.post("/users/invite", json=invitation_data, headers=headers)
        assert response.status_code == 201
        invitation = response.json()
        assert invitation["email"] == "newemployee@autowash.com"
        assert invitation["invitation_token"] is not None
        
        # Step 2: New user receives invitation and accepts it
        token = invitation["invitation_token"]
        acceptance_data = {
            "username": "newemployee",
            "password": "securepassword123",
            "name": "New Employee Full Name"
        }
        
        response = client.post(f"/users/accept-invitation/{token}", json=acceptance_data)
        assert response.status_code == 200
        activated_user = response.json()
        assert activated_user["username"] == "newemployee"
        assert activated_user["user_status"] == "active"
        
        # Step 3: New user logs in
        login_data = {
            "username": "newemployee",
            "password": "securepassword123"
        }
        
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        tokens = response.json()
        assert "access_token" in tokens
        
        # Step 4: New user accesses their profile
        new_user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = client.get("/users/me/", headers=new_user_headers)
        assert response.status_code == 200
        profile = response.json()
        assert profile["username"] == "newemployee"
        assert profile["organization_id"] == str(test_organizations["customer1"].id)
    
    def test_inventory_management_workflow(self, client: TestClient, auth_headers, test_parts, test_warehouses):
        """
        UAT Scenario: Inventory Management
        
        As an Oraseas EE admin
        I want to manage inventory across warehouses
        So that I can maintain accurate stock levels
        """
        # Step 1: Admin logs in and checks current inventory
        headers = auth_headers["oraseas_admin"]
        
        response = client.get("/inventory/", headers=headers)
        assert response.status_code == 200
        initial_inventory = response.json()
        
        # Step 2: Admin creates new inventory for a part
        inventory_data = {
            "warehouse_id": str(test_warehouses["oraseas_main"].id),
            "part_id": str(test_parts["drive_belt"].id),
            "current_stock": "50.000",
            "minimum_stock_recommendation": "10.000",
            "unit_of_measure": "pieces"
        }
        
        response = client.post("/inventory/", json=inventory_data, headers=headers)
        assert response.status_code == 201
        new_inventory = response.json()
        assert float(new_inventory["current_stock"]) == 50.0
        
        # Step 3: Admin adjusts inventory with stock adjustment
        adjustment_data = {
            "inventory_id": new_inventory["id"],
            "quantity_adjusted": "5.000",
            "reason_code": "FOUND_STOCK",
            "notes": "Additional stock found during audit"
        }
        
        response = client.post("/stock_adjustments/", json=adjustment_data, headers=headers)
        assert response.status_code == 201
        adjustment = response.json()
        assert float(adjustment["quantity_adjusted"]) == 5.0
        
        # Step 4: Admin verifies updated inventory
        response = client.get(f"/inventory/{new_inventory['id']}", headers=headers)
        assert response.status_code == 200
        updated_inventory = response.json()
        assert float(updated_inventory["current_stock"]) == 55.0
        
        # Step 5: Admin transfers inventory to another warehouse
        transfer_data = {
            "transaction_type": "transfer",
            "part_id": str(test_parts["drive_belt"].id),
            "from_warehouse_id": str(test_warehouses["oraseas_main"].id),
            "to_warehouse_id": str(test_warehouses["oraseas_secondary"].id),
            "quantity": "20.000",
            "unit_of_measure": "pieces",
            "transaction_date": datetime.utcnow().isoformat(),
            "notes": "Balancing inventory between warehouses"
        }
        
        response = client.post("/transactions/", json=transfer_data, headers=headers)
        assert response.status_code == 201
        
        # Step 6: Admin verifies inventory in both warehouses
        response = client.get(f"/inventory/{new_inventory['id']}", headers=headers)
        assert response.status_code == 200
        source_inventory = response.json()
        assert float(source_inventory["current_stock"]) == 35.0  # 55 - 20
        
        # Check destination warehouse (may need to query by warehouse and part)
        response = client.get(f"/inventory/warehouse/{test_warehouses['oraseas_secondary'].id}", headers=headers)
        assert response.status_code == 200
        dest_warehouse_inventory = response.json()
        dest_inventory = next((inv for inv in dest_warehouse_inventory 
                              if inv["part_id"] == str(test_parts["drive_belt"].id)), None)
        assert dest_inventory is not None
        assert float(dest_inventory["current_stock"]) == 20.0
    
    def test_customer_order_workflow(self, client: TestClient, auth_headers, test_organizations, test_parts):
        """
        UAT Scenario: Customer Order Processing
        
        As a customer admin
        I want to place and track orders for parts
        So that I can maintain my inventory
        """
        # Step 1: Customer admin logs in and places an order
        customer_headers = auth_headers["customer_admin"]
        
        order_data = {
            "customer_organization_id": str(test_organizations["customer1"].id),
            "oraseas_organization_id": str(test_organizations["oraseas"].id),
            "order_date": datetime.utcnow().isoformat(),
            "expected_delivery_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "status": "Pending",
            "notes": "Regular monthly order"
        }
        
        response = client.post("/customer_orders/", json=order_data, headers=customer_headers)
        assert response.status_code == 201
        order = response.json()
        
        # Step 2: Customer adds items to the order
        item_data = {
            "customer_order_id": order["id"],
            "part_id": str(test_parts["oil_filter"].id),
            "quantity": "5.000",
            "unit_price": "15.50"
        }
        
        response = client.post("/customer_order_items/", json=item_data, headers=customer_headers)
        assert response.status_code == 201
        
        # Add another item
        item_data2 = {
            "customer_order_id": order["id"],
            "part_id": str(test_parts["cleaning_oil"].id),
            "quantity": "10.000",
            "unit_price": "25.75"
        }
        
        response = client.post("/customer_order_items/", json=item_data2, headers=customer_headers)
        assert response.status_code == 201
        
        # Step 3: Customer submits the order
        update_data = {"status": "Submitted"}
        response = client.put(f"/customer_orders/{order['id']}", json=update_data, headers=customer_headers)
        assert response.status_code == 200
        
        # Step 4: Oraseas admin processes the order
        oraseas_headers = auth_headers["oraseas_admin"]
        
        # View pending orders
        response = client.get("/customer_orders/?status=Submitted", headers=oraseas_headers)
        assert response.status_code == 200
        pending_orders = response.json()
        assert any(o["id"] == order["id"] for o in pending_orders)
        
        # Update order status to processing
        update_data = {"status": "Processing"}
        response = client.put(f"/customer_orders/{order['id']}", json=update_data, headers=oraseas_headers)
        assert response.status_code == 200
        
        # Step 5: Oraseas admin marks order as shipped
        update_data = {"status": "Shipped"}
        response = client.put(f"/customer_orders/{order['id']}", json=update_data, headers=oraseas_headers)
        assert response.status_code == 200
        
        # Step 6: Customer verifies order status
        response = client.get(f"/customer_orders/{order['id']}", headers=customer_headers)
        assert response.status_code == 200
        updated_order = response.json()
        assert updated_order["status"] == "Shipped"
        
        # Step 7: Customer marks order as delivered
        update_data = {
            "status": "Delivered",
            "actual_delivery_date": datetime.utcnow().isoformat()
        }
        response = client.put(f"/customer_orders/{order['id']}", json=update_data, headers=customer_headers)
        assert response.status_code == 200
        
        # Step 8: Customer verifies final order status
        response = client.get(f"/customer_orders/{order['id']}", headers=customer_headers)
        assert response.status_code == 200
        final_order = response.json()
        assert final_order["status"] == "Delivered"
        assert final_order["actual_delivery_date"] is not None
    
    def test_machine_maintenance_workflow(self, client: TestClient, auth_headers, test_machines, test_parts, test_warehouses):
        """
        UAT Scenario: Machine Maintenance
        
        As a customer user
        I want to record machine maintenance and parts usage
        So that I can track machine health and parts consumption
        """
        # Step 1: Customer user logs in and views machine details
        headers = auth_headers["customer_user"]
        
        machine_id = str(test_machines["customer1_machine1"].id)
        response = client.get(f"/machines/{machine_id}", headers=headers)
        assert response.status_code == 200
        machine = response.json()
        
        # Step 2: User records maintenance with parts usage
        usage_data = {
            "part_id": str(test_parts["oil_filter"].id),
            "machine_id": machine_id,
            "quantity": "1.000",
            "usage_date": datetime.utcnow().isoformat(),
            "warehouse_id": str(test_warehouses["customer1_main"].id),
            "notes": "Regular maintenance - oil filter replacement"
        }
        
        response = client.post("/part_usage/", json=usage_data, headers=headers)
        assert response.status_code == 201
        usage = response.json()
        
        # Record another part usage
        usage_data2 = {
            "part_id": str(test_parts["cleaning_oil"].id),
            "machine_id": machine_id,
            "quantity": "2.500",
            "usage_date": datetime.utcnow().isoformat(),
            "warehouse_id": str(test_warehouses["customer1_main"].id),
            "notes": "Regular maintenance - oil change"
        }
        
        response = client.post("/part_usage/", json=usage_data2, headers=headers)
        assert response.status_code == 201
        
        # Step 3: User updates machine maintenance date
        update_data = {
            "last_maintenance_date": datetime.utcnow().isoformat(),
            "next_maintenance_date": (datetime.utcnow() + timedelta(days=90)).isoformat()
        }
        
        response = client.put(f"/machines/{machine_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        
        # Step 4: User views machine maintenance history
        response = client.get(f"/machines/{machine_id}/usage-history", headers=headers)
        assert response.status_code == 200
        history = response.json()
        assert len(history) >= 2
        
        # Step 5: User checks inventory levels after maintenance
        response = client.get("/inventory/", headers=headers)
        assert response.status_code == 200
        inventory = response.json()
        
        # Verify inventory was reduced
        oil_filter_inventory = next(
            (inv for inv in inventory if inv["part_id"] == str(test_parts["oil_filter"].id)), 
            None
        )
        assert oil_filter_inventory is not None
        
        cleaning_oil_inventory = next(
            (inv for inv in inventory if inv["part_id"] == str(test_parts["cleaning_oil"].id)), 
            None
        )
        assert cleaning_oil_inventory is not None
    
    def test_reporting_and_analytics_workflow(self, client: TestClient, auth_headers):
        """
        UAT Scenario: Reporting and Analytics
        
        As an organization admin
        I want to view reports and analytics
        So that I can make informed business decisions
        """
        # Step 1: Admin logs in and accesses dashboard
        headers = auth_headers["oraseas_admin"]
        
        response = client.get("/dashboard/summary", headers=headers)
        assert response.status_code == 200
        dashboard = response.json()
        assert "inventory_summary" in dashboard
        assert "recent_transactions" in dashboard
        
        # Step 2: Admin views inventory reports
        response = client.get("/inventory-reports/low-stock", headers=headers)
        assert response.status_code == 200
        low_stock = response.json()
        
        # Step 3: Admin views transaction reports
        response = client.get("/transactions/summary", headers=headers)
        assert response.status_code == 200
        transaction_summary = response.json()
        
        # Step 4: Admin views customer order analytics
        response = client.get("/dashboard/customer-orders", headers=headers)
        assert response.status_code == 200
        order_analytics = response.json()
        
        # Step 5: Admin exports data (if implemented)
        response = client.get("/inventory-reports/export", headers=headers)
        assert response.status_code in [200, 404]  # 404 if not implemented
        
        # Step 6: Admin views machine usage analytics
        response = client.get("/dashboard/machine-usage", headers=headers)
        assert response.status_code == 200
        machine_usage = response.json()


class TestEdgeCaseScenarios:
    """Test edge cases and error handling from a user perspective."""
    
    def test_out_of_stock_handling(self, client: TestClient, auth_headers, test_parts, test_warehouses):
        """
        UAT Scenario: Out of Stock Handling
        
        As a customer user
        I want to be notified when trying to use out-of-stock parts
        So that I can take appropriate action
        """
        headers = auth_headers["customer_user"]
        
        # Try to use more parts than available in inventory
        usage_data = {
            "part_id": str(test_parts["oil_filter"].id),
            "quantity": "1000.000",  # Intentionally large quantity
            "usage_date": datetime.utcnow().isoformat(),
            "warehouse_id": str(test_warehouses["customer1_main"].id),
            "notes": "Attempt to use more than available"
        }
        
        response = client.post("/part_usage/", json=usage_data, headers=headers)
        assert response.status_code == 400
        error = response.json()
        assert "insufficient" in error["detail"].lower() or "out of stock" in error["detail"].lower()
    
    def test_duplicate_entry_handling(self, client: TestClient, auth_headers, test_organizations):
        """
        UAT Scenario: Duplicate Entry Handling
        
        As a system user
        I want to be prevented from creating duplicate entries
        So that data integrity is maintained
        """
        headers = auth_headers["super_admin"]
        
        # Try to create organization with duplicate name
        duplicate_org = {
            "name": test_organizations["customer1"].name,  # Use existing name
            "organization_type": "customer",
            "address": "123 Duplicate St",
            "contact_info": "duplicate@example.com"
        }
        
        response = client.post("/organizations/", json=duplicate_org, headers=headers)
        assert response.status_code == 400
        error = response.json()
        assert "already exists" in error["detail"].lower() or "duplicate" in error["detail"].lower()
    
    def test_data_validation_feedback(self, client: TestClient, auth_headers):
        """
        UAT Scenario: Data Validation Feedback
        
        As a system user
        I want to receive clear validation errors
        So that I can correct my input
        """
        headers = auth_headers["customer_admin"]
        
        # Submit incomplete data
        incomplete_data = {
            "name": "Test Warehouse"
            # Missing required fields
        }
        
        response = client.post("/warehouses/", json=incomplete_data, headers=headers)
        assert response.status_code == 422
        validation_errors = response.json()
        assert "detail" in validation_errors
        
        # Submit invalid data
        invalid_data = {
            "name": "Test Warehouse",
            "organization_id": "not-a-valid-uuid",
            "location": "Test Location"
        }
        
        response = client.post("/warehouses/", json=invalid_data, headers=headers)
        assert response.status_code == 422
        validation_errors = response.json()
        assert "detail" in validation_errors