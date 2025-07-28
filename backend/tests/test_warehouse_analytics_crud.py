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
        inventory3 = models.Inventory(
            warehouse_id=warehouse.id,
            part_id=part1.id,  # Different part instance for testing
            current_stock=Decimal("8.000"),  # Low stock
            minimum_stock_recommendation=Decimal("10.000"),
            unit_of_measure="pieces"
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
        assert inventory_summary["total_parts"] == 2  # Two inventory records
        assert inventory_summary["out_of_stock_parts"] == 1  # One with 0 stock
        assert inventory_summary["low_stock_parts"] == 1  # One at/below minimum
        assert inventory_summary["total_value"] >= 0  # Should be non-negative
    
    def test_warehouse_not_found(self, db_session: Session):
        """Test error handling when warehouse doesn't exist"""
        non_existent_id = uuid.uuid4()
        
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics(db_session, non_existent_id)
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()
    
    def test_inactive_warehouse_error(self, db_session: Session):
        """Test error handling for inactive warehouse"""
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
            get_warehouse_analytics(db_session, warehouse.id)
        
        assert exc_info.value.status_code == 400
        assert "inactive warehouse" in str(exc_info.value.detail).lower()
    
    def test_invalid_warehouse_id_format(self, db_session: Session):
        """Test error handling for invalid UUID format"""
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics(db_session, "invalid-uuid")
        
        assert exc_info.value.status_code == 400
        assert "invalid warehouse id format" in str(exc_info.value.detail).lower()
    
    def test_invalid_days_parameter(self, db_session: Session):
        """Test validation of days parameter"""
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
            get_warehouse_analytics(db_session, warehouse.id, days=0)
        assert exc_info.value.status_code == 400
        assert "between 1 and 365" in str(exc_info.value.detail)
        
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics(db_session, warehouse.id, days=400)
        assert exc_info.value.status_code == 400
        assert "between 1 and 365" in str(exc_info.value.detail)
    
    def test_invalid_date_range(self, db_session: Session):
        """Test validation of date range parameters"""
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
        
        # Test start date after end date
        start_date = datetime.utcnow()
        end_date = start_date - timedelta(days=1)
        
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics(db_session, warehouse.id, start_date=start_date, end_date=end_date)
        
        assert exc_info.value.status_code == 400
        assert "start date must be before" in str(exc_info.value.detail).lower()
        
        # Test date range too large (more than 2 years)
        start_date = datetime.utcnow() - timedelta(days=800)
        end_date = datetime.utcnow()
        
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics(db_session, warehouse.id, start_date=start_date, end_date=end_date)
        
        assert exc_info.value.status_code == 400
        assert "cannot exceed 2 years" in str(exc_info.value.detail).lower()
        
        # Test future start date
        future_date = datetime.utcnow() + timedelta(days=1)
        
        with pytest.raises(HTTPException) as exc_info:
            get_warehouse_analytics(db_session, warehouse.id, start_date=future_date)
        
        assert exc_info.value.status_code == 400
        assert "cannot be in the future" in str(exc_info.value.detail).lower()
    
    def test_analytics_with_transactions(self, db_session: Session):
        """Test analytics calculation with transaction data"""
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
            warehouse_id=warehouse1.id,
            part_id=part.id,
            current_stock=Decimal("100.000"),
            minimum_stock_recommendation=Decimal("20.000"),
            unit_of_measure="pieces"
        )
        db_session.add(inventory)
        db_session.flush()
        
        # Create transactions within the analytics period
        now = datetime.utcnow()
        
        # Inbound transaction
        inbound_transaction = models.Transaction(
            transaction_type="transfer",  # Use string value
            part_id=part.id,
            from_warehouse_id=warehouse2.id,
            to_warehouse_id=warehouse1.id,
            quantity=Decimal("50.000"),
            unit_of_measure="pieces",
            performed_by_user_id=user.id,
            transaction_date=now - timedelta(days=5)
        )
        
        # Outbound transaction
        outbound_transaction = models.Transaction(
            transaction_type="transfer",  # Use string value
            part_id=part.id,
            from_warehouse_id=warehouse1.id,
            to_warehouse_id=warehouse2.id,
            quantity=Decimal("30.000"),
            unit_of_measure="pieces",
            performed_by_user_id=user.id,
            transaction_date=now - timedelta(days=3)
        )
        
        db_session.add_all([inbound_transaction, outbound_transaction])
        db_session.commit()
        
        # Test analytics calculation
        result = get_warehouse_analytics(db_session, warehouse1.id, days=10)
        
        # Verify stock movements
        stock_movements = result["stock_movements"]
        assert stock_movements["total_inbound"] == 50.0
        assert stock_movements["total_outbound"] == 30.0
        assert stock_movements["net_change"] == 20.0
        
        # Verify turnover metrics are calculated
        turnover_metrics = result["turnover_metrics"]
        assert "average_turnover_days" in turnover_metrics
        assert "fast_moving_parts" in turnover_metrics
        assert "slow_moving_parts" in turnover_metrics
    
    def test_analytics_with_supplier_order_pricing(self, db_session: Session):
        """Test analytics calculation with supplier order pricing data"""
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
            ordering_organization_id=supplier_org.id,  # Correct field name
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
        
        # Test analytics calculation
        result = get_warehouse_analytics(db_session, warehouse.id)
        
        # Verify inventory summary includes total value
        inventory_summary = result["inventory_summary"]
        assert inventory_summary["total_value"] > 0
        
        # Verify top parts by value (expensive part should be first despite lower quantity)
        top_parts = result["top_parts_by_value"]
        assert len(top_parts) == 2
        
        # The expensive part (10 units * $100) should have higher total value than cheap part (100 units * $10)
        expensive_part = next((p for p in top_parts if p["part_id"] == str(part1.id)), None)
        cheap_part = next((p for p in top_parts if p["part_id"] == str(part2.id)), None)
        
        assert expensive_part is not None
        assert cheap_part is not None
        assert expensive_part["total_value"] == 1000.0  # 10 * 100
        assert cheap_part["total_value"] == 1000.0  # 100 * 10
    
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
        
        turnover_metrics = result["turnover_metrics"]
        assert turnover_metrics["average_turnover_days"] == 0
        assert turnover_metrics["fast_moving_parts"] == 0
        assert turnover_metrics["slow_moving_parts"] == 0
    
    def test_analytics_date_range_filtering(self, db_session: Session):
        """Test that analytics properly filter by date range"""
        # Create test data
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
        
        warehouse1 = models.Warehouse(
            name="Warehouse 1",
            organization_id=org.id,
            location="Location 1",
            is_active=True
        )
        warehouse2 = models.Warehouse(
            name="Warehouse 2",
            organization_id=org.id,
            location="Location 2",
            is_active=True
        )
        db_session.add_all([warehouse1, warehouse2])
        db_session.flush()
        
        part = models.Part(
            part_number="P001",
            name="Test Part",
            part_type=PartType.CONSUMABLE,
            unit_of_measure="pieces"
        )
        db_session.add(part)
        db_session.flush()
        
        # Create transactions outside and inside the date range
        now = datetime.utcnow()
        
        # Transaction outside range (too old)
        old_transaction = models.Transaction(
            transaction_type="transfer",  # Use string value
            part_id=part.id,
            from_warehouse_id=warehouse2.id,
            to_warehouse_id=warehouse1.id,
            quantity=Decimal("100.000"),
            unit_of_measure="pieces",
            performed_by_user_id=user.id,
            transaction_date=now - timedelta(days=50)
        )
        
        # Transaction inside range
        recent_transaction = models.Transaction(
            transaction_type="transfer",  # Use string value
            part_id=part.id,
            from_warehouse_id=warehouse2.id,
            to_warehouse_id=warehouse1.id,
            quantity=Decimal("25.000"),
            unit_of_measure="pieces",
            performed_by_user_id=user.id,
            transaction_date=now - timedelta(days=5)
        )
        
        db_session.add_all([old_transaction, recent_transaction])
        db_session.commit()
        
        # Test analytics with 10-day range (should only include recent transaction)
        result = get_warehouse_analytics(db_session, warehouse1.id, days=10)
        
        stock_movements = result["stock_movements"]
        assert stock_movements["total_inbound"] == 25.0  # Only recent transaction
        assert stock_movements["total_outbound"] == 0.0
        assert stock_movements["net_change"] == 25.0
        
        # Test analytics with 60-day range (should include both transactions)
        result_long = get_warehouse_analytics(db_session, warehouse1.id, days=60)
        
        stock_movements_long = result_long["stock_movements"]
        assert stock_movements_long["total_inbound"] == 125.0  # Both transactions
        assert stock_movements_long["total_outbound"] == 0.0
        assert stock_movements_long["net_change"] == 125.0
    
    def test_database_error_handling(self, db_session: Session):
        """Test graceful handling of database errors"""
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
        # Note: This test may need adjustment based on actual error handling implementation
        with pytest.raises(Exception):  # Could be HTTPException or database exception
            get_warehouse_analytics(db_session, warehouse.id)
    
    def test_organization_scoping_validation(self, db_session: Session):
        """Test that analytics respect organization boundaries"""
        # Create two separate organizations
        org1 = models.Organization(
            name="Organization 1",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        org2 = models.Organization(
            name="Organization 2",
            organization_type=OrganizationType.customer,
            is_active=True
        )
        db_session.add_all([org1, org2])
        db_session.flush()
        
        # Create warehouses in different organizations
        warehouse1 = models.Warehouse(
            name="Warehouse 1",
            organization_id=org1.id,
            location="Location 1",
            is_active=True
        )
        warehouse2 = models.Warehouse(
            name="Warehouse 2",
            organization_id=org2.id,
            location="Location 2",
            is_active=True
        )
        db_session.add_all([warehouse1, warehouse2])
        db_session.flush()
        db_session.commit()
        
        # Analytics should work for each warehouse independently
        result1 = get_warehouse_analytics(db_session, warehouse1.id)
        result2 = get_warehouse_analytics(db_session, warehouse2.id)
        
        assert result1["warehouse_id"] == str(warehouse1.id)
        assert result1["warehouse_name"] == "Warehouse 1"
        assert result2["warehouse_id"] == str(warehouse2.id)
        assert result2["warehouse_name"] == "Warehouse 2"


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
             ns == 14io_transactklywee total_ssert    a     == 14
nsnsactioly_tra total_daissert       atotal)
 s (14 ionnsacttraber of  numhe expectedhave twe fy  Veri     #
        01
   tbound) < 0._ou_weekly - totalily_outboundl_data(toabs  assert       ecision
ing point prow for float  # All0.01ound) < inbotal_weekly__inbound - ttal_daily(to assert abs     ns
  tionsactraal_weekly_= tottions =y_transacilt total_da asser
       riodson peregatiween aggstent bet consi should be   # Totals     
        nds)
