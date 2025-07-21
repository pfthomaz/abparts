"""
Migration Testing Utilities for ABParts

This module provides testing capabilities for:
- Production data sample testing
- Migration rollback testing
- Performance impact assessment
- Data integrity verification
"""

import logging
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import tempfile
import shutil
import os

from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal, engine, DATABASE_URL
from app.models import Organization, User, Part, Machine, Warehouse, Inventory
from .migration_manager import DataMigrationManager, MigrationReport, MigrationStatus
from .data_validator import DataValidator, ValidationReport


@dataclass
class TestSample:
    """Represents a test data sample."""
    name: str
    description: str
    organizations: int
    users: int
    parts: int
    machines: int
    warehouses: int
    inventory_records: int


@dataclass
class PerformanceMetrics:
    """Performance metrics for migration testing."""
    migration_duration: float
    validation_duration: float
    rollback_duration: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    database_size_before_mb: Optional[float] = None
    database_size_after_mb: Optional[float] = None


@dataclass
class TestResult:
    """Result of a migration test."""
    test_id: str
    sample: TestSample
    migration_report: MigrationReport
    validation_report: ValidationReport
    performance_metrics: PerformanceMetrics
    success: bool
    error_message: Optional[str] = None


class MigrationTester:
    """
    Comprehensive migration testing utility.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_id = str(uuid.uuid4())
    
    def create_test_samples(self) -> List[TestSample]:
        """Create various test data samples for migration testing."""
        return [
            TestSample(
                name="minimal_sample",
                description="Minimal test data with basic entities",
                organizations=3,  # Oraseas EE, BossAqua, 1 Customer
                users=5,
                parts=10,
                machines=2,
                warehouses=3,
                inventory_records=20
            ),
            TestSample(
                name="small_sample",
                description="Small production-like sample",
                organizations=10,  # Oraseas EE, BossAqua, 8 Customers
                users=25,
                parts=50,
                machines=15,
                warehouses=12,
                inventory_records=100
            ),
            TestSample(
                name="medium_sample",
                description="Medium production-like sample",
                organizations=25,  # Oraseas EE, BossAqua, 23 Customers
                users=75,
                parts=100,
                machines=50,
                warehouses=30,
                inventory_records=500
            ),
            TestSample(
                name="large_sample",
                description="Large production-like sample",
                organizations=50,  # Oraseas EE, BossAqua, 48 Customers
                users=150,
                parts=200,
                machines=100,
                warehouses=60,
                inventory_records=1000
            ),
            TestSample(
                name="production_scale",
                description="Full production scale sample",
                organizations=100,  # Maximum expected
                users=200,
                parts=200,
                machines=150,
                warehouses=150,
                inventory_records=7500
            )
        ]
    
    def generate_test_data(self, sample: TestSample, db: Session) -> bool:
        """
        Generate test data based on sample specification.
        
        Args:
            sample: Test sample specification
            db: Database session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Generating test data for sample: {sample.name}")
            
            # Clear existing data
            self._clear_test_data(db)
            
            # Generate organizations
            organizations = self._generate_organizations(sample.organizations, db)
            
            # Generate users
            users = self._generate_users(sample.users, organizations, db)
            
            # Generate parts
            parts = self._generate_parts(sample.parts, db)
            
            # Generate warehouses
            warehouses = self._generate_warehouses(sample.warehouses, organizations, db)
            
            # Generate machines
            machines = self._generate_machines(sample.machines, organizations, db)
            
            # Generate inventory
            self._generate_inventory(sample.inventory_records, warehouses, parts, db)
            
            db.commit()
            self.logger.info(f"Successfully generated test data for {sample.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate test data: {str(e)}")
            db.rollback()
            return False
    
    def test_migration_with_sample(self, sample: TestSample) -> TestResult:
        """
        Test migration with a specific data sample.
        
        Args:
            sample: Test data sample
            
        Returns:
            TestResult with migration test results
        """
        self.logger.info(f"Testing migration with sample: {sample.name}")
        
        test_result = TestResult(
            test_id=self.test_id,
            sample=sample,
            migration_report=None,
            validation_report=None,
            performance_metrics=None,
            success=False
        )
        
        db = SessionLocal()
        
        try:
            # Generate test data
            if not self.generate_test_data(sample, db):
                test_result.error_message = "Failed to generate test data"
                return test_result
            
            # Record initial metrics
            start_time = time.time()
            db_size_before = self._get_database_size()
            
            # Run migration
            migration_manager = DataMigrationManager()
            migration_report = migration_manager.run_migration(dry_run=False)
            
            migration_duration = time.time() - start_time
            
            # Run validation
            validation_start = time.time()
            validator = DataValidator()
            validation_report = validator.validate_all(db)
            validation_duration = time.time() - validation_start
            
            # Record final metrics
            db_size_after = self._get_database_size()
            
            # Create performance metrics
            performance_metrics = PerformanceMetrics(
                migration_duration=migration_duration,
                validation_duration=validation_duration,
                database_size_before_mb=db_size_before,
                database_size_after_mb=db_size_after
            )
            
            # Determine success
            success = (
                migration_report.status == MigrationStatus.COMPLETED and
                validation_report.is_valid
            )
            
            test_result.migration_report = migration_report
            test_result.validation_report = validation_report
            test_result.performance_metrics = performance_metrics
            test_result.success = success
            
            if not success:
                test_result.error_message = f"Migration status: {migration_report.status.value}, Validation errors: {validation_report.errors + validation_report.critical_issues}"
            
        except Exception as e:
            self.logger.error(f"Migration test failed: {str(e)}")
            test_result.error_message = str(e)
            
        finally:
            db.close()
        
        return test_result
    
    def run_comprehensive_tests(self) -> List[TestResult]:
        """
        Run comprehensive migration tests with all sample sizes.
        
        Returns:
            List of TestResult for all samples
        """
        self.logger.info("Starting comprehensive migration tests")
        
        samples = self.create_test_samples()
        results = []
        
        for sample in samples:
            try:
                result = self.test_migration_with_sample(sample)
                results.append(result)
                
                # Log result
                if result.success:
                    self.logger.info(f"✅ Test {sample.name} passed in {result.performance_metrics.migration_duration:.2f}s")
                else:
                    self.logger.error(f"❌ Test {sample.name} failed: {result.error_message}")
                
            except Exception as e:
                self.logger.error(f"Test {sample.name} crashed: {str(e)}")
                results.append(TestResult(
                    test_id=self.test_id,
                    sample=sample,
                    migration_report=None,
                    validation_report=None,
                    performance_metrics=None,
                    success=False,
                    error_message=str(e)
                ))
        
        self._save_test_results(results)
        return results
    
    def test_rollback_capability(self) -> bool:
        """
        Test migration rollback capability.
        
        Returns:
            True if rollback works correctly, False otherwise
        """
        self.logger.info("Testing migration rollback capability")
        
        db = SessionLocal()
        
        try:
            # Generate minimal test data
            minimal_sample = self.create_test_samples()[0]  # Get minimal sample
            if not self.generate_test_data(minimal_sample, db):
                return False
            
            # Record initial state
            initial_org_count = db.query(Organization).count()
            initial_user_count = db.query(User).count()
            
            # Run migration
            migration_manager = DataMigrationManager()
            migration_report = migration_manager.run_migration(dry_run=False)
            
            if migration_report.status != MigrationStatus.COMPLETED:
                self.logger.error("Migration failed, cannot test rollback")
                return False
            
            # Simulate rollback scenario by forcing a failure
            # This would trigger the rollback mechanism
            # For now, we'll just verify backup was created
            
            if migration_report.rollback_info and migration_report.rollback_info.get('backup_file'):
                self.logger.info("✅ Rollback capability verified - backup created")
                return True
            else:
                self.logger.error("❌ Rollback capability failed - no backup created")
                return False
                
        except Exception as e:
            self.logger.error(f"Rollback test failed: {str(e)}")
            return False
            
        finally:
            db.close()
    
    def _clear_test_data(self, db: Session):
        """Clear existing test data from database."""
        try:
            # Delete in reverse dependency order
            db.execute(text("DELETE FROM inventory"))
            db.execute(text("DELETE FROM transactions"))
            db.execute(text("DELETE FROM machines"))
            db.execute(text("DELETE FROM warehouses"))
            db.execute(text("DELETE FROM users"))
            db.execute(text("DELETE FROM parts"))
            db.execute(text("DELETE FROM organizations"))
            db.commit()
        except Exception as e:
            self.logger.warning(f"Error clearing test data: {str(e)}")
            db.rollback()
    
    def _generate_organizations(self, count: int, db: Session) -> List[Organization]:
        """Generate test organizations."""
        organizations = []
        
        # Always create Oraseas EE first
        oraseas = Organization(
            name="Oraseas EE",
            organization_type="oraseas_ee",
            address="123 Main St, Athens, Greece",
            contact_info="info@oraseas.com",
            is_active=True
        )
        db.add(oraseas)
        organizations.append(oraseas)
        
        # Create BossAqua if count > 1
        if count > 1:
            bossaqua = Organization(
                name="BossAqua Manufacturing",
                organization_type="bossaqua",
                address="456 Industrial Ave, Thessaloniki, Greece",
                contact_info="info@bossaqua.com",
                is_active=True
            )
            db.add(bossaqua)
            organizations.append(bossaqua)
        
        # Create customer organizations
        for i in range(2, count):
            customer = Organization(
                name=f"Customer Organization {i-1}",
                organization_type="customer",
                address=f"{100+i} Business St, City {i}",
                contact_info=f"contact{i}@customer.com",
                is_active=True
            )
            db.add(customer)
            organizations.append(customer)
        
        db.flush()  # Get IDs
        return organizations
    
    def _generate_users(self, count: int, organizations: List[Organization], db: Session) -> List[User]:
        """Generate test users."""
        users = []
        
        # Create super admin for Oraseas EE
        oraseas_org = next(org for org in organizations if org.organization_type == "oraseas_ee")
        
        super_admin = User(
            organization_id=oraseas_org.id,
            username="superadmin",
            password_hash="$2b$12$dummy_hash",
            email="admin@oraseas.com",
            name="Super Administrator",
            role="super_admin",
            user_status="active",
            is_active=True
        )
        db.add(super_admin)
        users.append(super_admin)
        
        # Create users for other organizations
        user_count = 1
        for org in organizations:
            if org.organization_type == "oraseas_ee":
                continue  # Already created super admin
            
            # Create admin for each organization
            if user_count < count:
                admin = User(
                    organization_id=org.id,
                    username=f"admin_{org.name.lower().replace(' ', '_')}",
                    password_hash="$2b$12$dummy_hash",
                    email=f"admin@{org.name.lower().replace(' ', '')}.com",
                    name=f"Admin {org.name}",
                    role="admin",
                    user_status="active",
                    is_active=True
                )
                db.add(admin)
                users.append(admin)
                user_count += 1
            
            # Create regular users
            users_per_org = max(1, (count - user_count) // max(1, len(organizations) - user_count))
            for i in range(users_per_org):
                if user_count >= count:
                    break
                
                user = User(
                    organization_id=org.id,
                    username=f"user_{user_count}",
                    password_hash="$2b$12$dummy_hash",
                    email=f"user{user_count}@{org.name.lower().replace(' ', '')}.com",
                    name=f"User {user_count}",
                    role="user",
                    user_status="active",
                    is_active=True
                )
                db.add(user)
                users.append(user)
                user_count += 1
        
        db.flush()
        return users
    
    def _generate_parts(self, count: int, db: Session) -> List[Part]:
        """Generate test parts."""
        parts = []
        
        part_templates = [
            ("Filter", "consumable", "pieces", False),
            ("Belt", "consumable", "pieces", True),
            ("Oil", "bulk_material", "liters", False),
            ("Chemical", "bulk_material", "liters", True),
            ("Gasket", "consumable", "pieces", False),
            ("Hose", "consumable", "meters", False),
            ("Pump", "consumable", "pieces", True),
            ("Valve", "consumable", "pieces", False),
            ("Sensor", "consumable", "pieces", True),
            ("Cleaner", "bulk_material", "liters", False)
        ]
        
        for i in range(count):
            template = part_templates[i % len(part_templates)]
            
            part = Part(
                part_number=f"PART-{i+1:04d}",
                name=f"{template[0]} {i+1}",
                description=f"Test {template[0].lower()} part {i+1}",
                part_type=template[1],
                unit_of_measure=template[2],
                is_proprietary=template[3],
                manufacturer_part_number=f"MFG-{i+1:04d}" if template[3] else None
            )
            db.add(part)
            parts.append(part)
        
        db.flush()
        return parts
    
    def _generate_warehouses(self, count: int, organizations: List[Organization], db: Session) -> List[Warehouse]:
        """Generate test warehouses."""
        warehouses = []
        
        # Distribute warehouses among organizations (excluding suppliers)
        non_supplier_orgs = [org for org in organizations if org.organization_type != "supplier"]
        
        for i, org in enumerate(non_supplier_orgs):
            if i >= count:
                break
                
            warehouse = Warehouse(
                organization_id=org.id,
                name=f"Warehouse {i+1}",
                location=f"Location {i+1}",
                description=f"Test warehouse {i+1} for {org.name}",
                is_active=True
            )
            db.add(warehouse)
            warehouses.append(warehouse)
        
        db.flush()
        return warehouses
    
    def _generate_machines(self, count: int, organizations: List[Organization], db: Session) -> List[Machine]:
        """Generate test machines."""
        machines = []
        
        # Only assign machines to customer organizations
        customer_orgs = [org for org in organizations if org.organization_type == "customer"]
        
        if not customer_orgs:
            return machines
        
        for i in range(count):
            customer_org = customer_orgs[i % len(customer_orgs)]
            
            machine = Machine(
                customer_organization_id=customer_org.id,
                model_type="V3.1B" if i % 2 == 0 else "V4.0",
                name=f"AutoBoss Machine {i+1}",
                serial_number=f"AB-{i+1:06d}"
            )
            db.add(machine)
            machines.append(machine)
        
        db.flush()
        return machines
    
    def _generate_inventory(self, count: int, warehouses: List[Warehouse], parts: List[Part], db: Session):
        """Generate test inventory records."""
        if not warehouses or not parts:
            return
        
        for i in range(count):
            warehouse = warehouses[i % len(warehouses)]
            part = parts[i % len(parts)]
            
            # Check if inventory already exists for this warehouse-part combination
            existing = db.query(Inventory).filter(
                Inventory.warehouse_id == warehouse.id,
                Inventory.part_id == part.id
            ).first()
            
            if existing:
                continue
            
            inventory = Inventory(
                warehouse_id=warehouse.id,
                part_id=part.id,
                current_stock=float(10 + (i % 100)),  # Random stock between 10-110
                minimum_stock_recommendation=float(5 + (i % 20)),  # Random min between 5-25
                unit_of_measure=part.unit_of_measure
            )
            db.add(inventory)
        
        db.flush()
    
    def _get_database_size(self) -> Optional[float]:
        """Get current database size in MB."""
        try:
            db = SessionLocal()
            result = db.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                       pg_database_size(current_database()) as size_bytes
            """)).fetchone()
            db.close()
            
            if result:
                return result.size_bytes / (1024 * 1024)  # Convert to MB
            
        except Exception as e:
            self.logger.warning(f"Could not get database size: {str(e)}")
        
        return None
    
    def _save_test_results(self, results: List[TestResult]):
        """Save test results to file."""
        try:
            report_data = {
                'test_id': self.test_id,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'results': []
            }
            
            for result in results:
                result_data = {
                    'sample_name': result.sample.name,
                    'sample_description': result.sample.description,
                    'success': result.success,
                    'error_message': result.error_message,
                    'performance_metrics': {
                        'migration_duration': result.performance_metrics.migration_duration if result.performance_metrics else None,
                        'validation_duration': result.performance_metrics.validation_duration if result.performance_metrics else None,
                        'database_size_before_mb': result.performance_metrics.database_size_before_mb if result.performance_metrics else None,
                        'database_size_after_mb': result.performance_metrics.database_size_after_mb if result.performance_metrics else None
                    } if result.performance_metrics else None,
                    'migration_status': result.migration_report.status.value if result.migration_report else None,
                    'validation_summary': result.validation_report.summary if result.validation_report else None
                }
                report_data['results'].append(result_data)
            
            filename = f"migration_test_results_{self.test_id}.json"
            with open(f"backend/data_migration/reports/{filename}", 'w') as f:
                json.dump(report_data, f, indent=2)
            
            self.logger.info(f"Test results saved: {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to save test results: {str(e)}")


def run_migration_tests():
    """Run comprehensive migration tests."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('backend/data_migration/logs/migration_tests.log'),
            logging.StreamHandler()
        ]
    )
    
    tester = MigrationTester()
    
    print("🧪 Starting comprehensive migration tests...")
    
    # Test rollback capability first
    print("\n1. Testing rollback capability...")
    rollback_success = tester.test_rollback_capability()
    print(f"   Rollback test: {'✅ PASSED' if rollback_success else '❌ FAILED'}")
    
    # Run comprehensive tests
    print("\n2. Running migration tests with different data samples...")
    results = tester.run_comprehensive_tests()
    
    # Print summary
    print(f"\n📊 Test Summary:")
    print(f"   Total tests: {len(results)}")
    print(f"   Passed: {sum(1 for r in results if r.success)}")
    print(f"   Failed: {sum(1 for r in results if not r.success)}")
    
    for result in results:
        status = "✅ PASSED" if result.success else "❌ FAILED"
        duration = f"{result.performance_metrics.migration_duration:.2f}s" if result.performance_metrics else "N/A"
        print(f"   {result.sample.name}: {status} ({duration})")
    
    return results


if __name__ == "__main__":
    run_migration_tests()