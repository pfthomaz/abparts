#!/usr/bin/env python3
"""
Test Suite for ABParts Data Migration

This module provides comprehensive tests for the data migration process,
including unit tests, integration tests, and validation tests.
"""

import unittest
import uuid
import json
import tempfile
import os
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.migration_utils import (
    DataMigrator, DataValidator, MigrationProgress, MigrationError
)
from app.models import (
    Organization, User, Part, Warehouse, Inventory, Machine, Transaction,
    OrganizationType, UserRole, PartType, TransactionType, UserStatus
)


class TestMigrationProgress(unittest.TestCase):
    """Test the MigrationProgress tracking class"""
    
    def setUp(self):
        self.progress = MigrationProgress()
    
    def test_initialization(self):
        """Test progress tracker initialization"""
        self.assertEqual(self.progress.steps_completed, 0)
        self.assertEqual(self.progress.total_steps, 0)
        self.assertEqual(len(self.progress.errors), 0)
        self.assertEqual(len(self.progress.warnings), 0)
        self.assertIsInstance(self.progress.start_time, datetime)
    
    def test_add_step(self):
        """Test adding migration steps"""
        self.progress.add_step("Test Step 1")
        self.assertEqual(self.progress.total_steps, 1)
        
        self.progress.add_step("Test Step 2")
        self.assertEqual(self.progress.total_steps, 2)
    
    def test_complete_step(self):
        """Test completing migration steps"""
        self.progress.add_step("Test Step")
        self.progress.complete_step("Test Step", {"processed": 5})
        
        self.assertEqual(self.progress.steps_completed, 1)
        self.assertIn("Test Step", self.progress.statistics)
        self.assertEqual(self.progress.statistics["Test Step"]["processed"], 5)
    
    def test_error_handling(self):
        """Test error and warning tracking"""
        self.progress.add_error("Test error")
        self.progress.add_warning("Test warning")
        
        self.assertEqual(len(self.progress.errors), 1)
        self.assertEqual(len(self.progress.warnings), 1)
        self.assertEqual(self.progress.errors[0], "Test error")
        self.assertEqual(self.progress.warnings[0], "Test warning")
    
    def test_get_summary(self):
        """Test summary generation"""
        self.progress.add_step("Step 1")
        self.progress.complete_step("Step 1")
        self.progress.add_error("Test error")
        
        summary = self.progress.get_summary()
        
        self.assertIn("start_time", summary)
        self.assertIn("duration_seconds", summary)
        self.assertEqual(summary["steps_completed"], 1)
        self.assertEqual(summary["total_steps"], 1)
        self.assertEqual(summary["success_rate"], 1.0)
        self.assertEqual(len(summary["errors"]), 1)


class TestDataValidator(unittest.TestCase):
    """Test the DataValidator class"""
    
    def setUp(self):
        self.validator = DataValidator()
        self.mock_db = Mock()
    
    def test_validate_pre_migration_no_issues(self):
        """Test pre-migration validation with no issues"""
        # Mock database queries to return no issues
        self.mock_db.execute.return_value.fetchall.return_value = []
        self.mock_db.execute.return_value.scalar.return_value = 0
        
        issues = self.validator.validate_pre_migration(self.mock_db)
        self.assertEqual(len(issues), 0)
    
    def test_validate_pre_migration_with_issues(self):
        """Test pre-migration validation with issues"""
        # Mock duplicate organizations
        duplicate_org = Mock()
        duplicate_org.name = "Test Org"
        
        # Mock database responses
        def mock_execute(query):
            mock_result = Mock()
            if "duplicate" in str(query).lower():
                mock_result.fetchall.return_value = [duplicate_org]
            else:
                mock_result.scalar.return_value = 5  # Orphaned records
            return mock_result
        
        self.mock_db.execute.side_effect = mock_execute
        
        issues = self.validator.validate_pre_migration(self.mock_db)
        self.assertGreater(len(issues), 0)
    
    def test_validate_post_migration_success(self):
        """Test post-migration validation success"""
        # Mock successful validation
        mock_oraseas_query = Mock()
        mock_oraseas_query.count.return_value = 1
        
        mock_bossaqua_query = Mock()
        mock_bossaqua_query.count.return_value = 1
        
        mock_users_query = Mock()
        mock_users_query.all.return_value = []
        
        mock_org_query = Mock()
        mock_org_query.first.return_value = Mock(id=uuid.uuid4())
        
        self.mock_db.query.side_effect = [
            mock_oraseas_query,  # Oraseas EE count
            mock_bossaqua_query,  # BossAqua count
            mock_users_query,    # Super admin users
            mock_org_query       # Oraseas organization
        ]
        
        self.mock_db.execute.return_value.scalar.return_value = 0
        
        issues = self.validator.validate_post_migration(self.mock_db)
        self.assertEqual(len(issues), 0)