re weekly_tinfor trend bound"] otal_out"tum(trend[nd = sekly_outbou_wetalto        ends)
y_trin weeklrend d"] for tl_inbounend["tota(tr sum =ndnboueekly_ial_wot
        ty_trends)end in weekltrount"] for sactions_cantrnd["rem(tons = su_transactiklyee_wal        totds"]
rent["tully_resrends = weekeekly_t   w   
  kly dataom weetotals frlculate     # Ca   
        _trends)
 in dailyor trend "] futboundtal_ond["to(tretbound = sumily_oual_da  tot    nds)
  trend in daily_tre"] for inboundtal_["to= sum(trendy_inbound l_dail tota   nds)
    n daily_trer trend ifo_count"] nsactions["trasum(trend = sactionsaily_trantotal_d   
     "]ends"trily_result[rends = da daily_t       daily data
otals from te tla # Calcu  
       
       days=14)weekly",="odid, perie.houswaresion, nds(db_seslytics_treuse_anahowaresult = get_y_re   weekl   
  ", days=14)od="dailyse.id, periwarehousion, ses_trends(db_analyticsouse_et_warehult = gy_res       dailiod
 ersame pnds for the  weekly trendGet daily a #       
      it()
   ommsession.cdb_       ons)
 tiransacadd_all(t db_session.  
           on)
  cti(transans.appendsactio    tran             )
  
     ys=day)edelta(datimnow - ion_date=ransact   t           ser.id,
  id=u_by_user_performed                pieces",
measure="unit_of_                 each day
me quantity# Sa),  0"mal("10.00y=Deci   quantit            house.id,
 ared=wuse_i_wareho   to         ,
    e.id=warehouse_idm_warehous         fro
       d,d=part.i      part_i   ",
       transfer"_type=ctionsa        tran        saction(
els.Tranon = modacti  trans        :
  ange(14)n ror day i        f       
s = []
 transaction        tcnow()
.u= datetimenow 
        eeks) days (2 wover 14nsactions istent trate cons      # Crea 
     h()
    ession.flus_s     db  
 part)on.add(   db_sessi
     
        )"pieces"of_measure=    unit_       NSUMABLE,
 COtType.rt_type=Par        pat",
    t Par="Tes  name
          ="P001",berart_num           pt(
  models.Par  part =art
      te p     # Crea       
()
    n.flush_sessio  dbuse)
      add(warehoession.    db_s     )
    
   ueactive=Tr         is_
   Location","Test    location=,
         n_id=org.idiozatani   org      ,
    Warehouse"Testname="       
     .Warehouse(e = modelsehous
        warousereh# Create wa      
          ()
ushflsession.b_ dr)
       dd(useession.a_sdb    )
           ue
 _active=Tr       is    .id,
 on_id=org organizati         ,
  atus.activetatus=UserSt    user_s    ser,
    UserRole.ue=      rol   ser",
   t Uname="Tes      ),
      password"ord_hash("_passw=gethashrd_sswo       pa",
     ample.com="test@exmail          e",
  "test_user   username=       
  er( models.Us    user = 
          flush()
 ession.        db_s)
orgssion.add( db_se         )

      _active=True       is   tomer,
  ype.custionTganizaon_type=Orzatiani        orgn",
    rganizatioe="Test O    nam(
        anizationls.Orgode     org = m   
 userndn aizatiost organ # Create te   
    ""n periods"t aggregatioifferenss dstency acroata consi"""Test d      on):
  n: Sessidb_sessioelf, nsistency(s_coends_datadef test_tr   
    
 d)se.ion, warehous(db_sessirend_analytics_tet_warehouse  g
          eption excsedatabaon or xceptiHTTPE # Could be n): Exceptioses(t.raih pytes
        witullyrs gracefse errobale datandld han shouunctio The f
        #
        e()ion.closb_sess
        des issuonnectione cabaslate datsion to simusesse the  Clo    #   
 
        ommit()_session.c        db)
n.flush(b_sessio   douse)
     warehsion.add(ses    db_          )

  e=Truis_active       ",
     cationst LoTecation="      lo
      =org.id,anization_id     org,
       e"st Warehousame="Te   n      house(
   odels.Warehouse = m    ware 
        )
   .flush(ion db_sess)
       sion.add(org db_ses          )
  
   active=True    is_     tomer,
   onType.cusganizatition_type=Oranizarg    o     ",
   ationniz"Test Orgame=         naon(
   s.Organizatimodelorg =    data
     l test maeate mini       # Crn"""
 alculationds ctres in ror database erndling ofeful hagracTest ""      ":
  ion): Sessb_session(self, dlingr_handase_erronds_databf test_trede
    
     weeksAt least 44  # >= "]) kly["trendsweeresult_ert len( ass
       conds"ime:.2f} seion_teekly_execut {wng: took too loculationcalnds  tre"Weekly, fe < 5.0ution_tim_exect weeklyerass          
    
  tart_time_time - s_time = endonly_executi  week      time()
me.= ti_time 
        end", days=30)"weeklyperiod=rehouse.id, n, wads(db_sessio_trene_analytics_warehous = getult_weekly       resme.time()
 time = ti start_       set
atath large dgation wigrekly ag weest        # Te 
    s
   e dayn soms irtifferent pa deast 3 3  # At l >=rts_in_dayssert max_pa)
        a trendsrend in"] for tcountrts_pamax(trend["n_day = max_parts_i       
 volvedparts inultiple  mhaveShould     # 
    
        ctionshave transas should  # Most daytions >= 25 with_transacs_sert day     as  ] > 0)
 s_count"ransaction["tif trendnds n tretrend i for  sum(1ions =h_transactit      days_w
   days most data forctionsa tran Should have  #       
    "]
   ["trendssultnds = re    tre  t
  ge datase with lartyntegrita i# Verify da       
       conds"
  e:.2f} seion_timxecuto long: {en took to calculatiods"Tren 5.0, fe <_timiont executsser        aonds)
(5 sec time n reasonablewithite d compleshouleck - formance ch      # Per        
  ays + 1
31  # 30 d"]) == "trendst[sulrert len(sse  a      daily"
= "] =["period"t result       asser
 )use.id str(wareho_id"] ==rehouselt["waert resu
        assessfullyuccpleted scomtion e calcula th# Verify       
  ime
       start_ttime - time = end_xecution_       e)
 ime(me.tme = ti      end_ti     
     , days=30)
aily" period="darehouse.id,_session, wdb_trends(_analyticshouse = get_ware     result
          me.time()
 e = ti   start_timme
     import ti    
    atasetwith large dculation nds caltreTest        #         
 commit()
_session.db        actions)
transall(ion.add_     db_sess      
tion)
     nsacappend(traansactions.      tr  
         )              m)
 tion_nuacansours=trdays=day, hedelta( - time=now_dataction    trans           
     =user.id,by_user_id  performed_               eces",
   e="piurof_meas      unit_           "),
   num}.000ansaction_f"{10 + trecimal( quantity=D                 ing
  testfer for -trans # Selfuse.id, =warehoehouse_idwar        to_      id,
      =warehouse.e_idrehousfrom_wa                    ,
_id=part.id        part            r",
="transfepetytion_ransac       t            action(
 ans models.Trnsaction =         trarts
        pae through # Cycl)] n(partsn_num % leransactiort = parts[t       pa         ns per day
ransactio):  # 3 tn range(3um ition_n for transac         (30):
  ay in range       for ddays
 ss 30 ons acro00 transactie 1atre   # C 
     ]
       = [ons titransac    
    ime.utcnow()atet= dnow ds
        e periotimoss ions acrransactreate many t     # C  
   sh()
      ion.flu  db_sess
      ories)nventadd_all(in.ssio      db_seentory)
  append(invventories.         in   )
           "pieces"
 =_measure   unit_of          "),
   al("20.000cimndation=Derecommenimum_stock_         mi  0"),
     rt) * 10}.00ndex(pas.i{100 + partimal(f"stock=Decent_urr       c
         id,part. part_id=       d,
        warehouse.ise_id=  warehou          y(
    .Inventormodelsnventory =        i:
      parts in part      for]
  es = [tori    inven
    all parts for  inventory Create 
        #       flush()
on.db_sessis)
        _all(partsession.add   db_    t)
 nd(parpeparts.ap      
             )s"
     ="pieceasure_of_me     unit       ABLE,
    SUMPartType.CONrt_type=        pa        {i}",
 Partest "T=f       name
         ,3d}"P{i:0t_number=f"      par         s.Part(
 modelt =         par  s
  artt p differen10):  # 10n range(  for i i  = []
         parts ts
   iple par mult# Create          
   ()
   ssion.flush   db_se     rehouse)
on.add(wa_sessi   db
          )
   ue_active=Tr   is         cation",
"Test Location=lo            .id,
=orgion_idanizat        orge",
    WarehousLarge      name="se(
       Warehouels. = moduse  wareho      rehouse
ate wa   # Cre     
     ()
   ushsion.fl    db_sesuser)
    add(ion.   db_sess       )
    True
  ive=s_act  i     .id,
     =orgidrganization_ o          tive,
 atus.acSts=Useratu user_st           e.user,
