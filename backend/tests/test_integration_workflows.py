"""
Comprehensive integration tests for ABParts business workflows.
Tests complete end-to-end business processes with proper data flow.
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import (
    Organization, User, Part, Warehouse, Inventory, Machine, Transaction,
    CustomerOrder, CustomerOrderItem, SupplierOrder, SupplierOrderItem,
    PartUsage, StockAdjustment, OrganizationType, UserRole, TransactionType
)


class TestCompleteBusinessWorkflows:
    """Test complete end-to-end business workflows."""
    
    def test_complete_customer_order_fulfillment_workflow(
        self, client: TestClient, auth_headers, test_organizations, 
        test_parts, test_warehouses, test_inventory, db_session: Session
    ):
        """Test complete customer order fulfillment from order to delivery."""
        customer_headers = auth_headers["customer_admin"]
        oraseas_headers = auth_headers["oraseas_admin"]
        
        # Step 1: Customer creates order
        order_data = {
            "customer_organization_id": str(test_organizations["customer1"].id),
            "oraseas_organization_id": str(test_organizations["oraseas"].id),
            "order_date": datetime.utcnow().isoformat(),
            "expected_delivery_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "status": "Pending",
            "notes": "Urgent maintenance order"
        }
        
        response = client.post("/customer_orders/", json=order_data, headers=customer_headers)
        assert response.status_code == 201
        order = response.json()
        order_id = order["id"]
        
        # Step 2: Add multiple items to order
        order_items = [
            {
                "customer_order_id": order_id,
                "part_id": str(test_parts["oil_filter"].id),
                "quantity": "5.000",
                "unit_price": "15.50"
            },
            {
                "customer_order_id": order_id,
                "part_id": str(test_parts["cleaning_oil"].id),
                "quantity": "10.000",
                "unit_price": "25.00"
            }
        ]
        
        created_items = []
        for item_data in order_items:
            response = client.post("/customer_order_items/", json=item_data, headers=customer_headers)
            assert response.status_code == 201
            created_items.append(response.json())
        
        # Step 3: Oraseas admin reviews and processes order
        response = client.get(f"/customer_orders/{order_id}", headers=oraseas_headers)
        assert response.status_code == 200
        
        # Update order status to processing
        update_data = {"status": "Processing"}
        response = client.put(f"/customer_orders/{order_id}", json=update_data, headers=oraseas_headers)
        assert response.status_code == 200
        
        # Step 4: Check inventory availability
        for item in created_items:
            part_id = item["part_id"]
            quantity_needed = float(item["quantity"])
            
            # Get Oraseas inventory for this part
            response = client.get("/inventory/", headers=oraseas_headers)
            assert response.status_code == 200
            inventory_items = response.json()
            
            oraseas_inventory = [
                inv for inv in inventory_items 
                if inv["part_id"] == part_id and 
                inv["warehouse"]["organization_id"] == str(test_organizations["oraseas"].id)
            ]
            
            total_available = sum(float(inv["current_stock"]) for inv in oraseas_inventory)
            assert total_available >= quantity_needed, f"Insufficient stock for part {part_id}"
        
        # Step 5: Fulfill order with inventory transfers
        for item in created_items:
            transfer_data = {
                "transaction_type": "transfer",
                "part_id": item["part_id"],
                "from_warehouse_id": str(test_warehouses["oraseas_main"].id),
                "to_warehouse_id": str(test_warehouses["customer1_main"].id),
                "quantity": item["quantity"],
                "unit_of_measure": "pieces" if "oil_filter" in str(item["part_id"]) else "liters",
                "transaction_date": datetime.utcnow().isoformat(),
                "reference_number": order_id,
                "notes": f"Order fulfillment for order {order_id}"
            }
            
            response = client.post("/transactions/", json=transfer_data, headers=oraseas_headers)
            assert response.status_code == 201
        
        # Step 6: Mark order as shipped
        ship_data = {
            "status": "Shipped",
            "actual_delivery_date": datetime.utcnow().isoformat()
        }
        response = client.put(f"/customer_orders/{order_id}", json=ship_data, headers=oraseas_headers)
        assert response.status_code == 200
        
        # Step 7: Customer confirms delivery
        delivery_data = {"status": "Delivered"}
        response = client.put(f"/customer_orders/{order_id}", json=delivery_data, headers=customer_headers)
        assert response.status_code == 200
        
        # Step 8: Verify final state
        response = client.get(f"/customer_orders/{order_id}", headers=customer_headers)
        assert response.status_code == 200
        final_order = response.json()
        assert final_order["status"] == "Delivered"
        assert final_order["actual_delivery_date"] is not None
        
        # Verify inventory was transferred correctly
        response = client.get("/inventory/", headers=customer_headers)
        assert response.status_code == 200
        customer_inventory = response.json()
        
        for item in created_items:
            part_inventory = [
                inv for inv in customer_inventory 
                if inv["part_id"] == item["part_id"]
            ]
            assert len(part_inventory) > 0, f"Customer should have inventory for part {item['part_id']}"
    
    def test_machine_maintenance_with_parts_consumption_workflow(
        self, client: TestClient, auth_headers, test_machines, 
        test_parts, test_warehouses, test_inventory, db_session: Session
    ):
        """Test complete machine maintenance workflow with parts consumption."""
        customer_headers = auth_headers["customer_user"]
        admin_headers = auth_headers["customer_admin"]
        
        machine_id = str(test_machines["customer1_machine1"].id)
        
        # Step 1: Schedule maintenance
        maintenance_data = {
            "machine_id": machine_id,
            "maintenance_type": "routine",
            "scheduled_date": datetime.utcnow().isoformat(),
            "notes": "Routine 3-month maintenance"
        }
        
        # Note: This would require a maintenance endpoint, simulating with machine update
        machine_update = {
            "status": "maintenance",
            "last_maintenance_date": datetime.utcnow().isoformat(),
            "next_maintenance_date": (datetime.utcnow() + timedelta(days=90)).isoformat()
        }
        
        response = client.put(f"/machines/{machine_id}", json=machine_update, headers=admin_headers)
        assert response.status_code == 200
        
        # Step 2: Record parts usage during maintenance
        maintenance_parts = [
            {
                "part_id": str(test_parts["oil_filter"].id),
                "quantity": "1.000",
                "notes": "Oil filter replacement"
            },
            {
                "part_id": str(test_parts["cleaning_oil"].id),
                "quantity": "2.500",
                "notes": "Oil system flush and refill"
            },
            {
                "part_id": str(test_parts["drive_belt"].id),
                "quantity": "1.000",
                "notes": "Drive belt replacement"
            }
        ]
        
        usage_records = []
        for part_usage in maintenance_parts:
            usage_data = {
                "part_id": part_usage["part_id"],
                "machine_id": machine_id,
                "quantity": part_usage["quantity"],
                "usage_date": datetime.utcnow().isoformat(),
                "warehouse_id": str(test_warehouses["customer1_main"].id),
                "notes": part_usage["notes"]
            }
            
            response = client.post("/part_usage/", json=usage_data, headers=customer_headers)
            assert response.status_code == 201
            usage_records.append(response.json())
        
        # Step 3: Verify inventory was reduced
        response = client.get("/inventory/", headers=admin_headers)
        assert response.status_code == 200
        current_inventory = response.json()
        
        for usage in usage_records:
            part_inventory = [
                inv for inv in current_inventory 
                if inv["part_id"] == usage["part_id"]
            ]
            assert len(part_inventory) > 0
            # Verify stock was reduced (would need initial stock comparison)
        
        # Step 4: Complete maintenance
        completion_update = {
            "status": "active",
            "notes": "Maintenance completed successfully"
        }
        
        response = client.put(f"/machines/{machine_id}", json=completion_update, headers=admin_headers)
        assert response.status_code == 200
        
        # Step 5: Verify maintenance history
        response = client.get(f"/machines/{machine_id}/usage-history", headers=customer_headers)
        assert response.status_code == 200
        history = response.json()
        
        # Should have all maintenance parts usage
        assert len(history) >= len(maintenance_parts)
        
        # Verify all parts are recorded
        used_part_ids = {record["part_id"] for record in history}
        expected_part_ids = {part["part_id"] for part in maintenance_parts}
        assert expected_part_ids.issubset(used_part_ids)
    
    def test_supplier_order_to_inventory_replenishment_workflow(
        self, client: TestClient, auth_headers, test_organizations, 
        test_parts, test_warehouses, db_session: Session
    ):
        """Test supplier order creation and inventory replenishment workflow."""
        oraseas_headers = auth_headers["oraseas_admin"]
        
        # Step 1: Create supplier order
        supplier_order_data = {
            "ordering_organization_id": str(test_organizations["oraseas"].id),
            "supplier_name": "External Parts Supplier Ltd",
            "order_date": datetime.utcnow().isoformat(),
            "expected_delivery_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "status": "Pending",
            "notes": "Quarterly stock replenishment"
        }
        
        response = client.post("/supplier_orders/", json=supplier_order_data, headers=oraseas_headers)
        assert response.status_code == 201
        supplier_order = response.json()
        order_id = supplier_order["id"]
        
        # Step 2: Add items to supplier order
        order_items = [
            {
                "supplier_order_id": order_id,
                "part_id": str(test_parts["oil_filter"].id),
                "quantity": "100.000",
                "unit_price": "12.00"
            },
            {
                "supplier_order_id": order_id,
                "part_id": str(test_parts["drive_belt"].id),
                "quantity": "50.000",
                "unit_price": "8.50"
            }
        ]
        
        for item_data in order_items:
            response = client.post("/supplier_order_items/", json=item_data, headers=oraseas_headers)
            assert response.status_code == 201
        
        # Step 3: Mark order as shipped by supplier
        update_data = {"status": "Shipped"}
        response = client.put(f"/supplier_orders/{order_id}", json=update_data, headers=oraseas_headers)
        assert response.status_code == 200
        
        # Step 4: Receive goods and update inventory
        for item in order_items:
            # Create inventory creation transaction
            creation_data = {
                "transaction_type": "creation",
                "part_id": item["part_id"],
                "to_warehouse_id": str(test_warehouses["oraseas_main"].id),
                "quantity": item["quantity"],
                "unit_of_measure": "pieces",
                "transaction_date": datetime.utcnow().isoformat(),
                "reference_number": order_id,
                "notes": f"Supplier delivery from order {order_id}"
            }
            
            response = client.post("/transactions/", json=creation_data, headers=oraseas_headers)
            assert response.status_code == 201
        
        # Step 5: Mark supplier order as delivered
        delivery_data = {
            "status": "Delivered",
            "actual_delivery_date": datetime.utcnow().isoformat()
        }
        response = client.put(f"/supplier_orders/{order_id}", json=delivery_data, headers=oraseas_headers)
        assert response.status_code == 200
        
        # Step 6: Verify inventory was updated
        response = client.get("/inventory/", headers=oraseas_headers)
        assert response.status_code == 200
        inventory = response.json()
        
        oraseas_inventory = [
            inv for inv in inventory 
            if inv["warehouse"]["organization_id"] == str(test_organizations["oraseas"].id)
        ]
        
        # Verify we have inventory for the ordered parts
        ordered_part_ids = {item["part_id"] for item in order_items}
        inventory_part_ids = {inv["part_id"] for inv in oraseas_inventory}
        assert ordered_part_ids.issubset(inventory_part_ids)
    
    def test_stock_adjustment_and_audit_trail_workflow(
        self, client: TestClient, auth_headers, test_inventory, 
        test_parts, test_warehouses, db_session: Session
    ):
        """Test stock adjustment workflow with complete audit trail."""
        admin_headers = auth_headers["customer_admin"]
        
        # Step 1: Perform stocktake and identify discrepancies
        inventory_item = test_inventory["customer1_oil_filter"]
        original_stock = float(inventory_item.current_stock)
        
        # Simulate finding discrepancy during stocktake
        actual_count = original_stock - 2.0  # Found 2 pieces missing
        
        # Step 2: Create stock adjustment for discrepancy
        adjustment_data = {
            "inventory_id": str(inventory_item.id),
            "quantity_adjusted": "-2.000",
            "reason_code": "STOCKTAKE_DISCREPANCY",
            "notes": "Physical count shows 2 pieces missing - possible theft or miscount"
        }
        
        response = client.post("/stock_adjustments/", json=adjustment_data, headers=admin_headers)
        assert response.status_code == 201
        adjustment = response.json()
        
        # Step 3: Verify inventory was updated
        response = client.get(f"/inventory/{inventory_item.id}", headers=admin_headers)
        assert response.status_code == 200
        updated_inventory = response.json()
        assert float(updated_inventory["current_stock"]) == actual_count
        
        # Step 4: Create adjustment transaction for audit trail
        adjustment_transaction_data = {
            "transaction_type": "adjustment",
            "part_id": str(test_parts["oil_filter"].id),
            "to_warehouse_id": str(test_warehouses["customer1_main"].id),
            "quantity": "-2.000",
            "unit_of_measure": "pieces",
            "transaction_date": datetime.utcnow().isoformat(),
            "reference_number": adjustment["id"],
            "notes": f"Stock adjustment - {adjustment['reason_code']}"
        }
        
        response = client.post("/transactions/", json=adjustment_transaction_data, headers=admin_headers)
        assert response.status_code == 201
        
        # Step 5: Verify complete audit trail
        part_id = str(test_parts["oil_filter"].id)
        response = client.get(f"/transactions/?part_id={part_id}", headers=admin_headers)
        assert response.status_code == 200
        transactions = response.json()
        
        # Should have adjustment transaction
        adjustment_transactions = [
            txn for txn in transactions 
            if txn["transaction_type"] == "adjustment" and 
            txn["reference_number"] == adjustment["id"]
        ]
        assert len(adjustment_transactions) == 1
        
        # Step 6: Get stock adjustment history
        response = client.get(f"/stock_adjustments/?inventory_id={inventory_item.id}", headers=admin_headers)
        assert response.status_code == 200
        adjustments = response.json()
        
        # Should have our adjustment
        our_adjustments = [
            adj for adj in adjustments 
            if adj["id"] == adjustment["id"]
        ]
        assert len(our_adjustments) == 1
        assert our_adjustments[0]["reason_code"] == "STOCKTAKE_DISCREPANCY"


class TestCrossOrganizationWorkflows:
    """Test workflows that span multiple organizations."""
    
    def test_multi_organization_inventory_transfer(
        self, client: TestClient, auth_headers, test_organizations, 
        test_parts, test_warehouses, db_session: Session
    ):
        """Test inventory transfers between different organization types."""
        oraseas_headers = auth_headers["oraseas_admin"]
        super_admin_headers = auth_headers["super_admin"]
        
        # Step 1: Transfer from Oraseas to customer (simulating order fulfillment)
        transfer_data = {
            "transaction_type": "transfer",
            "part_id": str(test_parts["bossaqua_pump"].id),
            "from_warehouse_id": str(test_warehouses["oraseas_main"].id),
            "to_warehouse_id": str(test_warehouses["customer1_main"].id),
            "quantity": "1.000",
            "unit_of_measure": "pieces",
            "transaction_date": datetime.utcnow().isoformat(),
            "notes": "Cross-organization transfer - proprietary part"
        }
        
        response = client.post("/transactions/", json=transfer_data, headers=oraseas_headers)
        assert response.status_code == 201
        transfer_transaction = response.json()
        
        # Step 2: Verify transaction appears in both organizations' records
        # Oraseas should see outbound transfer
        response = client.get("/transactions/", headers=oraseas_headers)
        assert response.status_code == 200
        oraseas_transactions = response.json()
        
        oraseas_transfer = [
            txn for txn in oraseas_transactions 
            if txn["id"] == transfer_transaction["id"]
        ]
        assert len(oraseas_transfer) == 1
        
        # Customer should see inbound transfer
        customer_headers = auth_headers["customer_admin"]
        response = client.get("/transactions/", headers=customer_headers)
        assert response.status_code == 200
        customer_transactions = response.json()
        
        customer_transfer = [
            txn for txn in customer_transactions 
            if txn["id"] == transfer_transaction["id"]
        ]
        assert len(customer_transfer) == 1
        
        # Step 3: Super admin should see all transactions
        response = client.get("/transactions/", headers=super_admin_headers)
        assert response.status_code == 200
        all_transactions = response.json()
        
        super_admin_transfer = [
            txn for txn in all_transactions 
            if txn["id"] == transfer_transaction["id"]
        ]
        assert len(super_admin_transfer) == 1
    
    def test_hierarchical_organization_data_access(
        self, client: TestClient, auth_headers, test_organizations, db_session: Session
    ):
        """Test that organization hierarchy affects data access properly."""
        super_admin_headers = auth_headers["super_admin"]
        oraseas_headers = auth_headers["oraseas_admin"]
        customer_headers = auth_headers["customer_admin"]
        
        # Super admin can see all organizations
        response = client.get("/organizations/", headers=super_admin_headers)
        assert response.status_code == 200
        all_orgs = response.json()
        assert len(all_orgs) >= 4  # Should see all test organizations
        
        org_types = {org["organization_type"] for org in all_orgs}
        expected_types = {"oraseas_ee", "bossaqua", "customer", "supplier"}
        assert expected_types.issubset(org_types)
        
        # Oraseas admin can see own organization and related data
        response = client.get("/organizations/", headers=oraseas_headers)
        assert response.status_code == 200
        oraseas_orgs = response.json()
        
        # Should see own organization and potentially suppliers
        oraseas_org_ids = {org["id"] for org in oraseas_orgs}
        assert str(test_organizations["oraseas"].id) in oraseas_org_ids
        
        # Customer admin can only see own organization
        response = client.get("/organizations/", headers=customer_headers)
        assert response.status_code == 200
        customer_orgs = response.json()
        
        # Should only see own organization
        customer_org_ids = {org["id"] for org in customer_orgs}
        assert customer_org_ids == {str(test_organizations["customer1"].id)}


class TestBusinessRuleEnforcement:
    """Test that business rules are properly enforced across workflows."""
    
    def test_proprietary_parts_business_rules(
        self, client: TestClient, auth_headers, test_parts, 
        test_organizations, db_session: Session
    ):
        """Test business rules around proprietary parts handling."""
        customer_headers = auth_headers["customer_admin"]
        oraseas_headers = auth_headers["oraseas_admin"]
        
        # Step 1: Verify proprietary part identification
        response = client.get("/parts/", headers=customer_headers)
        assert response.status_code == 200
        parts = response.json()
        
        proprietary_parts = [part for part in parts if part["is_proprietary"]]
        assert len(proprietary_parts) > 0
        
        bossaqua_parts = [
            part for part in proprietary_parts 
            if "bossaqua" in part["name"].lower()
        ]
        assert len(bossaqua_parts) > 0
        
        # Step 2: Test that proprietary parts have special handling
        proprietary_part = bossaqua_parts[0]
        
        # Proprietary parts should have specific supplier information
        assert proprietary_part["is_proprietary"] is True
        assert "bossaqua" in proprietary_part["manufacturer_part_number"].lower()
    
    def test_organization_type_constraints(
        self, client: TestClient, auth_headers, test_organizations, db_session: Session
    ):
        """Test that organization type constraints are enforced."""
        super_admin_headers = auth_headers["super_admin"]
        
        # Test 1: Cannot create duplicate Oraseas EE
        duplicate_oraseas = {
            "name": "Another Oraseas EE",
            "organization_type": "oraseas_ee",
            "address": "456 Duplicate Street",
            "contact_info": "duplicate@oraseas.com"
        }
        
        response = client.post("/organizations/", json=duplicate_oraseas, headers=super_admin_headers)
        assert response.status_code == 400
        
        # Test 2: Supplier must have parent organization
        orphan_supplier = {
            "name": "Orphan Supplier",
            "organization_type": "supplier",
            "address": "789 Orphan Lane",
            "contact_info": "orphan@supplier.com"
        }
        
        response = client.post("/organizations/", json=orphan_supplier, headers=super_admin_headers)
        assert response.status_code == 400
        
        # Test 3: Valid supplier with parent should work
        valid_supplier = {
            "name": "Valid Supplier",
            "organization_type": "supplier",
            "parent_organization_id": str(test_organizations["oraseas"].id),
            "address": "123 Valid Street",
            "contact_info": "valid@supplier.com"
        }
        
        response = client.post("/organizations/", json=valid_supplier, headers=super_admin_headers)
        assert response.status_code == 201
    
    def test_inventory_consistency_rules(
        self, client: TestClient, auth_headers, test_inventory, 
        test_parts, test_warehouses, db_session: Session
    ):
        """Test that inventory consistency rules are enforced."""
        customer_headers = auth_headers["customer_admin"]
        
        # Test 1: Cannot consume more than available stock
        inventory_item = test_inventory["customer1_oil_filter"]
        available_stock = float(inventory_item.current_stock)
        
        # Try to use more than available
        excessive_usage = {
            "part_id": str(test_parts["oil_filter"].id),
            "quantity": str(available_stock + 10.0),  # More than available
            "usage_date": datetime.utcnow().isoformat(),
            "warehouse_id": str(test_warehouses["customer1_main"].id),
            "notes": "Excessive usage test"
        }
        
        response = client.post("/part_usage/", json=excessive_usage, headers=customer_headers)
        # Should either fail or require approval
        assert response.status_code in [400, 422, 409]  # Various error codes possible
        
        # Test 2: Valid usage within stock limits should work
        valid_usage = {
            "part_id": str(test_parts["oil_filter"].id),
            "quantity": "1.000",  # Within available stock
            "usage_date": datetime.utcnow().isoformat(),
            "warehouse_id": str(test_warehouses["customer1_main"].id),
            "notes": "Valid usage test"
        }
        
        response = client.post("/part_usage/", json=valid_usage, headers=customer_headers)
        assert response.status_code == 201


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery scenarios."""
    
    def test_transaction_rollback_on_failure(
        self, client: TestClient, auth_headers, test_parts, 
        test_warehouses, db_session: Session
    ):
        """Test that failed transactions are properly rolled back."""
        oraseas_headers = auth_headers["oraseas_admin"]
        
        # Get initial inventory state
        response = client.get("/inventory/", headers=oraseas_headers)
        assert response.status_code == 200
        initial_inventory = response.json()
        
        # Try to create invalid transaction (negative quantity)
        invalid_transaction = {
            "transaction_type": "creation",
            "part_id": str(test_parts["oil_filter"].id),
            "to_warehouse_id": str(test_warehouses["oraseas_main"].id),
            "quantity": "-10.000",  # Invalid negative quantity for creation
            "unit_of_measure": "pieces",
            "transaction_date": datetime.utcnow().isoformat(),
            "notes": "Invalid transaction test"
        }
        
        response = client.post("/transactions/", json=invalid_transaction, headers=oraseas_headers)
        assert response.status_code in [400, 422]  # Should fail validation
        
        # Verify inventory unchanged
        response = client.get("/inventory/", headers=oraseas_headers)
        assert response.status_code == 200
        final_inventory = response.json()
        
        # Inventory should be unchanged
        assert len(initial_inventory) == len(final_inventory)
        for initial_item in initial_inventory:
            final_item = next(
                (item for item in final_inventory if item["id"] == initial_item["id"]), 
                None
            )
            assert final_item is not None
            assert final_item["current_stock"] == initial_item["current_stock"]
    
    def test_concurrent_inventory_updates(
        self, client: TestClient, auth_headers, test_inventory, 
        test_parts, test_warehouses, db_session: Session
    ):
        """Test handling of concurrent inventory updates."""
        customer_headers = auth_headers["customer_admin"]
        
        inventory_item = test_inventory["customer1_oil_filter"]
        
        # Simulate concurrent stock adjustments
        adjustment1_data = {
            "inventory_id": str(inventory_item.id),
            "quantity_adjusted": "2.000",
            "reason_code": "FOUND_STOCK",
            "notes": "Concurrent test adjustment 1"
        }
        
        adjustment2_data = {
            "inventory_id": str(inventory_item.id),
            "quantity_adjusted": "3.000",
            "reason_code": "FOUND_STOCK",
            "notes": "Concurrent test adjustment 2"
        }
        
        # Both should succeed (or one should fail with proper error)
        response1 = client.post("/stock_adjustments/", json=adjustment1_data, headers=customer_headers)
        response2 = client.post("/stock_adjustments/", json=adjustment2_data, headers=customer_headers)
        
        # At least one should succeed
        assert response1.status_code == 201 or response2.status_code == 201
        
        # Verify final inventory state is consistent
        response = client.get(f"/inventory/{inventory_item.id}", headers=customer_headers)
        assert response.status_code == 200
        final_inventory = response.json()
        
        # Stock should have increased by the sum of successful adjustments
        expected_increase = 0
        if response1.status_code == 201:
            expected_increase += 2.0
        if response2.status_code == 201:
            expected_increase += 3.0
        
        expected_stock = float(inventory_item.current_stock) + expected_increase
        assert float(final_inventory["current_stock"]) == expected_stock


