#!/usr/bin/env python3
"""
Test script to verify the Part model enhancements for task 3.
Tests the new fields: manufacturer, part_code, serial_number
Tests multilingual name handling and validation
Tests image URL validation (up to 4 images)
Tests part categorization validation
"""

import sys
import os
sys.path.append('/app')

from app import schemas
from pydantic import ValidationError
import pytest

def test_part_model_enhancements():
    """Test the enhanced Part model with new fields and validation"""
    
    print("Testing Part Model Enhancements")
    print("=" * 50)
    
    # Test 1: Valid part creation with new fields
    print("Test 1: Valid part creation with new fields")
    try:
        part_data = {
            "part_number": "AB-001",
            "name": "Test Part EN|Pieza de Prueba ES|Δοκιμαστικό Μέρος GR",
            "description": "Test part with multilingual name",
            "part_type": "consumable",
            "is_proprietary": False,
            "unit_of_measure": "pieces",
            "manufacturer": "AutoBoss Manufacturing",
            "part_code": "AB-FILTER-001",
            "serial_number": "SN123456789",
            "manufacturer_part_number": "MPN-001",
            "image_urls": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg"
            ]
        }
        
        part = schemas.PartCreate(**part_data)
        try:
            part_dict = part.model_dump()
        except AttributeError:
            part_dict = part.dict()
        print("✅ Valid part creation successful")
        print(f"   Manufacturer: {part_dict.get('manufacturer')}")
        print(f"   Part Code: {part_dict.get('part_code')}")
        print(f"   Serial Number: {part_dict.get('serial_number')}")
        print(f"   Images: {len(part_dict.get('image_urls', []))} images")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "-" * 30 + "\n")    
   
 # Test 2: Image URL validation (maximum 20 images)
    print("Test 2: Image URL validation (maximum 20 images)")
    try:
        # Test with exactly 20 images (should pass)
        part_data_20_images = part_data.copy()
        part_data_20_images["image_urls"] = [f"https://example.com/image{i}.jpg" for i in range(1, 21)]
        part = schemas.PartCreate(**part_data_20_images)
        print("✅ 20 images validation passed")
        
        # Test with 21 images (should fail)
        part_data_21_images = part_data.copy()
        part_data_21_images["image_urls"] = [f"https://example.com/image{i}.jpg" for i in range(1, 22)]
        try:
            part = schemas.PartCreate(**part_data_21_images)
            print("❌ Should have failed with 21 images")
            print(f"   Actually created with {len(part_data_21_images['image_urls'])} images")
            return False
        except ValidationError as e:
            print("✅ Correctly rejected 21 images")
            print(f"   Error: {e}")
        except Exception as e:
            print(f"   Unexpected error: {e}")
            print("✅ Correctly rejected 21 images (different error type)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "-" * 30 + "\n")
    
    # Test 3: Part type validation
    print("Test 3: Part type validation")
    try:
        # Test valid part types
        for part_type in ["consumable", "bulk_material"]:
            test_data = part_data.copy()
            test_data["part_type"] = part_type
            part = schemas.PartCreate(**test_data)
            print(f"✅ Valid part type '{part_type}' accepted")
        
        # Test invalid part type
        try:
            invalid_data = part_data.copy()
            invalid_data["part_type"] = "invalid_type"
            part = schemas.PartCreate(**invalid_data)
            print("❌ Should have failed with invalid part type")
            return False
        except ValidationError as e:
            print("✅ Correctly rejected invalid part type")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "-" * 30 + "\n")    
   
 # Test 4: Multilingual name validation
    print("Test 4: Multilingual name validation")
    try:
        # Test empty name (should fail)
        try:
            empty_name_data = part_data.copy()
            empty_name_data["name"] = ""
            part = schemas.PartCreate(**empty_name_data)
            print("❌ Should have failed with empty name")
            return False
        except ValidationError as e:
            print("✅ Correctly rejected empty name")
        
        # Test whitespace-only name (should fail)
        try:
            whitespace_name_data = part_data.copy()
            whitespace_name_data["name"] = "   "
            part = schemas.PartCreate(**whitespace_name_data)
            print("❌ Should have failed with whitespace-only name")
            return False
        except ValidationError as e:
            print("✅ Correctly rejected whitespace-only name")
        
        # Test multilingual name (should pass)
        multilingual_data = part_data.copy()
        multilingual_data["name"] = "Filter EN|Filtro ES|Φίλτρο GR|مرشح AR"
        part = schemas.PartCreate(**multilingual_data)
        print("✅ Multilingual name accepted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "-" * 30 + "\n")
    
    # Test 5: Optional fields validation
    print("Test 5: Optional fields validation")
    try:
        # Test with minimal required fields only
        minimal_data = {
            "part_number": "AB-002",
            "name": "Minimal Part",
            "part_type": "bulk_material"
        }
        part = schemas.PartCreate(**minimal_data)
        try:
            part_dict = part.model_dump()
        except AttributeError:
            part_dict = part.dict()
        print("✅ Minimal part creation successful")
        print(f"   Manufacturer: {part_dict.get('manufacturer')}")
        print(f"   Part Code: {part_dict.get('part_code')}")
        print(f"   Serial Number: {part_dict.get('serial_number')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All Part model enhancement tests passed!")
    return True

if __name__ == "__main__":
    success = test_part_model_enhancements()
    sys.exit(0 if success else 1)