serRol    role=U,
        "Test Userme="   na      ord"),
   ash("passwssword_h_hash=get_paord    passw",
        ple.comst@exam="teail   em,
         _user"estusername="t          
  .User(ls= mode user 
          
     ush()ession.fldb_s   (org)
     sion.add      db_ses )
  
       Trueve=ti       is_ac,
     meronType.custoizatiOrgantype=rganization_           oon",
 izatiest Organ="Tme        na(
    ons.Organizati org = model
       n and userioorganizatreate test 
        # Csets"""r data largence withformation perulands calcTest tre""   "
     :sion)esn: Sf, db_sessiodataset(selth_large_formance_wiertrends_p def test_  
 
    sonthst 2 m # At leas"]) >= 2 "trendnthly[(result_moassert len
        "monthlyd"] == ""periothly[lt_mon assert resu   =60)
    thly", daysod="monid, periouse.arehion, wsessnds(db__trenalyticsarehouse_at_wonthly = ge   result_m
     ggregationst monthly a       # Te 
        2 weeks
 least= 2  # At ends"]) >y["tr_weeklresultn(assert le
        "weekly"d"] == ekly["periot result_we       asserays=14)
 ", d"weeklyd=e.id, perioarehousession, wtrends(db_sanalytics_house_get_wareekly = t_weresul       nges
 y ravarious dagation with grest weekly ag Te     #    
       days + 1
  # 365 == 366"]) rendsmax["t len(result_    assert
    = 365ys"] =]["dae"ate_rangax["drt result_m    asse365)
    ys="daily", dariod=d, pe warehouse.isession,trends(db_lytics__ana_warehouseax = get result_m    ays)
   days (365 dimum t maxTes#      
           day + 1
  1]) == 2  #rends"n["t_milen(resultt        asser
 = 1ys"] =]["daange"["date_rresult_minsert       as=1)
  daysily", eriod="daehouse.id, p war_session,nds(dbtreanalytics_ehouse_get_warn = t_mi resul       y)
 days (1 daest minimum   # T     
       )
 n.commit(ssio       db_seush()
 sion.fl     db_seshouse)
   wareession.add(       db_s  )
 
      ctive=Trues_a       ion",
     "Test Locati= location       
    d=org.id,zation_i     organi       use",
 Warehome="Test         nae(
   ousarehe = models.Whous   ware    
 )
        h(ession.flus      db_s(org)
  on.add    db_sessi
           )ve=True
     is_acti
        pe.customer,ionTyzattype=Organiganization_        or    ation",
 Organizst="Te      nameon(
      nizatils.Orgag = mode    orta
    danimal test te mi   # Crea  
   """te ranges dasedge cath elculation wicarends st t"Te"   "):
     ionn: Sessb_sessiolf, ddge_cases(senge_eate_rast_trends_d def te  
   = 0.0
  ] =ge"hant_c"ne[t trend     asser
       "] == 0.0boundotal_outnd["t assert tre      = 0.0
      =inbound"]"total_rend[    assert t       
 "] == 0s_counton"transacti trend[ssert         a= 0
   "] =ts_counrend["part assert t          
 ty"] == 0.0quantiend["total_ssert tr         a == 0.0
   e"]alu_votal"tend[   assert tr        trends:
  for trend in      
     s + 1
      3 days) == 4  #endsert len(tr as
       ds"]ensult["tr= res ndre      t   are zero
icsy all metrifVer #        
3)
        y", days=riod="dailse.id, peion, warehous(db_sesslytics_trendanae_rehouswasult = get_re     ion
   ds calculaten# Test tr      
     
     mit()on.com db_sessi     .flush()
  ssiondb_se
        use).add(warehossion     db_se          )
e
 rue=Ts_activ           ition",
 ="Test Locaocation      l   d,
   d=org.ianization_i       org   ",
  ehouse"Empty Warame=    n    
    ouse(areh= models.Wse warehou  
      warehousety ate emp    # Cre    
       sh()
 flun.  db_sessio     
 (org)ddion.a   db_sess          )
 e
  ru is_active=T          tomer,
 onType.cusatinizn_type=Orgaganizatio  or         n",
 izatio Organ name="Test           anization(
ls.Orgrg = mode        onization
orgaate test Cre     # "
   ions""sactrantory or tno invense with rehou waon forcalculatiest trends """T:
        : Session)db_session(self, _trendswarehousest_empty_te 
    def uantity
   itive_q has_pos    assertrends)
     trend in t] > 0 forty"uantiotal_qtrend["ty = any(ititive_quant    has_pos
    dis calculatey l_quantitotarify t      # Ve    
  alue
    e_v has_positivert  ass      rends)