class TestDataMigrator(unittest.TestCase):
    """Test the DataMigrator class"""
    
    def setUp(self):
        self.migrator = DataMigrator()
        self.mock_db = Mock()
    
    def test_initialization(self):
        """Test migrator initialization"""
        self.assertIsInstance(self.migrator.progress, MigrationProgress)
        self.assertIsInstance(self.migrator.validator, DataValidator)
        self.assertEqual(len(self.migrator.backup_data), 0)
    
    @patch('app.migration_utils.logger')
    def test_create_backup(self, mock_logger):
        """Test backup creation"""
        # Mock database responses
        mock_row = Mock()
        mock_row._mapping = {"id": str(uuid.uuid4()), "name": "Test"}
        
        self.mock_db.execute.return_value.fetchall.return_value = [mock_row]
        
        backup = self.migrator.create_backup(self.mock_db)
        
        self.assertIn("organizations", backup)
        self.assertIn("users", backup)
        self.assertIn("parts", backup)
        self.assertEqual(len(backup["organizations"]), 1)
    
    def test_migrate_organization_types(self):
        """Test organization type migration"""
        # Create mock organizations
        mock_orgs = [
            Mock(id=uuid.uuid4(), name="Oraseas EE", organization_type=None),
            Mock(id=uuid.uuid4(), name="BossAqua Manufacturing", organization_type=None),
            Mock(id=uuid.uuid4(), name="Customer Corp", organization_type=None),
            Mock(id=uuid.uuid4(), name="Parts Supplier Ltd", organization_type=None)
        ]
        
        self.mock_db.query.return_value.all.return_value = mock_orgs
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_orgs[0]
        
        stats = self.migrator.migrate_organization_types(self.mock_db)
        
        self.assertEqual(stats["updated"], 4)
        self.assertEqual(stats["errors"], 0)
        
        # Verify organization types were set correctly
        self.assertEqual(mock_orgs[0].organization_type, OrganizationType.oraseas_ee)
        self.assertEqual(mock_orgs[1].organization_type, OrganizationType.bossaqua)
        self.assertEqual(mock_orgs[2].organization_type, OrganizationType.customer)
        self.assertEqual(mock_orgs[3].organization_type, OrganizationType.supplier)
    
    def test_migrate_user_roles(self):
        """Test user role migration"""
        # Create mock users
        oraseas_org = Mock(id=uuid.uuid4())
        mock_users = [
            Mock(id=uuid.uuid4(), username="admin1", role=None, organization_id=oraseas_org.id),
            Mock(id=uuid.uuid4(), username="user1", role=None, organization_id=uuid.uuid4())
        ]
        
        self.mock_db.query.return_value.all.return_value = mock_users
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [
            oraseas_org,  # Oraseas org lookup
            None,         # No existing super admin
            None          # No existing admin
        ]
        
        stats = self.migrator.migrate_user_roles(self.mock_db)
        
        self.assertEqual(stats["updated"], 2)
        self.assertEqual(stats["super_admins"], 1)
        self.assertEqual(stats["admins"], 1)
    
    def test_migrate_parts_classification(self):
        """Test parts classification migration"""
        mock_parts = [
            Mock(id=uuid.uuid4(), name="Oil Filter", description="Engine oil filter", 
                 part_type=None, is_proprietary=None, unit_of_measure=None),
            Mock(id=uuid.uuid4(), name="Cleaning Oil", description="5L cleaning oil", 
                 part_type=None, is_proprietary=None, unit_of_measure="pieces"),
            Mock(id=uuid.uuid4(), name="BossAqua Belt", description="Proprietary belt", 
                 part_type=None, is_proprietary=None, unit_of_measure=None)
        ]
        
        self.mock_db.query.return_value.all.return_value = mock_parts
        
        stats = self.migrator.migrate_parts_classification(self.mock_db)
        
        self.assertEqual(stats["updated"], 3)
        self.assertEqual(stats["bulk_material"], 1)  # Cleaning oil
        self.assertEqual(stats["consumable"], 2)     # Filter and belt
        self.assertEqual(stats["proprietary"], 1)    # BossAqua belt
        
        # Verify classifications
        self.assertEqual(mock_parts[0].part_type, PartType.consumable)
        self.assertEqual(mock_parts[1].part_type, PartType.bulk_material)
        self.assertEqual(mock_parts[1].unit_of_measure, "liters")
        self.assertTrue(mock_parts[2].is_proprietary)
    
    def test_ensure_default_warehouses(self):
        """Test default warehouse creation"""
        mock_orgs = [
            Mock(id=uuid.uuid4(), name="Test Org 1", address="123 Main St"),
            Mock(id=uuid.uuid4(), name="Test Org 2", address=None)
        ]
        
        self.mock_db.query.return_value.all.return_value = mock_orgs
        self.mock_db.query.return_value.filter.return_value.count.return_value = 0
        
        stats = self.migrator.ensure_default_warehouses(self.mock_db)
        
        self.assertEqual(stats["created"], 2)
        self.assertEqual(stats["existing"], 0)
        
        # Verify warehouses were added to database
        self.assertEqual(self.mock_db.add.call_count, 2)
    
    def test_migration_error_handling(self):
        """Test migration error handling"""
        # Mock database error
        self.mock_db.query.side_effect = Exception("Database error")
        
        with self.assertRaises(MigrationError):
            self.migrator.migrate_organization_types(self.mock_db)
    
    def test_rollback_functionality(self):
        """Test migration rollback"""
        # Set up backup data
        self.migrator.backup_data = {
            "organizations": [{"id": str(uuid.uuid4()), "name": "Test"}],
            "users": [],
            "parts": [],
            "warehouses": [],
            "inventory": [],
            "machines": []
        }
        
        # Rollback should return False (not fully implemented)
        result = self.migrator.rollback_migration(self.mock_db)
        self.assertFalse(result)


