#!/usr/bin/env python3
"""
Test script to validate parts performance indexes.
This script tests the database indexes created for parts table performance optimization.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import DATABASE_URL, engine


def test_parts_indexes():
    """Test that the parts performance indexes are created and working."""
    
    # Use the existing database connection
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        print("Testing parts performance indexes...")
        
        # Test 1: Check if composite index exists
        result = db.execute(text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'parts' 
            AND indexname = 'idx_parts_type_proprietary'
        """))
        composite_index = result.fetchone()
        
        if composite_index:
            print("✓ Composite index (part_type, is_proprietary) exists")
            print(f"  Definition: {composite_index[1]}")
        else:
            print("✗ Composite index (part_type, is_proprietary) NOT found")
        
        # Test 2: Check if manufacturer index exists
        result = db.execute(text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'parts' 
            AND indexname = 'idx_parts_manufacturer'
        """))
        manufacturer_index = result.fetchone()
        
        if manufacturer_index:
            print("✓ Manufacturer index exists")
            print(f"  Definition: {manufacturer_index[1]}")
        else:
            print("✗ Manufacturer index NOT found")
        
        # Test 3: Check if full-text search index exists
        result = db.execute(text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'parts' 
            AND indexname = 'idx_parts_name_fulltext'
        """))
        fulltext_index = result.fetchone()
        
        if fulltext_index:
            print("✓ Full-text search index exists")
            print(f"  Definition: {fulltext_index[1]}")
        else:
            print("✗ Full-text search index NOT found")
        
        # Test 4: List all indexes on parts table
        print("\nAll indexes on parts table:")
        result = db.execute(text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'parts'
            ORDER BY indexname
        """))
        
        for row in result:
            print(f"  - {row[0]}: {row[1]}")
        
        # Test 5: Test query performance with EXPLAIN
        print("\nTesting query performance with EXPLAIN:")
        
        # Test composite index usage
        result = db.execute(text("""
            EXPLAIN (ANALYZE, BUFFERS) 
            SELECT * FROM parts 
            WHERE part_type = 'consumable' AND is_proprietary = false
            LIMIT 10
        """))
        
        print("\nQuery plan for filtering by part_type and is_proprietary:")
        for row in result:
            print(f"  {row[0]}")
        
        # Test manufacturer index usage
        result = db.execute(text("""
            EXPLAIN (ANALYZE, BUFFERS) 
            SELECT * FROM parts 
            WHERE manufacturer = 'BossAqua'
            LIMIT 10
        """))
        
        print("\nQuery plan for filtering by manufacturer:")
        for row in result:
            print(f"  {row[0]}")
        
        # Test full-text search usage
        result = db.execute(text("""
            EXPLAIN (ANALYZE, BUFFERS) 
            SELECT * FROM parts 
            WHERE to_tsvector('english', name) @@ to_tsquery('english', 'filter')
            LIMIT 10
        """))
        
        print("\nQuery plan for full-text search on name:")
        for row in result:
            print(f"  {row[0]}")


if __name__ == "__main__":
    test_parts_indexes()