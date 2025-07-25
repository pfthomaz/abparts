"""
Pytest configuration and fixtures for ABParts integration testing.
"""

import pytest
import asyncio
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Import application components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app as fastapi_app
from app.database import get_db, Base
from app.models import (
    Organization, User, Part, Warehouse, Inventory, Machine, Transaction,
    OrganizationType, UserRole, UserStatus, PartType, TransactionType, MachineStatus
)
# Import all models to ensure they're registered with SQLAlchemy
import app.models
from app.auth import get_password_hash
from app.session_manager import session_manager


# Test database configuration
# Use PostgreSQL for testing to match production environment
# Check if we're running in Docker test environment or local development
import os
if os.getenv("ENVIRONMENT") == "testing":
    # Running in Docker test service
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://abparts_test_user:abparts_test_pass@test_db:5432/abparts_test")
else:
    # Running locally or in development container
    SQLALCHEMY_DATABASE_URL = "postgresql://abparts_user:abparts_pass@db:5432/abparts_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Clean up after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    """Create test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    fastapi_app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(fastapi_app) as test_client:
        yield test_client
    
    fastapi_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_organizations(db_session: Session) -> Dict[str, Organization]:
    """Create test organizations representing the business model."""
    organizations = {}
    
    # Create Oraseas EE (app owner and distributor)
    oraseas = Organization(
        name="Oraseas EE",
        organization_type=OrganizationType.oraseas_ee,
        address="123 Distributor Street, Athens, Greece",
        contact_info="info@oraseas.com"
    )
    db_session.add(oraseas)
    db_session.flush()
    organizations["oraseas"] = oraseas
    
    # Create BossAqua (manufacturer)
    bossaqua = Organization(
        name="BossAqua Manufacturing",
        organization_type=OrganizationType.bossaqua,
        address="456 Manufacturing Ave, Thessaloniki, Greece",
        contact_info="manufacturing@bossaqua.com"
    )
    db_session.add(bossaqua)
    db_session.flush()
    organizations["bossaqua"] = bossaqua
    
    # Create customer organizations
    customer1 = Organization(
        name="AutoWash Solutions Ltd",
        organization_type=OrganizationType.customer,
        address="789 Customer Blvd, Patras, Greece",
        contact_info="orders@autowash.com"
    )
    db_session.add(customer1)
    db_session.flush()
    organizations["customer1"] = customer1
    
    customer2 = Organization(
        name="CleanCar Services",
        organization_type=OrganizationType.customer,
        address="321 Service Road, Larissa, Greece",
        contact_info="parts@cleancar.com"
    )
    db_session.add(customer2)
    db_session.flush()
    organizations["customer2"] = customer2
    
    # Create supplier organization
    supplier = Organization(
        name="Parts Supplier Inc",
        organization_type=OrganizationType.supplier,
        parent_organization_id=oraseas.id,
        address="654 Supplier Lane, Volos, Greece",
        contact_info="sales@partssupplier.com"
    )
    db_session.add(supplier)
    db_session.flush()
    organizations["supplier"] = supplier
    
    db_session.commit()
    return organizations


@pytest.fixture(scope="function")
def test_users(db_session: Session, test_organizations: Dict[str, Organization]) -> Dict[str, User]:
    """Create test users with different roles and organizations."""
    users = {}
    
    # Super admin (Oraseas EE)
    super_admin = User(
        username="super_admin",
        email="admin@oraseas.com",
        password_hash=get_password_hash("superadmin123"),
        name="Super Administrator",
        role=UserRole.super_admin,
        user_status=UserStatus.active,
        organization_id=test_organizations["oraseas"].id,
        is_active=True
    )
    db_session.add(super_admin)
    db_session.flush()
    users["super_admin"] = super_admin
    
    # Oraseas admin
    oraseas_admin = User(
        username="oraseas_admin",
        email="manager@oraseas.com",
        password_hash=get_password_hash("admin123"),
        name="Oraseas Manager",
        role=UserRole.admin,
        user_status=UserStatus.active,
        organization_id=test_organizations["oraseas"].id,
        is_active=True
    )
    db_session.add(oraseas_admin)
    db_session.flush()
    users["oraseas_admin"] = oraseas_admin
    
    # Customer admin
    customer_admin = User(
        username="customer_admin",
        email="admin@autowash.com",
        password_hash=get_password_hash("customer123"),
        name="Customer Administrator",
        role=UserRole.admin,
        user_status=UserStatus.active,
        organization_id=test_organizations["customer1"].id,
        is_active=True
    )
    db_session.add(customer_admin)
    db_session.flush()
    users["customer_admin"] = customer_admin
    
    # Customer user
    customer_user = User(
        username="customer_user",
        email="operator@autowash.com",
        password_hash=get_password_hash("user123"),
        name="Customer Operator",
        role=UserRole.user,
        user_status=UserStatus.active,
        organization_id=test_organizations["customer1"].id,
        is_active=True
    )
    db_session.add(customer_user)
    db_session.flush()
    users["customer_user"] = customer_user
    
    # Second customer admin
    customer2_admin = User(
        username="customer2_admin",
        email="admin@cleancar.com",
        password_hash=get_password_hash("customer2123"),
        name="CleanCar Administrator",
        role=UserRole.admin,
        user_status=UserStatus.active,
        organization_id=test_organizations["customer2"].id,
        is_active=True
    )
    db_session.add(customer2_admin)
    db_session.flush()
    users["customer2_admin"] = customer2_admin
    
    db_session.commit()
    return users


