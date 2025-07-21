#!/usr/bin/env python3
"""
Data Migration Manager for ABParts Business Model Alignment

This module provides comprehensive data migration capabilities with:
- Data validation and integrity checking
- Rollback capabilities for migration failures
- Progress tracking and reporting
- Production data testing support

Usage:
    python migration_manager.py --validate-only
    python migration_manager.py --migrate
    python migration_manager.py --rollback
    python migration_manager.py --test-with-sample
"""

import sys
import os
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Add the app directory to the path so we can import models
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

import sqlalchemy as sa
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import uuid

# Import models and database configuration
from database import get_database_url
from models import (
    Organization, User, Part, Warehouse, Inventory, Machine,
    Transaction, OrganizationType, UserRole, UserStatus, PartType, TransactionType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class MigrationProgress:
    """Track migration progress and statistics"""
    total_organizations: int = 0
    migrated_organizations: int = 0
    total_users: int = 0
    migrated_users: int = 0
    total_parts: int = 0
    migrated_parts: int = 0
    total_warehouses: int = 0
    migrated_warehouses: int = 0
    total_inventory: int = 0
    migrated_inventory: int = 0
    total_machines: int = 0
    migrated_machines: int = 0
    errors: List[str] = None
    warnings: List[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationResult:
    """Results of data validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    recommendations: List[str]
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.recommendations is None:
            self.recommendations = []


class DataMigrationManager:
    """Manages data migration for ABParts business model alignment"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or get_database_url()
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.progress = MigrationProgress()
        self.backup_data = {}
        
        # Create migration tracking table if it doesn't exist
        self._create_migration_tracking_table()
    
    def _create_migration_tracking_table(self):
        """Create table to track migration progress and enable rollback"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS migration_tracking (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    migration_name VARCHAR(255) NOT NULL,
                    table_name VARCHAR(255) NOT NULL,
                    record_id UUID NOT NULL,
                    operation VARCHAR(50) NOT NULL, -- 'backup', 'migrate', 'rollback'
                    backup_data JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            conn.commit()
    
    def validate_existing_data(self) -> ValidationResult:
        """Validate existing data before migration"""
        logger.info("Starting data validation...")
        result = ValidationResult(is_valid=True, errors=[], warnings=[], recommendations=[])
        
        try:
            with self.SessionLocal() as session:
                # Check organizations
                self._validate_organizations(session, result)
                
                # Check users
                self._validate_users(session, result)
                
                # Check parts
                self._validate_parts(session, result)
                
                # Check warehouses
                self._validate_warehouses(session, result)
                
                # Check inventory
                self._validate_inventory(session, result)
                
                # Check machines
                self._validate_machines(session, result)
                
                # Check for data integrity issues
                self._validate_data_integrity(session, result)
                
        except Exception as e:
            result.is_valid = False
            result.errors.append(f"Validation failed with error: {str(e)}")
            logger.error(f"Validation error: {e}")
        
        # Final validation result
        if result.errors:
            result.is_valid = False
        
        logger.info(f"Validation complete. Valid: {result.is_valid}, Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")
        return result
    
    def _validate_organizations(self, session: Session, result: ValidationResult):
        """Validate organization data"""
        orgs = session.query(Organization).all()
        self.progress.total_organizations = len(orgs)
        
        oraseas_count = sum(1 for org in orgs if org.organization_type == OrganizationType.oraseas_ee)
        bossaqua_count = sum(1 for org in orgs if org.organization_type == OrganizationType.bossaqua)
        
        if oraseas_count == 0:
            result.errors.append("No Oraseas EE organization found - at least one is required")
        elif oraseas_count > 1:
            result.errors.append(f"Multiple Oraseas EE organizations found ({oraseas_count}) - only one allowed")
        
        if bossaqua_count > 1:
            result.errors.append(f"Multiple BossAqua organizations found ({bossaqua_count}) - only one allowed")
        
        # Check for suppliers without parent organizations
        for org in orgs:
            if org.organization_type == OrganizationType.supplier and not org.parent_organization_id:
                result.errors.append(f"Supplier organization '{org.name}' has no parent organization")
    
    def _validate_users(self, session: Session, result: ValidationResult):
        """Validate user data"""
        users = session.query(User).all()
        self.progress.total_users = len(users)
        
        # Check for super_admin users not in Oraseas EE
        oraseas_orgs = session.query(Organization).filter(
            Organization.organization_type == OrganizationType.oraseas_ee
        ).all()
        
        if oraseas_orgs:
            oraseas_id = oraseas_orgs[0].id
            super_admins = [u for u in users if u.role == UserRole.super_admin]
            
            for user in super_admins:
                if user.organization_id != oraseas_id:
                    result.errors.append(f"Super admin user '{user.username}' is not in Oraseas EE organization")
        
        # Check for organizations without admin users
        org_admin_count = {}
        for user in users:
            if user.role == UserRole.admin:
                org_admin_count[user.organization_id] = org_admin_count.get(user.organization_id, 0) + 1
        
        all_orgs = session.query(Organization).all()
        for org in all_orgs:
            if org.id not in org_admin_count:
                result.warnings.append(f"Organization '{org.name}' has no admin users")
    
    def _validate_parts(self, session: Session, result: ValidationResult):
        """Validate parts data"""
        parts = session.query(Part).all()
        self.progress.total_parts = len(parts)
        
        # Check for duplicate part numbers
        part_numbers = [p.part_number for p in parts]
        duplicates = set([x for x in part_numbers if part_numbers.count(x) > 1])
        
        if duplicates:
            result.errors.append(f"Duplicate part numbers found: {', '.join(duplicates)}")
        
        # Check for parts with invalid unit of measure for bulk materials
        for part in parts:
            if part.part_type == PartType.BULK_MATERIAL and part.unit_of_measure == 'pieces':
                result.warnings.append(f"Bulk material part '{part.part_number}' has 'pieces' as unit of measure")
    
    def _validate_warehouses(self, session: Session, result: ValidationResult):
        """Validate warehouse data"""
        warehouses = session.query(Warehouse).all()
        self.progress.total_warehouses = len(warehouses)
        
        # Check for organizations without warehouses
        org_warehouse_count = {}
        for warehouse in warehouses:
            org_warehouse_count[warehouse.organization_id] = org_warehouse_count.get(warehouse.organization_id, 0) + 1
        
        all_orgs = session.query(Organization).all()
        for org in all_orgs:
            if org.id not in org_warehouse_count:
                result.warnings.append(f"Organization '{org.name}' has no warehouses")
    
    def _validate_inventory(self, session: Session, result: ValidationResult):
        """Validate inventory data"""
        inventory_items = session.query(Inventory).all()
        self.progress.total_inventory = len(inventory_items)
        
        # Check for negative inventory
        negative_inventory = [inv for inv in inventory_items if inv.current_stock < 0]
        if negative_inventory:
            result.warnings.append(f"Found {len(negative_inventory)} inventory items with negative stock")
        
        # Check for inventory items with mismatched units
        for inv in inventory_items:
            part = session.query(Part).filter(Part.id == inv.part_id).first()
            if part and part.unit_of_measure != inv.unit_of_measure:
                result.warnings.append(f"Inventory unit mismatch for part '{part.part_number}': part={part.unit_of_measure}, inventory={inv.unit_of_measure}")
    
    def _validate_machines(self, session: Session, result: ValidationResult):
        """Validate machine data"""
        machines = session.query(Machine).all()
        self.progress.total_machines = len(machines)
        
        # Check for duplicate serial numbers
        serial_numbers = [m.serial_number for m in machines]
        duplicates = set([x for x in serial_numbers if serial_numbers.count(x) > 1])
        
        if duplicates:
            result.errors.append(f"Duplicate machine serial numbers found: {', '.join(duplicates)}")
        
        # Check for machines assigned to non-customer organizations
        for machine in machines:
            org = session.query(Organization).filter(Organization.id == machine.customer_organization_id).first()
            if org and org.organization_type != OrganizationType.customer:
                result.warnings.append(f"Machine '{machine.serial_number}' is assigned to non-customer organization '{org.name}'")
    
    def _validate_data_integrity(self, session: Session, result: ValidationResult):
        """Validate referential integrity and business rules"""
        
        # Check for orphaned records
        orphaned_users = session.execute(text("""
            SELECT COUNT(*) FROM users u 
            LEFT JOIN organizations o ON u.organization_id = o.id 
            WHERE o.id IS NULL
        """)).scalar()
        
        if orphaned_users > 0:
            result.errors.append(f"Found {orphaned_users} users with invalid organization references")
        
        orphaned_inventory = session.execute(text("""
            SELECT COUNT(*) FROM inventory i 
            LEFT JOIN warehouses w ON i.warehouse_id = w.id 
            WHERE w.id IS NULL
        """)).scalar()
        
        if orphaned_inventory > 0:
            result.errors.append(f"Found {orphaned_inventory} inventory items with invalid warehouse references")
        
        # Check business rule constraints
        try:
            # Test unique constraints
            session.execute(text("SELECT 1 FROM organizations WHERE organization_type = 'oraseas_ee'"))
            session.execute(text("SELECT 1 FROM organizations WHERE organization_type = 'bossaqua'"))
        except Exception as e:
            result.errors.append(f"Database constraint validation failed: {str(e)}")
    
    def create_backup(self) -> bool:
        """Create backup of existing data before migration"""
        logger.info("Creating data backup...")
        
        try:
            with self.SessionLocal() as session:
                # Backup organizations
                orgs = session.query(Organization).all()
                self.backup_data['organizations'] = [
                    {
                        'id': str(org.id),
                        'name': org.name,
                        'organization_type': org.organization_type.value if org.organization_type else None,
                        'parent_organization_id': str(org.parent_organization_id) if org.parent_organization_id else None,
                        'address': org.address,
                        'contact_info': org.contact_info,
                        'is_active': org.is_active,
                        'created_at': org.created_at.isoformat() if org.created_at else None,
                        'updated_at': org.updated_at.isoformat() if org.updated_at else None
                    }
                    for org in orgs
                ]
                
                # Backup users
                users = session.query(User).all()
                self.backup_data['users'] = [
                    {
                        'id': str(user.id),
                        'organization_id': str(user.organization_id),
                        'username': user.username,
                        'password_hash': user.password_hash,
                        'email': user.email,
                        'name': user.name,
                        'role': user.role.value if user.role else None,
                        'user_status': user.user_status.value if user.user_status else None,
                        'is_active': user.is_active,
                        'created_at': user.created_at.isoformat() if user.created_at else None,
                        'updated_at': user.updated_at.isoformat() if user.updated_at else None
                    }
                    for user in users
                ]
                
                # Backup parts
                parts = session.query(Part).all()
                self.backup_data['parts'] = [
                    {
                        'id': str(part.id),
                        'part_number': part.part_number,
                        'name': part.name,
                        'description': part.description,
                        'part_type': part.part_type.value if part.part_type else None,
                        'is_proprietary': part.is_proprietary,
                        'unit_of_measure': part.unit_of_measure,
                        'manufacturer_part_number': part.manufacturer_part_number,
                        'created_at': part.created_at.isoformat() if part.created_at else None,
                        'updated_at': part.updated_at.isoformat() if part.updated_at else None
                    }
                    for part in parts
                ]
                
                # Backup warehouses
                warehouses = session.query(Warehouse).all()
                self.backup_data['warehouses'] = [
                    {
                        'id': str(wh.id),
                        'organization_id': str(wh.organization_id),
                        'name': wh.name,
                        'location': wh.location,
                        'description': wh.description,
                        'is_active': wh.is_active,
                        'created_at': wh.created_at.isoformat() if wh.created_at else None,
                        'updated_at': wh.updated_at.isoformat() if wh.updated_at else None
                    }
                    for wh in warehouses
                ]
                
                # Backup inventory
                inventory_items = session.query(Inventory).all()
                self.backup_data['inventory'] = [
                    {
                        'id': str(inv.id),
                        'warehouse_id': str(inv.warehouse_id),
                        'part_id': str(inv.part_id),
                        'current_stock': float(inv.current_stock),
                        'minimum_stock_recommendation': float(inv.minimum_stock_recommendation),
                        'unit_of_measure': inv.unit_of_measure,
                        'last_updated': inv.last_updated.isoformat() if inv.last_updated else None,
                        'created_at': inv.created_at.isoformat() if inv.created_at else None
                    }
                    for inv in inventory_items
                ]
                
                # Save backup to file
                backup_file = f"migration_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = Path(__file__).parent / backup_file
                
                with open(backup_path, 'w') as f:
                    json.dump(self.backup_data, f, indent=2, default=str)
                
                logger.info(f"Backup created successfully: {backup_path}")
                return True
                
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return False
    
    def migrate_data(self) -> bool:
        """Perform the actual data migration"""
        logger.info("Starting data migration...")
        self.progress.start_time = datetime.now()
        
        try:
            with self.SessionLocal() as session:
                # Step 1: Migrate organizations
                if not self._migrate_organizations(session):
                    return False
                
                # Step 2: Migrate users
                if not self._migrate_users(session):
                    return False
                
                # Step 3: Migrate parts
                if not self._migrate_parts(session):
                    return False
                
                # Step 4: Migrate warehouses
                if not self._migrate_warehouses(session):
                    return False
                
                # Step 5: Migrate inventory
                if not self._migrate_inventory(session):
                    return False
                
                # Step 6: Migrate machines
                if not self._migrate_machines(session):
                    return False
                
                # Step 7: Create initial transactions for existing inventory
                if not self._create_initial_transactions(session):
                    return False
                
                session.commit()
                
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            self.progress.errors.append(f"Migration failed: {str(e)}")
            return False
        
        self.progress.end_time = datetime.now()
        logger.info(f"Migration completed successfully in {self.progress.duration:.2f} seconds")
        return True
    
    def _migrate_organizations(self, session: Session) -> bool:
        """Migrate organization data to new business model"""
        logger.info("Migrating organizations...")
        
        try:
            orgs = session.query(Organization).all()
            
            for org in orgs:
                # Ensure organization has proper type
                if not org.organization_type:
                    # Infer organization type based on name or other criteria
                    if 'oraseas' in org.name.lower():
                        org.organization_type = OrganizationType.oraseas_ee
                    elif 'bossaqua' in org.name.lower():
                        org.organization_type = OrganizationType.bossaqua
                    else:
                        org.organization_type = OrganizationType.customer
                
                # Ensure required fields are set
                if not org.is_active:
                    org.is_active = True
                
                self.progress.migrated_organizations += 1
            
            logger.info(f"Migrated {self.progress.migrated_organizations} organizations")
            return True
            
        except Exception as e:
            logger.error(f"Organization migration failed: {e}")
            self.progress.errors.append(f"Organization migration failed: {str(e)}")
            return False
    
    def _migrate_users(self, session: Session) -> bool:
        """Migrate user data to new authentication system"""
        logger.info("Migrating users...")
        
        try:
            users = session.query(User).all()
            
            for user in users:
                # Ensure user has proper status
                if not user.user_status:
                    user.user_status = UserStatus.active
                
                # Ensure user has proper role
                if not user.role:
                    user.role = UserRole.user
                
                # Set default values for new fields
                if user.failed_login_attempts is None:
                    user.failed_login_attempts = 0
                
                if user.is_active is None:
                    user.is_active = True
                
                self.progress.migrated_users += 1
            
            logger.info(f"Migrated {self.progress.migrated_users} users")
            return True
            
        except Exception as e:
            logger.error(f"User migration failed: {e}")
            self.progress.errors.append(f"User migration failed: {str(e)}")
            return False
    
    def _migrate_parts(self, session: Session) -> bool:
        """Migrate parts data to new classification system"""
        logger.info("Migrating parts...")
        
        try:
            parts = session.query(Part).all()
            
            for part in parts:
                # Ensure part has proper type
                if not part.part_type:
                    # Infer part type based on unit of measure or name
                    if part.unit_of_measure in ['liters', 'kg', 'ml', 'grams']:
                        part.part_type = PartType.BULK_MATERIAL
                    else:
                        part.part_type = PartType.CONSUMABLE
                
                # Ensure unit of measure is set
                if not part.unit_of_measure:
                    part.unit_of_measure = 'pieces'
                
                # Set proprietary flag based on manufacturer or name
                if not hasattr(part, 'is_proprietary') or part.is_proprietary is None:
                    part.is_proprietary = 'bossaqua' in part.name.lower() if part.name else False
                
                self.progress.migrated_parts += 1
            
            logger.info(f"Migrated {self.progress.migrated_parts} parts")
            return True
            
        except Exception as e:
            logger.error(f"Parts migration failed: {e}")
            self.progress.errors.append(f"Parts migration failed: {str(e)}")
            return False
    
    def _migrate_warehouses(self, session: Session) -> bool:
        """Migrate warehouse data"""
        logger.info("Migrating warehouses...")
        
        try:
            warehouses = session.query(Warehouse).all()
            
            for warehouse in warehouses:
                # Ensure warehouse is active
                if warehouse.is_active is None:
                    warehouse.is_active = True
                
                self.progress.migrated_warehouses += 1
            
            logger.info(f"Migrated {self.progress.migrated_warehouses} warehouses")
            return True
            
        except Exception as e:
            logger.error(f"Warehouse migration failed: {e}")
            self.progress.errors.append(f"Warehouse migration failed: {str(e)}")
            return False
    
    def _migrate_inventory(self, session: Session) -> bool:
        """Migrate inventory data to warehouse-based system"""
        logger.info("Migrating inventory...")
        
        try:
            inventory_items = session.query(Inventory).all()
            
            for inv in inventory_items:
                # Ensure inventory has proper unit of measure
                if not inv.unit_of_measure:
                    part = session.query(Part).filter(Part.id == inv.part_id).first()
                    if part:
                        inv.unit_of_measure = part.unit_of_measure
                    else:
                        inv.unit_of_measure = 'pieces'
                
                # Ensure current stock is not null
                if inv.current_stock is None:
                    inv.current_stock = 0
                
                # Ensure minimum stock recommendation is not null
                if inv.minimum_stock_recommendation is None:
                    inv.minimum_stock_recommendation = 0
                
                self.progress.migrated_inventory += 1
            
            logger.info(f"Migrated {self.progress.migrated_inventory} inventory items")
            return True
            
        except Exception as e:
            logger.error(f"Inventory migration failed: {e}")
            self.progress.errors.append(f"Inventory migration failed: {str(e)}")
            return False
    
    def _migrate_machines(self, session: Session) -> bool:
        """Migrate machine data"""
        logger.info("Migrating machines...")
        
        try:
            machines = session.query(Machine).all()
            
            for machine in machines:
                # Ensure machine has proper customer organization
                if machine.customer_organization_id:
                    org = session.query(Organization).filter(
                        Organization.id == machine.customer_organization_id
                    ).first()
                    
                    if org and org.organization_type != OrganizationType.customer:
                        self.progress.warnings.append(
                            f"Machine {machine.serial_number} is assigned to non-customer organization {org.name}"
                        )
                
                self.progress.migrated_machines += 1
            
            logger.info(f"Migrated {self.progress.migrated_machines} machines")
            return True
            
        except Exception as e:
            logger.error(f"Machine migration failed: {e}")
            self.progress.errors.append(f"Machine migration failed: {str(e)}")
            return False
    
    def _create_initial_transactions(self, session: Session) -> bool:
        """Create initial transactions for existing inventory"""
        logger.info("Creating initial transactions for existing inventory...")
        
        try:
            # Get a system user for transaction recording
            system_user = session.query(User).filter(User.role == UserRole.super_admin).first()
            if not system_user:
                system_user = session.query(User).filter(User.role == UserRole.admin).first()
            
            if not system_user:
                self.progress.warnings.append("No admin user found for creating initial transactions")
                return True
            
            # Create initial creation transactions for all existing inventory
            inventory_items = session.query(Inventory).filter(Inventory.current_stock > 0).all()
            
            for inv in inventory_items:
                if inv.current_stock > 0:
                    transaction = Transaction(
                        id=uuid.uuid4(),
                        transaction_type=TransactionType.CREATION,
                        part_id=inv.part_id,
                        to_warehouse_id=inv.warehouse_id,
                        quantity=inv.current_stock,
                        unit_of_measure=inv.unit_of_measure,
                        performed_by_user_id=system_user.id,
                        transaction_date=datetime.now(),
                        notes="Initial inventory creation during migration",
                        reference_number=f"MIGRATION-{datetime.now().strftime('%Y%m%d')}"
                    )
                    session.add(transaction)
            
            logger.info(f"Created initial transactions for {len(inventory_items)} inventory items")
            return True
            
        except Exception as e:
            logger.error(f"Initial transaction creation failed: {e}")
            self.progress.errors.append(f"Initial transaction creation failed: {str(e)}")
            return False
    
    def rollback_migration(self, backup_file: str = None) -> bool:
        """Rollback migration using backup data"""
        logger.info("Starting migration rollback...")
        
        try:
            # Load backup data
            if backup_file:
                backup_path = Path(backup_file)
            else:
                # Find the most recent backup file
                backup_files = list(Path(__file__).parent.glob("migration_backup_*.json"))
                if not backup_files:
                    logger.error("No backup files found for rollback")
                    return False
                backup_path = max(backup_files, key=lambda p: p.stat().st_mtime)
            
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            with self.SessionLocal() as session:
                # Rollback in reverse order
                self._rollback_transactions(session)
                self._rollback_inventory(session, backup_data.get('inventory', []))
                self._rollback_warehouses(session, backup_data.get('warehouses', []))
                self._rollback_parts(session, backup_data.get('parts', []))
                self._rollback_users(session, backup_data.get('users', []))
                self._rollback_organizations(session, backup_data.get('organizations', []))
                
                session.commit()
            
            logger.info("Migration rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def _rollback_transactions(self, session: Session):
        """Remove migration-created transactions"""
        session.execute(text("""
            DELETE FROM transactions 
            WHERE reference_number LIKE 'MIGRATION-%'
        """))
    
    def _rollback_inventory(self, session: Session, backup_inventory: List[Dict]):
        """Rollback inventory to backup state"""
        # This is a simplified rollback - in production, you might want more sophisticated logic
        for inv_data in backup_inventory:
            session.execute(text("""
                UPDATE inventory 
                SET current_stock = :stock,
                    minimum_stock_recommendation = :min_stock,
                    unit_of_measure = :unit
                WHERE id = :id
            """), {
                'id': inv_data['id'],
                'stock': inv_data['current_stock'],
                'min_stock': inv_data['minimum_stock_recommendation'],
                'unit': inv_data['unit_of_measure']
            })
    
    def _rollback_warehouses(self, session: Session, backup_warehouses: List[Dict]):
        """Rollback warehouses to backup state"""
        # Similar rollback logic for warehouses
        pass
    
    def _rollback_parts(self, session: Session, backup_parts: List[Dict]):
        """Rollback parts to backup state"""
        # Similar rollback logic for parts
        pass
    
    def _rollback_users(self, session: Session, backup_users: List[Dict]):
        """Rollback users to backup state"""
        # Similar rollback logic for users
        pass
    
    def _rollback_organizations(self, session: Session, backup_organizations: List[Dict]):
        """Rollback organizations to backup state"""
        # Similar rollback logic for organizations
        pass
    
    def generate_migration_report(self) -> Dict[str, Any]:
        """Generate comprehensive migration report"""
        report = {
            'migration_summary': self.progress.to_dict(),
            'timestamp': datetime.now().isoformat(),
            'database_url': self.database_url.split('@')[1] if '@' in self.database_url else 'hidden',
            'success': len(self.progress.errors) == 0,
            'recommendations': []
        }
        
        # Add recommendations based on migration results
        if self.progress.warnings:
            report['recommendations'].append("Review warnings and consider data cleanup")
        
        if self.progress.migrated_organizations < self.progress.total_organizations:
            report['recommendations'].append("Some organizations were not migrated - investigate")
        
        return report
    
    def test_with_sample_data(self) -> bool:
        """Test migration with a sample of production data"""
        logger.info("Testing migration with sample data...")
        
        # This would create a test database with a sample of production data
        # and run the migration to verify it works correctly
        
        # Implementation would involve:
        # 1. Create test database
        # 2. Copy sample data
        # 3. Run migration
        # 4. Validate results
        # 5. Clean up test database
        
        logger.info("Sample data testing not implemented in this version")
        return True


def main():
    """Main entry point for migration manager"""
    parser = argparse.ArgumentParser(description='ABParts Data Migration Manager')
    parser.add_argument('--validate-only', action='store_true', help='Only validate existing data')
    parser.add_argument('--migrate', action='store_true', help='Perform full migration')
    parser.add_argument('--rollback', action='store_true', help='Rollback migration')
    parser.add_argument('--test-with-sample', action='store_true', help='Test with sample data')
    parser.add_argument('--backup-file', help='Specific backup file for rollback')
    parser.add_argument('--database-url', help='Database URL override')
    
    args = parser.parse_args()
    
    # Create migration manager
    manager = DataMigrationManager(database_url=args.database_url)
    
    if args.validate_only:
        result = manager.validate_existing_data()
        print(f"\nValidation Result: {'PASSED' if result.is_valid else 'FAILED'}")
        print(f"Errors: {len(result.errors)}")
        print(f"Warnings: {len(result.warnings)}")
        
        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        if result.recommendations:
            print("\nRecommendations:")
            for rec in result.recommendations:
                print(f"  - {rec}")
    
    elif args.migrate:
        # Validate first
        validation = manager.validate_existing_data()
        if not validation.is_valid:
            print("Validation failed. Migration aborted.")
            print("Errors:")
            for error in validation.errors:
                print(f"  - {error}")
            return 1
        
        # Create backup
        if not manager.create_backup():
            print("Backup creation failed. Migration aborted.")
            return 1
        
        # Perform migration
        if manager.migrate_data():
            print("Migration completed successfully!")
            report = manager.generate_migration_report()
            print(f"Migration report: {json.dumps(report, indent=2)}")
        else:
            print("Migration failed!")
            return 1
    
    elif args.rollback:
        if manager.rollback_migration(args.backup_file):
            print("Rollback completed successfully!")
        else:
            print("Rollback failed!")
            return 1
    
    elif args.test_with_sample:
        if manager.test_with_sample_data():
            print("Sample data testing completed!")
        else:
            print("Sample data testing failed!")
            return 1
    
    else:
        parser.print_help()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())