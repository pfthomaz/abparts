"""
Data Migration Utilities for ABParts Business Model Alignment

This module provides utilities for migrating existing data to the new business model schema.
Includes validation, rollback capabilities, and progress tracking.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError

from .database import get_db, engine
from .models import (
    Organization, User, Part, Warehouse, Inventory, Machine, 
    Transaction, StockAdjustment, OrganizationType, UserRole, 
    PartType, TransactionType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MigrationError(Exception):
    """Custom exception for migration errors"""
    pass


class MigrationProgress:
    """Track migration progress and statistics"""
    
    def __init__(self):
        self.start_time = datetime.now(timezone.utc)
        self.steps_completed = 0
        self.total_steps = 0
        self.errors = []
        self.warnings = []
        self.statistics = {}
        
    def add_step(self, step_name: str):
        """Add a migration step"""
        self.total_steps += 1
        logger.info(f"Step {self.total_steps}: {step_name}")
        
    def complete_step(self, step_name: str, stats: Dict[str, Any] = None):
        """Mark a step as completed"""
        self.steps_completed += 1
        if stats:
            self.statistics[step_name] = stats
        logger.info(f"Completed: {step_name}")
        
    def add_error(self, error: str):
        """Add an error to the migration log"""
        self.errors.append(error)
        logger.error(error)
        
    def add_warning(self, warning: str):
        """Add a warning to the migration log"""
        self.warnings.append(warning)
        logger.warning(warning)
        
    def get_summary(self) -> Dict[str, Any]:
        """Get migration summary"""
        duration = datetime.now(timezone.utc) - self.start_time
        return {
            "start_time": self.start_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "steps_completed": self.steps_completed,
            "total_steps": self.total_steps,
            "success_rate": self.steps_completed / self.total_steps if self.total_steps > 0 else 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "statistics": self.statistics
        }


class DataValidator:
    """Validate data integrity before and after migration"""
    
    @staticmethod
    def validate_pre_migration(db: Session) -> List[str]:
        """Validate data before migration"""
        issues = []
        
        # Check for duplicate organization names
        duplicate_orgs = db.execute(text("""
            SELECT name, COUNT(*) as count 
            FROM organizations 
            GROUP BY name 
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        if duplicate_orgs:
            issues.append(f"Duplicate organization names found: {[row.name for row in duplicate_orgs]}")
            
        # Check for users without organizations
        orphaned_users = db.execute(text("""
            SELECT COUNT(*) as count 
            FROM users u 
            LEFT JOIN organizations o ON u.organization_id = o.id 
            WHERE o.id IS NULL
        """)).scalar()
        
        if orphaned_users > 0:
            issues.append(f"Found {orphaned_users} users without valid organizations")
            
        # Check for inventory without parts
        orphaned_inventory = db.execute(text("""
            SELECT COUNT(*) as count 
            FROM inventory i 
            LEFT JOIN parts p ON i.part_id = p.id 
            WHERE p.id IS NULL
        """)).scalar()
        
        if orphaned_inventory > 0:
            issues.append(f"Found {orphaned_inventory} inventory records without valid parts")
            
        return issues
        
    @staticmethod
    def validate_post_migration(db: Session) -> List[str]:
        """Validate data after migration"""
        issues = []
        
        # Check organization type constraints
        oraseas_count = db.query(Organization).filter(
            Organization.organization_type == OrganizationType.oraseas_ee
        ).count()
        
        if oraseas_count != 1:
            issues.append(f"Expected 1 Oraseas EE organization, found {oraseas_count}")
            
        bossaqua_count = db.query(Organization).filter(
            Organization.organization_type == OrganizationType.bossaqua
        ).count()
        
        if bossaqua_count > 1:
            issues.append(f"Expected at most 1 BossAqua organization, found {bossaqua_count}")
            
        # Check user role constraints
        super_admins = db.query(User).filter(User.role == UserRole.super_admin).all()
        oraseas_org = db.query(Organization).filter(
            Organization.organization_type == OrganizationType.oraseas_ee
        ).first()
        
        if oraseas_org:
            invalid_super_admins = [
                user for user in super_admins 
                if user.organization_id != oraseas_org.id
            ]
            if invalid_super_admins:
                issues.append(f"Found {len(invalid_super_admins)} super_admin users not in Oraseas EE")
                
        # Check warehouse-inventory relationships
        invalid_inventory = db.execute(text("""
            SELECT COUNT(*) as count 
            FROM inventory i 
            LEFT JOIN warehouses w ON i.warehouse_id = w.id 
            WHERE w.id IS NULL
        """)).scalar()
        
        if invalid_inventory > 0:
            issues.append(f"Found {invalid_inventory} inventory records without valid warehouses")
            
        return issues