class TestPerformanceAndScalability:
    """Test performance characteristics of business workflows."""
    
    def test_large_transaction_batch_processing(
        self, client: TestClient, auth_headers, test_parts, 
        test_warehouses, db_session: Session
    ):
        """Test processing of large batches of transactions."""
        oraseas_headers = auth_headers["oraseas_admin"]
        
        # Create multiple transactions in sequence
        transaction_count = 50
        created_transactions = []
        
        for i in range(transaction_count):
            transaction_data = {
                "transaction_type": "creation",
                "part_id": str(test_parts["oil_filter"].id),
                "to_warehouse_id": str(test_warehouses["oraseas_main"].id),
                "quantity": "1.000",
                "unit_of_measure": "pieces",
                "transaction_date": datetime.utcnow().isoformat(),
                "notes": f"Batch transaction {i+1}"
            }
            
            response = client.post("/transactions/", json=transaction_data, headers=oraseas_headers)
            assert response.status_code == 201
            created_transactions.append(response.json())
        
        # Verify all transactions were created
        assert len(created_transactions) == transaction_count
        
        # Test querying large transaction set
        response = client.get("/transactions/", headers=oraseas_headers)
        assert response.status_code == 200
        all_transactions = response.json()
        
        # Should include all our created transactions
        our_transaction_ids = {txn["id"] for txn in created_transactions}
        fetched_transaction_ids = {txn["id"] for txn in all_transactions}
        assert our_transaction_ids.issubset(fetched_transaction_ids)
    
    def test_complex_inventory_queries(
        self, client: TestClient, auth_headers, test_organizations, db_session: Session
    ):
        """Test performance of complex inventory queries."""
        oraseas_headers = auth_headers["oraseas_admin"]
        customer_headers = auth_headers["customer_admin"]
        
        # Test organization-wide inventory query
        response = client.get("/inventory/", headers=oraseas_headers)
        assert response.status_code == 200
        oraseas_inventory = response.json()
        
        # Should return results efficiently
        assert isinstance(oraseas_inventory, list)
        
        # Test filtered inventory queries
        if len(oraseas_inventory) > 0:
            sample_part_id = oraseas_inventory[0]["part_id"]
            response = client.get(f"/inventory/?part_id={sample_part_id}", headers=oraseas_headers)
            assert response.status_code == 200
            filtered_inventory = response.json()
            
            # All results should match the filter
            for item in filtered_inventory:
                assert item["part_id"] == sample_part_id
        
        # Test cross-organization inventory aggregation (super admin view)
        super_admin_headers = auth_headers["super_admin"]
        response = client.get("/inventory/", headers=super_admin_headers)
        assert response.status_code == 200
        all_inventory = response.json()
        
        # Should include inventory from multiple organizations
        org_ids = {item["warehouse"]["organization_id"] for item in all_inventory}
        assert len(org_ids) >= 2  # Should have multiple organizations