#!/usr/bin/env python3
"""
Schema Compliance Validation Script for ABParts Business Model Realignment
Task 18: Data Migration and Seeding

This script validates that all data in the database complies with the new business model schema.
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path so we can import models
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, '..', 'app')
sys.path.insert(0, app_dir)

try:
    import models
    from models import (
        Organization, OrganizationType, User, UserRole, UserStatus,
        Warehouse, Part, PartType, Machine, MachineModelType, MachineStatus
    )
except ImportError as e:
    print(f"Error importing models: {e}")
    print(f"Current directory: {current_dir}")
    print(f"App directory: {app_dir}")
    print("Make sure you're running this script from the correct directory")
    sys.exit(1)

def get_database_url():
    """Get database URL from environment variable."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    return database_url

class SchemaComplianceValidator:
    """Validates database schema compliance for business model realignment."""
    
    def __init__(self, database_url=None):
        """Initialize the validator with database connection."""
        self.database_url = database_url or get_database_url()
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.validation_results = []
        
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def add_result(self, category, check_name, status, message, details=None):
        """Add a validation result."""
        self.validation_results.append({
            'category': category,
            'check_name': check_name,
            'status': status,  # 'PASS', 'FAIL', 'WARNING'
            'message': message,
            'details': details or [],
            'timestamp': datetime.now()
        })
    
    def validate_all(self):
        """Run all validation checks."""
        print("🔍 Running comprehensive schema compliance validation...")
        print("=" * 60)
        
        with self.get_session() as session:
            # Organization validations
            self.validate_organizations(session)
            
            # User validations
            self.validate_users(session)
            
            # Warehouse validations
            self.validate_warehouses(session)
            
            # Machine validations
            self.validate_machines(session)
            
            # Parts validations
            self.validate_parts(session)
            
            # Business rule validations
            self.validate_business_rules(session)
            
            # Data integrity validations
            self.validate_data_integrity(session)
        
        # Generate report
        self.generate_report()
        
        return self.get_overall_status()
    
    def validate_organizations(self, session):
        """Validate organization-related constraints."""
        print("📋 Validating Organizations...")
        
        # 1. Check unique Oraseas EE organization
        oraseas_count = session.query(Organization).filter(
            Organization.organization_type == OrganizationType.oraseas_ee
        ).count()
        
        if oraseas_count == 1:
            self.add_result('Organizations', 'Unique Oraseas EE', 'PASS', 
                          'Exactly one Oraseas EE organization exists')
        elif oraseas_count == 0:
            self.add_result('Organizations', 'Unique Oraseas EE', 'FAIL', 
                          'No Oraseas EE organization found')
        else:
            self.add_result('Organizations', 'Unique Oraseas EE', 'FAIL', 
                          f'Multiple Oraseas EE organizations found: {oraseas_count}')
        
        # 2. Check unique BossAqua organization
        bossaqua_count = session.query(Organization).filter(
            Organization.organization_type == OrganizationType.bossaqua
        ).count()
        
        if bossaqua_count == 1:
            self.add_result('Organizations', 'Unique BossAqua', 'PASS', 
                          'Exactly one BossAqua organization exists')
        elif bossaqua_count == 0:
            self.add_result('Organizations', 'Unique BossAqua', 'FAIL', 
                          'No BossAqua organization found')
        else:
            self.add_result('Organizations', 'Unique BossAqua', 'FAIL', 
                          f'Multiple BossAqua organizations found: {bossaqua_count}')
        
        # 3. Check supplier parent relationships
        suppliers_without_parent = session.query(Organization).filter(
            Organization.organization_type == OrganizationType.supplier,
            Organization.parent_organization_id.is_(None)
        ).all()
        
        if not suppliers_without_parent:
            self.add_result('Organizations', 'Supplier Parent Relationships', 'PASS', 
                          'All suppliers have parent organizations')
        else:
            details = [f"Supplier '{org.name}' (ID: {org.id}) has no parent" 
                      for org in suppliers_without_parent]
            self.add_result('Organizations', 'Supplier Parent Relationships', 'FAIL', 
                          f'{len(suppliers_without_parent)} suppliers without parent organizations',
                          details)
        
        # 4. Check country constraints
        orgs_without_country = session.query(Organization).filter(
            Organization.country.is_(None)
        ).all()
        
        if not orgs_without_country:
            self.add_result('Organizations', 'Country Assignment', 'PASS', 
                          'All organizations have countries assigned')
        else:
            details = [f"Organization '{org.name}' (ID: {org.id}) has no country" 
                      for org in orgs_without_country]
            self.add_result('Organizations', 'Country Assignment', 'FAIL', 
                          f'{len(orgs_without_country)} organizations without country',
                          details)
        
        # 5. Check valid country values
        invalid_countries = session.execute(text("""
            SELECT name, country FROM organizations 
            WHERE country NOT IN ('GR', 'KSA', 'ES', 'CY', 'OM')
            AND country IS NOT NULL
        """)).fetchall()
        
        if not invalid_countries:
            self.add_result('Organizations', 'Valid Countries', 'PASS', 
                          'All organizations have valid country codes')
        else:
            details = [f"Organization '{row.name}' has invalid country '{row.country}'" 
                      for row in invalid_countries]
            self.add_result('Organizations', 'Valid Countries', 'FAIL', 
                          f'{len(invalid_countries)} organizations with invalid countries',
                          details)
    
    def validate_users(self, session):
        """Validate user-related constraints."""
        print("👥 Validating Users...")
        
        # 1. Check superadmin constraints (must be in Oraseas EE)
        superadmins_outside_oraseas = session.execute(text("""
            SELECT u.username, o.name as org_name, o.organization_type
            FROM users u
            JOIN organizations o ON u.organization_id = o.id
            WHERE u.role = 'super_admin' AND o.organization_type != 'oraseas_ee'
        """)).fetchall()
        
        if not superadmins_outside_oraseas:
            self.add_result('Users', 'Superadmin Organization', 'PASS', 
                          'All superadmins belong to Oraseas EE')
        else:
            details = [f"Superadmin '{row.username}' belongs to '{row.org_name}' ({row.organization_type})" 
                      for row in superadmins_outside_oraseas]
            self.add_result('Users', 'Superadmin Organization', 'FAIL', 
                          f'{len(superadmins_outside_oraseas)} superadmins outside Oraseas EE',
                          details)
        
        # 2. Check user status validity
        users_with_invalid_status = session.execute(text("""
            SELECT username, user_status FROM users 
            WHERE user_status NOT IN ('active', 'inactive', 'pending_invitation', 'locked')
        """)).fetchall()
        
        if not users_with_invalid_status:
            self.add_result('Users', 'Valid User Status', 'PASS', 
                          'All users have valid status values')
        else:
            details = [f"User '{row.username}' has invalid status '{row.user_status}'" 
                      for row in users_with_invalid_status]
            self.add_result('Users', 'Valid User Status', 'FAIL', 
                          f'{len(users_with_invalid_status)} users with invalid status',
                          details)
        
        # 3. Check role validity
        users_with_invalid_role = session.execute(text("""
            SELECT username, role FROM users 
            WHERE role NOT IN ('user', 'admin', 'super_admin')
        """)).fetchall()
        
        if not users_with_invalid_role:
            self.add_result('Users', 'Valid User Roles', 'PASS', 
                          'All users have valid role values')
        else:
            details = [f"User '{row.username}' has invalid role '{row.role}'" 
                      for row in users_with_invalid_role]
            self.add_result('Users', 'Valid User Roles', 'FAIL', 
                          f'{len(users_with_invalid_role)} users with invalid roles',
                          details)
    
    def validate_warehouses(self, session):
        """Validate warehouse-related constraints."""
        print("🏭 Validating Warehouses...")
        
        # 1. Check that all required organizations have warehouses
        orgs_without_warehouses = session.execute(text("""
            SELECT o.name, o.organization_type
            FROM organizations o
            WHERE o.organization_type IN ('oraseas_ee', 'bossaqua', 'customer')
            AND NOT EXISTS (
                SELECT 1 FROM warehouses w WHERE w.organization_id = o.id
            )
        """)).fetchall()
        
        if not orgs_without_warehouses:
            self.add_result('Warehouses', 'Required Warehouses', 'PASS', 
                          'All required organizations have warehouses')
        else:
            details = [f"Organization '{row.name}' ({row.organization_type}) has no warehouses" 
                      for row in orgs_without_warehouses]
            self.add_result('Warehouses', 'Required Warehouses', 'FAIL', 
                          f'{len(orgs_without_warehouses)} organizations without warehouses',
                          details)
        
        # 2. Check warehouse name uniqueness within organizations
        duplicate_warehouse_names = session.execute(text("""
            SELECT organization_id, name, COUNT(*) as count
            FROM warehouses
            GROUP BY organization_id, name
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        if not duplicate_warehouse_names:
            self.add_result('Warehouses', 'Unique Names', 'PASS', 
                          'All warehouse names are unique within organizations')
        else:
            details = [f"Organization {row.organization_id} has {row.count} warehouses named '{row.name}'" 
                      for row in duplicate_warehouse_names]
            self.add_result('Warehouses', 'Unique Names', 'FAIL', 
                          f'{len(duplicate_warehouse_names)} duplicate warehouse names found',
                          details)
    
    def validate_machines(self, session):
        """Validate machine-related constraints."""
        print("🤖 Validating Machines...")
        
        # 1. Check machine model types
        invalid_model_types = session.execute(text("""
            SELECT name, serial_number, model_type
            FROM machines 
            WHERE model_type NOT IN ('V3.1B', 'V4.0')
        """)).fetchall()
        
        if not invalid_model_types:
            self.add_result('Machines', 'Valid Model Types', 'PASS', 
                          'All machines have valid model types')
        else:
            details = [f"Machine '{row.name}' ({row.serial_number}) has invalid model type '{row.model_type}'" 
                      for row in invalid_model_types]
            self.add_result('Machines', 'Valid Model Types', 'FAIL', 
                          f'{len(invalid_model_types)} machines with invalid model types',
                          details)
        
        # 2. Check serial number uniqueness
        duplicate_serial_numbers = session.execute(text("""
            SELECT serial_number, COUNT(*) as count
            FROM machines
            GROUP BY serial_number
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        if not duplicate_serial_numbers:
            self.add_result('Machines', 'Unique Serial Numbers', 'PASS', 
                          'All machine serial numbers are unique')
        else:
            details = [f"Serial number '{row.serial_number}' is used by {row.count} machines" 
                      for row in duplicate_serial_numbers]
            self.add_result('Machines', 'Unique Serial Numbers', 'FAIL', 
                          f'{len(duplicate_serial_numbers)} duplicate serial numbers found',
                          details)
        
        # 3. Check machine ownership (should belong to customer organizations)
        machines_invalid_ownership = session.execute(text("""
            SELECT m.name, m.serial_number, o.name as org_name, o.organization_type
            FROM machines m
            JOIN organizations o ON m.customer_organization_id = o.id
            WHERE o.organization_type NOT IN ('customer', 'oraseas_ee')
        """)).fetchall()
        
        if not machines_invalid_ownership:
            self.add_result('Machines', 'Valid Ownership', 'PASS', 
                          'All machines belong to valid organizations')
        else:
            details = [f"Machine '{row.name}' ({row.serial_number}) belongs to '{row.org_name}' ({row.organization_type})" 
                      for row in machines_invalid_ownership]
            self.add_result('Machines', 'Valid Ownership', 'WARNING', 
                          f'{len(machines_invalid_ownership)} machines with unusual ownership',
                          details)
    
    def validate_parts(self, session):
        """Validate parts-related constraints."""
        print("🔧 Validating Parts...")
        
        # 1. Check part type validity
        invalid_part_types = session.execute(text("""
            SELECT part_number, name, part_type
            FROM parts 
            WHERE part_type NOT IN ('consumable', 'bulk_material')
        """)).fetchall()
        
        if not invalid_part_types:
            self.add_result('Parts', 'Valid Part Types', 'PASS', 
                          'All parts have valid part types')
        else:
            details = [f"Part '{row.part_number}' ({row.name}) has invalid type '{row.part_type}'" 
                      for row in invalid_part_types]
            self.add_result('Parts', 'Valid Part Types', 'FAIL', 
                          f'{len(invalid_part_types)} parts with invalid types',
                          details)
        
        # 2. Check part number uniqueness
        duplicate_part_numbers = session.execute(text("""
            SELECT part_number, COUNT(*) as count
            FROM parts
            GROUP BY part_number
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        if not duplicate_part_numbers:
            self.add_result('Parts', 'Unique Part Numbers', 'PASS', 
                          'All part numbers are unique')
        else:
            details = [f"Part number '{row.part_number}' is used by {row.count} parts" 
                      for row in duplicate_part_numbers]
            self.add_result('Parts', 'Unique Part Numbers', 'FAIL', 
                          f'{len(duplicate_part_numbers)} duplicate part numbers found',
                          details)
        
        # 3. Check image URL limits (max 4 images)
        parts_too_many_images = session.execute(text("""
            SELECT part_number, name, array_length(image_urls, 1) as image_count
            FROM parts 
            WHERE array_length(image_urls, 1) > 4
        """)).fetchall()
        
        if not parts_too_many_images:
            self.add_result('Parts', 'Image URL Limits', 'PASS', 
                          'All parts have 4 or fewer images')
        else:
            details = [f"Part '{row.part_number}' ({row.name}) has {row.image_count} images" 
                      for row in parts_too_many_images]
            self.add_result('Parts', 'Image URL Limits', 'FAIL', 
                          f'{len(parts_too_many_images)} parts exceed 4 image limit',
                          details)
    
    def validate_business_rules(self, session):
        """Validate business rule constraints."""
        print("📊 Validating Business Rules...")
        
        # 1. Check that suppliers have valid parent organizations
        suppliers_invalid_parents = session.execute(text("""
            SELECT s.name as supplier_name, p.name as parent_name, p.organization_type
            FROM organizations s
            LEFT JOIN organizations p ON s.parent_organization_id = p.id
            WHERE s.organization_type = 'supplier'
            AND (p.id IS NULL OR p.organization_type NOT IN ('customer', 'oraseas_ee'))
        """)).fetchall()
        
        if not suppliers_invalid_parents:
            self.add_result('Business Rules', 'Supplier Parent Validity', 'PASS', 
                          'All suppliers have valid parent organizations')
        else:
            details = [f"Supplier '{row.supplier_name}' has invalid parent '{row.parent_name}' ({row.organization_type})" 
                      for row in suppliers_invalid_parents]
            self.add_result('Business Rules', 'Supplier Parent Validity', 'FAIL', 
                          f'{len(suppliers_invalid_parents)} suppliers with invalid parents',
                          details)
        
        # 2. Check inventory consistency
        negative_inventory = session.execute(text("""
            SELECT w.name as warehouse_name, p.part_number, i.current_stock
            FROM inventory i
            JOIN warehouses w ON i.warehouse_id = w.id
            JOIN parts p ON i.part_id = p.id
            WHERE i.current_stock < 0
        """)).fetchall()
        
        if not negative_inventory:
            self.add_result('Business Rules', 'Non-negative Inventory', 'PASS', 
                          'All inventory levels are non-negative')
        else:
            details = [f"Warehouse '{row.warehouse_name}' has negative stock for part '{row.part_number}': {row.current_stock}" 
                      for row in negative_inventory]
            self.add_result('Business Rules', 'Non-negative Inventory', 'WARNING', 
                          f'{len(negative_inventory)} negative inventory levels found',
                          details)
    
    def validate_data_integrity(self, session):
        """Validate data integrity constraints."""
        print("🔗 Validating Data Integrity...")
        
        # 1. Check for orphaned records
        orphaned_warehouses = session.execute(text("""
            SELECT w.name, w.organization_id
            FROM warehouses w
            LEFT JOIN organizations o ON w.organization_id = o.id
            WHERE o.id IS NULL
        """)).fetchall()
        
        if not orphaned_warehouses:
            self.add_result('Data Integrity', 'Orphaned Warehouses', 'PASS', 
                          'No orphaned warehouses found')
        else:
            details = [f"Warehouse '{row.name}' references non-existent organization {row.organization_id}" 
                      for row in orphaned_warehouses]
            self.add_result('Data Integrity', 'Orphaned Warehouses', 'FAIL', 
                          f'{len(orphaned_warehouses)} orphaned warehouses found',
                          details)
        
        # 2. Check for orphaned users
        orphaned_users = session.execute(text("""
            SELECT u.username, u.organization_id
            FROM users u
            LEFT JOIN organizations o ON u.organization_id = o.id
            WHERE o.id IS NULL
        """)).fetchall()
        
        if not orphaned_users:
            self.add_result('Data Integrity', 'Orphaned Users', 'PASS', 
                          'No orphaned users found')
        else:
            details = [f"User '{row.username}' references non-existent organization {row.organization_id}" 
                      for row in orphaned_users]
            self.add_result('Data Integrity', 'Orphaned Users', 'FAIL', 
                          f'{len(orphaned_users)} orphaned users found',
                          details)
        
        # 3. Check for orphaned machines
        orphaned_machines = session.execute(text("""
            SELECT m.name, m.customer_organization_id
            FROM machines m
            LEFT JOIN organizations o ON m.customer_organization_id = o.id
            WHERE o.id IS NULL
        """)).fetchall()
        
        if not orphaned_machines:
            self.add_result('Data Integrity', 'Orphaned Machines', 'PASS', 
                          'No orphaned machines found')
        else:
            details = [f"Machine '{row.name}' references non-existent organization {row.customer_organization_id}" 
                      for row in orphaned_machines]
            self.add_result('Data Integrity', 'Orphaned Machines', 'FAIL', 
                          f'{len(orphaned_machines)} orphaned machines found',
                          details)
    
    def generate_report(self):
        """Generate a comprehensive validation report."""
        print("\n" + "=" * 60)
        print("📊 SCHEMA COMPLIANCE VALIDATION REPORT")
        print("=" * 60)
        
        # Count results by status
        pass_count = sum(1 for r in self.validation_results if r['status'] == 'PASS')
        fail_count = sum(1 for r in self.validation_results if r['status'] == 'FAIL')
        warning_count = sum(1 for r in self.validation_results if r['status'] == 'WARNING')
        total_count = len(self.validation_results)
        
        print(f"Total Checks: {total_count}")
        print(f"✅ Passed: {pass_count}")
        print(f"⚠️  Warnings: {warning_count}")
        print(f"❌ Failed: {fail_count}")
        print()
        
        # Group results by category
        categories = {}
        for result in self.validation_results:
            category = result['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Print detailed results
        for category, results in categories.items():
            print(f"📋 {category}")
            print("-" * 40)
            
            for result in results:
                status_icon = {
                    'PASS': '✅',
                    'FAIL': '❌',
                    'WARNING': '⚠️ '
                }[result['status']]
                
                print(f"  {status_icon} {result['check_name']}: {result['message']}")
                
                if result['details']:
                    for detail in result['details'][:5]:  # Show max 5 details
                        print(f"    • {detail}")
                    if len(result['details']) > 5:
                        print(f"    • ... and {len(result['details']) - 5} more")
            print()
    
    def get_overall_status(self):
        """Get the overall validation status."""
        has_failures = any(r['status'] == 'FAIL' for r in self.validation_results)
        has_warnings = any(r['status'] == 'WARNING' for r in self.validation_results)
        
        if has_failures:
            return 'FAIL'
        elif has_warnings:
            return 'WARNING'
        else:
            return 'PASS'


def main():
    """Main function to run schema compliance validation."""
    print("ABParts Schema Compliance Validation Tool")
    print("=" * 50)
    
    try:
        validator = SchemaComplianceValidator()
        overall_status = validator.validate_all()
        
        if overall_status == 'PASS':
            print("\n🎉 All validation checks passed!")
            return 0
        elif overall_status == 'WARNING':
            print("\n⚠️  Validation completed with warnings.")
            return 1
        else:
            print("\n❌ Validation failed. Please address the issues above.")
            return 2
            
    except Exception as e:
        print(f"\n💥 Validation failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    exit(main())