"""
Unit tests for warehouse analytics CRUD functions.
Tests the get_warehouse_analytics function with various scenarios.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app import models
from app.models import OrganizationType, UserRole, UserStatus, PartType, TransactionType, MachineStatus
from app.crud.inventory import get_warehouse_analytics, get_warehouse_analytics_trends
from app.auth import get_password_hash


class TestGetWarehouseAnalytics:
    """Test cases for get_warehouse_analytics function"""
    
    def test_basic_analytics_calculation(self, db_session: Session):
        """Test basic analytics calculation with simple inventory data"""
        # Create test organization
        org = models.Organization(
            name="Test Organization",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add(org)
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
            part_type=PartType.BULK_MATERIAL,
            unit_of_measure="liters"
        )
        db_session.add_all([part1, part2])
        db_session.flush()
        
        # Create inventory items
        inventory1 = models.Inventory(
            warehouse_id=warehouse.id,
            part_id=part1.id,
            current_stock=Decimal("50.000"),
            minimum_stock_recommendation=Decimal("10.000"),
            unit_of_measure="pieces"
        )
        inventory2 = models.Inventory(
            warehouse_id=warehouse.id,
            part_id=part2.id,
            current_stock=Decimal("0.000"),  # Out of stock
            minimum_stock_recommendation=Decimal("5.000"),
            unit_of_measure="liters"
        )
        db_session.add_all([inventory1, inventory2])
        db_session.flush()
        db_session.commit()
        
        # Test analytics calculation
        result = get_warehouse_analytics(db_session, warehouse.id)
        
        # Verify basic structure
        assert result["warehouse_id"] == str(warehouse.id)
        assert result["warehouse_name"] == "Test Warehouse"
        assert "analytics_period" in result
        assert "inventory_summary" in result
        assert "top_parts_by_value" in result
        assert "stock_movements" in result
        assert "turnover_metrics" in result
        
        # Verify inventory summary
        inventory_summary = result["inventory_summary"]
        assert inventory_summary["total_parts"] == 2
        assert inventory_summary["out_of_stock_parts"] == 1
        assert inventory_summary["total_value"] >= 0
    
    def test_warehouse_not_found(self, db_session: Session):
        """Test error handling when warehouse doesn't exist"""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics(db_session, non_existent_id)
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()
    
    def test_empty_warehouse_analytics(self, db_session: Session):
        """Test analytics calculation for warehouse with no inventory"""
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
        
        # Test analytics calculation
        result = get_warehouse_analytics(db_session, warehouse.id)
        
        # Verify all metrics are zero or empty
        inventory_summary = result["inventory_summary"]
        assert inventory_summary["total_parts"] == 0
        assert inventory_summary["total_value"] == 0.0
        assert inventory_summary["low_stock_parts"] == 0
        assert inventory_summary["out_of_stock_parts"] == 0
        
        assert result["top_parts_by_value"] == []
        
        stock_movements = result["stock_movements"]
        assert stock_movements["total_inbound"] == 0.0
        assert stock_movements["total_outbound"] == 0.0
        assert stock_movements["net_change"] == 0.0


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
        
        # Create test warehouse
        warehouse = models.Warehouse(
            name="Test Warehouse",
            organization_id=org.id,
            location="Test Location",
            is_active=True
        )
        db_session.add(warehouse)
        db_session.flush()
        db_session.commit()
        
        # Test trends calculation
        result = get_warehouse_analytics_trends(db_session, warehouse.id, period="daily")
        
        # Verify basic structure
        assert "warehouse_id" in result
        assert "trends" in result
        assert result["period"] == "daily"
    
    def test_trends_weekly_aggregation(self, db_session: Session):
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
        
        # Test weekly trends
        result = get_warehouse_analytics_trends(db_session, warehouse.id, period="weekly")
        
        # Verify structure
        assert "warehouse_id" in result
        assert "trends" in result
        assert result["period"] == "weekly"
    
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
        
        # Test invalid period
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics_trends(db_session, warehouse.id, period="invalid")
        
        assert exc_info.value.status_code == 400
        assert "invalid period" in str(exc_info.value.detail).lower()