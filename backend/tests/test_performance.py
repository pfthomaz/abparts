"""
Performance testing for ABParts data model and relationships.
Tests system performance under various load conditions.
"""

import pytest
import time
import uuid
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import (
    Organization, User, Part, Warehouse, Inventory, Machine, Transaction,
    OrganizationType, UserRole, UserStatus, PartType, TransactionType, MachineStatus
)


class TestDataModelPerformance:
    """Test performance of data model and relationships."""
    
    @pytest.fixture(scope="function")
    def large_dataset(self, db_session: Session) -> Dict[str, Any]:
        """Create a large dataset for performance testing."""
        # This fixture creates a larger dataset based on scale requirements
        data = {
            "organizations": [],
            "users": [],
            "parts": [],
            "warehouses": [],
            "machines": [],
            "inventory": [],
            "transactions": []
        }
        
        # Create Oraseas EE
        oraseas = Organization(
            name="Oraseas EE",
            organization_type=OrganizationType.oraseas_ee,
            address="123 Main St, Athens, Greece",
            contact_info="info@oraseas.com"
        )
        db_session.add(oraseas)
        db_session.flush()
        data["organizations"].append(oraseas)
        
        # Create BossAqua
        bossaqua = Organization(
            name="BossAqua Manufacturing",
            organization_type=OrganizationType.bossaqua,
            address="456 Factory Rd, Thessaloniki, Greece",
            contact_info="info@bossaqua.com"
        )
        db_session.add(bossaqua)
        db_session.flush()
        data["organizations"].append(bossaqua)
        
        # Create super admin
        super_admin = User(
            username="superadmin",
            email="admin@oraseas.com",
            password_hash="$2b$12$CwT1BvcjNvJdYkTJOb9pveq6Y7.iiCN2FhH8qZpVxzXn3w1cVPmEO",  # hashed "admin123"
            name="Super Administrator",
            role=UserRole.super_admin,
            user_status=UserStatus.active,
            organization_id=oraseas.id,
            is_active=True
        )
        db_session.add(super_admin)
        db_session.flush()
        data["users"].append(super_admin)
        
        # Create customer organizations (up to 100)
        for i in range(1, 51):  # Create 50 customer organizations
            customer = Organization(
                name=f"Customer Organization {i}",
                organization_type=OrganizationType.customer,
                address=f"{i} Customer St, City {i}, Greece",
                contact_info=f"contact@customer{i}.com"
            )
            db_session.add(customer)
            db_session.flush()
            data["organizations"].append(customer)
            
            # Create admin user for each customer
            admin = User(
                username=f"admin{i}",
                email=f"admin@customer{i}.com",
                password_hash="$2b$12$CwT1BvcjNvJdYkTJOb9pveq6Y7.iiCN2FhH8qZpVxzXn3w1cVPmEO",  # hashed "admin123"
                name=f"Admin {i}",
                role=UserRole.admin,
                user_status=UserStatus.active,
                organization_id=customer.id,
                is_active=True
            )
            db_session.add(admin)
            db_session.flush()
            data["users"].append(admin)
            
            # Create regular users for each customer (1-3 per customer)
            for j in range(1, random.randint(2, 4)):
                user = User(
                    username=f"user{i}_{j}",
                    email=f"user{j}@customer{i}.com",
                    password_hash="$2b$12$CwT1BvcjNvJdYkTJOb9pveq6Y7.iiCN2FhH8qZpVxzXn3w1cVPmEO",  # hashed "admin123"
                    name=f"User {j} of Customer {i}",
                    role=UserRole.user,
                    user_status=UserStatus.active,
                    organization_id=customer.id,
                    is_active=True
                )
                db_session.add(user)
                db_session.flush()
                data["users"].append(user)
            
            # Create warehouses for each customer (1-2 per customer)
            for j in range(1, random.randint(2, 3)):
                warehouse = Warehouse(
                    name=f"Warehouse {j} of Customer {i}",
                    organization_id=customer.id,
                    location=f"Location {j}, City {i}",
                    description=f"Warehouse {j} for Customer {i}"
                )
                db_session.add(warehouse)
                db_session.flush()
                data["warehouses"].append(warehouse)
            
            # Create machines for each customer (1-3 per customer)
            for j in range(1, random.randint(2, 4)):
                machine = Machine(
                    name=f"Machine {j} of Customer {i}",
                    model_type=random.choice(["V3.1B", "V4.0"]),
                    serial_number=f"SN-{i}-{j}-{uuid.uuid4().hex[:8]}",
                    customer_organization_id=customer.id,
                    purchase_date=datetime.utcnow() - timedelta(days=random.randint(30, 730)),
                    warranty_expiry_date=datetime.utcnow() + timedelta(days=random.randint(30, 730)),
                    status=MachineStatus.ACTIVE,
                    location=f"Bay {j}"
                )
                db_session.add(machine)
                db_session.flush()
                data["machines"].append(machine)
        
        # Create Oraseas warehouses
        main_warehouse = Warehouse(
            name="Oraseas Main Warehouse",
            organization_id=oraseas.id,
            location="Athens Central",
            description="Main distribution warehouse"
        )
        db_session.add(main_warehouse)
        db_session.flush()
        data["warehouses"].append(main_warehouse)
        
        secondary_warehouse = Warehouse(
            name="Oraseas Secondary Warehouse",
            organization_id=oraseas.id,
            location="Thessaloniki Branch",
            description="Secondary distribution point"
        )
        db_session.add(secondary_warehouse)
        db_session.flush()
        data["warehouses"].append(secondary_warehouse)
        
        # Create parts (up to 200)
        for i in range(1, 101):  # Create 100 parts
            part_type = PartType.CONSUMABLE if i % 3 != 0 else PartType.BULK_MATERIAL
            is_proprietary = i % 5 == 0
            unit = "pieces" if part_type == PartType.CONSUMABLE else "liters"
            
            part = Part(
                part_number=f"P-{i:04d}",
                name=f"Part {i}",
                description=f"Description for part {i}",
                part_type=part_type,
                is_proprietary=is_proprietary,
                unit_of_measure=unit,
                manufacturer_part_number=f"MFG-{i:04d}" if is_proprietary else None
            )
            db_session.add(part)
            db_session.flush()
            data["parts"].append(part)
            
            # Create inventory for this part in Oraseas warehouses
            inventory_main = Inventory(
                warehouse_id=main_warehouse.id,
                part_id=part.id,
                current_stock=Decimal(str(random.randint(50, 500))),
                minimum_stock_recommendation=Decimal(str(random.randint(10, 50))),
                unit_of_measure=unit
            )
            db_session.add(inventory_main)
            db_session.flush()
            data["inventory"].append(inventory_main)
            
            # Add some inventory to secondary warehouse
            if i % 3 == 0:
                inventory_secondary = Inventory(
                    warehouse_id=secondary_warehouse.id,
                    part_id=part.id,
                    current_stock=Decimal(str(random.randint(20, 200))),
                    minimum_stock_recommendation=Decimal(str(random.randint(5, 25))),
                    unit_of_measure=unit
                )
                db_session.add(inventory_secondary)
                db_session.flush()
                data["inventory"].append(inventory_secondary)
            
            # Add some inventory to customer warehouses
            for j in range(5):  # Add to 5 random customer warehouses
                if j < len(data["warehouses"]):
                    warehouse = random.choice([w for w in data["warehouses"] 
                                             if w.id != main_warehouse.id and w.id != secondary_warehouse.id])
                    
                    inventory_customer = Inventory(
                        warehouse_id=warehouse.id,
                        part_id=part.id,
                        current_stock=Decimal(str(random.randint(1, 50))),
                        minimum_stock_recommendation=Decimal(str(random.randint(1, 10))),
                        unit_of_measure=unit
                    )
                    db_session.add(inventory_customer)
                    db_session.flush()
                    data["inventory"].append(inventory_customer)
        
        # Create transactions (up to 7,500 per year, we'll create 500 for testing)
        transaction_types = list(TransactionType)
        for i in range(500):
            transaction_type = random.choice(transaction_types)
            part = random.choice(data["parts"])
            user = random.choice(data["users"])
            
            # Set up warehouse IDs based on transaction type
            from_warehouse_id = None
            to_warehouse_id = None
            machine_id = None
            
            if transaction_type == TransactionType.CREATION:
                # Creation transaction (to warehouse only)
                to_warehouse_id = random.choice(data["warehouses"]).id
            elif transaction_type == TransactionType.TRANSFER:
                # Transfer transaction (from and to warehouse)
                warehouses = random.sample(data["warehouses"], 2)
                from_warehouse_id = warehouses[0].id
                to_warehouse_id = warehouses[1].id
            elif transaction_type == TransactionType.CONSUMPTION:
                # Consumption transaction (from warehouse and machine)
                from_warehouse_id = random.choice(data["warehouses"]).id
                machine_id = random.choice(data["machines"]).id
            else:  # ADJUSTMENT
                # Adjustment transaction (from warehouse only)
                from_warehouse_id = random.choice(data["warehouses"]).id
            
            transaction = Transaction(
                transaction_type=transaction_type,
                part_id=part.id,
                from_warehouse_id=from_warehouse_id,
                to_warehouse_id=to_warehouse_id,
                machine_id=machine_id,
                quantity=Decimal(str(random.randint(1, 50))),
                unit_of_measure=part.unit_of_measure,
                performed_by_user_id=user.id,
                transaction_date=datetime.utcnow() - timedelta(days=random.randint(0, 365)),
                notes=f"Test transaction {i}"
            )
            db_session.add(transaction)
            db_session.flush()
            data["transactions"].append(transaction)
        
        db_session.commit()
        return data
    
    def test_query_performance_organization_hierarchy(self, db_session: Session, large_dataset):
        """Test query performance for organization hierarchy."""
        start_time = time.time()
        
        # Query all organizations with their parent/child relationships
        query = """
        SELECT o.id, o.name, o.organization_type, p.id as parent_id, p.name as parent_name,
               (SELECT COUNT(*) FROM organizations c WHERE c.parent_organization_id = o.id) as child_count
        FROM organizations o
        LEFT JOIN organizations p ON o.parent_organization_id = p.id
        """
        
        result = db_session.execute(text(query)).fetchall()
        
        duration = time.time() - start_time
        print(f"Organization hierarchy query: {len(result)} rows in {duration:.4f} seconds")
        
        # Performance assertion - should complete in under 1 second
        assert duration < 1.0, f"Organization hierarchy query took {duration:.4f} seconds, exceeding 1.0 second threshold"
    
    def test_query_performance_inventory_aggregation(self, db_session: Session, large_dataset):
        """Test query performance for inventory aggregation across warehouses."""
        start_time = time.time()
        
        # Query total inventory by part across all warehouses
        query = """
        SELECT p.id, p.name, p.part_number, 
               SUM(i.current_stock) as total_stock,
               COUNT(DISTINCT i.warehouse_id) as warehouse_count
        FROM parts p
        JOIN inventory i ON p.id = i.part_id
        GROUP BY p.id, p.name, p.part_number
        ORDER BY total_stock DESC
        """
        
        result = db_session.execute(text(query)).fetchall()
        
        duration = time.time() - start_time
        print(f"Inventory aggregation query: {len(result)} rows in {duration:.4f} seconds")
        
        # Performance assertion - should complete in under 1 second
        assert duration < 1.0, f"Inventory aggregation query took {duration:.4f} seconds, exceeding 1.0 second threshold"
    
    def test_query_performance_transaction_history(self, db_session: Session, large_dataset):
        """Test query performance for transaction history."""
        start_time = time.time()
        
        # Query transaction history with joins to related entities
        query = """
        SELECT t.id, t.transaction_type, t.transaction_date, 
               p.name as part_name, p.part_number,
               u.username as performed_by,
               fw.name as from_warehouse, 
               tw.name as to_warehouse,
               m.name as machine_name
        FROM transactions t
        JOIN parts p ON t.part_id = p.id
        JOIN users u ON t.performed_by_user_id = u.id
        LEFT JOIN warehouses fw ON t.from_warehouse_id = fw.id
        LEFT JOIN warehouses tw ON t.to_warehouse_id = tw.id
        LEFT JOIN machines m ON t.machine_id = m.id
        ORDER BY t.transaction_date DESC
        LIMIT 100
        """
        
        result = db_session.execute(text(query)).fetchall()
        
        duration = time.time() - start_time
        print(f"Transaction history query: {len(result)} rows in {duration:.4f} seconds")
        
        # Performance assertion - should complete in under 1 second
        assert duration < 1.0, f"Transaction history query took {duration:.4f} seconds, exceeding 1.0 second threshold"
    
    def test_query_performance_machine_parts_usage(self, db_session: Session, large_dataset):
        """Test query performance for machine parts usage analysis."""
        start_time = time.time()
        
        # Query parts usage by machine with aggregation
        query = """
        SELECT m.id, m.name, m.serial_number, m.model_type,
               COUNT(DISTINCT t.part_id) as unique_parts_used,
               COUNT(t.id) as total_usage_records,
               MAX(t.transaction_date) as last_usage_date
        FROM machines m
        LEFT JOIN transactions t ON m.id = t.machine_id AND t.transaction_type = 'consumption'
        GROUP BY m.id, m.name, m.serial_number, m.model_type
        ORDER BY total_usage_records DESC
        """
        
        result = db_session.execute(text(query)).fetchall()
        
        duration = time.time() - start_time
        print(f"Machine parts usage query: {len(result)} rows in {duration:.4f} seconds")
        
        # Performance assertion - should complete in under 1 second
        assert duration < 1.0, f"Machine parts usage query took {duration:.4f} seconds, exceeding 1.0 second threshold"
    
    def test_api_performance_inventory_listing(self, client: TestClient, auth_headers, large_dataset):
        """Test API performance for inventory listing."""
        headers = auth_headers["super_admin"]
        
        start_time = time.time()
        response = client.get("/inventory/", headers=headers)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        inventory = response.json()
        
        print(f"Inventory API listing: {len(inventory)} items in {duration:.4f} seconds")
        
        # Performance assertion - should complete in under 2 seconds
        assert duration < 2.0, f"Inventory API listing took {duration:.4f} seconds, exceeding 2.0 second threshold"
    
    def test_api_performance_transaction_listing(self, client: TestClient, auth_headers, large_dataset):
        """Test API performance for transaction listing."""
        headers = auth_headers["super_admin"]
        
        start_time = time.time()
        response = client.get("/transactions/", headers=headers)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        transactions = response.json()
        
        print(f"Transactions API listing: {len(transactions)} items in {duration:.4f} seconds")
        
        # Performance assertion - should complete in under 2 seconds
        assert duration < 2.0, f"Transactions API listing took {duration:.4f} seconds, exceeding 2.0 second threshold"
    
    def test_api_performance_dashboard(self, client: TestClient, auth_headers, large_dataset):
        """Test API performance for dashboard data."""
        headers = auth_headers["super_admin"]
        
        start_time = time.time()
        response = client.get("/dashboard/summary", headers=headers)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        dashboard = response.json()
        
        print(f"Dashboard API: loaded in {duration:.4f} seconds")
        
        # Performance assertion - should complete in under 2 seconds
        assert duration < 2.0, f"Dashboard API took {duration:.4f} seconds, exceeding 2.0 second threshold"


