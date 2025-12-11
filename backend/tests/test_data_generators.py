"""
Enhanced test data generators for large dataset testing.
Supports configurable generation of parts and related data beyond the previous 200-part limit.
"""

import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.models import (
    Organization, User, Part, Warehouse, Inventory, Machine, Transaction,
    OrganizationType, UserRole, UserStatus, PartType, TransactionType, 
    MachineStatus, MachineModelType
)
from app.auth import get_password_hash


class LargeDatasetGenerator:
    """Generator for large test datasets with configurable sizes."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.data = {
            "organizations": [],
            "users": [],
            "parts": [],
            "warehouses": [],
            "machines": [],
            "inventory": [],
            "transactions": []
        }
    
    def generate_parts_dataset(
        self, 
        parts_count: int = 1000,
        include_inventory: bool = True,
        include_transactions: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a large parts dataset with configurable size.
        
        Args:
            parts_count: Number of parts to generate (default: 1000)
            include_inventory: Whether to generate inventory records
            include_transactions: Whether to generate transaction records
            
        Returns:
            Dictionary containing generated data
        """
        # Create base organizations first
        self._create_base_organizations()
        
        # Generate parts
        self._generate_parts(parts_count)
        
        if include_inventory:
            self._generate_inventory_for_parts()
        
        if include_transactions:
            self._generate_transactions_for_parts()
        
        self.db_session.commit()
        return self.data
    
    def _create_base_organizations(self):
        """Create basic organizations needed for testing or use existing ones."""
        # Check if Oraseas EE already exists (by type since it's unique)
        oraseas = self.db_session.query(Organization).filter(
            Organization.organization_type == OrganizationType.oraseas_ee
        ).first()
        
        if not oraseas:
            # Create Oraseas EE
            oraseas = Organization(
                name="Oraseas EE",
                organization_type=OrganizationType.oraseas_ee,
                address="123 Main St, Athens, Greece",
                contact_info="info@oraseas.com"
            )
            self.db_session.add(oraseas)
            self.db_session.flush()
        
        self.data["organizations"].append(oraseas)
        
        # Check if BossAqua already exists (by type since it's unique)
        bossaqua = self.db_session.query(Organization).filter(
            Organization.organization_type == OrganizationType.bossaqua
        ).first()
        
        if not bossaqua:
            # Create BossAqua
            bossaqua = Organization(
                name="BossAqua Manufacturing",
                organization_type=OrganizationType.bossaqua,
                address="456 Factory Rd, Thessaloniki, Greece",
                contact_info="info@bossaqua.com"
            )
            self.db_session.add(bossaqua)
            self.db_session.flush()
        
        self.data["organizations"].append(bossaqua)
        
        # Use existing superadmin user
        super_admin = self.db_session.query(User).filter(
            User.username == "superadmin"
        ).first()
        
        if not super_admin:
            # Create superadmin if it doesn't exist (fallback)
            super_admin = User(
                username="superadmin",
                email="admin@oraseas.com",
                password_hash=get_password_hash("superadmin"),
                name="Super Administrator",
                role=UserRole.super_admin,
                user_status=UserStatus.active,
                organization_id=oraseas.id,
                is_active=True
            )
            self.db_session.add(super_admin)
            self.db_session.flush()
        
        self.data["users"].append(super_admin)
        
        # Check if main warehouse already exists
        main_warehouse = self.db_session.query(Warehouse).filter(
            Warehouse.name == "Oraseas Main Warehouse",
            Warehouse.organization_id == oraseas.id
        ).first()
        
        if not main_warehouse:
            # Create main warehouse
            main_warehouse = Warehouse(
                name="Oraseas Main Warehouse",
                organization_id=oraseas.id,
                location="Athens Central",
                description="Main distribution warehouse"
            )
            self.db_session.add(main_warehouse)
            self.db_session.flush()
        
        self.data["warehouses"].append(main_warehouse)
    
    def _generate_parts(self, parts_count: int):
        """Generate the specified number of parts."""
        print(f"Generating {parts_count} parts...")
        
        # Use timestamp to ensure unique part numbers across test runs
        import time
        timestamp = int(time.time() * 1000) % 1000000  # Last 6 digits of timestamp
        
        # Part name variations for realistic data
        part_categories = [
            "Filter", "Pump", "Belt", "Valve", "Sensor", "Motor", "Gasket",
            "Bearing", "Seal", "Hose", "Connector", "Switch", "Relay", "Fuse",
            "Oil", "Fluid", "Cleaner", "Lubricant", "Additive", "Chemical"
        ]
        
        part_types_list = ["Oil", "Air", "Fuel", "Water", "Hydraulic", "Pneumatic",
                          "Electric", "Mechanical", "Electronic", "Thermal"]
        
        manufacturers = ["BossAqua", "AutoParts Inc", "CleanTech", "Industrial Solutions",
                        "Premium Parts", "Quality Components", "Reliable Systems"]
        
        for i in range(1, parts_count + 1):
            # Determine part characteristics
            part_type = PartType.CONSUMABLE if i % 3 != 0 else PartType.BULK_MATERIAL
            is_proprietary = i % 7 == 0  # ~14% proprietary parts
            unit = "pieces" if part_type == PartType.CONSUMABLE else random.choice(["liters", "kg", "meters"])
            
            # Generate realistic part names
            category = random.choice(part_categories)
            type_modifier = random.choice(part_types_list)
            manufacturer = random.choice(manufacturers)
            
            if part_type == PartType.BULK_MATERIAL:
                name = f"{type_modifier} {category}"
            else:
                name = f"{manufacturer} {type_modifier} {category}"
            
            # Use timestamp prefix to ensure unique part numbers
            part_number = f"PERF-{timestamp}-{i:06d}"
            
            part = Part(
                part_number=part_number,
                name=name,
                description=f"High-quality {name.lower()} for AutoBoss machines. Part #{i}",
                part_type=part_type,
                is_proprietary=is_proprietary,
                unit_of_measure=unit,
                manufacturer_part_number=f"{manufacturer[:3].upper()}-{timestamp}-{i:06d}" if is_proprietary else None,
                manufacturer=manufacturer if is_proprietary else None
            )
            self.db_session.add(part)
            
            # Flush every 100 parts to avoid memory issues
            if i % 100 == 0:
                self.db_session.flush()
                print(f"Generated {i} parts...")
            
            self.data["parts"].append(part)
        
        self.db_session.flush()
        print(f"Completed generating {parts_count} parts")
    
    def _generate_inventory_for_parts(self):
        """Generate inventory records for all parts."""
        print("Generating inventory records...")
        
        warehouse = self.data["warehouses"][0]  # Use main warehouse
        
        for i, part in enumerate(self.data["parts"]):
            # Generate realistic stock levels
            if part.part_type == PartType.BULK_MATERIAL:
                current_stock = Decimal(str(random.randint(100, 2000)))
                min_stock = Decimal(str(random.randint(20, 200)))
            else:
                current_stock = Decimal(str(random.randint(10, 500)))
                min_stock = Decimal(str(random.randint(5, 50)))
            
            inventory = Inventory(
                warehouse_id=warehouse.id,
                part_id=part.id,
                current_stock=current_stock,
                minimum_stock_recommendation=min_stock,
                unit_of_measure=part.unit_of_measure
            )
            self.db_session.add(inventory)
            self.data["inventory"].append(inventory)
            
            # Flush every 100 inventory records
            if (i + 1) % 100 == 0:
                self.db_session.flush()
                print(f"Generated inventory for {i + 1} parts...")
        
        self.db_session.flush()
        print(f"Completed generating inventory for {len(self.data['parts'])} parts")
    
    def _generate_transactions_for_parts(self):
        """Generate transaction records for parts."""
        print("Generating transaction records...")
        
        user = self.data["users"][0]  # Use super admin
        warehouse = self.data["warehouses"][0]  # Use main warehouse
        
        # Generate transactions for a subset of parts to simulate realistic usage
        transaction_count = min(1000, len(self.data["parts"]) * 2)  # 2 transactions per part max
        
        for i in range(transaction_count):
            part = random.choice(self.data["parts"])
            
            # Create mostly CREATION transactions for initial stock
            transaction_type = TransactionType.CREATION if i < transaction_count * 0.7 else random.choice([
                TransactionType.ADJUSTMENT, TransactionType.TRANSFER
            ])
            
            quantity = Decimal(str(random.randint(1, 100)))
            
            transaction = Transaction(
                transaction_type=transaction_type.value,  # Use enum value (string)
                part_id=part.id,
                to_warehouse_id=warehouse.id if transaction_type == TransactionType.CREATION else None,
                from_warehouse_id=warehouse.id if transaction_type != TransactionType.CREATION else None,
                quantity=quantity,
                unit_of_measure=part.unit_of_measure,
                performed_by_user_id=user.id,
                transaction_date=datetime.utcnow() - timedelta(days=random.randint(0, 365)),
                notes=f"Test transaction for {part.name}"
            )
            self.db_session.add(transaction)
            self.data["transactions"].append(transaction)
            
            # Flush every 100 transactions
            if (i + 1) % 100 == 0:
                self.db_session.flush()
                print(f"Generated {i + 1} transactions...")
        
        self.db_session.flush()
        print(f"Completed generating {transaction_count} transactions")


