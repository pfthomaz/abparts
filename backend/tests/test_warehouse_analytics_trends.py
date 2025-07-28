"""
Unit tests for warehouse analytics trends CRUD function.
Tests the get_warehouse_analytics_trends function with various scenarios.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app import models
from app.models import OrganizationType, UserRole, UserStatus, PartType, TransactionType, MachineStatus
from app.crud.inventory import get_warehouse_analytics_trends
from app.auth import get_password_hash


class TestGetWarehouseAnalyticsTrends:
    """Test cases for get_warehouse_analytics_trends function"""
    
    def test_basic_trends_calculation_daily(self, db_session: Session):
        """Test basic trends calculation with daily aggregation"""
        # Create test organization
        org = models.Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
        db_session.flush()
        
        # Create test user
        user = models.User(
            username="test_user",
            email="test@example.com",
            password_hash=get_password_hash("password"),
            name="Test User",
            role=UserRole.user,
            user_status=UserStatus.active,
            organization_id=org.id,
            is_active=True
        )
        db_session.add(user)
        db_session.flush()
        
        # Create test warehouse
        warehouse = models.Warehouse(
            name="Test Warehouse",
            organization_id=org.id,
            location="Test Location",
            is_active=True
        )
        db_session.add(warehouse)
        db_session.flush()
        
        # Create test part
        part = models.Part(
            part_number="P001",
            name="Test Part",
            part_type=PartType.CONSUMABLE,
            unit_of_measure="pieces"
        )
        db_session.add(part)
        db_session.flush()
        
        # Create inventory
        inventory = models.Inventory(
            warehouse_id=warehouse.id,
            part_id=part.id,
            current_stock=Decimal("100.000"),
            minimum_stock_recommendation=Decimal("20.000"),
            unit_of_measure="pieces"
        )
        db_session.add(inventory)
        db_session.flush()
        
        # Create transactions over multiple days
        now = datetime.utcnow()
        transactions = []
        
        for i in range(5):
            transaction = models.Transaction(
                transaction_type="transfer",
                part_id=part.id,
                from_warehouse_id=warehouse.id,
                to_warehouse_id=warehouse.id,  # Self-transfer for testing
                quantity=Decimal(f"{10 + i}.000"),
                unit_of_measure="pieces",
                performed_by_user_id=user.id,
                transaction_date=now - timedelta(days=i)
            )
            transactions.append(transaction)
        
        db_session.add_all(transactions)
        db_session.commit()
        
        # Test daily trends calculation
        result = get_warehouse_analytics_trends(db_session, warehouse.id, period="daily", days=7)
        
        # Verify basic structure
        assert result["warehouse_id"] == str(warehouse.id)
        assert result["period"] == "daily"
        assert "date_range" in result
        assert "trends" in result
        
        # Verify date range
        date_range = result["date_range"]
        assert date_range["days"] == 7
        assert "start_date" in date_range
        assert "end_date" in date_range
        
        # Verify trends data
        trends = result["trends"]
        assert len(trends) == 8  # 7 days + 1 (inclusive range)
        
        # Each trend point should have required fields
        for trend in trends:
            assert "date" in trend
            assert "total_value" in trend
            assert "total_quantity" in trend
            assert "parts_count" in trend
            assert "transactions_count" in trend
            assert "total_inbound" in trend
            assert "total_outbound" in trend
            assert "net_change" in trend
    
    def test_trends_calculation_weekly(self, db_session: Session):
        """Test trends calculation with weekly aggregation"""
        # Create minimal test data
        org = models.Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
        db_session.flush()
        
        warehouse = models.Warehouse(
            name="Test Warehouse",
            organization_id=org.id,
            location="Test Location",
            is_active=True
        )
        db_session.add(warehouse)
        db_session.flush()
        db_session.commit()
        
        # Test weekly trends calculation
        result = get_warehouse_analytics_trends(db_session, warehouse.id, period="weekly", days=21)
        
        # Verify structure
        assert result["warehouse_id"] == str(warehouse.id)
        assert result["period"] == "weekly"
        assert result["date_range"]["days"] == 21
        
        # Weekly aggregation should have fewer data points
        trends = result["trends"]
        assert len(trends) >= 3  # At least 3 weeks for 21 days
        
        # Verify all trend points have required fields
        for trend in trends:
            assert all(key in trend for key in [
                "date", "total_value", "total_quantity", "parts_count",
                "transactions_count", "total_inbound", "total_outbound", "net_change"
            ])
    
    def test_trends_calculation_monthly(self, db_session: Session):
        """Test trends calculation with monthly aggregation"""
        # Create minimal test data
        org = models.Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
        db_session.flush()
        
        warehouse = models.Warehouse(
            name="Test Warehouse",
            organization_id=org.id,
            location="Test Location",
            is_active=True
        )
        db_session.add(warehouse)
        db_session.flush()
        db_session.commit()
        
        # Test monthly trends calculation
        result = get_warehouse_analytics_trends(db_session, warehouse.id, period="monthly", days=90)
        
        # Verify structure
        assert result["warehouse_id"] == str(warehouse.id)
        assert result["period"] == "monthly"
        assert result["date_range"]["days"] == 90
        
        # Monthly aggregation should have fewer data points
        trends = result["trends"]
        assert len(trends) >= 3  # At least 3 months for 90 days
        
        # Verify all trend points have required fields
        for trend in trends:
            assert all(key in trend for key in [
                "date", "total_value", "total_quantity", "parts_count",
                "transactions_count", "total_inbound", "total_outbound", "net_change"
            ])
    
    def test_warehouse_not_found_trends(self, db_session: Session):
        """Test error handling when warehouse doesn't exist for trends"""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics_trends(db_session, non_existent_id)
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()
    
    def test_inactive_warehouse_error_trends(self, db_session: Session):
        """Test error handling for inactive warehouse in trends"""
        # Create test organization
        org = models.Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
        db_session.flush()
        
        # Create inactive warehouse
        warehouse = models.Warehouse(
            name="Inactive Warehouse",
            organization_id=org.id,
            location="Test Location",
            is_active=False  # Inactive
        )
        db_session.add(warehouse)
        db_session.flush()
        db_session.commit()
        
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics_trends(db_session, warehouse.id)
        
        assert exc_info.value.status_code == 400
        assert "inactive warehouse" in str(exc_info.value.detail).lower()
    
    def test_invalid_warehouse_id_format_trends(self, db_session: Session):
        """Test error handling for invalid UUID format in trends"""
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics_trends(db_session, "invalid-uuid")
        
        assert exc_info.value.status_code == 400
        assert "invalid warehouse id format" in str(exc_info.value.detail).lower()
    
    def test_invalid_period_parameter(self, db_session: Session):
        """Test validation of period parameter"""
        # Create minimal test data
        org = models.Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
        db_session.flush()
        
        warehouse = models.Warehouse(
            name="Test Warehouse",
            organization_id=org.id,
            location="Test Location",
            is_active=True
        )
        db_session.add(warehouse)
        db_session.flush()
        db_session.commit()
        
        # Test invalid period values
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics_trends(db_session, warehouse.id, period="invalid")
        assert exc_info.value.status_code == 400
        assert "invalid period" in str(exc_info.value.detail).lower()
        
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics_trends(db_session, warehouse.id, period="yearly")
        assert exc_info.value.status_code == 400
        assert "must be one of" in str(exc_info.value.detail).lower()
    
    def test_invalid_days_parameter_trends(self, db_session: Session):
        """Test validation of days parameter in trends"""
        # Create minimal test data
        org = models.Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
        db_session.flush()
        
        warehouse = models.Warehouse(
            name="Test Warehouse",
            organization_id=org.id,
            location="Test Location",
            is_active=True
        )
        db_session.add(warehouse)
        db_session.flush()
        db_session.commit()
        
        # Test invalid days values
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics_trends(db_session, warehouse.id, days=0)
        assert exc_info.value.status_code == 400
        assert "between 1 and 365" in str(exc_info.value.detail)
        
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics_trends(db_session, warehouse.id, days=400)
        assert exc_info.value.status_code == 400
        assert "between 1 and 365" in str(exc_info.value.detail)  
  
    def test_trends_with_transaction_data(self, db_session: Session):
        """Test trends calculation with actual transaction data"""
        # Create test organization and user
        org = models.Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
        db_session.flush()
        
        user = models.User(
            username="test_user",
            email="test@example.com",
            password_hash=get_password_hash("password"),
            name="Test User",
            role=UserRole.user,
            user_status=UserStatus.active,
            organization_id=org.id,
            is_active=True
        )
        db_session.add(user)
        db_session.flush()
        
        # Create warehouses
        warehouse1 = models.Warehouse(
            name="Source Warehouse",
            organization_id=org.id,
            location="Location 1",
            is_active=True
        )
        warehouse2 = models.Warehouse(
            name="Target Warehouse",
            organization_id=org.id,
            location="Location 2",
            is_active=True
        )
        db_session.add_all([warehouse1, warehouse2])
        db_session.flush()
        
        # Create test parts
        part1 = models.Part(
            part_number="P001",
            name="Test Part 1",
            part_type=PartType.CONSUMABLE,
            unit_of_measure="pieces"
        )
        part2 = models.Part(
            part_number="P002",
            name="Test Part 2",
            part_type=PartType.CONSUMABLE,
            unit_of_measure="pieces"
        )
        db_session.add_all([part1, part2])
        db_session.flush()
        
        # Create inventory
        inventory1 = models.Inventory(
            warehouse_id=warehouse1.id,
            part_id=part1.id,
            current_stock=Decimal("100.000"),
            minimum_stock_recommendation=Decimal("20.000"),
            unit_of_measure="pieces"
        )
        inventory2 = models.Inventory(
            warehouse_id=warehouse1.id,
            part_id=part2.id,
            current_stock=Decimal("50.000"),
            minimum_stock_recommendation=Decimal("10.000"),
            unit_of_measure="pieces"
        )
        db_session.add_all([inventory1, inventory2])
        db_session.flush()
        
        # Create transactions across multiple days
        now = datetime.utcnow()
        transactions = []
        
        # Day 1: Multiple transactions
        for i in range(3):
            transaction = models.Transaction(
                transaction_type="transfer",
                part_id=part1.id,
                from_warehouse_id=warehouse2.id,
                to_warehouse_id=warehouse1.id,
                quantity=Decimal(f"{10 + i}.000"),
                unit_of_measure="pieces",
                performed_by_user_id=user.id,
                transaction_date=now - timedelta(days=1)
            )
            transactions.append(transaction)
        
        # Day 2: Different part
        transaction = models.Transaction(
            transaction_type="transfer",
            part_id=part2.id,
            from_warehouse_id=warehouse1.id,
            to_warehouse_id=warehouse2.id,
            quantity=Decimal("15.000"),
            unit_of_measure="pieces",
            performed_by_user_id=user.id,
            transaction_date=now - timedelta(days=2)
        )
        transactions.append(transaction)
        
        # Day 4: Large transaction
        transaction = models.Transaction(
            transaction_type="transfer",
            part_id=part1.id,
            from_warehouse_id=warehouse1.id,
            to_warehouse_id=warehouse2.id,
            quantity=Decimal("50.000"),
            unit_of_measure="pieces",
            performed_by_user_id=user.id,
            transaction_date=now - timedelta(days=4)
        )
        transactions.append(transaction)
        
        db_session.add_all(transactions)
        db_session.commit()
        
        # Test daily trends calculation
        result = get_warehouse_analytics_trends(db_session, warehouse1.id, period="daily", days=5)
        
        # Verify trends data
        trends = result["trends"]
        assert len(trends) == 6  # 5 days + 1
        
        # Find specific days and verify transaction data
        day1_trends = [t for t in trends if (now - timedelta(days=1)).date().isoformat() in t["date"]]
        day2_trends = [t for t in trends if (now - timedelta(days=2)).date().isoformat() in t["date"]]
        day4_trends = [t for t in trends if (now - timedelta(days=4)).date().isoformat() in t["date"]]
        
        # Day 1 should have inbound transactions (3 transactions, 1 part)
        if day1_trends:
            day1 = day1_trends[0]
            assert day1["transactions_count"] == 3
            assert day1["parts_count"] == 1  # Only part1 involved
            assert day1["total_inbound"] == 33.0  # 10 + 11 + 12
            assert day1["total_outbound"] == 0.0
            assert day1["net_change"] == 33.0
        
        # Day 2 should have outbound transaction (1 transaction, 1 part)
        if day2_trends:
            day2 = day2_trends[0]
            assert day2["transactions_count"] == 1
            assert day2["parts_count"] == 1  # Only part2 involved
            assert day2["total_inbound"] == 0.0
            assert day2["total_outbound"] == 15.0
            assert day2["net_change"] == -15.0
        
        # Day 4 should have outbound transaction (1 transaction, 1 part)
        if day4_trends:
            day4 = day4_trends[0]
            assert day4["transactions_count"] == 1
            assert day4["parts_count"] == 1  # Only part1 involved
            assert day4["total_inbound"] == 0.0
            assert day4["total_outbound"] == 50.0
            assert day4["net_change"] == -50.0
    
    def test_trends_with_supplier_order_pricing(self, db_session: Session):
        """Test trends calculation with supplier order pricing for inventory value"""
        # Create test organization
        org = models.Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
        db_session.flush()
        
        # Create supplier organization
        supplier_org = models.Organization(
            name="Supplier Organization",
            organization_type=OrganizationType.supplier,
            parent_organization_id=org.id,
            is_active=True
        )
        db_session.add(supplier_org)
        db_session.flush()
        
        # Create warehouse
        warehouse = models.Warehouse(
            name="Test Warehouse",
            organization_id=org.id,
            location="Test Location",
            is_active=True
        )
        db_session.add(warehouse)
        db_session.flush()
        
        # Create parts
        part1 = models.Part(
            part_number="P001",
            name="Expensive Part",
            part_type=PartType.CONSUMABLE,
            unit_of_measure="pieces"
        )
        part2 = models.Part(
            part_number="P002",
            name="Cheap Part",
            part_type=PartType.CONSUMABLE,
            unit_of_measure="pieces"
        )
        db_session.add_all([part1, part2])
        db_session.flush()
        
        # Create inventory
        inventory1 = models.Inventory(
            warehouse_id=warehouse.id,
            part_id=part1.id,
            current_stock=Decimal("10.000"),
            minimum_stock_recommendation=Decimal("5.000"),
            unit_of_measure="pieces"
        )
        inventory2 = models.Inventory(
            warehouse_id=warehouse.id,
            part_id=part2.id,
            current_stock=Decimal("100.000"),
            minimum_stock_recommendation=Decimal("20.000"),
            unit_of_measure="pieces"
        )
        db_session.add_all([inventory1, inventory2])
        db_session.flush()
        
        # Create supplier order with pricing
        supplier_order = models.SupplierOrder(
            ordering_organization_id=supplier_org.id,
            supplier_name="Test Supplier",
            order_date=datetime.utcnow() - timedelta(days=30),
            status="completed"
        )
        db_session.add(supplier_order)
        db_session.flush()
        
        # Create supplier order items with different prices
        order_item1 = models.SupplierOrderItem(
            supplier_order_id=supplier_order.id,
            part_id=part1.id,
            quantity=Decimal("5.000"),
            unit_price=Decimal("100.00")  # Expensive part
        )
        order_item2 = models.SupplierOrderItem(
            supplier_order_id=supplier_order.id,
            part_id=part2.id,
            quantity=Decimal("100.000"),
            unit_price=Decimal("10.00")  # Cheap part
        )
        db_session.add_all([order_item1, order_item2])
        db_session.commit()
        
        # Test trends calculation
        result = get_warehouse_analytics_trends(db_session, warehouse.id, period="daily", days=3)
        
        # Verify trends include inventory value calculations
        trends = result["trends"]
        assert len(trends) == 4  # 3 days + 1
        
        # At least one trend point should have positive total_value
        has_positive_value = any(trend["total_value"] > 0 for trend in trends)
        assert has_positive_value
        
        # Verify total_quantity is calculated
        has_positive_quantity = any(trend["total_quantity"] > 0 for trend in trends)
        assert has_positive_quantity
    
    def test_empty_warehouse_trends(self, db_session: Session):
        """Test trends calculation for warehouse with no inventory or transactions"""
        # Create test organization
        org = models.Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
        db_session.flush()
        
        # Create empty warehouse
        warehouse = models.Warehouse(
            name="Empty Warehouse",
            organization_id=org.id,
            location="Test Location",
            is_active=True
        )
        db_session.add(warehouse)
        db_session.flush()
        db_session.commit()
        
        # Test trends calculation
        result = get_warehouse_analytics_trends(db_session, warehouse.id, period="daily", days=3)
        
        # Verify all metrics are zero
        trends = result["trends"]
        assert len(trends) == 4  # 3 days + 1
        
        for trend in trends:
            assert trend["total_value"] == 0.0
            assert trend["total_quantity"] == 0.0
            assert trend["parts_count"] == 0
            assert trend["transactions_count"] == 0
            assert trend["total_inbound"] == 0.0
            assert trend["total_outbound"] == 0.0
            assert trend["net_change"] == 0.0
    
    def test_trends_date_range_edge_cases(self, db_session: Session):
        """Test trends calculation with edge case date ranges"""
        # Create minimal test data
        org = models.Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
        db_session.flush()
        
        warehouse = models.Warehouse(
            name="Test Warehouse",
            organization_id=org.id,
            location="Test Location",
            is_active=True
        )
        db_session.add(warehouse)
        db_session.flush()
        db_session.commit()
        
        # Test minimum days (1 day)
        result_min = get_warehouse_analytics_trends(db_session, warehouse.id, period="daily", days=1)
        assert result_min["date_range"]["days"] == 1
        assert len(result_min["trends"]) == 2  # 1 day + 1
        
        # Test maximum days (365 days)
        result_max = get_warehouse_analytics_trends(db_session, warehouse.id, period="daily", days=365)
        assert result_max["date_range"]["days"] == 365
        assert len(result_max["trends"]) == 366  # 365 days + 1
        
        # Test weekly aggregation with various day ranges
        result_weekly = get_warehouse_analytics_trends(db_session, warehouse.id, period="weekly", days=14)
        assert result_weekly["period"] == "weekly"
        assert len(result_weekly["trends"]) >= 2  # At least 2 weeks
        
        # Test monthly aggregation
        result_monthly = get_warehouse_analytics_trends(db_session, warehouse.id, period="monthly", days=60)
        assert result_monthly["period"] == "monthly"
        assert len(result_monthly["trends"]) >= 2  # At least 2 months
    
    def test_trends_performance_with_large_dataset(self, db_session: Session):
        """Test trends calculation performance with larger datasets"""
        # Create test organization and user
        org = models.Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
        db_session.flush()
        
        user = models.User(
            username="test_user",
            email="test@example.com",
            password_hash=get_password_hash("password"),
            name="Test User",
            role=UserRole.user,
            user_status=UserStatus.active,
            organization_id=org.id,
            is_active=True
        )
        db_session.add(user)
        db_session.flush()
        
        # Create warehouse
        warehouse = models.Warehouse(
            name="Large Warehouse",
            organization_id=org.id,
            location="Test Location",
            is_active=True
        )
        db_session.add(warehouse)
        db_session.flush()
        
        # Create multiple parts
        parts = []
        for i in range(10):  # 10 different parts
            part = models.Part(
                part_number=f"P{i:03d}",
                name=f"Test Part {i}",
                part_type=PartType.CONSUMABLE,
                unit_of_measure="pieces"
            )
            parts.append(part)
        db_session.add_all(parts)
        db_session.flush()
        
        # Create inventory for all parts
        inventories = []
        for part in parts:
            inventory = models.Inventory(
                warehouse_id=warehouse.id,
                part_id=part.id,
                current_stock=Decimal(f"{100 + parts.index(part) * 10}.000"),
                minimum_stock_recommendation=Decimal("20.000"),
                unit_of_measure="pieces"
            )
            inventories.append(inventory)
        db_session.add_all(inventories)
        db_session.flush()
        
        # Create many transactions across time periods
        now = datetime.utcnow()
        transactions = []
        
        # Create 90 transactions across 30 days (3 per day)
        for day in range(30):
            for transaction_num in range(3):  # 3 transactions per day
                part = parts[transaction_num % len(parts)]  # Cycle through parts
                transaction = models.Transaction(
                    transaction_type="transfer",
                    part_id=part.id,
                    from_warehouse_id=warehouse.id,
                    to_warehouse_id=warehouse.id,  # Self-transfer for testing
                    quantity=Decimal(f"{10 + transaction_num}.000"),
                    unit_of_measure="pieces",
                    performed_by_user_id=user.id,
                    transaction_date=now - timedelta(days=day, hours=transaction_num)
                )
                transactions.append(transaction)
        
        db_session.add_all(transactions)
        db_session.commit()
        
        # Test trends calculation with large dataset
        import time
        start_time = time.time()
        
        result = get_warehouse_analytics_trends(db_session, warehouse.id, period="daily", days=30)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify the calculation completed successfully
        assert result["warehouse_id"] == str(warehouse.id)
        assert result["period"] == "daily"
        assert len(result["trends"]) == 31  # 30 days + 1
        
        # Performance check - should complete within reasonable time (5 seconds)
        assert execution_time < 5.0, f"Trends calculation took too long: {execution_time:.2f} seconds"
        
        # Verify data integrity with large dataset
        trends = result["trends"]
        
        # Should have transaction data for most days
        days_with_transactions = sum(1 for trend in trends if trend["transactions_count"] > 0)
        assert days_with_transactions >= 25  # Most days should have transactions
        
        # Should have multiple parts involved
        max_parts_in_day = max(trend["parts_count"] for trend in trends)
        assert max_parts_in_day >= 3  # At least 3 different parts in some days
        
        # Test weekly aggregation with large dataset
        start_time = time.time()
        result_weekly = get_warehouse_analytics_trends(db_session, warehouse.id, period="weekly", days=30)
        end_time = time.time()
        weekly_execution_time = end_time - start_time
        
        assert weekly_execution_time < 5.0, f"Weekly trends calculation took too long: {weekly_execution_time:.2f} seconds"
        assert len(result_weekly["trends"]) >= 4  # At least 4 weeks
    
    def test_trends_database_error_handling(self, db_session: Session):
        """Test graceful handling of database errors in trends calculation"""
        # Create minimal test data
        org = models.Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
        db_session.flush()
        
        warehouse = models.Warehouse(
            name="Test Warehouse",
            organization_id=org.id,
            location="Test Location",
            is_active=True
        )
        db_session.add(warehouse)
        db_session.flush()
        db_session.commit()
        
        # Close the session to simulate database connection issues
        db_session.close()
        
        # The function should handle database errors gracefully
        with pytest.raises(Exception):  # Could be HTTPException or database exception
            get_warehouse_analytics_trends(db_session, warehouse.id)
    
    def test_trends_data_consistency(self, db_session: Session):
        """Test data consistency across different aggregation periods"""
        # Create test organization and user
        org = models.Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
        db_session.flush()
        
        user = models.User(
            username="test_user",
            email="test@example.com",
            password_hash=get_password_hash("password"),
            name="Test User",
            role=UserRole.user,
            user_status=UserStatus.active,
            organization_id=org.id,
            is_active=True
        )
        db_session.add(user)
        db_session.flush()
        
        # Create warehouse
        warehouse = models.Warehouse(
            name="Test Warehouse",
            organization_id=org.id,
            location="Test Location",
            is_active=True
        )
        db_session.add(warehouse)
        db_session.flush()
        
        # Create part
        part = models.Part(
            part_number="P001",
            name="Test Part",
            part_type=PartType.CONSUMABLE,
            unit_of_measure="pieces"
        )
        db_session.add(part)
        db_session.flush()
        
        # Create consistent transactions over 14 days (2 weeks)
        now = datetime.utcnow()
        transactions = []
        
        for day in range(14):
            transaction = models.Transaction(
                transaction_type="transfer",
                part_id=part.id,
                from_warehouse_id=warehouse.id,
                to_warehouse_id=warehouse.id,
                quantity=Decimal("10.000"),  # Same quantity each day
                unit_of_measure="pieces",
                performed_by_user_id=user.id,
                transaction_date=now - timedelta(days=day)
            )
            transactions.append(transaction)
        
        db_session.add_all(transactions)
        db_session.commit()
        
        # Get daily and weekly trends for the same period
        daily_result = get_warehouse_analytics_trends(db_session, warehouse.id, period="daily", days=14)
        weekly_result = get_warehouse_analytics_trends(db_session, warehouse.id, period="weekly", days=14)
        
        # Calculate totals from daily data
        daily_trends = daily_result["trends"]
        total_daily_transactions = sum(trend["transactions_count"] for trend in daily_trends)
        total_daily_inbound = sum(trend["total_inbound"] for trend in daily_trends)
        total_daily_outbound = sum(trend["total_outbound"] for trend in daily_trends)
        
        # Calculate totals from weekly data
        weekly_trends = weekly_result["trends"]
        total_weekly_transactions = sum(trend["transactions_count"] for trend in weekly_trends)
        total_weekly_inbound = sum(trend["total_inbound"] for trend in weekly_trends)
        total_weekly_outbound = sum(trend["total_outbound"] for trend in weekly_trends)
        
        # Totals should be consistent between aggregation periods
        assert total_daily_transactions == total_weekly_transactions
        assert abs(total_daily_inbound - total_weekly_inbound) < 0.01  # Allow for floating point precision
        assert abs(total_daily_outbound - total_weekly_outbound) < 0.01
        
        # Verify we have the expected number of transactions (14 total)
        assert total_daily_transactions == 14
        assert total_weekly_transactions == 14