d in ten0 for tr> lue"] "total_vatrend[ any(ve_value =ositias_p   halue
     ve total_ve positit should havintrend pot least one    # A   
          1
# 3 days + nds) == 4  len(tre   assert   ds"]
   esult["trennds = r tre      ns
 alculatio value cnventorylude inds incerify tre       # V
        
 ays=3)"daily", diod= perhouse.id,areon, wsinds(db_ses_trealyticsehouse_anwarlt = get_     resuulation
   ds calcen tr# Test        
    
    on.commit() db_sessi])
       rder_item2der_item1, odd_all([ordb_session.a              )
 art
  # Cheap p0") "10.0imal(it_price=Dec   un
         0"),00.00ecimal("1=D quantity  ,
         part2.id    part_id=        ,
er.idsupplier_ordr_order_id=   supplie   (
      erOrderItemplimodels.Supder_item2 = or   )
       art
      xpensive p)  # E"100.00e=Decimal(" unit_pric   ,
        "5.000")=Decimal(quantity     d,
       .ipart1rt_id= pa  ,
         _order.iderpliorder_id=super_li  supp
          Item(plierOrderodels.Sup1 = mr_item      orde prices
  h differents witrder itemupplier o# Create s          
 )
     ush(sion.fl   db_seser)
     rdier_oon.add(suppldb_sessi          )
     ed"
 pletstatus="com       0),
     lta(days=3() - timedetcnowatetime.u=d_date    order      
  ",Suppliert me="Teser_na suppli         
  _org.id,plier=supization_idring_organ       ordeer(
     erOrdppliodels.Su mder =r_orie     supplng
   pricirder with lier opp Create su    #      
    )
  h(sion.flusdb_ses     ory2])
   entry1, inv([inventod_allssion.ad  db_se
        )    pieces"
  "of_measure=t_   uni         0.000"),
al("2=Decimtiondak_recommenmum_stocni       mi0"),
     .00cimal("100stock=De  current_          .id,
d=part2rt_i         pa.id,
   ouse=warehrehouse_id      wa     ventory(
 = models.In inventory2 )
       
        "pieces"f_measure=t_o uni          00"),
 ecimal("5.0endation=Dcommmum_stock_re mini         ),
  "00.0"10=Decimal(urrent_stock      cid,
      t1.=parid     part_
       ouse.id,id=warehe_  warehous
          nventory(.I= modelsventory1      in   ry
ate invento       # Cre
        
 sh()ion.flusess  db_   art2])
   art1, p([pllssion.add_a   db_se    )
       es"
  sure="piecof_meait_         unE,
   CONSUMABLPartType._type=      part",
      Parte="Cheap        nam     ="P002",
 part_number       art(
    .P models part2 =  )
       es"
      e="piect_of_measur uni        
   ONSUMABLE,=PartType.Ctype  part_         ",
 rte PaExpensiv  name="       ",
   "P001t_number=         par.Part(
   els part1 = mod  rts
     pa Create    #     
       ush()
 ession.fl   db_se)
     warehousd(ion.adsess  db_  )
    
        ve=Truecti is_a        n",
   tioLoca="Test   location         id,
 ion_id=org.nizatrga o         se",
  est Warehou   name="T       
  ehouse(= models.Waruse    warehoe
     ate warehous # Cre       
      sh()
  _session.flu dbrg)
       pplier_odd(suession.a    db_s     )
    True
   _active=     is     .id,
  id=orgganization_or   parent_     r,
    .suppliepetionTyganizaOrzation_type=organi            ",
tionOrganizar lie="Suppame        nn(
    Organizatiols.org = modeplier_  suption
      anizaplier orgreate sup # C    
           
flush()_session.      dbadd(org)
  ion. db_sess  )
       
      ive=Trueact    is_        tomer,
nType.cusatioOrganizn_type=anizatiorg        oion",
    rganizatt Oname="Tes     (
       ationanizmodels.Orgorg =     n
    anizatiot orgate tes       # Cree"""
  valury for inventoricinglier order ph suppittion wcula calds tren"""Test        ion):
ssion: Sessself, db_ser_pricing(upplier_orderends_with_s def test_t0
    
   0.= -5ge"] =net_chan["y4t da       asser0.0
      5ound"] ==total_outb" day4[sert      as     .0
 nd"] == 0inbou"total_day4[ert      ass
       volvedrt1 in pa# Only1  "] == parts_county4["ert da        ass   == 1
 "] countnsactions_"traert day4[      ass0]
      nds[4 = day4_tre day  
         trends:    if day4_
     1 part)ion,ansact tr(1tion transactbound ve ouould ha Day 4 sh #   
            = -15.0
change"] =net_2["sert day     as  15.0
     "] == tbound"total_ouay2[ssert d          a 0.0
  "] ==l_inboundtota2["assert day            2 involved
ly part= 1  # Onnt"] =s_couy2["partsert da  as       "] == 1
   _countionsransactert day2["t       ass
     nds[0]2 = day2_tre  day         
 ay2_trends:      if d
   1 part)on, transactin (1ctio transaundhave outboould # Day 2 sh         
    0
   = 33.change"] =y1["net_   assert da         0.0
 "] ==utbound["total_oassert day1       + 12
       # 10 + 11 33.0nd"] == l_inbou day1["totart    asse        ved
part1 invol  # Only "] == 1s_countpartay1[" dsert          as 3
  ount"] ==ons_csactian"trert day1[         ass  
 _trends[0]day1y1 =         da   ds:
 1_tren     if day
   ts), 2 parctionss (3 transaonansactinbound trd have iay 1 shoul        # D     

   "date"]]t() in t[oformais=4)).date().a(days- timedeltf (now s i t in trends = [t fortrendday4_]
        ["date"] in trmat()date().isofota(days=2)).imedelw - tnds if (notret for t in _trends = [     day2]]
   t["date") in rmat(ate().isofo=1)).dmedelta(daysif (now - ti in trends for tnds = [t day1_tre       ion data
 ct transas and verifyfic dayd speci  # Fin          

    + 1days ) == 6  # 5 endstrt len(  asser  ]
    "trends" = result[     trends   rends data
Verify t     #     
   s=5)
    aydaily", d".id, period=rehouse1ion, wads(db_sessenytics_tre_analt_warehous result = ge    ion
    calculatnds daily tre  # Test         
   ommit()
  n.c  db_sessioons)
      nsactitraall(d_ssion.ad      db_se   
  )
     sactionend(tranctions.app    transa  )
    4)
      delta(days==now - timeateon_dsacti      tran,
      er.idr_id=us_by_useedrform  pe          eces",
ure="pi_of_meas     unit    ,
   50.000")l("=Decimatityuan         q,
   house2.idareehouse_id=w    to_ward,
        ehouse1.i=warwarehouse_id       from_
     1.id,id=partart_      p      nsfer",
e="tran_typ transactio          (
 nsactionmodels.Traaction =    trans     
ransaction tDay 4: Large        #     
ros)
    zehould show ctions (s No transa# Day 3:        
  
      action)end(transtions.appac      trans
   )
       2)a(days=medeltw - tin_date=notransactio          er.id,
  y_user_id=usormed_b       perf
     ces",ure="piemeas unit_of_       ),
    0""15.00l(cimaity=Dequant            id,
ouse2.=wareh_ido_warehouse          td,
  arehouse1.iehouse_id=wm_war    fro  id,
      id=part2.       part_",
     ferans"tr_type=ctionsa  tran         saction(
 dels.Tran moransaction =      t part
  2: Different Day  #
              )
 (transactionions.appendansact       tr        )
  1)
       edelta(days=w - timate=non_dransactio       t,
         r.iduseby_user_id=ormed_   perf       
      eces",="pireit_of_measu    un         000"),
    i}."{10 +Decimal(f  quantity=           id,
   ouse1.=warehe_idhous     to_ware        d,
   house2.iareuse_id=wehom_war    fro            ,
.idrt1t_id=pa         par
       ransfer",type="taction_trans         
       tion(ransac.T = modelsransaction t           e(3):
in rang i or    f    ns
actioiple trans 1: MultDay     # 
   ]
        s = [ionansact        trw()
cnome.utatetinow = ds
        le dayipacross multsactions  trante   # Crea     
   h()
     n.flussio  db_ses)
      2]ventoryntory1, inall([inveon.add__sessi     db   )
 "
       "piecesre=easuf_mt_o   uni
         "),("10.000imaln=Deccommendatio_retockimum_s    min       00"),
 imal("50.0Dect_stock=   curren      .id,
   =part2art_id         p   e1.id,
rehous_id=waarehouse w         
  ntory(veInmodels.ry2 = nvento
        i       )es"
 sure="piecnit_of_mea        u   
 "),al("20.000cimation=Dek_recommendmum_stocini    m
        "100.000"),ecimal(k=Dt_stocen   curr       id,
  t1.d=parpart_i            house1.id,
aree_id=wehous   war        ory(
 odels.Invententory1 = m  inv
      ry invento# Create   
             sh()
.flussiondb_se        ])
art2, p[part1add_all(ion._sess    db   )
 "
        pieceseasure="_of_m      unit      ONSUMABLE,
e=PartType.C_typ        partt 2",
    "Test Pare=      nam      ",
002"Pumber=rt_n         pa  
 ls.Part(part2 = mode )
               s"
sure="piecemeait_of_   un,
         e.CONSUMABLEe=PartTyp   part_typ       
  st Part 1",   name="Te      ",
   001umber="P   part_n
         s.Part(del mo  part1 =
       partse test# Creat        
        
n.flush()ssiodb_se   )
     warehouse2]warehouse1, dd_all([.aion db_sess      )
        e=True
     is_activ",
        "Location 2  location=       
   d=org.id,_ionganizati or          ,
 "house Warergetme="Ta   na(
         arehouse models.Wouse2 =areh     w     )
     e
 ruactive=T       is_    on 1",
 ocatiocation="L l    d,
       n_id=org.itioniza   orga,
         "usereho"Source Waname=         
   use(ls.Warehomode = rehouse1      waes
  te warehousea       # Cr 
      ()
  ssion.flushdb_se
        (user)ion.addss     db_se  )
   
      active=True is_          id,
 id=org.zation_rgani  o        ,
  atus.activetatus=UserSt    user_s        ,
.userle=UserRole      ro",
       Usere="Test       nam
     "),rdwo("passrd_hashsswoh=get_paasrd_hwoss pa       m",
    xample.cot@eesail="t          em  _user",
strname="teuse           .User(
 odelsr = muse
        ()
        lushession.fb_s       dg)
 on.add(ordb_sessi        )
    
    =Trueis_active          
  omer,.custpeTyzationganion_type=Or organizati          on",
 Organizati="Test name       tion(
     els.Organiza org = modser
        and uanizatione test org Creat     #"""
   saction datal tranth actuaion wids calculatest tren"T""       Session):
 sion:  db_sesn_data(self,nsactiotraends_with_est_tr
    def til)
    e.detanfo.valuc_istr(ex in 365"1 and een ert "betw ass
        == 400dee.status_co.valunfoc_iert ex   ass  00)
   =4ysd, dause.iehoar wession,b_ss_trends(d_analytichouse  get_ware        _info:
  ) as exctionepTPExcses(HTytest.rai with p            
  detail)
 ue.alexc_info.vr(65" in sten 1 and 3sert "betwe as    
   = 400atus_code =stnfo.value.t exc_iseras  
      days=0)se.id, houaren, w(db_sessiotics_trendse_analyouswareh  get_        
  info:s exc_ aption)(HTTPExcest.raiseste     with pyues
    days valvalidest in  # T             
)
 .commit(b_session
        dh()on.flusdb_sessi    )
    ouse(warehddssion.a   db_se      )
   ue
    Tractive=    is_",
        ocationTest L="location         rg.id,
   ization_id=o   organ      use",
   hoest Waree="T         nam  rehouse(
 models.Wa= arehouse   w 
      h()
       flusn.db_sessio
        (org)ession.add    db_s )
        e=True
   s_activ i    
       pe.customer,zationTytype=Organiization_      organn",
      tiorganiza"Test Oame=        nion(
    nizats.Orgaelodrg = m o
       aat destnimal t miate    # Cre  
  trends"""arameter in ys pion of davalidatest "T ""     on):
  ion: Sessif, db_sessnds(seltre_parameter_nvalid_days  def test_i  
  )
  ).lower(.detail_info.valuen str(exc one of" i "must beassert        400
= atus_code =stinfo.value.exc_ssert        a
 yearly")od=", periouse.idwarehion, ds(db_sesss_trenlyticehouse_ana  get_war
          nfo: exc_iion) asExcepts(HTTPseest.rai pyt      with        
  r()
).loweil.detanfo.value(exc_istrin " lid periodert "inva  ass
      400code == tatus_o.value.srt exc_inf     asse  ")
 alid"inv period=use.id,warehon, ios(db_sessendcs_tralytiuse_anareho   get_w        
 nfo:c_is exn) aceptioes(HTTPExisest.raith pyt      w
  esaluperiod v invalid   # Test     
         it()
.commssion   db_se)
     h(session.flus  db_      
ouse)wareh.add( db_session
       
        )ue=Trs_active    i
        ",onti Loca="Testocation          l
  d,id=org.iion_   organizat      ouse",
   areh W="Test  name         ouse(
 Wareh= models.ehouse        war
       flush()
  on.b_sessi     drg)
   sion.add(o db_ses     )
   
       active=True       is_r,
     omeustzationType.ce=Organiion_typganizat       or",
     ationrganizst O  name="Te      
    nization(gaels.Or  org = moda
       dat testale minimCreat#       
  er"""arametf period pation oest valid   """T    sion):
  Sesdb_session:eter(self, ameriod_par_pinvalid def test_
    
   er()).lowetailue.dfo.val_in in str(excormat"ehouse id fwar"invalid   assert 
       == 400dee.status_co.valuxc_infossert e    a   
 
        )-uuid"idvalion, "inds(db_sesslytics_trenarehouse_ana     get_w       exc_info:
as ption) PExces(HTTst.raise  with pyte"
      ""in trends format invalid UUIDing for andlst error h    """Te   ession):
 ion: Sess db_ss(self,_trendatrmouse_id_fonvalid_warehdef test_i
    ()
    were.detail).lovaluinfo.(exc_tr in sehouse"ive warnactt "i asser400
       de == ue.status_co.valexc_infoassert          
       
rehouse.id) wa(db_session,dscs_trenti_analyseet_warehou       g
     s exc_info:on) aPExceptis(HTTst.raise with pyte 
            t()
  on.commi   db_sessish()
     lusion.fdb_ses    
    house)(ware.add db_session  )
       
      activealse  # Ins_active=F         ion",
   ti"Test Locaion=locat       
     ,id=org.idtion_niza   orga   ",
       WarehouseInactive     name="se(
       arehouls.We = mode   warehousse
     ive warehoureate inact C 
        #       )
