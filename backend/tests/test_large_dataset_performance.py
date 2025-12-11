"""
Performance tests for large parts datasets.
Tests system performance with 1,000, 5,000, and 10,000+ parts to ensure scalability.
"""

import pytest
import time
from typing import Dict, Any
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models import Part, PartType
from .test_data_generators import generate_performance_test_scenarios


@pytest.mark.large_dataset
@pytest.mark.performance
@pytest.mark.slow
class TestLargeDatasetPerformance:
    """Test performance with large parts datasets."""
    
    def test_parts_api_performance_1k_parts(self, client: TestClient, auth_headers, large_parts_dataset_1k):
        """Test parts API performance with 1,000 parts."""
        headers = auth_headers["super_admin"]
        
        # Test GET /parts endpoint
        start_time = time.time()
        response = client.get("/parts?limit=100", headers=headers)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 2.0, f"Parts API with 1k parts took {duration:.4f} seconds, exceeding 2.0 second threshold"
        
        data = response.json()
        assert len(data) <= 100  # Pagination working
        
        # Test search functionality
        start_time = time.time()
        response = client.get("/parts?search=Filter&limit=50", headers=headers)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 2.0, f"Parts search with 1k parts took {duration:.4f} seconds, exceeding 2.0 second threshold"
    
    def test_parts_api_performance_5k_parts(self, client: TestClient, auth_headers, large_parts_dataset_5k):
        """Test parts API performance with 5,000 parts."""
        headers = auth_headers["super_admin"]
        
        # Test GET /parts endpoint
        start_time = time.time()
        response = client.get("/parts?limit=100", headers=headers)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 3.0, f"Parts API with 5k parts took {duration:.4f} seconds, exceeding 3.0 second threshold"
        
        # Test filtering by type
        start_time = time.time()
        response = client.get("/parts?part_type=CONSUMABLE&limit=100", headers=headers)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 3.0, f"Parts filtering with 5k parts took {duration:.4f} seconds, exceeding 3.0 second threshold"
    
    def test_parts_api_performance_10k_parts(self, client: TestClient, auth_headers, large_parts_dataset_10k):
        """Test parts API performance with 10,000+ parts."""
        headers = auth_headers["super_admin"]
        
        # Test GET /parts endpoint
        start_time = time.time()
        response = client.get("/parts?limit=100", headers=headers)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 5.0, f"Parts API with 10k parts took {duration:.4f} seconds, exceeding 5.0 second threshold"
        
        # Test proprietary parts filtering
        start_time = time.time()
        response = client.get("/parts?is_proprietary=true&limit=50", headers=headers)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 5.0, f"Proprietary parts filtering with 10k parts took {duration:.4f} seconds, exceeding 5.0 second threshold"
    
    def test_database_query_performance_1k_parts(self, db_session: Session, large_parts_dataset_1k):
        """Test database query performance with 1,000 parts."""
        # Test basic parts query
        start_time = time.time()
        parts = db_session.query(Part).limit(100).all()
        duration = time.time() - start_time
        
        assert len(parts) == 100
        assert duration < 1.0, f"Basic parts query with 1k parts took {duration:.4f} seconds, exceeding 1.0 second threshold"
        
        # Test filtered query
        start_time = time.time()
        consumable_parts = db_session.query(Part).filter(Part.part_type == PartType.CONSUMABLE).limit(50).all()
        duration = time.time() - start_time
        
        assert len(consumable_parts) <= 50
        assert duration < 1.0, f"Filtered parts query with 1k parts took {duration:.4f} seconds, exceeding 1.0 second threshold"
    
    def test_database_query_performance_5k_parts(self, db_session: Session, large_parts_dataset_5k):
        """Test database query performance with 5,000 parts."""
        # Test parts search by name
        start_time = time.time()
        search_results = db_session.query(Part).filter(Part.name.ilike('%Filter%')).limit(100).all()
        duration = time.time() - start_time
        
        assert duration < 2.0, f"Parts name search with 5k parts took {duration:.4f} seconds, exceeding 2.0 second threshold"
        
        # Test proprietary parts query
        start_time = time.time()
        proprietary_parts = db_session.query(Part).filter(Part.is_proprietary == True).limit(100).all()
        duration = time.time() - start_time
        
        assert duration < 2.0, f"Proprietary parts query with 5k parts took {duration:.4f} seconds, exceeding 2.0 second threshold"
    
    def test_database_query_performance_10k_parts(self, db_session: Session, large_parts_dataset_10k):
        """Test database query performance with 10,000+ parts."""
        # Test complex query with multiple filters
        start_time = time.time()
        complex_query = db_session.query(Part).filter(
            Part.part_type == PartType.CONSUMABLE,
            Part.is_proprietary == False,
            Part.name.ilike('%Oil%')
        ).limit(100).all()
        duration = time.time() - start_time
        
        assert duration < 3.0, f"Complex parts query with 10k parts took {duration:.4f} seconds, exceeding 3.0 second threshold"
        
        # Test count query
        start_time = time.time()
        total_count = db_session.query(Part).count()
        duration = time.time() - start_time
        
        assert total_count >= 10000
        assert duration < 2.0, f"Parts count query with 10k parts took {duration:.4f} seconds, exceeding 2.0 second threshold"
    
    def test_pagination_performance_large_datasets(self, client: TestClient, auth_headers, large_parts_dataset_5k):
        """Test pagination performance with large datasets."""
        headers = auth_headers["super_admin"]
        
        # Test first page
        start_time = time.time()
        response = client.get("/parts?skip=0&limit=100", headers=headers)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 2.0, f"First page pagination took {duration:.4f} seconds, exceeding 2.0 second threshold"
        
        # Test middle page
        start_time = time.time()
        response = client.get("/parts?skip=2500&limit=100", headers=headers)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 2.0, f"Middle page pagination took {duration:.4f} seconds, exceeding 2.0 second threshold"
        
        # Test last page
        start_time = time.time()
        response = client.get("/parts?skip=4900&limit=100", headers=headers)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 2.0, f"Last page pagination took {duration:.4f} seconds, exceeding 2.0 second threshold"
    
    def test_inventory_performance_large_parts_catalog(self, client: TestClient, auth_headers, large_parts_dataset_1k):
        """Test inventory operations performance with large parts catalog."""
        headers = auth_headers["super_admin"]
        
        # Test inventory listing
        start_time = time.time()
        response = client.get("/inventory?limit=100", headers=headers)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 3.0, f"Inventory listing with large parts catalog took {duration:.4f} seconds, exceeding 3.0 second threshold"
        
        # Test inventory search
        start_time = time.time()
        response = client.get("/inventory?search=Filter&limit=50", headers=headers)
        duration = time.time() - start_time
        
        assert response.status_code == 200
        assert duration < 3.0, f"Inventory search with large parts catalog took {duration:.4f} seconds, exceeding 3.0 second threshold"


