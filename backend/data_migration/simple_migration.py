#!/usr/bin/env python3
"""
Simple Data Migration Script for ABParts Business Model Realignment
Task 18: Data Migration and Seeding

This script performs the migration using direct SQL commands to avoid import issues.
"""

import os
import sys
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def get_database_url():
    """Get database URL from environment variable."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    return database_url

class SimpleMigrationManager:
    """Simple migration manager using direct SQL commands."""
    
    def __init__(self, database_url=None):
        """Initialize the migration manager with database connection."""
        self.database_url = database_url or get_database_url()
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def run_migration(self):
        """Run the complete migration process."""
        print("🚀 Starting ABParts Business Model Realignment Migration")
        print("=" * 65)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        with self.get_session() as session:
            try:
                # Step 1: Ensure default organizations exist
                self.ensure_default_organizations(session)
                
                # Step 2: Update organization countries
                self.update_organization_countries(session)
                
                # Step 3: Create default warehouses
                self.create_default_warehouses(session)
                
                # Step 4: Validate machine model types
                self.validate_machine_model_types(session)
                
                # Step 5: Create sample machine hours if needed
                self.create_sample_machine_hours(session)
                
                session.commit()
                print("\n✅ Migration completed successfully!")
                
                # Step 6: Run validation
                self.validate_migration(session)
                
                return True
                
            except Exception as e:
                session.rollback()
                print(f"\n❌ Migration failed: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
    
    def ensure_default_organizations(self, session):
        """Ensure Oraseas EE and BossAqua organizations exist."""
        print("📋 Ensuring default organizations exist...")
        
        # Check if Oraseas EE exists
        oraseas_result = session.execute(text("""
            SELECT id, name, country FROM organizations 
            WHERE organization_type = 'oraseas_ee'
        """)).fetchone()
        
        if not oraseas_result:
            print("  Creating Oraseas EE organization...")
            oraseas_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO organizations (id, name, organization_type, country, address, contact_info, is_active)
                VALUES (:id, 'Oraseas EE', 'oraseas_ee', 'GR', 
                        '123 Industrial Avenue, Athens, Greece',
                        'Phone: +30 210 1234567\\nEmail: info@oraseas.com\\nWebsite: www.oraseas.com',
                        true)
            """), {'id': oraseas_id})
            print(f"  ✅ Created Oraseas EE organization (ID: {oraseas_id})")
        else:
            print(f"  ✅ Oraseas EE already exists (ID: {oraseas_result.id})")
            # Update country if missing
            if not oraseas_result.country:
                session.execute(text("""
                    UPDATE organizations SET country = 'GR' 
                    WHERE id = :id
                """), {'id': str(oraseas_result.id)})
                print("  📝 Updated Oraseas EE country to GR")
        
        # Check if BossAqua exists
        bossaqua_result = session.execute(text("""
            SELECT id, name, country FROM organizations 
            WHERE organization_type = 'bossaqua'
        """)).fetchone()
        
        if not bossaqua_result:
            print("  Creating BossAqua organization...")
            bossaqua_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO organizations (id, name, organization_type, country, address, contact_info, is_active)
                VALUES (:id, 'BossAqua', 'bossaqua', 'GR',
                        '456 Manufacturing Street, Thessaloniki, Greece',
                        'Phone: +30 231 7654321\\nEmail: info@bossaqua.com\\nWebsite: www.bossaqua.com',
                        true)
            """), {'id': bossaqua_id})
            print(f"  ✅ Created BossAqua organization (ID: {bossaqua_id})")
        else:
            print(f"  ✅ BossAqua already exists (ID: {bossaqua_result.id})")
            # Update country if missing
            if not bossaqua_result.country:
                session.execute(text("""
                    UPDATE organizations SET country = 'GR' 
                    WHERE id = :id
                """), {'id': str(bossaqua_result.id)})
                print("  📝 Updated BossAqua country to GR")
    
    def update_organization_countries(self, session):
        """Update organization countries where missing."""
        print("🌍 Updating organization countries...")
        
        # Update organizations without countries
        result = session.execute(text("""
            UPDATE organizations 
            SET country = 'GR' 
            WHERE country IS NULL
        """))
        
        updated_count = result.rowcount
        if updated_count > 0:
            print(f"  ✅ Updated {updated_count} organizations with default country 'GR'")
        else:
            print("  ✅ All organizations already have countries assigned")
    
    def create_default_warehouses(self, session):
        """Create default warehouses for organizations that don't have them."""
        print("🏭 Creating default warehouses...")
        
        # Get organizations that need warehouses
        orgs_without_warehouses = session.execute(text("""
            SELECT o.id, o.name, o.organization_type, o.address
            FROM organizations o
            WHERE o.organization_type IN ('oraseas_ee', 'bossaqua', 'customer')
            AND NOT EXISTS (
                SELECT 1 FROM warehouses w WHERE w.organization_id = o.id
            )
        """)).fetchall()
        
        created_count = 0
        for org in orgs_without_warehouses:
            warehouse_id = str(uuid.uuid4())
            warehouse_name = f"{org.name} Main Warehouse"
            location = org.address or "Default Location"
            description = f"Default warehouse for {org.name}"
            
            session.execute(text("""
                INSERT INTO warehouses (id, organization_id, name, location, description, is_active)
                VALUES (:id, :org_id, :name, :location, :description, true)
            """), {
                'id': warehouse_id,
                'org_id': str(org.id),
                'name': warehouse_name,
                'location': location,
                'description': description
            })
            
            created_count += 1
            print(f"  ✅ Created warehouse '{warehouse_name}' for {org.name}")
        
        if created_count > 0:
            print(f"  📊 Created {created_count} default warehouses")
        else:
            print("  ✅ All organizations already have warehouses")
    
    def validate_machine_model_types(self, session):
        """Validate and fix machine model types."""
        print("🤖 Validating machine model types...")
        
        # Update invalid machine model types
        result = session.execute(text("""
            UPDATE machines 
            SET model_type = 'V4_0' 
            WHERE model_type NOT IN ('V3_1B', 'V4_0')
            OR model_type IS NULL
        """))
        
        updated_count = result.rowcount
        if updated_count > 0:
            print(f"  📝 Updated {updated_count} machines with invalid model types to 'V4_0'")
        else:
            print("  ✅ All machine model types are valid")
    
    def create_sample_machine_hours(self, session):
        """Create initial machine hours records for machines without any."""
        print("⏰ Creating initial machine hours records...")
        
        # Get superadmin user
        superadmin = session.execute(text("""
            SELECT id FROM users WHERE role = 'super_admin' LIMIT 1
        """)).fetchone()
        
        if not superadmin:
            print("  ⚠️  No superadmin user found, skipping machine hours creation")
            return
        
        # Get machines without hours records
        machines_without_hours = session.execute(text("""
            SELECT m.id, m.name
            FROM machines m
            WHERE NOT EXISTS (
                SELECT 1 FROM machine_hours mh WHERE mh.machine_id = m.id
            )
        """)).fetchall()
        
        created_count = 0
        for machine in machines_without_hours:
            hours_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO machine_hours (id, machine_id, recorded_by_user_id, hours_value, recorded_date, notes)
                VALUES (:id, :machine_id, :user_id, 0.00, NOW(), 'Initial hours record created during data migration')
            """), {
                'id': hours_id,
                'machine_id': str(machine.id),
                'user_id': str(superadmin.id)
            })
            
            created_count += 1
            print(f"  ✅ Created initial hours record for machine '{machine.name}'")
        
        if created_count > 0:
            print(f"  📊 Created {created_count} initial machine hours records")
        else:
            print("  ✅ All machines already have hours records")
    
    def validate_migration(self, session):
        """Validate the migration results."""
        print("\n🔍 Validating migration results...")
        
        validation_errors = []
        
        # Check Oraseas EE
        oraseas_count = session.execute(text("""
            SELECT COUNT(*) FROM organizations WHERE organization_type = 'oraseas_ee'
        """)).scalar()
        
        if oraseas_count != 1:
            validation_errors.append(f"Expected 1 Oraseas EE, found {oraseas_count}")
        
        # Check BossAqua
        bossaqua_count = session.execute(text("""
            SELECT COUNT(*) FROM organizations WHERE organization_type = 'bossaqua'
        """)).scalar()
        
        if bossaqua_count != 1:
            validation_errors.append(f"Expected 1 BossAqua, found {bossaqua_count}")
        
        # Check organizations without countries
        orgs_without_country = session.execute(text("""
            SELECT COUNT(*) FROM organizations WHERE country IS NULL
        """)).scalar()
        
        if orgs_without_country > 0:
            validation_errors.append(f"Found {orgs_without_country} organizations without country")
        
        # Check organizations without warehouses
        orgs_without_warehouses = session.execute(text("""
            SELECT COUNT(*) FROM organizations o
            WHERE o.organization_type IN ('oraseas_ee', 'bossaqua', 'customer')
            AND NOT EXISTS (
                SELECT 1 FROM warehouses w WHERE w.organization_id = o.id
            )
        """)).scalar()
        
        if orgs_without_warehouses > 0:
            validation_errors.append(f"Found {orgs_without_warehouses} organizations without warehouses")
        
        # Check invalid machine model types
        invalid_machines = session.execute(text("""
            SELECT COUNT(*) FROM machines 
            WHERE model_type NOT IN ('V3_1B', 'V4_0')
        """)).scalar()
        
        if invalid_machines > 0:
            validation_errors.append(f"Found {invalid_machines} machines with invalid model types")
        
        # Report results
        if validation_errors:
            print("❌ Validation failed:")
            for error in validation_errors:
                print(f"  - {error}")
            return False
        else:
            print("✅ All validation checks passed!")
            return True
    
    def get_migration_status(self):
        """Get the current migration status."""
        print("📊 Checking Migration Status")
        print("=" * 30)
        
        with self.get_session() as session:
            try:
                # Check organizations
                oraseas_count = session.execute(text("""
                    SELECT COUNT(*) FROM organizations WHERE organization_type = 'oraseas_ee'
                """)).scalar()
                
                bossaqua_count = session.execute(text("""
                    SELECT COUNT(*) FROM organizations WHERE organization_type = 'bossaqua'
                """)).scalar()
                
                # Check warehouses
                orgs_without_warehouses = session.execute(text("""
                    SELECT COUNT(*) FROM organizations o
                    WHERE o.organization_type IN ('oraseas_ee', 'bossaqua', 'customer')
                    AND NOT EXISTS (
                        SELECT 1 FROM warehouses w WHERE w.organization_id = o.id
                    )
                """)).scalar()
                
                # Check machine hours
                machine_hours_count = session.execute(text("""
                    SELECT COUNT(*) FROM machine_hours
                """)).scalar()
                
                print(f"Oraseas EE organizations: {oraseas_count}")
                print(f"BossAqua organizations: {bossaqua_count}")
                print(f"Organizations without warehouses: {orgs_without_warehouses}")
                print(f"Machine hours records: {machine_hours_count}")
                
                # Determine status
                if oraseas_count == 1 and bossaqua_count == 1 and orgs_without_warehouses == 0:
                    print("\n✅ Migration appears to be complete")
                    return True
                else:
                    print("\n⚠️  Migration appears to be incomplete")
                    return False
                    
            except Exception as e:
                print(f"❌ Could not check migration status: {str(e)}")
                return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple ABParts Migration Tool")
    parser.add_argument('--status', action='store_true', help='Check migration status')
    parser.add_argument('--migrate', action='store_true', help='Run migration')
    
    args = parser.parse_args()
    
    try:
        manager = SimpleMigrationManager()
        
        if args.status:
            success = manager.get_migration_status()
        elif args.migrate:
            success = manager.run_migration()
        else:
            # Default to status check
            success = manager.get_migration_status()
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())