@pytest.fixture(scope="function")
def test_warehouses(db_session: Session, test_organizations: Dict[str, Organization]) -> Dict[str, Warehouse]:
    """Create test warehouses for different organizations."""
    warehouses = {}
    
    # Oraseas EE warehouses
    oraseas_main = Warehouse(
        name="Main Distribution Center",
        organization_id=test_organizations["oraseas"].id,
        location="Athens Distribution Hub",
        description="Primary distribution warehouse"
    )
    db_session.add(oraseas_main)
    db_session.flush()
    warehouses["oraseas_main"] = oraseas_main
    
    oraseas_secondary = Warehouse(
        name="Secondary Warehouse",
        organization_id=test_organizations["oraseas"].id,
        location="Thessaloniki Branch",
        description="Secondary distribution point"
    )
    db_session.add(oraseas_secondary)
    db_session.flush()
    warehouses["oraseas_secondary"] = oraseas_secondary
    
    # Customer warehouses
    customer1_warehouse = Warehouse(
        name="Main Storage",
        organization_id=test_organizations["customer1"].id,
        location="AutoWash Main Facility",
        description="Primary parts storage"
    )
    db_session.add(customer1_warehouse)
    db_session.flush()
    warehouses["customer1_main"] = customer1_warehouse
    
    customer2_warehouse = Warehouse(
        name="Parts Storage",
        organization_id=test_organizations["customer2"].id,
        location="CleanCar Service Center",
        description="Service center parts storage"
    )
    db_session.add(customer2_warehouse)
    db_session.flush()
    warehouses["customer2_main"] = customer2_warehouse
    
    db_session.commit()
    return warehouses


@pytest.fixture(scope="function")
def test_parts(db_session: Session) -> Dict[str, Part]:
    """Create test parts with different types and classifications."""
    parts = {}
    
    # Consumable parts
    oil_filter = Part(
        part_number="OF-001",
        name="Oil Filter",
        description="Standard oil filter for AutoBoss machines",
        part_type=PartType.CONSUMABLE,
        is_proprietary=False,
        unit_of_measure="pieces",
        manufacturer_part_number="MF-OF-001"
    )
    db_session.add(oil_filter)
    db_session.flush()
    parts["oil_filter"] = oil_filter
    
    # Bulk material parts
    cleaning_oil = Part(
        part_number="CO-001",
        name="Cleaning Oil",
        description="Specialized cleaning oil for AutoBoss systems",
        part_type=PartType.BULK_MATERIAL,
        is_proprietary=False,
        unit_of_measure="liters",
        manufacturer_part_number="MF-CO-001"
    )
    db_session.add(cleaning_oil)
    db_session.flush()
    parts["cleaning_oil"] = cleaning_oil
    
    # Proprietary parts
    bossaqua_pump = Part(
        part_number="BP-001",
        name="BossAqua Pump Assembly",
        description="Proprietary pump assembly for AutoBoss V4.0",
        part_type=PartType.CONSUMABLE,
        is_proprietary=True,
        unit_of_measure="pieces",
        manufacturer_part_number="BA-PUMP-V4"
    )
    db_session.add(bossaqua_pump)
    db_session.flush()
    parts["bossaqua_pump"] = bossaqua_pump
    
    # Additional consumable
    drive_belt = Part(
        part_number="DB-001",
        name="Drive Belt",
        description="Drive belt for AutoBoss machines",
        part_type=PartType.CONSUMABLE,
        is_proprietary=False,
        unit_of_measure="pieces",
        manufacturer_part_number="MF-DB-001"
    )
    db_session.add(drive_belt)
    db_session.flush()
    parts["drive_belt"] = drive_belt
    
    db_session.commit()
    return parts


@pytest.fixture(scope="function")
def test_machines(db_session: Session, test_organizations: Dict[str, Organization]) -> Dict[str, Machine]:
    """Create test machines for customer organizations."""
    machines = {}
    
    # Customer 1 machines
    machine1 = Machine(
        name="AutoBoss Unit 1",
        model_type="V4.0",
        serial_number="AB-V4-001",
        customer_organization_id=test_organizations["customer1"].id,
        purchase_date=datetime.utcnow() - timedelta(days=365),
        warranty_expiry_date=datetime.utcnow() + timedelta(days=365),
        status=MachineStatus.active,
        location="Bay 1"
    )
    db_session.add(machine1)
    db_session.flush()
    machines["customer1_machine1"] = machine1
    
    machine2 = Machine(
        name="AutoBoss Unit 2",
        model_type="V3.1B",
        serial_number="AB-V31B-001",
        customer_organization_id=test_organizations["customer1"].id,
        purchase_date=datetime.utcnow() - timedelta(days=730),
        warranty_expiry_date=datetime.utcnow() - timedelta(days=365),
        status=MachineStatus.active,
        location="Bay 2"
    )
    db_session.add(machine2)
    db_session.flush()
    machines["customer1_machine2"] = machine2
    
    # Customer 2 machine
    machine3 = Machine(
        name="AutoBoss Service Unit",
        model_type="V4.0",
        serial_number="AB-V4-002",
        customer_organization_id=test_organizations["customer2"].id,
        purchase_date=datetime.utcnow() - timedelta(days=180),
        warranty_expiry_date=datetime.utcnow() + timedelta(days=545),
        status=MachineStatus.active,
        location="Service Bay"
    )
    db_session.add(machine3)
    db_session.flush()
    machines["customer2_machine1"] = machine3
    
    db_session.commit()
    return machines


