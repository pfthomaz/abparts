"""
Data Validation Utilities for ABParts Migration

This module provides comprehensive data validation capabilities for:
- Pre-migration data integrity checks
- Post-migration validation
- Business rule enforcement
- Data consistency verification
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import text, func
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.models import (
    Organization, User, Part, Machine, Warehouse, Inventory, 
    Transaction, OrganizationType, UserRole, UserStatus, PartType
)


class ValidationSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Represents a single validation result."""
    check_name: str
    severity: ValidationSeverity
    message: str
    affected_records: int = 0
    details: Optional[Dict[str, Any]] = None
    
    def __str__(self):
        return f"[{self.severity.value.upper()}] {self.check_name}: {self.message} (Records: {self.affected_records})"


@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    timestamp: datetime
    total_checks: int
    passed_checks: int
    warnings: int
    errors: int
    critical_issues: int
    results: List[ValidationResult]
    
    @property
    def is_valid(self) -> bool:
        """Returns True if no critical errors or errors found."""
        return self.errors == 0 and self.critical_issues == 0
    
    @property
    def summary(self) -> str:
        """Returns a summary of the validation results."""
        return (f"Validation Summary: {self.passed_checks}/{self.total_checks} passed, "
                f"{self.warnings} warnings, {self.errors} errors, {self.critical_issues} critical")


