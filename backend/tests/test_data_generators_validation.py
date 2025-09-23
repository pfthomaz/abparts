"""
Validation tests for large dataset generators.
Ensures the new test data generation functions work correctly with large datasets.
"""

import pytest
from sqlalchemy.orm import Session
from app.models import Part, Inventory, Transaction, PartType


@pytest.mark.large_dataset
class TestDataGeneratorsValidation:
    """Test the large dataset generators."""
    
    def test_generate_1k_parts_dataset(self, db_session: Session):
        """Test generating 1,000 parts dataset."""
        from .test_data_generators import generate_large_parts_dataset
        
        data = generate_large_parts_dataset(
            db_session, 
            parts_count=1000,
            include_inventory=True,
            include_transactions=True
        )
        
        # Verify parts were created
        assert len(data["parts"]) == 1000
        assert len(data["organizations"]) >= 2  # Oraseas + BossAqua
        assert len(data["users"]) >= 1  # Super admin
        assert len(data["warehouses"]) >= 1  # Main warehouse
        
        # Verify inventory was created
        assert len(data["inventory"]) == 1000  # One inventory per part
        
        # Verify transactions were created
        assert len(data["transactions"]) > 0
        
        # Verify database records
        parts_count = db_session.query(Part).count()
        assert parts_count == 1000
        
        inventory_count = db_session.query(Inventory).count()
        assert inventory_count == 1000
        
        transaction_count = db_session.query(Transaction).count()
        assert transaction_count > 0
    
    def test_generate_parts_with_different_types(self, db_session: Session):
        """Test that generated parts have different types and characteristics."""
        from .test_data_generators import generate_large_parts_dataset
        
        data = generate_large_parts_dataset(
            db_session, 
            parts_count=500,
            include_inventory=False,
            include_transactions=False
        )
        
        parts = data["parts"]
        
        # Check part type distribution
        consumable_parts = [p for p in parts if p.part_type == PartType.CONSUMABLE]
        bulk_parts = [p for p in parts if p.part_type == PartType.BULK_MATERIAL]
        
        assert len(consumable_parts) > 0
        assert len(bulk_parts) > 0
        
        # Check proprietary parts
        proprietary_parts = [p for p in parts if p.is_proprietary]
        non_proprietary_parts = [p for p in parts if not p.is_proprietary]
        
        assert len(proprietary_parts) > 0
        assert len(non_proprietary_parts) > 0
        
        # Check part numbers are unique
        part_numbers = [p.part_number for p in parts]
        assert len(set(part_numbers)) == len(part_numbers)
        
        # Check part numbers follow expected format
        for part in parts:
            assert part.part_number.startswith("P-")
            assert len(part.part_number) == 8  # P-XXXXXX format
    
    def test_generate_5k_parts_performance(self, db_session: Session):
        """Test generating 5,000 parts for performance validation."""
        import time
        from .test_data_generators import generate_large_parts_dataset
        
        start_time = time.time()
        
        data = generate_large_parts_dataset(
            db_session, 
            parts_count=5000,
            include_inventory=True,
            include_transactions=False  # Skip transactions for faster generation
        )
        
        generation_time = time.time() - start_time
        
        # Verify data was created
        assert len(data["parts"]) == 5000
        assert len(data["inventory"]) == 5000
        
        # Verify generation time is reasonable (should be under 60 seconds)
        assert generation_time < 60, f"Generation took {generation_time:.2f} seconds, exceeding 60 second threshold"
        
        print(f"Generated 5,000 parts with inventory in {generation_time:.2f} seconds")
    
    def test_large_dataset_generator_class(self, db_session: Session):
        """Test the LargeDatasetGenerator class directly."""
        from .test_data_generators import LargeDatasetGenerator
        
        generator = LargeDatasetGenerator(db_session)
        
        # Test generating parts only
        data = generator.generate_parts_dataset(
            parts_count=100,
            include_inventory=False,
            include_transactions=False
        )
        
        assert len(data["parts"]) == 100
        assert len(data["organizations"]) >= 2
        assert len(data["users"]) >= 1
        assert len(data["warehouses"]) >= 1
        assert len(data["inventory"]) == 0  # Should be empty
        assert len(data["transactions"]) == 0  # Should be empty
    
    def test_configurable_dataset_sizes(self, db_session: Session):
        """Test that dataset generation works with different sizes."""
        from .test_data_generators import generate_large_parts_dataset
        
        test_sizes = [100, 250, 500, 1000]
        
        for size in test_sizes:
            # Clear previous data
            db_session.rollback()
            
            data = generate_large_parts_dataset(
                db_session, 
                parts_count=size,
                include_inventory=True,
                include_transactions=False
            )
            
            assert len(data["parts"]) == size
            assert len(data["inventory"]) == size
            
            # Verify database records
            parts_count = db_session.query(Part).count()
            assert parts_count == size
            
            print(f"Successfully generated {size} parts")
    
    def test_realistic_part_data(self, db_session: Session):
        """Test that generated parts have realistic data."""
        from .test_data_generators import generate_large_parts_dataset
        
        data = generate_large_parts_dataset(
            db_session, 
            parts_count=100,
            include_inventory=False,
            include_transactions=False
        )
        
        parts = data["parts"]
        
        # Check that parts have realistic names
        part_names = [p.name for p in parts]
        
        # Should have variety in names
        unique_names = set(part_names)
        assert len(unique_names) > 50  # At least 50% unique names
        
        # Check descriptions are present and meaningful
        for part in parts:
            assert part.description is not None
            assert len(part.description) > 10
            assert "AutoBoss" in part.description
        
        # Check units of measure are appropriate
        for part in parts:
            if part.part_type == PartType.CONSUMABLE:
                assert part.unit_of_measure == "pieces"
            else:  # BULK_MATERIAL
                assert part.unit_of_measure in ["liters", "kg", "meters"]
        
        # Check proprietary parts have manufacturer info
        proprietary_parts = [p for p in parts if p.is_proprietary]
        for part in proprietary_parts:
            assert part.manufacturer_part_number is not None
            assert part.manufacturer is not None