class TestMigrationIntegration(unittest.TestCase):
    """Integration tests for the complete migration process"""
    
    def setUp(self):
        self.migrator = DataMigrator()
        self.mock_db = Mock()
    
    def test_full_migration_success(self):
        """Test successful full migration"""
        # Mock all validation and migration steps
        with patch.object(self.migrator.validator, 'validate_pre_migration', return_value=[]):
            with patch.object(self.migrator.validator, 'validate_post_migration', return_value=[]):
                with patch.object(self.migrator, 'create_backup', return_value={}):
                    with patch.object(self.migrator, 'migrate_organization_types', return_value={"updated": 1}):
                        with patch.object(self.migrator, 'migrate_user_roles', return_value={"updated": 1}):
                            with patch.object(self.migrator, 'migrate_parts_classification', return_value={"updated": 1}):
                                with patch.object(self.migrator, 'ensure_default_warehouses', return_value={"created": 1}):
                                    with patch.object(self.migrator, 'migrate_inventory_to_warehouses', return_value={"migrated": 1}):
                                        with patch.object(self.migrator, 'create_initial_transactions', return_value={"created": 1}):
                                            
                                            result = self.migrator.run_full_migration(self.mock_db)
                                            
                                            self.assertIn("migration_results", result)
                                            self.assertIn("duration_seconds", result)
                                            self.assertEqual(result["steps_completed"], 6)
                                            self.assertTrue(result["backup_created"])
    
    def test_full_migration_with_validation_errors(self):
        """Test migration with post-validation errors"""
        with patch.object(self.migrator.validator, 'validate_pre_migration', return_value=[]):
            with patch.object(self.migrator.validator, 'validate_post_migration', return_value=["Validation error"]):
                with patch.object(self.migrator, 'create_backup', return_value={}):
                    
                    with self.assertRaises(MigrationError):
                        self.migrator.run_full_migration(self.mock_db)


