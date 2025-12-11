#!/usr/bin/env python3
"""
Data Migration Script for ABParts Business Model Realignment
Task 18: Data Migration and Seeding

This script migrates existing data to comply with the new business model schema
and ensures all required default organizations and warehouses are created.
"""

import os
import sys
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Add the app directory to the path so we can import models
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, '..', 'app')
sys.path.insert(0, app_dir)

try:
    import models
    from models import (
        Organization, OrganizationType, User, UserRole, UserStatus,
        Warehouse, Part, PartType, Machine, MachineModelType, MachineStatus,
        Inventory, MachineHours
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

class DataMigrationManager:
    """Manages data migration and seeding operations."""
    
    def __init__(self, database_url=None):
        """Initialize the migration manager with database connection."""
        self.database_url = database_url or get_database_url()
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def migrate_existing_data(self):
        """Main migration function that orchestrates all migration tasks."""
        print("Starting data migration for ABParts Business Model Realignment...")
        
        with self.get_session() as session:
            try:
                # 1. Ensure default organizations exist
                self.ensure_default_organizations(session)
                
                # 2. Update organization countries where missing
                self.update_organization_countries(session)
                
                # 3. Create default warehouses for customer organizations
                self.create_default_warehouses(session)
                
                # 4. Validate and fix machine model types
                self.validate_machine_model_types(session)
                
                # 5. Validate parts data compliance
                self.validate_parts_data(session)
                
                # 6. Create sample machine hours data if needed
                self.create_sample_machine_hours(session)
                
                session.commit()
                print("✅ Data migration completed successfully!")
                
            except Exception as e:
                session.rollback()
                print(f"❌ Migration failed: {str(e)}")
                raise
    
    def ensure_default_organizations(self, session):
        """Ensure Oraseas EE and BossAqua organizations exist."""
        print("📋 Ensuring default organizations exist...")
        
        # Check if Oraseas EE exists
        oraseas_ee = session.query(Organization).filter(
            Organization.organization_type == OrganizationType.oraseas_ee
        ).first()
        
        if not oraseas_ee:
            print("  Creating Oraseas EE organization...")
            oraseas_ee = Organization(
                id=uuid.uuid4(),
                name="Oraseas EE",
                organization_type=OrganizationType.oraseas_ee,
                country="GR",
                address="Athens, Greece",
                contact_info="info@oraseas.com",
                is_active=True
            )
            session.add(oraseas_ee)
            session.flush()  # Get the ID
            print(f"  ✅ Created Oraseas EE organization (ID: {oraseas_ee.id})")
        else:
            print(f"  ✅ Oraseas EE already exists (ID: {oraseas_ee.id})")
            # Update country if missing
            if not oraseas_ee.country:
                oraseas_ee.country = "GR"
                print("  📝 Updated Oraseas EE country to GR")
        
        # Check if BossAqua exists
        bossaqua = session.query(Organization).filter(
            Organization.organization_type == OrganizationType.bossaqua
        ).first()
        
        if not bossaqua:
            print("  Creating BossAqua organization...")
            bossaqua = Organization(
                id=uuid.uuid4(),
                name="BossAqua",
                organization_type=OrganizationType.bossaqua,
                country="GR",
                address="Thessaloniki, Greece",
                contact_info="info@bossaqua.com",
                is_active=True
            )
            session.add(bossaqua)
            session.flush()
            print(f"  ✅ Created BossAqua organization (ID: {bossaqua.id})")
        else:
            print(f"  ✅ BossAqua already exists (ID: {bossaqua.id})")
            # Update country if missing
            if not bossaqua.country:
                bossaqua.country = "GR"
                print("  📝 Updated BossAqua country to GR")
        
        return oraseas_ee, bossaqua
    
    def update_organization_countries(self, session):
        """Update organization countries where missing."""
        print("🌍 Updating organization countries...")
        
        # Default country mappings based on organization names or types
        country_mappings = {
            'oraseas_ee': 'GR',
            'bossaqua': 'GR',
            'customer': 'GR',  # Default for customers
            'supplier': 'GR'   # Default for suppliers
        }
        
        organizations = session.query(Organization).filter(
            Organization.country.is_(None)
        ).all()
        
        updated_count = 0
        for org in organizations:
            # Assign country based on organization type or name
            if org.organization_type.value in country_mappings:
                org.country = country_mappings[org.organization_type.value]
                updated_count += 1
                print(f"  📝 Updated {org.name} country to {org.country}")
        
        if updated_count > 0:
            print(f"  ✅ Updated {updated_count} organizations with default countries")
        else:
            print("  ✅ All organizations already have countries assigned")
    
    def create_default_warehouses(self, session):
        """Create default warehouses for organizations that don't have them."""
        print("🏭 Creating default warehouses...")
        
        # Get all organizations that should have warehouses
        organizations = session.query(Organization).filter(
            Organization.organization_type.in_([
                OrganizationType.oraseas_ee,
                OrganizationType.bossaqua,
                OrganizationType.customer
            ])
        ).all()
        
        created_count = 0
        for org in organizations:
            # Check if organization already has a warehouse
            existing_warehouse = session.query(Warehouse).filter(
                Warehouse.organization_id == org.id
            ).first()
            
            if not existing_warehouse:
                # Create default warehouse with organization name
                warehouse = Warehouse(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    name=f"{org.name} Main Warehouse",
                    location=org.address or "Default Location",
                    description=f"Default warehouse for {org.name}",
                    is_active=True
                )
                session.add(warehouse)
                created_count += 1
                print(f"  ✅ Created warehouse '{warehouse.name}' for {org.name}")
            else:
                print(f"  ✅ {org.name} already has warehouse: {existing_warehouse.name}")
        
        if created_count > 0:
            print(f"  ✅ Created {created_count} default warehouses")
        else:
            print("  ✅ All organizations already have warehouses")
    
    def validate_machine_model_types(self, session):
        """Validate and fix machine model types to comply with enum constraints."""
        print("🤖 Validating machine model types...")
        
        machines = session.query(Machine).all()
        updated_count = 0
        
        for machine in machines:
            # Check if model_type is valid
            try:
                # Try to convert to enum to validate
                if hasattr(machine, 'model_type') and machine.model_type:
                    if machine.model_type not in ['V3.1B', 'V4.0']:
                        # Default to V4.0 for invalid model types
                        old_type = machine.model_type
                        machine.model_type = 'V4.0'
                        updated_count += 1
                        print(f"  📝 Updated machine {machine.name} model type from '{old_type}' to 'V4.0'")
                else:
                    # Set default model type if missing
                    machine.model_type = 'V4.0'
                    updated_count += 1
                    print(f"  📝 Set default model type 'V4.0' for machine {machine.name}")
            except Exception as e:
                print(f"  ⚠️  Warning: Could not validate machine {machine.name}: {str(e)}")
        
        if updated_count > 0:
            print(f"  ✅ Updated {updated_count} machine model types")
        else:
            print("  ✅ All machine model types are valid")
    
    def validate_parts_data(self, session):
        """Validate parts data for schema compliance."""
        print("🔧 Validating parts data...")
        
        parts = session.query(Part).all()
        updated_count = 0
        
        for part in parts:
            # Ensure part_type is valid
            if not hasattr(part, 'part_type') or not part.part_type:
                part.part_type = PartType.CONSUMABLE  # Default to consumable
                updated_count += 1
                print(f"  📝 Set default part type 'CONSUMABLE' for part {part.part_number}")
            
            # Ensure unit_of_measure is set
            if not part.unit_of_measure:
                part.unit_of_measure = 'pieces'
                updated_count += 1
                print(f"  📝 Set default unit 'pieces' for part {part.part_number}")
            
            # Validate image_urls array (ensure it's not more than 4 images)
            if part.image_urls and len(part.image_urls) > 4:
                part.image_urls = part.image_urls[:4]  # Keep only first 4
                updated_count += 1
                print(f"  📝 Trimmed image URLs to 4 for part {part.part_number}")
        
        if updated_count > 0:
            print(f"  ✅ Updated {updated_count} parts for schema compliance")
        else:
            print("  ✅ All parts data is compliant")
    
    def create_sample_machine_hours(self, session):
        """Create sample machine hours data for existing machines if none exist."""
        print("⏰ Creating sample machine hours data...")
        
        machines = session.query(Machine).all()
        created_count = 0
        
        # Get a superadmin user to record the hours
        superadmin = session.query(User).filter(
            User.role == UserRole.super_admin
        ).first()
        
        if not superadmin:
            print("  ⚠️  No superadmin user found, skipping machine hours creation")
            return
        
        for machine in machines:
            # Check if machine already has hours recorded
            existing_hours = session.query(MachineHours).filter(
                MachineHours.machine_id == machine.id
            ).first()
            
            if not existing_hours:
                # Create initial hours record
                machine_hours = MachineHours(
                    id=uuid.uuid4(),
                    machine_id=machine.id,
                    recorded_by_user_id=superadmin.id,
                    hours_value=Decimal('0.00'),
                    recorded_date=datetime.now(),
                    notes="Initial hours record created during data migration"
                )
                session.add(machine_hours)
                created_count += 1
                print(f"  ✅ Created initial hours record for machine {machine.name}")
            else:
                print(f"  ✅ Machine {machine.name} already has hours records")
        
        if created_count > 0:
            print(f"  ✅ Created {created_count} initial machine hours records")
        else:
            print("  ✅ All machines already have hours records")
    
    def validate_schema_compliance(self):
        """Run comprehensive validation checks on the migrated data."""
        print("🔍 Running schema compliance validation...")
        
        with self.get_session() as session:
            validation_errors = []
            
            # 1. Check organization constraints
            print("  Validating organization constraints...")
            
            # Check unique Oraseas EE
            oraseas_count = session.query(Organization).filter(
                Organization.organization_type == OrganizationType.oraseas_ee
            ).count()
            if oraseas_count != 1:
                validation_errors.append(f"Expected 1 Oraseas EE organization, found {oraseas_count}")
            
            # Check unique BossAqua
            bossaqua_count = session.query(Organization).filter(
                Organization.organization_type == OrganizationType.bossaqua
            ).count()
            if bossaqua_count != 1:
                validation_errors.append(f"Expected 1 BossAqua organization, found {bossaqua_count}")
            
            # Check supplier parent relationships
            suppliers_without_parent = session.query(Organization).filter(
                Organization.organization_type == OrganizationType.supplier,
                Organization.parent_organization_id.is_(None)
            ).count()
            if suppliers_without_parent > 0:
                validation_errors.append(f"Found {suppliers_without_parent} suppliers without parent organizations")
            
            # 2. Check country constraints
            print("  Validating country constraints...")
            orgs_without_country = session.query(Organization).filter(
                Organization.country.is_(None)
            ).count()
            if orgs_without_country > 0:
                validation_errors.append(f"Found {orgs_without_country} organizations without country")
            
            # Check valid countries
            invalid_countries = session.execute(text("""
                SELECT COUNT(*) FROM organizations 
                WHERE country NOT IN ('GR', 'KSA', 'ES', 'CY', 'OM')
                AND country IS NOT NULL
            """)).scalar()
            if invalid_countries > 0:
                validation_errors.append(f"Found {invalid_countries} organizations with invalid countries")
            
            # 3. Check machine model types
            print("  Validating machine model types...")
            invalid_models = session.execute(text("""
                SELECT COUNT(*) FROM machines 
                WHERE model_type NOT IN ('V3.1B', 'V4.0')
            """)).scalar()
            if invalid_models > 0:
                validation_errors.append(f"Found {invalid_models} machines with invalid model types")
            
            # 4. Check warehouse requirements
            print("  Validating warehouse requirements...")
            orgs_without_warehouses = session.execute(text("""
                SELECT COUNT(*) FROM organizations o
                WHERE o.organization_type IN ('oraseas_ee', 'bossaqua', 'customer')
                AND NOT EXISTS (
                    SELECT 1 FROM warehouses w WHERE w.organization_id = o.id
                )
            """)).scalar()
            if orgs_without_warehouses > 0:
                validation_errors.append(f"Found {orgs_without_warehouses} organizations without warehouses")
            
            # 5. Check superadmin constraints
            print("  Validating superadmin constraints...")
            superadmins_outside_oraseas = session.execute(text("""
                SELECT COUNT(*) FROM users u
                JOIN organizations o ON u.organization_id = o.id
                WHERE u.role = 'super_admin' AND o.organization_type != 'oraseas_ee'
            """)).scalar()
            if superadmins_outside_oraseas > 0:
                validation_errors.append(f"Found {superadmins_outside_oraseas} superadmins outside Oraseas EE")
            
            # Report validation results
            if validation_errors:
                print("❌ Schema compliance validation failed:")
                for error in validation_errors:
                    print(f"  - {error}")
                return False
            else:
                print("✅ Schema compliance validation passed!")
                return True


def main():
    """Main function to run the data migration."""
    print("ABParts Data Migration and Seeding Tool")
    print("=" * 50)
    
    try:
        # Initialize migration manager
        migration_manager = DataMigrationManager()
        
        # Run the migration
        migration_manager.migrate_existing_data()
        
        # Validate the results
        if migration_manager.validate_schema_compliance():
            print("\n🎉 Migration completed successfully with full schema compliance!")
            return 0
        else:
            print("\n⚠️  Migration completed but with validation warnings.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Migration failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())