@pytest.mark.large_dataset
@pytest.mark.performance
@pytest.mark.slow
class TestScalabilityValidation:
    """Test system scalability with progressively larger datasets."""
    
    def test_progressive_dataset_scaling(self, db_session: Session):
        """Test system behavior with progressively larger datasets."""
        from .test_data_generators import LargeDatasetGenerator
        
        # Test with different dataset sizes
        dataset_sizes = [1000, 2500, 5000, 7500, 10000]
        performance_results = {}
        
        for size in dataset_sizes:
            print(f"Testing with {size} parts...")
            
            # Generate dataset
            generator = LargeDatasetGenerator(db_session)
            start_time = time.time()
            data = generator.generate_parts_dataset(
                parts_count=size,
                include_inventory=True,
                include_transactions=False  # Skip transactions for faster generation
            )
            generation_time = time.time() - start_time
            
            # Test query performance
            start_time = time.time()
            parts = db_session.query(Part).limit(100).all()
            query_time = time.time() - start_time
            
            # Test search performance
            start_time = time.time()
            search_results = db_session.query(Part).filter(Part.name.ilike('%Filter%')).limit(50).all()
            search_time = time.time() - start_time
            
            performance_results[size] = {
                "generation_time": generation_time,
                "query_time": query_time,
                "search_time": search_time,
                "parts_generated": len(data["parts"])
            }
            
            # Verify performance doesn't degrade significantly
            assert query_time < 2.0, f"Query time {query_time:.4f}s exceeded threshold for {size} parts"
            assert search_time < 3.0, f"Search time {search_time:.4f}s exceeded threshold for {size} parts"
            
            # Clean up for next iteration
            db_session.rollback()
        
        # Log performance results for analysis
        print("Performance Results:")
        for size, results in performance_results.items():
            print(f"{size} parts: Query={results['query_time']:.3f}s, Search={results['search_time']:.3f}s")
    
    def test_memory_usage_large_datasets(self, db_session: Session):
        """Test memory usage with large datasets."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate large dataset
        from .test_data_generators import generate_large_parts_dataset
        data = generate_large_parts_dataset(db_session, parts_count=5000, include_inventory=True)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Memory usage: Initial={initial_memory:.1f}MB, Final={final_memory:.1f}MB, Increase={memory_increase:.1f}MB")
        
        # Verify memory usage is reasonable (less than 500MB increase for 5k parts)
        assert memory_increase < 500, f"Memory increase {memory_increase:.1f}MB exceeded 500MB threshold"
        
        # Verify data was created successfully
        assert len(data["parts"]) == 5000
        assert len(data["inventory"]) == 5000