@pytest.fixture(scope="function")
def test_inventory(
    db_session: Session, 
    test_warehouses: Dict[str, Warehouse], 
    test_parts: Dict[str, Part]
) -> Dict[str, Inventory]:
    """Create test inventory records."""
    inventory = {}
    
    # Oraseas main warehouse inventory
    oraseas_oil_filter = Inventory(
        warehouse_id=test_warehouses["oraseas_main"].id,
        part_id=test_parts["oil_filter"].id,
        current_stock=Decimal("100.000"),
        minimum_stock_recommendation=Decimal("20.000"),
        unit_of_measure="pieces"
    )
    db_session.add(oraseas_oil_filter)
    db_session.flush()
    inventory["oraseas_oil_filter"] = oraseas_oil_filter
    
    oraseas_cleaning_oil = Inventory(
        warehouse_id=test_warehouses["oraseas_main"].id,
        part_id=test_parts["cleaning_oil"].id,
        current_stock=Decimal("500.000"),
        minimum_stock_recommendation=Decimal("100.000"),
        unit_of_measure="liters"
    )
    db_session.add(oraseas_cleaning_oil)
    db_session.flush()
    inventory["oraseas_cleaning_oil"] = oraseas_cleaning_oil
    
    # Customer warehouse inventory
    customer1_oil_filter = Inventory(
        warehouse_id=test_warehouses["customer1_main"].id,
        part_id=test_parts["oil_filter"].id,
        current_stock=Decimal("10.000"),
        minimum_stock_recommendation=Decimal("5.000"),
        unit_of_measure="pieces"
    )
    db_session.add(customer1_oil_filter)
    db_session.flush()
    inventory["customer1_oil_filter"] = customer1_oil_filter
    
    customer1_cleaning_oil = Inventory(
        warehouse_id=test_warehouses["customer1_main"].id,
        part_id=test_parts["cleaning_oil"].id,
        current_stock=Decimal("25.500"),
        minimum_stock_recommendation=Decimal("10.000"),
        unit_of_measure="liters"
    )
    db_session.add(customer1_cleaning_oil)
    db_session.flush()
    inventory["customer1_cleaning_oil"] = customer1_cleaning_oil
    
    db_session.commit()
    return inventory


@pytest.fixture(scope="function")
def auth_headers(test_users: Dict[str, User], db_session: Session) -> Dict[str, Dict[str, str]]:
    """Create authentication headers for different user types."""
    headers = {}
    
    for user_type, user in test_users.items():
        # Create a session token instead of JWT token
        session_token = session_manager.create_session(
            user=user,
            ip_address="127.0.0.1",
            user_agent="pytest-test-client",
            db=db_session
        )
        headers[user_type] = {"Authorization": f"Bearer {session_token}"}
    
    return headers


@pytest.fixture(scope="function")
def performance_test_data(db_session: Session) -> Dict[str, Any]:
    """Create larger dataset for performance testing."""
    # This fixture would create larger datasets for performance testing
    # Implementation would be similar to above but with more records
    return {
        "organizations_count": 100,
        "users_count": 200,
        "parts_count": 200,
        "machines_count": 150,
        "warehouses_count": 150,
        "transactions_count": 7500
    }


# Utility functions for tests
def create_test_transaction(
    db_session: Session,
    transaction_type: TransactionType,
    part_id: uuid.UUID,
    quantity: Decimal,
    performed_by_user_id: uuid.UUID,
    from_warehouse_id: uuid.UUID = None,
    to_warehouse_id: uuid.UUID = None,
    machine_id: uuid.UUID = None
) -> Transaction:
    """Helper function to create test transactions."""
    transaction = Transaction(
        transaction_type=transaction_type,
        part_id=part_id,
        from_warehouse_id=from_warehouse_id,
        to_warehouse_id=to_warehouse_id,
        machine_id=machine_id,
        quantity=quantity,
        unit_of_measure="pieces" if transaction_type != TransactionType.CONSUMPTION else "pieces",
        performed_by_user_id=performed_by_user_id,
        transaction_date=datetime.utcnow()
    )
    db_session.add(transaction)
    db_session.flush()
    return transaction


# Event loop fixture for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()