class DataValidator:
    """
    Comprehensive data validator for ABParts business model alignment.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_all(self, db: Session) -> ValidationReport:
        """
        Run all validation checks and return comprehensive report.
        
        Args:
            db: Database session
            
        Returns:
            ValidationReport with all validation results
        """
        self.logger.info("Starting comprehensive data validation")
        
        results = []
        
        # Run all validation checks
        validation_methods = [
            self._validate_organization_structure,
            self._validate_organization_business_rules,
            self._validate_user_structure,
            self._validate_user_business_rules,
            self._validate_part_structure,
            self._validate_part_business_rules,
            self._validate_warehouse_structure,
            self._validate_inventory_integrity,
            self._validate_machine_relationships,
            self._validate_transaction_integrity,
            self._validate_referential_integrity,
            self._validate_data_consistency
        ]
        
        for method in validation_methods:
            try:
                method_results = method(db)
                results.extend(method_results)
            except Exception as e:
                self.logger.error(f"Validation method {method.__name__} failed: {str(e)}")
                results.append(ValidationResult(
                    check_name=method.__name__,
                    severity=ValidationSeverity.CRITICAL,
                    message=f"Validation check failed: {str(e)}"
                ))
        
        # Generate report
        report = self._generate_report(results)
        self.logger.info(f"Validation completed: {report.summary}")
        
        return report
    
    def _validate_organization_structure(self, db: Session) -> List[ValidationResult]:
        """Validate organization table structure and basic data."""
        results = []
        
        # Check for organizations without names
        orgs_without_names = db.query(Organization).filter(
            Organization.name.is_(None) | (Organization.name == '')
        ).count()
        
        if orgs_without_names > 0:
            results.append(ValidationResult(
                check_name="organizations_without_names",
                severity=ValidationSeverity.ERROR,
                message="Organizations found without names",
                affected_records=orgs_without_names
            ))
        
        # Check for organizations without types
        orgs_without_types = db.query(Organization).filter(
            Organization.organization_type.is_(None)
        ).count()
        
        if orgs_without_types > 0:
            results.append(ValidationResult(
                check_name="organizations_without_types",
                severity=ValidationSeverity.ERROR,
                message="Organizations found without organization_type",
                affected_records=orgs_without_types
            ))
        
        # Check for duplicate organization names
        duplicate_names = db.execute(text("""
            SELECT name, COUNT(*) as count
            FROM organizations
            GROUP BY name
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        if duplicate_names:
            results.append(ValidationResult(
                check_name="duplicate_organization_names",
                severity=ValidationSeverity.ERROR,
                message="Duplicate organization names found",
                affected_records=len(duplicate_names),
                details={"duplicates": [{"name": row.name, "count": row.count} for row in duplicate_names]}
            ))
        
        return results
    
    def _validate_organization_business_rules(self, db: Session) -> List[ValidationResult]:
        """Validate organization business rules."""
        results = []
        
        # Check for exactly one Oraseas EE organization
        oraseas_count = db.query(Organization).filter(
            Organization.organization_type == OrganizationType.oraseas_ee
        ).count()
        
        if oraseas_count == 0:
            results.append(ValidationResult(
                check_name="missing_oraseas_ee",
                severity=ValidationSeverity.CRITICAL,
                message="No Oraseas EE organization found",
                affected_records=0
            ))
        elif oraseas_count > 1:
            results.append(ValidationResult(
                check_name="multiple_oraseas_ee",
                severity=ValidationSeverity.CRITICAL,
                message="Multiple Oraseas EE organizations found",
                affected_records=oraseas_count
            ))
        
        # Check for at most one BossAqua organization
        bossaqua_count = db.query(Organization).filter(
            Organization.organization_type == OrganizationType.bossaqua
        ).count()
        
        if bossaqua_count > 1:
            results.append(ValidationResult(
                check_name="multiple_bossaqua",
                severity=ValidationSeverity.ERROR,
                message="Multiple BossAqua organizations found",
                affected_records=bossaqua_count
            ))
        
        # Check supplier organizations have parent organizations
        suppliers_without_parent = db.query(Organization).filter(
            Organization.organization_type == OrganizationType.supplier,
            Organization.parent_organization_id.is_(None)
        ).count()
        
        if suppliers_without_parent > 0:
            results.append(ValidationResult(
                check_name="suppliers_without_parent",
                severity=ValidationSeverity.ERROR,
                message="Supplier organizations without parent organization",
                affected_records=suppliers_without_parent
            ))
        
        return results
    
    def _validate_user_structure(self, db: Session) -> List[ValidationResult]:
        """Validate user table structure and basic data."""
        results = []
        
        # Check for users without usernames
        users_without_username = db.query(User).filter(
            User.username.is_(None) | (User.username == '')
        ).count()
        
        if users_without_username > 0:
            results.append(ValidationResult(
                check_name="users_without_username",
                severity=ValidationSeverity.ERROR,
                message="Users found without usernames",
                affected_records=users_without_username
            ))
        
        # Check for users without emails
        users_without_email = db.query(User).filter(
            User.email.is_(None) | (User.email == '')
        ).count()
        
        if users_without_email > 0:
            results.append(ValidationResult(
                check_name="users_without_email",
                severity=ValidationSeverity.ERROR,
                message="Users found without email addresses",
                affected_records=users_without_email
            ))
        
        # Check for users without roles
        users_without_role = db.query(User).filter(
            User.role.is_(None)
        ).count()
        
        if users_without_role > 0:
            results.append(ValidationResult(
                check_name="users_without_role",
                severity=ValidationSeverity.ERROR,
                message="Users found without roles",
                affected_records=users_without_role
            ))
        
        # Check for duplicate usernames
        duplicate_usernames = db.execute(text("""
            SELECT username, COUNT(*) as count
            FROM users
            GROUP BY username
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        if duplicate_usernames:
            results.append(ValidationResult(
                check_name="duplicate_usernames",
                severity=ValidationSeverity.ERROR,
                message="Duplicate usernames found",
                affected_records=len(duplicate_usernames)
            ))
        
        # Check for duplicate emails
        duplicate_emails = db.execute(text("""
            SELECT email, COUNT(*) as count
            FROM users
            GROUP BY email
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        if duplicate_emails:
            results.append(ValidationResult(
                check_name="duplicate_emails",
                severity=ValidationSeverity.ERROR,
                message="Duplicate email addresses found",
                affected_records=len(duplicate_emails)
            ))
        
        return results
    
    def _validate_user_business_rules(self, db: Session) -> List[ValidationResult]:
        """Validate user business rules."""
        results = []
        
        # Check that super_admin users belong to Oraseas EE
        super_admin_non_oraseas = db.execute(text("""
            SELECT COUNT(*) as count
            FROM users u
            JOIN organizations o ON u.organization_id = o.id
            WHERE u.role = 'super_admin' AND o.organization_type != 'oraseas_ee'
        """)).scalar()
        
        if super_admin_non_oraseas > 0:
            results.append(ValidationResult(
                check_name="super_admin_non_oraseas",
                severity=ValidationSeverity.ERROR,
                message="Super admin users found in non-Oraseas EE organizations",
                affected_records=super_admin_non_oraseas
            ))
        
        # Check that each organization has at least one admin
        orgs_without_admin = db.execute(text("""
            SELECT o.id, o.name
            FROM organizations o
            LEFT JOIN users u ON o.id = u.organization_id AND u.role IN ('admin', 'super_admin')
            WHERE u.id IS NULL
        """)).fetchall()
        
        if orgs_without_admin:
            results.append(ValidationResult(
                check_name="organizations_without_admin",
                severity=ValidationSeverity.WARNING,
                message="Organizations without admin users",
                affected_records=len(orgs_without_admin),
                details={"organizations": [{"id": str(row.id), "name": row.name} for row in orgs_without_admin]}
            ))
        
        return results
    
    def _validate_part_structure(self, db: Session) -> List[ValidationResult]:
        """Validate part table structure and basic data."""
        results = []
        
        # Check for parts without part numbers
        parts_without_number = db.query(Part).filter(
            Part.part_number.is_(None) | (Part.part_number == '')
        ).count()
        
        if parts_without_number > 0:
            results.append(ValidationResult(
                check_name="parts_without_number",
                severity=ValidationSeverity.ERROR,
                message="Parts found without part numbers",
                affected_records=parts_without_number
            ))
        
        # Check for parts without names
        parts_without_name = db.query(Part).filter(
            Part.name.is_(None) | (Part.name == '')
        ).count()
        
        if parts_without_name > 0:
            results.append(ValidationResult(
                check_name="parts_without_name",
                severity=ValidationSeverity.ERROR,
                message="Parts found without names",
                affected_records=parts_without_name
            ))
        
        # Check for duplicate part numbers
        duplicate_part_numbers = db.execute(text("""
            SELECT part_number, COUNT(*) as count
            FROM parts
            GROUP BY part_number
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        if duplicate_part_numbers:
            results.append(ValidationResult(
                check_name="duplicate_part_numbers",
                severity=ValidationSeverity.ERROR,
                message="Duplicate part numbers found",
                affected_records=len(duplicate_part_numbers)
            ))
        
        return results
    
    def _validate_part_business_rules(self, db: Session) -> List[ValidationResult]:
        """Validate part business rules."""
        results = []
        
        # Check for parts without part types
        parts_without_type = db.query(Part).filter(
            Part.part_type.is_(None)
        ).count()
        
        if parts_without_type > 0:
            results.append(ValidationResult(
                check_name="parts_without_type",
                severity=ValidationSeverity.ERROR,
                message="Parts found without part_type classification",
                affected_records=parts_without_type
            ))
        
        # Check for parts without unit of measure
        parts_without_uom = db.query(Part).filter(
            Part.unit_of_measure.is_(None) | (Part.unit_of_measure == '')
        ).count()
        
        if parts_without_uom > 0:
            results.append(ValidationResult(
                check_name="parts_without_unit_of_measure",
                severity=ValidationSeverity.WARNING,
                message="Parts found without unit of measure",
                affected_records=parts_without_uom
            ))
        
        return results
    
    def _validate_warehouse_structure(self, db: Session) -> List[ValidationResult]:
        """Validate warehouse structure and relationships."""
        results = []
        
        # Check that all organizations have at least one warehouse
        orgs_without_warehouse = db.execute(text("""
            SELECT o.id, o.name
            FROM organizations o
            LEFT JOIN warehouses w ON o.id = w.organization_id
            WHERE w.id IS NULL AND o.organization_type != 'supplier'
        """)).fetchall()
        
        if orgs_without_warehouse:
            results.append(ValidationResult(
                check_name="organizations_without_warehouse",
                severity=ValidationSeverity.WARNING,
                message="Organizations without warehouses",
                affected_records=len(orgs_without_warehouse),
                details={"organizations": [{"id": str(row.id), "name": row.name} for row in orgs_without_warehouse]}
            ))
        
        # Check for warehouses without names
        warehouses_without_name = db.query(Warehouse).filter(
            Warehouse.name.is_(None) | (Warehouse.name == '')
        ).count()
        
        if warehouses_without_name > 0:
            results.append(ValidationResult(
                check_name="warehouses_without_name",
                severity=ValidationSeverity.ERROR,
                message="Warehouses found without names",
                affected_records=warehouses_without_name
            ))
        
        return results
    
    def _validate_inventory_integrity(self, db: Session) -> List[ValidationResult]:
        """Validate inventory data integrity."""
        results = []
        
        # Check for inventory records with invalid warehouse references
        orphaned_inventory = db.execute(text("""
            SELECT COUNT(*) as count
            FROM inventory i
            LEFT JOIN warehouses w ON i.warehouse_id = w.id
            WHERE w.id IS NULL
        """)).scalar()
        
        if orphaned_inventory > 0:
            results.append(ValidationResult(
                check_name="orphaned_inventory",
                severity=ValidationSeverity.ERROR,
                message="Inventory records with invalid warehouse references",
                affected_records=orphaned_inventory
            ))
        
        # Check for inventory records with invalid part references
        inventory_invalid_parts = db.execute(text("""
            SELECT COUNT(*) as count
            FROM inventory i
            LEFT JOIN parts p ON i.part_id = p.id
            WHERE p.id IS NULL
        """)).scalar()
        
        if inventory_invalid_parts > 0:
            results.append(ValidationResult(
                check_name="inventory_invalid_parts",
                severity=ValidationSeverity.ERROR,
                message="Inventory records with invalid part references",
                affected_records=inventory_invalid_parts
            ))
        
        # Check for negative inventory
        negative_inventory = db.query(Inventory).filter(
            Inventory.current_stock < 0
        ).count()
        
        if negative_inventory > 0:
            results.append(ValidationResult(
                check_name="negative_inventory",
                severity=ValidationSeverity.WARNING,
                message="Inventory records with negative stock levels",
                affected_records=negative_inventory
            ))
        
        return results
    
    def _validate_machine_relationships(self, db: Session) -> List[ValidationResult]:
        """Validate machine relationships and data."""
        results = []
        
        try:
            # Check for machines with invalid customer organization references
            machines_invalid_customer = db.execute(text("""
                SELECT COUNT(*) as count
                FROM machines m
                LEFT JOIN organizations o ON m.customer_organization_id = o.id
                WHERE o.id IS NULL
            """)).scalar()
            
            if machines_invalid_customer > 0:
                results.append(ValidationResult(
                    check_name="machines_invalid_customer",
                    severity=ValidationSeverity.ERROR,
                    message="Machines with invalid customer organization references",
                    affected_records=machines_invalid_customer
                ))
            
            # Check for machines assigned to non-customer organizations
            machines_non_customer_org = db.execute(text("""
                SELECT COUNT(*) as count
                FROM machines m
                JOIN organizations o ON m.customer_organization_id = o.id
                WHERE o.organization_type != 'customer'
            """)).scalar()
            
            if machines_non_customer_org > 0:
                results.append(ValidationResult(
                    check_name="machines_non_customer_org",
                    severity=ValidationSeverity.WARNING,
                    message="Machines assigned to non-customer organizations",
                    affected_records=machines_non_customer_org
                ))
            
        except Exception as e:
            if "does not exist" in str(e):
                # Machines table doesn't exist, which is fine
                pass
            else:
                raise
        
        return results
    
    def _validate_transaction_integrity(self, db: Session) -> List[ValidationResult]:
        """Validate transaction data integrity."""
        results = []
        
        try:
            # Check for transactions with invalid part references
            transactions_invalid_parts = db.execute(text("""
                SELECT COUNT(*) as count
                FROM transactions t
                LEFT JOIN parts p ON t.part_id = p.id
                WHERE p.id IS NULL
            """)).scalar()
            
            if transactions_invalid_parts > 0:
                results.append(ValidationResult(
                    check_name="transactions_invalid_parts",
                    severity=ValidationSeverity.ERROR,
                    message="Transactions with invalid part references",
                    affected_records=transactions_invalid_parts
                ))
            
            # Check for transactions with invalid user references
            transactions_invalid_users = db.execute(text("""
                SELECT COUNT(*) as count
                FROM transactions t
                LEFT JOIN users u ON t.performed_by_user_id = u.id
                WHERE u.id IS NULL
            """)).scalar()
            
            if transactions_invalid_users > 0:
                results.append(ValidationResult(
                    check_name="transactions_invalid_users",
                    severity=ValidationSeverity.ERROR,
                    message="Transactions with invalid user references",
                    affected_records=transactions_invalid_users
                ))
            
        except Exception as e:
            if "does not exist" in str(e):
                # Transactions table doesn't exist, which is fine
                pass
            else:
                raise
        
        return results
    
    def _validate_referential_integrity(self, db: Session) -> List[ValidationResult]:
        """Validate referential integrity across all tables."""
        results = []
        
        # Check for users with invalid organization references
        users_invalid_org = db.execute(text("""
            SELECT COUNT(*) as count
            FROM users u
            LEFT JOIN organizations o ON u.organization_id = o.id
            WHERE o.id IS NULL
        """)).scalar()
        
        if users_invalid_org > 0:
            results.append(ValidationResult(
                check_name="users_invalid_organization",
                severity=ValidationSeverity.CRITICAL,
                message="Users with invalid organization references",
                affected_records=users_invalid_org
            ))
        
        # Check for warehouses with invalid organization references
        warehouses_invalid_org = db.execute(text("""
            SELECT COUNT(*) as count
            FROM warehouses w
            LEFT JOIN organizations o ON w.organization_id = o.id
            WHERE o.id IS NULL
        """)).scalar()
        
        if warehouses_invalid_org > 0:
            results.append(ValidationResult(
                check_name="warehouses_invalid_organization",
                severity=ValidationSeverity.ERROR,
                message="Warehouses with invalid organization references",
                affected_records=warehouses_invalid_org
            ))
        
        return results
    
    def _validate_data_consistency(self, db: Session) -> List[ValidationResult]:
        """Validate data consistency across related tables."""
        results = []
        
        # Check inventory unit of measure consistency with parts
        inconsistent_uom = db.execute(text("""
            SELECT COUNT(*) as count
            FROM inventory i
            JOIN parts p ON i.part_id = p.id
            WHERE i.unit_of_measure != p.unit_of_measure
        """)).scalar()
        
        if inconsistent_uom > 0:
            results.append(ValidationResult(
                check_name="inconsistent_unit_of_measure",
                severity=ValidationSeverity.WARNING,
                message="Inventory records with unit of measure different from parts",
                affected_records=inconsistent_uom
            ))
        
        return results
    
    def _generate_report(self, results: List[ValidationResult]) -> ValidationReport:
        """Generate comprehensive validation report."""
        total_checks = len(results)
        warnings = sum(1 for r in results if r.severity == ValidationSeverity.WARNING)
        errors = sum(1 for r in results if r.severity == ValidationSeverity.ERROR)
        critical_issues = sum(1 for r in results if r.severity == ValidationSeverity.CRITICAL)
        passed_checks = total_checks - warnings - errors - critical_issues
        
        return ValidationReport(
            timestamp=datetime.now(),
            total_checks=total_checks,
            passed_checks=passed_checks,
            warnings=warnings,
            errors=errors,
            critical_issues=critical_issues,
            results=results
        )


def run_validation() -> ValidationReport:
    """Run comprehensive data validation and return report."""
    validator = DataValidator()
    db = SessionLocal()
    
    try:
        report = validator.validate_all(db)
        return report
    finally:
        db.close()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run validation
    report = run_validation()
    
    print(f"\n{report.summary}")
    print("=" * 50)
    
    for result in report.results:
        print(result)
    
    if not report.is_valid:
        print(f"\n⚠️  Validation failed with {report.errors} errors and {report.critical_issues} critical issues")
    else:
        print(f"\n✅ Validation passed with {report.warnings} warnings")