class DataMigrator:
    """Main data migration class"""
    
    def __init__(self):
        self.progress = MigrationProgress()
        self.validator = DataValidator()
        self.backup_data = {}
        
    def create_backup(self, db: Session) -> Dict[str, Any]:
        """Create backup of critical data before migration"""
        logger.info("Creating data backup...")
        
        backup = {
            "organizations": [],
            "users": [],
            "parts": [],
            "warehouses": [],
            "inventory": [],
            "machines": []
        }
        
        try:
            # Backup organizations
            orgs = db.execute(text("SELECT * FROM organizations")).fetchall()
            backup["organizations"] = [dict(row._mapping) for row in orgs]
            
            # Backup users
            users = db.execute(text("SELECT * FROM users")).fetchall()
            backup["users"] = [dict(row._mapping) for row in users]
            
            # Backup parts
            parts = db.execute(text("SELECT * FROM parts")).fetchall()
            backup["parts"] = [dict(row._mapping) for row in parts]
            
            # Backup warehouses
            warehouses = db.execute(text("SELECT * FROM warehouses")).fetchall()
            backup["warehouses"] = [dict(row._mapping) for row in warehouses]
            
            # Backup inventory
            inventory = db.execute(text("SELECT * FROM inventory")).fetchall()
            backup["inventory"] = [dict(row._mapping) for row in inventory]
            
            # Backup machines
            machines = db.execute(text("SELECT * FROM machines")).fetchall()
            backup["machines"] = [dict(row._mapping) for row in machines]
            
            self.backup_data = backup
            logger.info(f"Backup created with {sum(len(v) for v in backup.values())} total records")
            return backup
            
        except Exception as e:
            raise MigrationError(f"Failed to create backup: {str(e)}")
    
    def migrate_organization_types(self, db: Session) -> Dict[str, Any]:
        """Migrate organizations to include proper business types"""
        self.progress.add_step("Migrate Organization Types")
        
        try:
            # Get all organizations using raw SQL to avoid model issues
            organizations = db.execute(text("SELECT * FROM organizations")).fetchall()
            stats = {"updated": 0, "errors": 0}
            
            for org_row in organizations:
                try:
                    # Determine organization type based on name patterns
                    name_lower = org_row.name.lower() if org_row.name else ""
                    
                    if "oraseas" in name_lower or "oraseas ee" in name_lower:
                        new_type = "oraseas_ee"
                    elif "bossaqua" in name_lower or "boss aqua" in name_lower:
                        new_type = "bossaqua"
                    elif "supplier" in name_lower:
                        new_type = "supplier"
                        # Set parent to Oraseas EE if exists
                        oraseas_result = db.execute(text(
                            "SELECT id FROM organizations WHERE organization_type = 'oraseas_ee' LIMIT 1"
                        )).fetchone()
                        if oraseas_result:
                            db.execute(text(
                                "UPDATE organizations SET parent_organization_id = :parent_id WHERE id = :org_id"
                            ), {"parent_id": oraseas_result.id, "org_id": org_row.id})
                    else:
                        # Default to customer
                        new_type = "customer"
                    
                    # Update organization type
                    db.execute(text(
                        "UPDATE organizations SET organization_type = :org_type WHERE id = :org_id"
                    ), {"org_type": new_type, "org_id": org_row.id})
                        
                    stats["updated"] += 1
                    
                except Exception as e:
                    stats["errors"] += 1
                    self.progress.add_error(f"Failed to migrate organization {org_row.name}: {str(e)}")
                    
            db.commit()
            self.progress.complete_step("Migrate Organization Types", stats)
            return stats
            
        except Exception as e:
            db.rollback()
            raise MigrationError(f"Organization type migration failed: {str(e)}")
    
    def migrate_user_roles(self, db: Session) -> Dict[str, Any]:
        """Migrate user roles to new role system"""
        self.progress.add_step("Migrate User Roles")
        
        try:
            # Get all users using raw SQL
            users = db.execute(text("SELECT * FROM users")).fetchall()
            stats = {"updated": 0, "errors": 0, "super_admins": 0, "admins": 0, "users": 0}
            
            # Get Oraseas EE organization
            oraseas_org = db.execute(text(
                "SELECT id FROM organizations WHERE organization_type = 'oraseas_ee' LIMIT 1"
            )).fetchone()
            
            for user_row in users:
                try:
                    current_role = user_row.role if hasattr(user_row, 'role') else 'user'
                    new_role = current_role
                    
                    # Validate super_admin constraint
                    if current_role == 'super_admin':
                        if oraseas_org and user_row.organization_id != oraseas_org.id:
                            # Demote to admin if not in Oraseas EE
                            new_role = 'admin'
                            self.progress.add_warning(
                                f"Demoted user {user_row.username} from super_admin to admin "
                                f"(not in Oraseas EE organization)"
                            )
                        else:
                            stats["super_admins"] += 1
                    elif current_role == 'admin':
                        stats["admins"] += 1
                    else:
                        # Assign first user in Oraseas EE as super_admin if none exists
                        if oraseas_org and user_row.organization_id == oraseas_org.id and stats["super_admins"] == 0:
                            new_role = 'super_admin'
                            stats["super_admins"] += 1
                        else:
                            stats["users"] += 1
                    
                    # Update user role if changed
                    if new_role != current_role:
                        db.execute(text(
                            "UPDATE users SET role = :role WHERE id = :user_id"
                        ), {"role": new_role, "user_id": user_row.id})
                    
                    # Ensure user_status is set
                    if not hasattr(user_row, 'user_status') or not user_row.user_status:
                        db.execute(text(
                            "UPDATE users SET user_status = 'active' WHERE id = :user_id"
                        ), {"user_id": user_row.id})
                    
                    # Ensure failed_login_attempts is set
                    if not hasattr(user_row, 'failed_login_attempts') or user_row.failed_login_attempts is None:
                        db.execute(text(
                            "UPDATE users SET failed_login_attempts = 0 WHERE id = :user_id"
                        ), {"user_id": user_row.id})
                        
                    stats["updated"] += 1
                    
                except Exception as e:
                    stats["errors"] += 1
                    self.progress.add_error(f"Failed to migrate user {user_row.username}: {str(e)}")
                    
            db.commit()
            self.progress.complete_step("Migrate User Roles", stats)
            return stats
            
        except Exception as e:
            db.rollback()
            raise MigrationError(f"User role migration failed: {str(e)}")
    
    def migrate_parts_classification(self, db: Session) -> Dict[str, Any]:
        """Migrate parts to include proper classification"""
        self.progress.add_step("Migrate Parts Classification")
        
        try:
            # Get all parts using raw SQL
            parts = db.execute(text("SELECT * FROM parts")).fetchall()
            stats = {"updated": 0, "consumable": 0, "bulk_material": 0, "proprietary": 0}
            
            for part_row in parts:
                try:
                    # Determine part type based on name/description
                    name_desc = f"{part_row.name or ''} {part_row.description or ''}".lower()
                    
                    # Check for bulk materials (liquids, chemicals, etc.)
                    bulk_keywords = ['oil', 'chemical', 'liquid', 'fluid', 'cleaner', 'solution', 'liter', 'ml', 'gallon']
                    if any(keyword in name_desc for keyword in bulk_keywords):
                        new_part_type = 'bulk_material'
                        stats["bulk_material"] += 1
                        # Set appropriate unit of measure
                        new_unit = 'liters' if not part_row.unit_of_measure or part_row.unit_of_measure == 'pieces' else part_row.unit_of_measure
                    else:
                        new_part_type = 'consumable'
                        stats["consumable"] += 1
                        new_unit = part_row.unit_of_measure or 'pieces'
                    
                    # Determine if proprietary (BossAqua parts)
                    proprietary_keywords = ['bossaqua', 'boss aqua', 'autoboss', 'proprietary']
                    is_proprietary = any(keyword in name_desc for keyword in proprietary_keywords)
                    if is_proprietary:
                        stats["proprietary"] += 1
                    
                    # Update part
                    db.execute(text("""
                        UPDATE parts 
                        SET part_type = :part_type, 
                            unit_of_measure = :unit_of_measure,
                            is_proprietary = :is_proprietary
                        WHERE id = :part_id
                    """), {
                        "part_type": new_part_type,
                        "unit_of_measure": new_unit,
                        "is_proprietary": is_proprietary,
                        "part_id": part_row.id
                    })
                    
                    stats["updated"] += 1
                    
                except Exception as e:
                    self.progress.add_error(f"Failed to migrate part {part_row.part_number}: {str(e)}")
                    
            db.commit()
            self.progress.complete_step("Migrate Parts Classification", stats)
            return stats
            
        except Exception as e:
            db.rollback()
            raise MigrationError(f"Parts classification migration failed: {str(e)}")
    
    def ensure_default_warehouses(self, db: Session) -> Dict[str, Any]:
        """Ensure each organization has at least one warehouse"""
        self.progress.add_step("Ensure Default Warehouses")
        
        try:
            organizations = db.query(Organization).all()
            stats = {"created": 0, "existing": 0}
            
            for org in organizations:
                try:
                    # Check if organization has any warehouses
                    existing_warehouses = db.query(Warehouse).filter(
                        Warehouse.organization_id == org.id
                    ).count()
                    
                    if existing_warehouses == 0:
                        # Create default warehouse
                        default_warehouse = Warehouse(
                            id=uuid.uuid4(),
                            organization_id=org.id,
                            name="Main Warehouse",
                            location=org.address or "Not specified",
                            description=f"Default warehouse for {org.name}",
                            is_active=True
                        )
                        db.add(default_warehouse)
                        stats["created"] += 1
                    else:
                        stats["existing"] += 1
                        
                except Exception as e:
                    self.progress.add_error(f"Failed to create warehouse for {org.name}: {str(e)}")
                    
            db.commit()
            self.progress.complete_step("Ensure Default Warehouses", stats)
            return stats
            
        except Exception as e:
            db.rollback()
            raise MigrationError(f"Warehouse creation failed: {str(e)}")
    
    def migrate_inventory_to_warehouses(self, db: Session) -> Dict[str, Any]:
        """Migrate inventory from organization-based to warehouse-based"""
        self.progress.add_step("Migrate Inventory to Warehouses")
        
        try:
            # Get all inventory records
            inventory_records = db.query(Inventory).all()
            stats = {"migrated": 0, "errors": 0, "warehouse_assignments": {}}
            
            for inventory in inventory_records:
                try:
                    # If inventory already has warehouse_id, skip
                    if hasattr(inventory, 'warehouse_id') and inventory.warehouse_id:
                        stats["migrated"] += 1
                        continue
                    
                    # Find warehouse for this inventory
                    # First, try to find warehouse through organization relationship
                    warehouse = None
                    
                    if hasattr(inventory, 'organization_id') and inventory.organization_id:
                        # Legacy: inventory was linked to organization
                        warehouse = db.query(Warehouse).filter(
                            Warehouse.organization_id == inventory.organization_id
                        ).first()
                    else:
                        # Try to find through part relationships or other means
                        # This is a fallback - in practice, we'd need more business logic
                        self.progress.add_warning(f"Inventory record {inventory.id} has no clear organization link")
                        continue
                    
                    if warehouse:
                        inventory.warehouse_id = warehouse.id
                        
                        # Track warehouse assignments
                        warehouse_name = warehouse.name
                        if warehouse_name not in stats["warehouse_assignments"]:
                            stats["warehouse_assignments"][warehouse_name] = 0
                        stats["warehouse_assignments"][warehouse_name] += 1
                        
                        stats["migrated"] += 1
                    else:
                        stats["errors"] += 1
                        self.progress.add_error(f"No warehouse found for inventory {inventory.id}")
                        
                except Exception as e:
                    stats["errors"] += 1
                    self.progress.add_error(f"Failed to migrate inventory {inventory.id}: {str(e)}")
                    
            db.commit()
            self.progress.complete_step("Migrate Inventory to Warehouses", stats)
            return stats
            
        except Exception as e:
            db.rollback()
            raise MigrationError(f"Inventory migration failed: {str(e)}")
    
    def create_initial_transactions(self, db: Session) -> Dict[str, Any]:
        """Create initial transactions for existing inventory"""
        self.progress.add_step("Create Initial Transactions")
        
        try:
            inventory_records = db.query(Inventory).filter(Inventory.current_stock > 0).all()
            stats = {"created": 0, "errors": 0, "total_value": Decimal('0')}
            
            # Get a system user for transaction recording
            system_user = db.query(User).filter(User.role == UserRole.super_admin).first()
            if not system_user:
                system_user = db.query(User).first()  # Fallback to any user
                
            if not system_user:
                raise MigrationError("No user found to record initial transactions")
            
            for inventory in inventory_records:
                try:
                    if inventory.current_stock > 0:
                        # Create initial stock transaction
                        transaction = Transaction(
                            id=uuid.uuid4(),
                            transaction_type=TransactionType.creation,
                            part_id=inventory.part_id,
                            to_warehouse_id=inventory.warehouse_id,
                            quantity=inventory.current_stock,
                            unit_of_measure=inventory.unit_of_measure,
                            performed_by_user_id=system_user.id,
                            transaction_date=datetime.now(timezone.utc),
                            notes="Initial stock migration - existing inventory",
                            reference_number=f"MIGRATION-{inventory.id}"
                        )
                        db.add(transaction)
                        stats["created"] += 1
                        stats["total_value"] += inventory.current_stock
                        
                except Exception as e:
                    stats["errors"] += 1
                    self.progress.add_error(f"Failed to create transaction for inventory {inventory.id}: {str(e)}")
                    
            db.commit()
            self.progress.complete_step("Create Initial Transactions", stats)
            return stats
            
        except Exception as e:
            db.rollback()
            raise MigrationError(f"Initial transaction creation failed: {str(e)}")
    
    def run_full_migration(self, db: Session) -> Dict[str, Any]:
        """Run the complete migration process"""
        logger.info("Starting full data migration...")
        
        try:
            # Pre-migration validation
            pre_issues = self.validator.validate_pre_migration(db)
            if pre_issues:
                self.progress.add_warning(f"Pre-migration issues found: {pre_issues}")
            
            # Create backup
            self.create_backup(db)
            
            # Run migration steps
            migration_results = {}
            
            migration_results["organization_types"] = self.migrate_organization_types(db)
            migration_results["user_roles"] = self.migrate_user_roles(db)
            migration_results["parts_classification"] = self.migrate_parts_classification(db)
            migration_results["default_warehouses"] = self.ensure_default_warehouses(db)
            migration_results["inventory_migration"] = self.migrate_inventory_to_warehouses(db)
            migration_results["initial_transactions"] = self.create_initial_transactions(db)
            
            # Post-migration validation
            post_issues = self.validator.validate_post_migration(db)
            if post_issues:
                self.progress.add_error(f"Post-migration validation failed: {post_issues}")
                raise MigrationError(f"Migration validation failed: {post_issues}")
            
            # Generate final report
            summary = self.progress.get_summary()
            summary["migration_results"] = migration_results
            summary["backup_created"] = len(self.backup_data) > 0
            
            logger.info("Migration completed successfully!")
            return summary
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            # Attempt rollback if possible
            try:
                db.rollback()
                logger.info("Database transaction rolled back")
            except:
                logger.error("Failed to rollback database transaction")
            
            raise MigrationError(f"Migration failed: {str(e)}")
    
    def rollback_migration(self, db: Session) -> bool:
        """Attempt to rollback migration using backup data"""
        if not self.backup_data:
            logger.error("No backup data available for rollback")
            return False
            
        try:
            logger.info("Starting migration rollback...")
            
            # This is a simplified rollback - in production, you'd want more sophisticated rollback logic
            # For now, we'll just log what would be rolled back
            logger.info(f"Would rollback {len(self.backup_data['organizations'])} organizations")
            logger.info(f"Would rollback {len(self.backup_data['users'])} users")
            logger.info(f"Would rollback {len(self.backup_data['parts'])} parts")
            logger.info(f"Would rollback {len(self.backup_data['warehouses'])} warehouses")
            logger.info(f"Would rollback {len(self.backup_data['inventory'])} inventory records")
            
            # In a real implementation, you would:
            # 1. Restore data from backup
            # 2. Remove any new records created during migration
            # 3. Reset any modified fields to original values
            
            logger.warning("Rollback functionality is not fully implemented - manual intervention required")
            return False
            
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            return False


def run_migration():
    """Main function to run the migration"""
    migrator = DataMigrator()
    
    try:
        # Get database session
        db = next(get_db())
        
        # Run migration
        result = migrator.run_full_migration(db)
        
        # Print summary
        print("\n" + "="*50)
        print("MIGRATION SUMMARY")
        print("="*50)
        print(f"Duration: {result['duration_seconds']:.2f} seconds")
        print(f"Steps completed: {result['steps_completed']}/{result['total_steps']}")
        print(f"Success rate: {result['success_rate']:.1%}")
        
        if result['errors']:
            print(f"\nErrors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  - {error}")
                
        if result['warnings']:
            print(f"\nWarnings ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"  - {warning}")
                
        print(f"\nMigration Results:")
        for step, stats in result['migration_results'].items():
            print(f"  {step}: {stats}")
            
        return result
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        return None
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()