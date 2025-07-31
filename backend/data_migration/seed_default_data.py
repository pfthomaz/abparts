#!/usr/bin/env python3
"""
Default Data Seeding Script for ABParts Business Model Realignment
Task 18: Data Migration and Seeding

This script seeds the database with default organizations and warehouses
required by the business model.
"""

import os
import sys
import uuid
from datetime import datetime
from sqlalchemy import create_engine
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
        Warehouse, Part, PartType
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

class DefaultDataSeeder:
    """Seeds the database with default organizations and warehouses."""
    
    def __init__(self, database_url=None):
        """Initialize the seeder with database connection."""
        self.database_url = database_url or get_database_url()
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def seed_all(self):
        """Seed all default data."""
        print("🌱 Seeding default data for ABParts Business Model...")
        print("=" * 55)
        
        with self.get_session() as session:
            try:
                # 1. Seed default organizations
                oraseas_ee, bossaqua = self.seed_default_organizations(session)
                
                # 2. Seed default warehouses
                self.seed_default_warehouses(session, oraseas_ee, bossaqua)
                
                # 3. Seed sample parts if needed
                self.seed_sample_parts(session)
                
                session.commit()
                print("\n✅ Default data seeding completed successfully!")
                
            except Exception as e:
                session.rollback()
                print(f"\n❌ Seeding failed: {str(e)}")
                raise
    
    def seed_default_organizations(self, session):
        """Seed the default Oraseas EE and BossAqua organizations."""
        print("🏢 Seeding default organizations...")
        
        # 1. Seed Oraseas EE
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
                address="123 Industrial Avenue, Athens, Greece",
                contact_info="Phone: +30 210 1234567\nEmail: info@oraseas.com\nWebsite: www.oraseas.com",
                is_active=True
            )
            session.add(oraseas_ee)
            session.flush()  # Get the ID
            print(f"  ✅ Created Oraseas EE organization (ID: {oraseas_ee.id})")
        else:
            print(f"  ✅ Oraseas EE already exists (ID: {oraseas_ee.id})")
            # Update fields if they're missing
            if not oraseas_ee.country:
                oraseas_ee.country = "GR"
                print("    📝 Updated country to GR")
            if not oraseas_ee.address:
                oraseas_ee.address = "123 Industrial Avenue, Athens, Greece"
                print("    📝 Updated address")
            if not oraseas_ee.contact_info:
                oraseas_ee.contact_info = "Phone: +30 210 1234567\nEmail: info@oraseas.com\nWebsite: www.oraseas.com"
                print("    📝 Updated contact info")
        
        # 2. Seed BossAqua
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
                address="456 Manufacturing Street, Thessaloniki, Greece",
                contact_info="Phone: +30 231 7654321\nEmail: info@bossaqua.com\nWebsite: www.bossaqua.com",
                is_active=True
            )
            session.add(bossaqua)
            session.flush()
            print(f"  ✅ Created BossAqua organization (ID: {bossaqua.id})")
        else:
            print(f"  ✅ BossAqua already exists (ID: {bossaqua.id})")
            # Update fields if they're missing
            if not bossaqua.country:
                bossaqua.country = "GR"
                print("    📝 Updated country to GR")
            if not bossaqua.address:
                bossaqua.address = "456 Manufacturing Street, Thessaloniki, Greece"
                print("    📝 Updated address")
            if not bossaqua.contact_info:
                bossaqua.contact_info = "Phone: +30 231 7654321\nEmail: info@bossaqua.com\nWebsite: www.bossaqua.com"
                print("    📝 Updated contact info")
        
        return oraseas_ee, bossaqua
    
    def seed_default_warehouses(self, session, oraseas_ee, bossaqua):
        """Seed default warehouses for Oraseas EE and BossAqua."""
        print("🏭 Seeding default warehouses...")
        
        # Default warehouses configuration
        default_warehouses = [
            {
                'organization': oraseas_ee,
                'name': 'Main Warehouse',
                'location': 'Athens Distribution Center, Greece',
                'description': 'Primary distribution warehouse for Oraseas EE operations'
            },
            {
                'organization': oraseas_ee,
                'name': 'Spare Parts Warehouse',
                'location': 'Athens Service Center, Greece',
                'description': 'Dedicated warehouse for spare parts and service components'
            },
            {
                'organization': bossaqua,
                'name': 'Main Warehouse',
                'location': 'Thessaloniki Manufacturing Facility, Greece',
                'description': 'Primary warehouse for BossAqua manufactured parts and machines'
            },
            {
                'organization': bossaqua,
                'name': 'Quality Control Warehouse',
                'location': 'Thessaloniki QC Facility, Greece',
                'description': 'Warehouse for quality control and testing of manufactured parts'
            }
        ]
        
        created_count = 0
        for warehouse_config in default_warehouses:
            org = warehouse_config['organization']
            
            # Check if warehouse already exists
            existing_warehouse = session.query(Warehouse).filter(
                Warehouse.organization_id == org.id,
                Warehouse.name == warehouse_config['name']
            ).first()
            
            if not existing_warehouse:
                warehouse = Warehouse(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    name=warehouse_config['name'],
                    location=warehouse_config['location'],
                    description=warehouse_config['description'],
                    is_active=True
                )
                session.add(warehouse)
                created_count += 1
                print(f"  ✅ Created '{warehouse.name}' for {org.name}")
            else:
                print(f"  ✅ '{warehouse_config['name']}' already exists for {org.name}")
                # Update description if missing
                if not existing_warehouse.description:
                    existing_warehouse.description = warehouse_config['description']
                    print(f"    📝 Updated description for '{existing_warehouse.name}'")
        
        # Create default warehouses for existing customer organizations
        customer_orgs = session.query(Organization).filter(
            Organization.organization_type == OrganizationType.customer
        ).all()
        
        for customer_org in customer_orgs:
            # Check if customer already has a warehouse
            existing_warehouse = session.query(Warehouse).filter(
                Warehouse.organization_id == customer_org.id
            ).first()
            
            if not existing_warehouse:
                warehouse = Warehouse(
                    id=uuid.uuid4(),
                    organization_id=customer_org.id,
                    name=f"{customer_org.name} Main Warehouse",
                    location=customer_org.address or "Customer Location",
                    description=f"Default warehouse for {customer_org.name}",
                    is_active=True
                )
                session.add(warehouse)
                created_count += 1
                print(f"  ✅ Created default warehouse for customer '{customer_org.name}'")
            else:
                print(f"  ✅ Customer '{customer_org.name}' already has warehouse: {existing_warehouse.name}")
        
        if created_count > 0:
            print(f"  📊 Created {created_count} new warehouses")
        else:
            print("  📊 All required warehouses already exist")
    
    def seed_sample_parts(self, session):
        """Seed sample parts if the parts table is empty."""
        print("🔧 Checking for sample parts...")
        
        parts_count = session.query(Part).count()
        
        if parts_count == 0:
            print("  Creating sample parts...")
            
            sample_parts = [
                {
                    'part_number': 'AB-FILTER-001',
                    'name': 'AutoBoss Water Filter - Standard',
                    'description': 'Standard water filter for AutoBoss V3.1B and V4.0 machines',
                    'part_type': PartType.CONSUMABLE,
                    'is_proprietary': True,
                    'unit_of_measure': 'pieces',
                    'manufacturer': 'BossAqua',
                    'part_code': 'WF-STD-001'
                },
                {
                    'part_number': 'AB-SOAP-001',
                    'name': 'AutoBoss Cleaning Solution - Premium',
                    'description': 'Premium cleaning solution for AutoBoss machines',
                    'part_type': PartType.BULK_MATERIAL,
                    'is_proprietary': True,
                    'unit_of_measure': 'liters',
                    'manufacturer': 'BossAqua',
                    'part_code': 'CS-PREM-001'
                },
                {
                    'part_number': 'GEN-HOSE-001',
                    'name': 'High Pressure Hose - 10m',
                    'description': 'Generic high pressure hose compatible with AutoBoss machines',
                    'part_type': PartType.CONSUMABLE,
                    'is_proprietary': False,
                    'unit_of_measure': 'pieces',
                    'manufacturer': 'Generic Supplier',
                    'part_code': 'HPH-10M-001'
                },
                {
                    'part_number': 'AB-PUMP-001',
                    'name': 'AutoBoss Water Pump Assembly',
                    'description': 'Water pump assembly for AutoBoss V4.0 machines',
                    'part_type': PartType.CONSUMABLE,
                    'is_proprietary': True,
                    'unit_of_measure': 'pieces',
                    'manufacturer': 'BossAqua',
                    'part_code': 'WPA-V40-001'
                },
                {
                    'part_number': 'GEN-DETERGENT-001',
                    'name': 'Biodegradable Car Detergent',
                    'description': 'Eco-friendly car detergent suitable for AutoBoss machines',
                    'part_type': PartType.BULK_MATERIAL,
                    'is_proprietary': False,
                    'unit_of_measure': 'liters',
                    'manufacturer': 'EcoClean Solutions',
                    'part_code': 'BCD-ECO-001'
                }
            ]
            
            created_count = 0
            for part_config in sample_parts:
                part = Part(
                    id=uuid.uuid4(),
                    **part_config
                )
                session.add(part)
                created_count += 1
                print(f"    ✅ Created part '{part.part_number}' - {part.name}")
            
            print(f"  📊 Created {created_count} sample parts")
        else:
            print(f"  ✅ Parts table already contains {parts_count} parts")
    
    def verify_seeded_data(self):
        """Verify that all required default data has been seeded correctly."""
        print("\n🔍 Verifying seeded data...")
        
        with self.get_session() as session:
            verification_results = []
            
            # Check Oraseas EE
            oraseas_ee = session.query(Organization).filter(
                Organization.organization_type == OrganizationType.oraseas_ee
            ).first()
            
            if oraseas_ee:
                verification_results.append("✅ Oraseas EE organization exists")
                
                # Check Oraseas EE warehouses
                oraseas_warehouses = session.query(Warehouse).filter(
                    Warehouse.organization_id == oraseas_ee.id
                ).count()
                verification_results.append(f"✅ Oraseas EE has {oraseas_warehouses} warehouses")
            else:
                verification_results.append("❌ Oraseas EE organization missing")
            
            # Check BossAqua
            bossaqua = session.query(Organization).filter(
                Organization.organization_type == OrganizationType.bossaqua
            ).first()
            
            if bossaqua:
                verification_results.append("✅ BossAqua organization exists")
                
                # Check BossAqua warehouses
                bossaqua_warehouses = session.query(Warehouse).filter(
                    Warehouse.organization_id == bossaqua.id
                ).count()
                verification_results.append(f"✅ BossAqua has {bossaqua_warehouses} warehouses")
            else:
                verification_results.append("❌ BossAqua organization missing")
            
            # Check customer organizations have warehouses
            customers_without_warehouses = session.execute("""
                SELECT COUNT(*) FROM organizations o
                WHERE o.organization_type = 'customer'
                AND NOT EXISTS (
                    SELECT 1 FROM warehouses w WHERE w.organization_id = o.id
                )
            """).scalar()
            
            if customers_without_warehouses == 0:
                verification_results.append("✅ All customer organizations have warehouses")
            else:
                verification_results.append(f"⚠️  {customers_without_warehouses} customers without warehouses")
            
            # Check parts
            parts_count = session.query(Part).count()
            verification_results.append(f"📊 Database contains {parts_count} parts")
            
            # Print results
            for result in verification_results:
                print(f"  {result}")
            
            return all("❌" not in result for result in verification_results)


def main():
    """Main function to run the default data seeding."""
    print("ABParts Default Data Seeding Tool")
    print("=" * 40)
    
    try:
        seeder = DefaultDataSeeder()
        
        # Run the seeding
        seeder.seed_all()
        
        # Verify the results
        if seeder.verify_seeded_data():
            print("\n🎉 Default data seeding completed successfully!")
            return 0
        else:
            print("\n⚠️  Seeding completed but with verification warnings.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Seeding failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())