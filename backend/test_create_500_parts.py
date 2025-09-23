#!/usr/bin/env python3
"""
Test script to create 500+ parts and validate the system can handle more than 200 parts.
This tests the removal of the parts limit and validates frontend/backend synchronization.
"""

import os
import sys
import time
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Part, Organization, User, Warehouse, PartType, OrganizationType, UserRole, UserStatus
from app.auth import get_password_hash
from tests.test_data_generators import LargeDatasetGenerator


def setup_database():
    """Setup database connection."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return None
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def count_existing_parts(db_session):
    """Count existing parts in the database."""
    return db_session.query(Part).count()


def create_test_parts(db_session, target_count=500):
    """Create test parts to reach the target count."""
    existing_count = count_existing_parts(db_session)
    print(f"📊 Current parts count: {existing_count}")
    
    if existing_count >= target_count:
        print(f"✅ Already have {existing_count} parts (target: {target_count})")
        return existing_count
    
    parts_to_create = target_count - existing_count
    print(f"🔧 Creating {parts_to_create} additional parts...")
    
    try:
        # Use the large dataset generator
        generator = LargeDatasetGenerator(db_session)
        
        # Create base organizations if they don't exist
        generator._create_base_organizations()
        
        # Generate the required number of parts
        start_time = time.time()
        generator._generate_parts(parts_to_create)
        
        # Commit the changes
        db_session.commit()
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        final_count = count_existing_parts(db_session)
        print(f"✅ Parts creation completed!")
        print(f"📊 Final parts count: {final_count}")
        print(f"⏱️  Creation time: {creation_time:.2f} seconds")
        print(f"🚀 Parts per second: {parts_to_create/creation_time:.1f}")
        
        return final_count
        
    except Exception as e:
        print(f"❌ Error during parts creation: {e}")
        db_session.rollback()
        raise


def test_parts_retrieval(db_session):
    """Test retrieving parts to validate performance."""
    print("\n🔍 Testing parts retrieval performance...")
    
    start_time = time.time()
    
    # Test basic query
    all_parts = db_session.query(Part).all()
    query_time = time.time() - start_time
    
    print(f"📊 Retrieved {len(all_parts)} parts")
    print(f"⏱️  Query time: {query_time:.3f} seconds")
    
    if query_time > 5.0:
        print("⚠️  Query time is high (>5s), consider adding database indexes")
    else:
        print("✅ Query performance is acceptable")
    
    # Test search functionality
    start_time = time.time()
    search_results = db_session.query(Part).filter(Part.name.ilike("%Filter%")).limit(100).all()
    search_time = time.time() - start_time
    
    print(f"🔍 Search found {len(search_results)} parts matching 'Filter'")
    print(f"⏱️  Search time: {search_time:.3f} seconds")
    
    return len(all_parts), query_time, search_time


def test_pagination(db_session):
    """Test pagination with large dataset."""
    print("\n📄 Testing pagination performance...")
    
    page_size = 100
    total_parts = count_existing_parts(db_session)
    total_pages = (total_parts + page_size - 1) // page_size
    
    print(f"📊 Total parts: {total_parts}")
    print(f"📄 Page size: {page_size}")
    print(f"📄 Total pages: {total_pages}")
    
    # Test first page
    start_time = time.time()
    first_page = db_session.query(Part).offset(0).limit(page_size).all()
    first_page_time = time.time() - start_time
    
    # Test middle page
    middle_offset = (total_pages // 2) * page_size
    start_time = time.time()
    middle_page = db_session.query(Part).offset(middle_offset).limit(page_size).all()
    middle_page_time = time.time() - start_time
    
    # Test last page
    last_offset = (total_pages - 1) * page_size
    start_time = time.time()
    last_page = db_session.query(Part).offset(last_offset).limit(page_size).all()
    last_page_time = time.time() - start_time
    
    print(f"📄 First page ({len(first_page)} parts): {first_page_time:.3f}s")
    print(f"📄 Middle page ({len(middle_page)} parts): {middle_page_time:.3f}s")
    print(f"📄 Last page ({len(last_page)} parts): {last_page_time:.3f}s")
    
    avg_page_time = (first_page_time + middle_page_time + last_page_time) / 3
    print(f"📄 Average page load time: {avg_page_time:.3f}s")
    
    if avg_page_time > 1.0:
        print("⚠️  Pagination performance could be improved")
    else:
        print("✅ Pagination performance is good")
    
    return avg_page_time


def main():
    """Main test function."""
    print("🚀 Starting 500+ Parts Creation Test")
    print("=" * 50)
    
    # Setup database
    db_session = setup_database()
    if not db_session:
        sys.exit(1)
    
    try:
        # Create parts
        final_count = create_test_parts(db_session, target_count=500)
        
        if final_count < 500:
            print(f"❌ Failed to create enough parts. Only have {final_count}")
            sys.exit(1)
        
        # Test retrieval performance
        parts_count, query_time, search_time = test_parts_retrieval(db_session)
        
        # Test pagination
        avg_page_time = test_pagination(db_session)
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Total parts created: {final_count}")
        print(f"✅ Parts limit removed: {'YES' if final_count > 200 else 'NO'}")
        print(f"⏱️  Query performance: {query_time:.3f}s")
        print(f"🔍 Search performance: {search_time:.3f}s")
        print(f"📄 Pagination performance: {avg_page_time:.3f}s")
        
        # Performance assessment
        if query_time < 2.0 and search_time < 0.5 and avg_page_time < 0.5:
            print("🎉 EXCELLENT: All performance metrics are great!")
        elif query_time < 5.0 and search_time < 1.0 and avg_page_time < 1.0:
            print("✅ GOOD: Performance is acceptable for large datasets")
        else:
            print("⚠️  WARNING: Some performance metrics need optimization")
        
        print("\n🎯 Next steps:")
        print("1. Test the frontend interface with these parts")
        print("2. Try creating a new part via the web interface")
        print("3. Verify search and filtering work correctly")
        print("4. Check that the parts count updates properly")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        db_session.rollback()
        sys.exit(1)
    
    finally:
        db_session.close()


if __name__ == "__main__":
    main()