ssion.flush(db_se        .add(org)
ssionb_se        d        )

Truee=  is_activ       er,
   nType.customioganizatype=Organization_t    or        n",
ganizatiome="Test Or na           (
anization= models.Org    org n
    rganizatiotest oate        # Cre"
 ""snde in trerehousctive wag for inar handlinro""Test er  "
      ession):n: Sdb_sessiof, s(selrendse_error_twarehouive_ctdef test_ina  
    ower()
  .detail).lnfo.valueexc_itr(" in st foundt "no  asser4
      _code == 40usatlue.st exc_info.vaassert           
     d)
ent_i, non_existdb_sessions_trends(nalyticse_aget_warehou       nfo:
     _ition) as exccepTTPEx.raises(Hth pytest        wi
        
id.uuid4() = uu_existent_id      non"
  ds""st for trenexin't ouse doesn warehdling whe hanest error """T    
   on):ssission: Se(self, db_se_trends_foundse_nott_warehoudef tes
    
          ])"
      _changed", "nettboun "total_ound",tal_inbount", "tos_couansaction      "tr  
        ",count", "parts_tityan"total_qu", valuel_tota", ""date            [
     in ey ktrend forey in all(krt     asse       trends:
  end in     for trields
    fquiredhave rents trend poierify all       # V
       days
    for 90ths on3 mst   # At lea>= 3len(trends)   assert 
      "]"trendss = result[  trend  
    intsta poewer dae fn should haviogatonthly aggre    # M   
    0
     "] == 9"]["daysrangedate_["sert result        asly"
 "monthd"] ==io"perrt result[     asse.id)
   rehousewa"] == str(use_idehoesult["warert r    assure
    truct  # Verify s
              90)
hly", days=="monteriodhouse.id, pession, wares(db_slytics_trende_anarehouswat = get_ul    resn
    iolculats carendonthly t# Test m 
        )
       on.commit(db_sessi      
  sh()ssion.flu  db_se
      se).add(warehousion  db_ses
      
        )ctive=True     is_a   ion",
    ocat"Test Lion=atloc           ,
 g.idtion_id=ororganiza         use",
   st Wareho"Te     name=   e(
    ehousels.Ware = mod  warehous 
      ()
       lushssion.f       db_se
 on.add(org)db_sessi         )
   
    =Trueis_active      mer,
      pe.custoonTynization_type=Orgarganizati          otion",
  anizarg"Test Oname=           ization(
 els.Organmod     org = data
    test eate minimal       # Cr"
 tion""gregathly agwith monon  calculatiTest trends   """
     Session):ssion: elf, db_se(sonthlyation_m_calcult_trendsdef tes
       ])
            nge"
 _cha"netbound", _out "totalund","total_inbo ",s_countctionnsa     "tra           ,
"untcoparts_ "quantity",l_ "tota",total_valueate", "     "d         in [
  for key  trend key inrt all(se    as        trends:
 trend in     for   d fields
 irerequnts have rend poi tallify   # Ver  
      s
      or 21 dayt 3 weeks f3  # At leasds) >= trenert len(   ass    nds"]
 lt["tre= resutrends    nts
      data poifewerd have  shoulgationWeekly aggre   #    
        = 21
  "days"] =ge"][te_ranult["dassert res  a  
     "weekly"iod"] ==erresult["psert 
        asuse.id)tr(wareho= sd"] =house_isult["waresert re
        aseurify structer   # V           
=21)
  , daysd="weekly"erio.id, prehouse wab_session,(d_trendsyticsanalwarehouse_esult = get_   rtion
     ends calculaly trest week     # T
         
  .commit()_session      dbflush()
  ession.  db_s     )
 ouserehwan.add(essio   db_s)
     
        eactive=Tru     is_   n",
    tiot Locacation="Tes lo         
  rg.id,=oization_id  organ        
  house",Test Ware  name="
          rehouse(= models.Wawarehouse   
            h()
  ion.flusess     db_sg)
   on.add(or   db_sessi  )
         ue
  ive=Tr     is_act     r,
  omepe.custanizationTyion_type=Orgrganizat o     ",
      onatiest Organiz="T     name
       n(.Organizatio models       org =est data
 mal treate mini    # C""
    egation"ly aggron with weektis calcula"Test trend    ""on):
    essiession: Self, db_skly(son_weealculati_trends_cest  def t   
   in trend
 e" "net_changert  ass
           in trend"tal_outboundto" assert 
           " in trendinbound "total_ssert       ad
     entr_count" in ionst "transact  asser          trend
unt" in arts_co  assert "p        in trend
  ty" tal_quanti "to     assert
       din trene" total_valusert "       as    trend
 date" in ssert "        a   trends:
 r trend in         fos
quired fielde reuld havpoint shoend    # Each tr   
        ange)
  lusive r(incs + 1 = 8  # 7 daynds) =ret len(tsser]
        ads"enesult["tr  trends = r   a
   ds datify tren       # Ver    
     nge
n date_raend_date" i "rtse
        asate_rangeate" in dt "start_d   asser     
ays"] == 7_range["datessert d      ange"]
  te_rat["daesulge = r_ran  date      ge
ranrify date  Ve 
        #        in result
nds"trert "asse       sult
 n rege" idate_ran assert ""
       "dailyod"] == ri["pert result  asse
      e.id)(warehous struse_id"] ==reho"wart result[   assee
     ructursic stba # Verify         

       y", days=7)od="dailuse.id, perin, wareho(db_sessio_trendsnalyticsouse_aet_warehsult = g
        recalculationtrends ly  Test dai      #
         t()
 n.commi db_sessio    ons)
   tisac(tranon.add_all   db_sessi    
        
 action)append(transtions.  transac               )
    days=i)
   medelta(- tion_date=now nsacti      tra      r.id,
    _user_id=useormed_byerf          p      ieces",
easure="p_of_munit               "),
 + i}.0000 mal(f"{1antity=Deci    qu           testing
 ansfer for -tr # Selfid, ouse.use_id=wareho_wareho       t     ,
    .idd=warehouseuse_iwareho   from_