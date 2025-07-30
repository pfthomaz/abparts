#!/usr/bin/env python3
"""
Test script to verify the Part CRUD operations work with new fields
"""

import sys
sys.path.append('/app')

def test_part_crud_direct():
    """Test Part CRUD operations directly"""
    
    print("Testing Part CRUD with New Fields")
    print("=" * 40)
    
    try:
        from app.database import get_db
        from app import schemas, crud
        from sqlalchemy.orm import Session
        
        # Get database session
        db_gen = get_db()
        db: Session = next(db_gen)
        
        # Test 1: Create a part with new fields
        print("Test 1: Create part with new fields")
        part_data = schemas.PartCreate(
            part_number="TEST-NEW-001",
            name="Test Part with New Fields EN|Pieza de Prueba ES",
            description="Test part with manufacturer, part_code, and serial_number",
            part_type="consumable",
            is_proprietary=False,
            unit_of_measure="pieces",
            manufacturer="AutoBoss Manufacturing",
            part_code="AB-TEST-001",
            serial_number="SN123456789",
            manufacturer_part_number="MPN-TEST-001",
            image_urls=[
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg"
            ]
        )
        
        created_part = crud.parts.create_part(db, part_data)
        if created_part:
            print("✅ Part created successfully")
            print(f"   ID: {created_part.id}")
            print(f"   Manufacturer: {created_part.manufacturer}")
            print(f"   Part Code: {created_part.part_code}")
            print(f"   Serial Number: {created_part.serial_number}")
            print(f"   Images: {len(created_part.image_urls or [])} images")
        else:
            print("❌ Failed to create part")
            return False
        
        # Test 2: Retrieve the part
        print("\nTest 2: Retrieve created part")
        retrieved_part = crud.parts.get_part(db, created_part.id)
        if retrieved_part:
            print("✅ Part retrieved successfully")
            print(f"   Name: {retrieved_part.name}")
            print(f"   Manufacturer: {retrieved_part.manufacturer}")
            print(f"   Part Code: {retrieved_part.part_code}")
            print(f"   Serial Number: {retrieved_part.serial_number}")
        else:
            print("❌ Failed to retrieve part")
            return False
        
        # Test 3: Update the part
        print("\nTest 3: Update part with new fields")
        update_data = schemas.PartUpdate(
            manufacturer="Updated Manufacturer",
            part_code="UPDATED-001",
            serial_number="UPDATED-SN123"
        )
        
        updated_part = crud.parts.update_part(db, created_part.id, update_data)
        if updated_part:
            print("✅ Part updated successfully")
            print(f"   Updated Manufacturer: {updated_part.manufacturer}")
            print(f"   Updated Part Code: {updated_part.part_code}")
            print(f"   Updated Serial Number: {updated_part.serial_number}")
        else:
            print("❌ Failed to update part")
            return False
        
        # Test 4: Clean up - delete the test part
        print("\nTest 4: Clean up test part")
        delete_result = crud.parts.delete_part(db, created_part.id)
        if delete_result:
            print("✅ Test part deleted successfully")
        else:
            print("❌ Failed to delete test part")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 40)
    print("✅ Part CRUD test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_part_crud_direct()
    sys.exit(0 if success else 1)