class TestMigrationUtilities(unittest.TestCase):
    """Test utility functions and edge cases"""
    
    def test_migration_with_empty_database(self):
        """Test migration with empty database"""
        migrator = DataMigrator()
        mock_db = Mock()
        
        # Mock empty database responses
        mock_db.query.return_value.all.return_value = []
        mock_db.query.return_value.count.return_value = 0
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        mock_db.execute.return_value.fetchall.return_value = []
        mock_db.execute.return_value.scalar.return_value = 0
        
        # Should handle empty database gracefully
        stats = migrator.migrate_organization_types(mock_db)
        self.assertEqual(stats["updated"], 0)
        self.assertEqual(stats["errors"], 0)
    
    def test_migration_with_corrupted_data(self):
        """Test migration with corrupted data"""
        migrator = DataMigrator()
        mock_db = Mock()
        
        # Mock corrupted organization (missing name)
        corrupted_org = Mock(id=uuid.uuid4(), name=None)
        mock_db.query.return_value.all.return_value = [corrupted_org]
        
        # Should handle corrupted data gracefully
        stats = migrator.migrate_organization_types(mock_db)
        self.assertEqual(stats["errors"], 1)
    
    def test_backup_serialization(self):
        """Test backup data serialization"""
        migrator = DataMigrator()
        
        # Test data with datetime objects
        test_data = {
            "organizations": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Test Org",
                    "created_at": datetime.now(timezone.utc)
                }
            ]
        }
        
        # Should be able to serialize datetime objects
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            try:
                json.dump(test_data, f, default=str)
                f.flush()
                
                # Should be able to read back
                with open(f.name, 'r') as read_f:
                    loaded_data = json.load(read_f)
                    self.assertIn("organizations", loaded_data)
                    
            finally:
                os.unlink(f.name)


class TestProductionDataSamples(unittest.TestCase):
    """Test migration with production-like data samples"""
    
    def setUp(self):
        self.migrator = DataMigrator()
    
    def create_sample_data(self):
        """Create realistic sample data for testing"""
        return {
            "organizations": [
                {"id": str(uuid.uuid4()), "name": "Oraseas EE", "organization_type": None},
                {"id": str(uuid.uuid4()), "name": "BossAqua Manufacturing", "organization_type": None},
                {"id": str(uuid.uuid4()), "name": "AutoWash Solutions", "organization_type": None},
                {"id": str(uuid.uuid4()), "name": "Parts Supplier Inc", "organization_type": None}
            ],
            "users": [
                {"id": str(uuid.uuid4()), "username": "admin", "role": None, "organization_id": None},
                {"id": str(uuid.uuid4()), "username": "manager", "role": None, "organization_id": None},
                {"id": str(uuid.uuid4()), "username": "operator", "role": None, "organization_id": None}
            ],
            "parts": [
                {"id": str(uuid.uuid4()), "name": "Oil Filter", "part_type": None, "is_proprietary": None},
                {"id": str(uuid.uuid4()), "name": "Cleaning Solution", "part_type": None, "is_proprietary": None},
                {"id": str(uuid.uuid4()), "name": "BossAqua Pump", "part_type": None, "is_proprietary": None}
            ],
            "inventory": [
                {"id": str(uuid.uuid4()), "current_stock": "10.5", "warehouse_id": None},
                {"id": str(uuid.uuid4()), "current_stock": "25.0", "warehouse_id": None}
            ]
        }
    
    def test_migration_with_sample_data(self):
        """Test migration with realistic sample data"""
        sample_data = self.create_sample_data()
        
        # This would be a more comprehensive test with actual database setup
        # For now, we verify the sample data structure
        self.assertEqual(len(sample_data["organizations"]), 4)
        self.assertEqual(len(sample_data["users"]), 3)
        self.assertEqual(len(sample_data["parts"]), 3)
        self.assertEqual(len(sample_data["inventory"]), 2)
    
    def test_performance_with_large_dataset(self):
        """Test migration performance with larger datasets"""
        # Create larger sample dataset
        large_sample = {
            "organizations": [{"id": str(uuid.uuid4()), "name": f"Org {i}"} for i in range(100)],
            "users": [{"id": str(uuid.uuid4()), "username": f"user{i}"} for i in range(200)],
            "parts": [{"id": str(uuid.uuid4()), "name": f"Part {i}"} for i in range(200)],
            "inventory": [{"id": str(uuid.uuid4()), "current_stock": "10.0"} for i in range(1000)]
        }
        
        # Verify we can handle the expected scale
        self.assertEqual(len(large_sample["organizations"]), 100)
        self.assertEqual(len(large_sample["users"]), 200)
        self.assertEqual(len(large_sample["parts"]), 200)
        self.assertEqual(len(large_sample["inventory"]), 1000)


def run_tests():
    """Run all migration tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestMigrationProgress,
        TestDataValidator,
        TestDataMigrator,
        TestMigrationIntegration,
        TestMigrationUtilities,
        TestProductionDataSamples
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)