def generate_large_parts_dataset(
    db_session: Session,
    parts_count: int = 1000,
    include_inventory: bool = True,
    include_transactions: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to generate large parts dataset.
    
    Args:
        db_session: Database session
        parts_count: Number of parts to generate
        include_inventory: Whether to generate inventory records
        include_transactions: Whether to generate transaction records
        
    Returns:
        Dictionary containing generated data
    """
    generator = LargeDatasetGenerator(db_session)
    return generator.generate_parts_dataset(
        parts_count=parts_count,
        include_inventory=include_inventory,
        include_transactions=include_transactions
    )


def generate_performance_test_scenarios(db_session: Session) -> Dict[str, Dict[str, Any]]:
    """
    Generate multiple test scenarios with different dataset sizes.
    
    Returns:
        Dictionary with scenario names as keys and dataset info as values
    """
    scenarios = {}
    
    # Scenario 1: 1,000 parts
    print("Creating 1,000 parts scenario...")
    generator_1k = LargeDatasetGenerator(db_session)
    data_1k = generator_1k.generate_parts_dataset(parts_count=1000)
    scenarios["1k_parts"] = {
        "parts_count": len(data_1k["parts"]),
        "inventory_count": len(data_1k["inventory"]),
        "transactions_count": len(data_1k["transactions"]),
        "data": data_1k
    }
    
    # Clear session for next scenario
    db_session.rollback()
    
    # Scenario 2: 5,000 parts
    print("Creating 5,000 parts scenario...")
    generator_5k = LargeDatasetGenerator(db_session)
    data_5k = generator_5k.generate_parts_dataset(parts_count=5000)
    scenarios["5k_parts"] = {
        "parts_count": len(data_5k["parts"]),
        "inventory_count": len(data_5k["inventory"]),
        "transactions_count": len(data_5k["transactions"]),
        "data": data_5k
    }
    
    # Clear session for next scenario
    db_session.rollback()
    
    # Scenario 3: 10,000 parts
    print("Creating 10,000 parts scenario...")
    generator_10k = LargeDatasetGenerator(db_session)
    data_10k = generator_10k.generate_parts_dataset(parts_count=10000)
    scenarios["10k_parts"] = {
        "parts_count": len(data_10k["parts"]),
        "inventory_count": len(data_10k["inventory"]),
        "transactions_count": len(data_10k["transactions"]),
        "data": data_10k
    }
    
    return scenarios