class TestConcurrencyPerformance:
    """Test system performance under concurrent load."""
    
    @pytest.mark.parametrize("concurrent_users", [5, 10, 20])
    def test_concurrent_inventory_queries(self, client: TestClient, auth_headers, large_dataset, concurrent_users):
        """Test performance under concurrent inventory queries."""
        import threading
        import queue
        
        results = queue.Queue()
        headers = auth_headers["super_admin"]
        
        def worker():
            start_time = time.time()
            response = client.get("/inventory/", headers=headers)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                results.put({"success": True, "duration": duration, "items": len(response.json())})
            else:
                results.put({"success": False, "duration": duration, "status": response.status_code})
        
        # Start concurrent threads
        threads = []
        for _ in range(concurrent_users):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        durations = []
        successes = 0
        failures = 0
        
        while not results.empty():
            result = results.get()
            if result["success"]:
                durations.append(result["duration"])
                successes += 1
            else:
                failures += 1
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        
        print(f"Concurrent inventory queries ({concurrent_users} users):")
        print(f"  Successes: {successes}, Failures: {failures}")
        print(f"  Average duration: {avg_duration:.4f}s, Max duration: {max_duration:.4f}s")
        
        # Performance assertions
        assert failures == 0, f"Had {failures} failed requests under concurrent load"
        assert avg_duration < 5.0, f"Average request duration {avg_duration:.4f}s exceeds 5.0 second threshold"
        assert max_duration < 10.0, f"Maximum request duration {max_duration:.4f}s exceeds 10.0 second threshold"
    
    def test_concurrent_transaction_creation(self, client: TestClient, auth_headers, test_parts, test_warehouses, test_users):
        """Test performance under concurrent transaction creation."""
        import threading
        import queue
        
        results = queue.Queue()
        headers = auth_headers["super_admin"]
        
        def worker(i):
            # Create a unique transaction
            transaction_data = {
                "transaction_type": "creation",
                "part_id": str(test_parts["oil_filter"].id),
                "to_warehouse_id": str(test_warehouses["oraseas_main"].id),
                "quantity": "10.000",
                "unit_of_measure": "pieces",
                "transaction_date": datetime.utcnow().isoformat(),
                "notes": f"Concurrent test transaction {i}"
            }
            
            start_time = time.time()
            response = client.post("/transactions/", json=transaction_data, headers=headers)
            duration = time.time() - start_time
            
            if response.status_code == 201:
                results.put({"success": True, "duration": duration, "id": response.json()["id"]})
            else:
                results.put({"success": False, "duration": duration, "status": response.status_code})
        
        # Start concurrent threads (5 concurrent transaction creations)
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        durations = []
        successes = 0
        failures = 0
        
        while not results.empty():
            result = results.get()
            if result["success"]:
                durations.append(result["duration"])
                successes += 1
            else:
                failures += 1
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        
        print(f"Concurrent transaction creation (5 transactions):")
        print(f"  Successes: {successes}, Failures: {failures}")
        print(f"  Average duration: {avg_duration:.4f}s, Max duration: {max_duration:.4f}s")
        
        # Performance assertions
        assert failures == 0, f"Had {failures} failed transaction creations under concurrent load"
        assert avg_duration < 2.0, f"Average transaction creation {avg_duration:.4f}s exceeds 2.0 second threshold"