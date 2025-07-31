#!/usr/bin/env python3
"""
Final Validation Script for ABParts Business Model Realignment
Task 18: Data Migration and Seeding

This script performs comprehensive validation to ensure all migration requirements are met.
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def get_database_url():
    """Get database URL from environment variable."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    return database_url

class FinalValidator:
    """Comprehensive validator for migration completion."""
    
    def __init__(self, database_url=None):
        """Initialize the validator with database connection."""
        self.database_url = database_url or get_database_url()
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.results = []
        
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def add_result(self, category, test_name, status, message, details=None):
        """Add a validation result."""
        self.results.append({
            'category': category,
            'test_name': test_name,
            'status': status,  # 'PASS', 'FAIL', 'WARNING'
            'message': message,
            'details': details or [],
            'timestamp': datetime.now()
        })
    
    def run_comprehensive_validation(self):
        """Run all validation tests."""
        print("🔍 Running Comprehensive Migration Validation")
        print("=" * 55)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        with self.get_session() as session:
            # Test 1: Default Organizations
            self.test_default_organizations(session)
            
            # Test 2: Organization Countries
            self.test_organization_countries(session)
            
            # Test 3: Warehouse Requirements
            self.test_warehouse_requirements(session)
            
            # Test 4: Machine Model Types
            self.test_machine_model_types(session)
            
            # Test 5: Machine Hours Records
            self.test_machine_hours_records(session)
            
            # Test 6: Business Rules
            self.test_business_rules(session)
            
            # Test 7: Data Integrity
            self.test_data_integrity(session)
            
            # Test 8: Schema Constraints
            self.test_schema_constraints(session)
        
        # Generate final report
        return self.generate_final_report()
    
    def test_default_organizations(self, session):
        """Test that default organizations exist and are properly configured."""
        print("🏢 Testing Default Organizations...")
        
        # Test Oraseas EE
        oraseas = session.execute(text("""
            SELECT id, name, organization_type, country, address, contact_info, is_active
            FROM organizations 
            WHERE organization_type = 'oraseas_ee'
        """)).fetchone()
        
        if oraseas:
            if oraseas.country == 'GR' and oraseas.is_active:
                self.add_result('Organizations', 'Oraseas EE Configuration', 'PASS',
                              'Oraseas EE exists and is properly configured')
            else:
                self.add_result('Organizations', 'Oraseas EE Configuration', 'FAIL',
                              f'Oraseas EE configuration issues: country={oraseas.country}, active={oraseas.is_active}')
        else:
            self.add_result('Organizations', 'Oraseas EE Configuration', 'FAIL',
                          'Oraseas EE organization not found')
        
        # Test BossAqua
        bossaqua = session.execute(text("""
            SELECT id, name, organization_type, country, address, contact_info, is_active
            FROM organizations 
            WHERE organization_type = 'bossaqua'
        """)).fetchone()
        
        if bossaqua:
            if bossaqua.country == 'GR' and bossaqua.is_active:
                self.add_result('Organizations', 'BossAqua Configuration', 'PASS',
                              'BossAqua exists and is properly configured')
            else:
                self.add_result('Organizations', 'BossAqua Configuration', 'FAIL',
                              f'BossAqua configuration issues: country={bossaqua.country}, active={bossaqua.is_active}')
        else:
            self.add_result('Organizations', 'BossAqua Configuration', 'FAIL',
                          'BossAqua organization not found')
        
        # Test uniqueness
        org_counts = session.execute(text("""
            SELECT organization_type, COUNT(*) as count
            FROM organizations 
            WHERE organization_type IN ('oraseas_ee', 'bossaqua')
            GROUP BY organization_type
        """)).fetchall()
        
        for org_count in org_counts:
            if org_count.count == 1:
                self.add_result('Organizations', f'{org_count.organization_type.title()} Uniqueness', 'PASS',
                              f'Exactly one {org_count.organization_type} organization exists')
            else:
                self.add_result('Organizations', f'{org_count.organization_type.title()} Uniqueness', 'FAIL',
                              f'Found {org_count.count} {org_count.organization_type} organizations')
    
    def test_organization_countries(self, session):
        """Test that all organizations have valid countries."""
        print("🌍 Testing Organization Countries...")
        
        # Test for missing countries
        orgs_without_country = session.execute(text("""
            SELECT COUNT(*) FROM organizations WHERE country IS NULL
        """)).scalar()
        
        if orgs_without_country == 0:
            self.add_result('Countries', 'Country Assignment', 'PASS',
                          'All organizations have countries assigned')
        else:
            self.add_result('Countries', 'Country Assignment', 'FAIL',
                          f'{orgs_without_country} organizations without countries')
        
        # Test for valid country values
        invalid_countries = session.execute(text("""
            SELECT name, country FROM organizations 
            WHERE country NOT IN ('GR', 'KSA', 'ES', 'CY', 'OM')
            AND country IS NOT NULL
        """)).fetchall()
        
        if not invalid_countries:
            self.add_result('Countries', 'Valid Country Codes', 'PASS',
                          'All organizations have valid country codes')
        else:
            details = [f"{row.name}: {row.country}" for row in invalid_countries]
            self.add_result('Countries', 'Valid Country Codes', 'FAIL',
                          f'{len(invalid_countries)} organizations with invalid countries',
                          details)
    
    def test_warehouse_requirements(self, session):
        """Test that all required organizations have warehouses."""
        print("🏭 Testing Warehouse Requirements...")
        
        # Test organizations without warehouses
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
            details = [f"{row.name} ({row.organization_type})" for row in orgs_without_warehouses]
            self.add_result('Warehouses', 'Required Warehouses', 'FAIL',
                          f'{len(orgs_without_warehouses)} organizations without warehouses',
                          details)
        
        # Test warehouse counts for default organizations
        warehouse_counts = session.execute(text("""
            SELECT o.name, o.organization_type, COUNT(w.id) as warehouse_count
            FROM organizations o
            LEFT JOIN warehouses w ON o.id = w.organization_id
            WHERE o.organization_type IN ('oraseas_ee', 'bossaqua')
            GROUP BY o.id, o.name, o.organization_type
        """)).fetchall()
        
        for org in warehouse_counts:
            if org.warehouse_count > 0:
                self.add_result('Warehouses', f'{org.name} Warehouses', 'PASS',
                              f'{org.name} has {org.warehouse_count} warehouses')
            else:
                self.add_result('Warehouses', f'{org.name} Warehouses', 'FAIL',
                              f'{org.name} has no warehouses')
    
    def test_machine_model_types(self, session):
        """Test that all machines have valid model types."""
        print("🤖 Testing Machine Model Types...")
        
        # Test for invalid model types
        invalid_machines = session.execute(text("""
            SELECT name, serial_number, model_type
            FROM machines 
            WHERE model_type NOT IN ('V3_1B', 'V4_0')
            OR model_type IS NULL
        """)).fetchall()
        
        if not invalid_machines:
            self.add_result('Machines', 'Valid Model Types', 'PASS',
                          'All machines have valid model types')
        else:
            details = [f"{row.name} ({row.serial_number}): {row.model_type}" for row in invalid_machines]
            self.add_result('Machines', 'Valid Model Types', 'FAIL',
                          f'{len(invalid_machines)} machines with invalid model types',
                          details)
        
        # Test model type distribution
        model_distribution = session.execute(text("""
            SELECT model_type, COUNT(*) as count
            FROM machines
            GROUP BY model_type
        """)).fetchall()
        
        for model in model_distribution:
            self.add_result('Machines', f'Model {model.model_type} Count', 'PASS',
                          f'{model.count} machines with model type {model.model_type}')
    
    def test_machine_hours_records(self, session):
        """Test that all machines have hours records."""
        print("⏰ Testing Machine Hours Records...")
        
        # Test machines without hours records
        machines_without_hours = session.execute(text("""
            SELECT m.name, m.serial_number
            FROM machines m
            WHERE NOT EXISTS (
                SELECT 1 FROM machine_hours mh WHERE mh.machine_id = m.id
            )
        """)).fetchall()
        
        if not machines_without_hours:
            self.add_result('Machine Hours', 'Hours Records Coverage', 'PASS',
                          'All machines have hours records')
        else:
            details = [f"{row.name} ({row.serial_number})" for row in machines_without_hours]
            self.add_result('Machine Hours', 'Hours Records Coverage', 'FAIL',
                          f'{len(machines_without_hours)} machines without hours records',
                          details)
        
        # Test total hours records
        total_hours_records = session.execute(text("""
            SELECT COUNT(*) FROM machine_hours
        """)).scalar()
        
        total_machines = session.execute(text("""
            SELECT COUNT(*) FROM machines
        """)).scalar()
        
        self.add_result('Machine Hours', 'Total Records', 'PASS',
                      f'{total_hours_records} hours records for {total_machines} machines')
    
    def test_business_rules(self, session):
        """Test business rule compliance."""
        print("📊 Testing Business Rules...")
        
        # Test supplier parent relationships
        suppliers_without_parents = session.execute(text("""
            SELECT name FROM organizations 
            WHERE organization_type = 'supplier' 
            AND parent_organization_id IS NULL
        """)).fetchall()
        
        if not suppliers_without_parents:
            self.add_result('Business Rules', 'Supplier Parents', 'PASS',
                          'All suppliers have parent organizations')
        else:
            details = [row.name for row in suppliers_without_parents]
            self.add_result('Business Rules', 'Supplier Parents', 'FAIL',
                          f'{len(suppliers_without_parents)} suppliers without parents',
                          details)
        
        # Test superadmin organization constraint
        superadmins_outside_oraseas = session.execute(text("""
            SELECT u.username, o.name as org_name
            FROM users u
            JOIN organizations o ON u.organization_id = o.id
            WHERE u.role = 'super_admin' AND o.organization_type != 'oraseas_ee'
        """)).fetchall()
        
        if not superadmins_outside_oraseas:
            self.add_result('Business Rules', 'Superadmin Organization', 'PASS',
                          'All superadmins belong to Oraseas EE')
        else:
            details = [f"{row.username} in {row.org_name}" for row in superadmins_outside_oraseas]
            self.add_result('Business Rules', 'Superadmin Organization', 'FAIL',
                          f'{len(superadmins_outside_oraseas)} superadmins outside Oraseas EE',
                          details)
    
    def test_data_integrity(self, session):
        """Test data integrity constraints."""
        print("🔗 Testing Data Integrity...")
        
        # Test for orphaned warehouses
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
            details = [f"{row.name} (org: {row.organization_id})" for row in orphaned_warehouses]
            self.add_result('Data Integrity', 'Orphaned Warehouses', 'FAIL',
                          f'{len(orphaned_warehouses)} orphaned warehouses',
                          details)
        
        # Test for orphaned users
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
            details = [f"{row.username} (org: {row.organization_id})" for row in orphaned_users]
            self.add_result('Data Integrity', 'Orphaned Users', 'FAIL',
                          f'{len(orphaned_users)} orphaned users',
                          details)
    
    def test_schema_constraints(self, session):
        """Test database schema constraints."""
        print("🗄️  Testing Schema Constraints...")
        
        # Test unique constraints
        try:
            # Test organization name uniqueness
            duplicate_org_names = session.execute(text("""
                SELECT name, COUNT(*) as count
                FROM organizations
                GROUP BY name
                HAVING COUNT(*) > 1
            """)).fetchall()
            
            if not duplicate_org_names:
                self.add_result('Schema', 'Organization Name Uniqueness', 'PASS',
                              'All organization names are unique')
            else:
                details = [f"{row.name}: {row.count} duplicates" for row in duplicate_org_names]
                self.add_result('Schema', 'Organization Name Uniqueness', 'FAIL',
                              f'{len(duplicate_org_names)} duplicate organization names',
                              details)
            
            # Test machine serial number uniqueness
            duplicate_serials = session.execute(text("""
                SELECT serial_number, COUNT(*) as count
                FROM machines
                GROUP BY serial_number
                HAVING COUNT(*) > 1
            """)).fetchall()
            
            if not duplicate_serials:
                self.add_result('Schema', 'Machine Serial Uniqueness', 'PASS',
                              'All machine serial numbers are unique')
            else:
                details = [f"{row.serial_number}: {row.count} duplicates" for row in duplicate_serials]
                self.add_result('Schema', 'Machine Serial Uniqueness', 'FAIL',
                              f'{len(duplicate_serials)} duplicate serial numbers',
                              details)
            
        except Exception as e:
            self.add_result('Schema', 'Constraint Testing', 'WARNING',
                          f'Could not test all constraints: {str(e)}')
    
    def generate_final_report(self):
        """Generate the final validation report."""
        print("\n" + "=" * 65)
        print("📊 FINAL MIGRATION VALIDATION REPORT")
        print("=" * 65)
        
        # Count results by status
        pass_count = sum(1 for r in self.results if r['status'] == 'PASS')
        fail_count = sum(1 for r in self.results if r['status'] == 'FAIL')
        warning_count = sum(1 for r in self.results if r['status'] == 'WARNING')
        total_count = len(self.results)
        
        print(f"Validation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total tests run: {total_count}")
        print(f"✅ Passed: {pass_count}")
        print(f"⚠️  Warnings: {warning_count}")
        print(f"❌ Failed: {fail_count}")
        print()
        
        # Calculate success rate
        success_rate = (pass_count / total_count * 100) if total_count > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        print()
        
        # Group results by category
        categories = {}
        for result in self.results:
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
                
                print(f"  {status_icon} {result['test_name']}: {result['message']}")
                
                if result['details']:
                    for detail in result['details'][:3]:  # Show max 3 details
                        print(f"    • {detail}")
                    if len(result['details']) > 3:
                        print(f"    • ... and {len(result['details']) - 3} more")
            print()
        
        # Overall status
        if fail_count == 0:
            if warning_count == 0:
                print("🎉 MIGRATION VALIDATION: COMPLETE SUCCESS!")
                print("All requirements have been met and the migration is fully compliant.")
                overall_status = 'SUCCESS'
            else:
                print("✅ MIGRATION VALIDATION: SUCCESS WITH WARNINGS")
                print("Migration requirements are met but some warnings were noted.")
                overall_status = 'SUCCESS_WITH_WARNINGS'
        else:
            print("❌ MIGRATION VALIDATION: FAILED")
            print("Some migration requirements are not met. Please address the failures above.")
            overall_status = 'FAILED'
        
        print(f"\nOverall Status: {overall_status}")
        print("=" * 65)
        
        return overall_status


def main():
    """Main function."""
    print("ABParts Final Migration Validation Tool")
    print("=" * 45)
    
    try:
        validator = FinalValidator()
        overall_status = validator.run_comprehensive_validation()
        
        if overall_status == 'SUCCESS':
            return 0
        elif overall_status == 'SUCCESS_WITH_WARNINGS':
            return 1
        else:
            return 2
            
    except Exception as e:
        print(f"\n💥 Validation failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    exit(main())