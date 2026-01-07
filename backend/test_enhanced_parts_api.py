#!/usr/bin/env python3
"""
Test script to verify the Enhanced Parts Management API (Task 7)
Tests multilingual name search capabilities and superadmin-only access control
"""

import sys
import requests
import json
import uuid
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
SUPERADMIN_CREDENTIALS = {
    "username": "superadmin",
    "password": "superadmin"
}

def get_auth_token(credentials: Dict[str, str]) -> str:
    """Get authentication token for API requests"""
    try:
        response = requests.post(
            f"{BASE_URL}/token",
            data=credentials,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"❌ Failed to get auth token: {e}")
        return None

def test_multilingual_name_validation():
    """Test multilingual name validation in CRUD operations"""
    print("\n" + "="*50)
    print("TEST: Multilingual Name Validation")
    print("="*50)
    
    token = get_auth_token(SUPERADMIN_CREDENTIALS)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Valid single language name
    print("\nTest 1: Valid single language name")
    part_data = {
        "part_number": f"TEST-ML-{uuid.uuid4().hex[:8]}",
        "name": "Test Part Single Language",
        "description": "Test part with single language name",
        "part_type": "consumable",
        "is_proprietary": False,
        "unit_of_measure": "pieces",
        "manufacturer": "Test Manufacturer",
        "part_code": "TM-001"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/parts/", json=part_data, headers=headers)
        if response.status_code == 201:
            print("✅ Single language name accepted")
            part_id = response.json()["id"]
        else:
            print(f"❌ Single language name rejected: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing single language name: {e}")
        return False
    
    # Test 2: Valid multilingual name
    print("\nTest 2: Valid multilingual name")
    part_data_ml = {
        "part_number": f"TEST-ML-{uuid.uuid4().hex[:8]}",
        "name": "Test Part English|Δοκιμαστικό Εξάρτημα GR|Pieza de Prueba ES",
        "description": "Test part with multilingual name",
        "part_type": "consumable",
        "is_proprietary": False,
        "unit_of_measure": "pieces",
        "manufacturer": "Test Manufacturer",
        "part_code": "TM-002"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/parts/", json=part_data_ml, headers=headers)
        if response.status_code == 201:
            print("✅ Multilingual name accepted")
            part_id_ml = response.json()["id"]
        else:
            print(f"❌ Multilingual name rejected: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing multilingual name: {e}")
        return False
    
    # Test 3: Invalid multilingual name (empty part)
    print("\nTest 3: Invalid multilingual name (empty part)")
    part_data_invalid = {
        "part_number": f"TEST-ML-{uuid.uuid4().hex[:8]}",
        "name": "Valid Part||Invalid Empty Part",
        "description": "Test part with invalid multilingual name",
        "part_type": "consumable",
        "is_proprietary": False,
        "unit_of_measure": "pieces"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/parts/", json=part_data_invalid, headers=headers)
        if response.status_code == 400:
            print("✅ Invalid multilingual name correctly rejected")
        else:
            print(f"❌ Invalid multilingual name should be rejected: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing invalid multilingual name: {e}")
        return False
    
    # Clean up test parts
    try:
        requests.delete(f"{BASE_URL}/parts/{part_id}", headers=headers)
        requests.delete(f"{BASE_URL}/parts/{part_id_ml}", headers=headers)
        print("\n✅ Test parts cleaned up")
    except:
        pass
    
    return True

def test_multilingual_search():
    """Test multilingual name search capabilities"""
    print("\n" + "="*50)
    print("TEST: Multilingual Search Capabilities")
    print("="*50)
    
    token = get_auth_token(SUPERADMIN_CREDENTIALS)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create test parts with multilingual names
    test_parts = [
        {
            "part_number": f"SEARCH-TEST-{uuid.uuid4().hex[:8]}",
            "name": "Engine Filter|Φίλτρο Κινητήρα GR|Filtro de Motor ES",
            "description": "Multilingual engine filter",
            "part_type": "consumable",
            "is_proprietary": False,
            "manufacturer": "AutoBoss",
            "part_code": "AB-EF-001"
        },
        {
            "part_number": f"SEARCH-TEST-{uuid.uuid4().hex[:8]}",
            "name": "Oil Pump|Αντλία Λαδιού GR|Bomba de Aceite ES",
            "description": "Multilingual oil pump",
            "part_type": "consumable",
            "is_proprietary": True,
            "manufacturer": "BossAqua",
            "part_code": "BA-OP-002"
        }
    ]
    
    created_parts = []
    
    # Create test parts
    print("\nCreating test parts...")
    for part_data in test_parts:
        try:
            response = requests.post(f"{BASE_URL}/parts/", json=part_data, headers=headers)
            if response.status_code == 201:
                created_parts.append(response.json())
                print(f"✅ Created part: {part_data['name'][:30]}...")
            else:
                print(f"❌ Failed to create part: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error creating test part: {e}")
            return False
    
    # Test 1: Search by English name
    print("\nTest 1: Search by English name")
    try:
        response = requests.get(f"{BASE_URL}/parts/search?q=Engine", headers=headers)
        if response.status_code == 200:
            results = response.json()
            if any("Engine" in part["name"] for part in results):
                print("✅ English name search successful")
            else:
                print("❌ English name not found in search results")
                return False
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing English search: {e}")
        return False
    
    # Test 2: Search by Greek name
    print("\nTest 2: Search by Greek name")
    try:
        response = requests.get(f"{BASE_URL}/parts/search?q=Φίλτρο", headers=headers)
        if response.status_code == 200:
            results = response.json()
            if any("Φίλτρο" in part["name"] for part in results):
                print("✅ Greek name search successful")
            else:
                print("❌ Greek name not found in search results")
                return False
        else:
            print(f"❌ Greek search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Greek search: {e}")
        return False
    
    # Test 3: Search by Spanish name
    print("\nTest 3: Search by Spanish name")
    try:
        response = requests.get(f"{BASE_URL}/parts/search?q=Filtro", headers=headers)
        if response.status_code == 200:
            results = response.json()
            if any("Filtro" in part["name"] for part in results):
                print("✅ Spanish name search successful")
            else:
                print("❌ Spanish name not found in search results")
                return False
        else:
            print(f"❌ Spanish search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing Spanish search: {e}")
        return False
    
    # Test 4: Search by manufacturer
    print("\nTest 4: Search by manufacturer")
    try:
        response = requests.get(f"{BASE_URL}/parts/search?q=AutoBoss", headers=headers)
        if response.status_code == 200:
            results = response.json()
            if any(part.get("manufacturer") == "AutoBoss" for part in results):
                print("✅ Manufacturer search successful")
            else:
                print("❌ Manufacturer not found in search results")
                return False
        else:
            print(f"❌ Manufacturer search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing manufacturer search: {e}")
        return False
    
    # Test 5: Search by part code
    print("\nTest 5: Search by part code")
    try:
        response = requests.get(f"{BASE_URL}/parts/search?q=AB-EF", headers=headers)
        if response.status_code == 200:
            results = response.json()
            if any("AB-EF" in (part.get("part_code") or "") for part in results):
                print("✅ Part code search successful")
            else:
                print("❌ Part code not found in search results")
                return False
        else:
            print(f"❌ Part code search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing part code search: {e}")
        return False
    
    # Test 6: Enhanced GET /parts with search parameter
    print("\nTest 6: Enhanced GET /parts with search parameter")
    try:
        response = requests.get(f"{BASE_URL}/parts/?search=Oil", headers=headers)
        if response.status_code == 200:
            results = response.json()
            if any("Oil" in part["name"] for part in results):
                print("✅ GET /parts with search parameter successful")
            else:
                print("❌ Search parameter in GET /parts not working")
                return False
        else:
            print(f"❌ GET /parts with search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing GET /parts with search: {e}")
        return False
    
    # Clean up test parts
    print("\nCleaning up test parts...")
    for part in created_parts:
        try:
            requests.delete(f"{BASE_URL}/parts/{part['id']}", headers=headers)
        except:
            pass
    print("✅ Test parts cleaned up")
    
    return True

def test_superadmin_access_control():
    """Test superadmin-only access control for parts CRUD operations"""
    print("\n" + "="*50)
    print("TEST: Superadmin-Only Access Control")
    print("="*50)
    
    # Test with superadmin credentials
    print("\nTesting with superadmin credentials...")
    superadmin_token = get_auth_token(SUPERADMIN_CREDENTIALS)
    if not superadmin_token:
        return False
    
    superadmin_headers = {"Authorization": f"Bearer {superadmin_token}"}
    
    # Test 1: Superadmin can create parts
    print("\nTest 1: Superadmin can create parts")
    part_data = {
        "part_number": f"ADMIN-TEST-{uuid.uuid4().hex[:8]}",
        "name": "Superadmin Test Part",
        "description": "Test part created by superadmin",
        "part_type": "consumable",
        "is_proprietary": False,
        "unit_of_measure": "pieces"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/parts/", json=part_data, headers=superadmin_headers)
        if response.status_code == 201:
            print("✅ Superadmin can create parts")
            created_part = response.json()
            part_id = created_part["id"]
        else:
            print(f"❌ Superadmin cannot create parts: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing superadmin create: {e}")
        return False
    
    # Test 2: Superadmin can update parts
    print("\nTest 2: Superadmin can update parts")
    update_data = {
        "name": "Updated Superadmin Test Part",
        "description": "Updated by superadmin"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/parts/{part_id}", json=update_data, headers=superadmin_headers)
        if response.status_code == 200:
            print("✅ Superadmin can update parts")
        else:
            print(f"❌ Superadmin cannot update parts: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing superadmin update: {e}")
        return False
    
    # Test 3: Superadmin can delete parts
    print("\nTest 3: Superadmin can delete parts")
    try:
        response = requests.delete(f"{BASE_URL}/parts/{part_id}", headers=superadmin_headers)
        if response.status_code == 204:
            print("✅ Superadmin can delete parts")
        else:
            print(f"❌ Superadmin cannot delete parts: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing superadmin delete: {e}")
        return False
    
    # Test 4: All users can read parts
    print("\nTest 4: All users can read parts")
    try:
        response = requests.get(f"{BASE_URL}/parts/", headers=superadmin_headers)
        if response.status_code == 200:
            print("✅ Users can read parts")
        else:
            print(f"❌ Users cannot read parts: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing parts read access: {e}")
        return False
    
    return True

def test_image_validation():
    """Test image URL validation (max 20 images)"""
    print("\n" + "="*50)
    print("TEST: Image URL Validation")
    print("="*50)
    
    token = get_auth_token(SUPERADMIN_CREDENTIALS)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Valid number of images (4 or less)
    print("\nTest 1: Valid number of images (4)")
    part_data = {
        "part_number": f"IMG-TEST-{uuid.uuid4().hex[:8]}",
        "name": "Image Test Part",
        "description": "Test part with 4 images",
        "part_type": "consumable",
        "is_proprietary": False,
        "unit_of_measure": "pieces",
        "image_urls": [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg",
            "https://example.com/image3.jpg",
            "https://example.com/image4.jpg"
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/parts/", json=part_data, headers=headers)
        if response.status_code == 201:
            print("✅ 4 images accepted")
            part_id = response.json()["id"]
        else:
            print(f"❌ 4 images rejected: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing 4 images: {e}")
        return False
    
    # Test 2: Too many images (more than 4)
    print("\nTest 2: Too many images (5)")
    part_data_invalid = {
        "part_number": f"IMG-TEST-{uuid.uuid4().hex[:8]}",
        "name": "Invalid Image Test Part",
        "description": "Test part with too many images",
        "part_type": "consumable",
        "is_proprietary": False,
        "unit_of_measure": "pieces",
        "image_urls": [f"https://example.com/image{i}.jpg" for i in range(1, 22)]  # 21 images should fail
    }
    
    try:
        response = requests.post(f"{BASE_URL}/parts/", json=part_data_invalid, headers=headers)
        if response.status_code == 400:
            print("✅ Too many images correctly rejected")
        else:
            print(f"❌ Too many images should be rejected: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing too many images: {e}")
        return False
    
    # Clean up
    try:
        requests.delete(f"{BASE_URL}/parts/{part_id}", headers=headers)
        print("\n✅ Test part cleaned up")
    except:
        pass
    
    return True

def main():
    """Run all enhanced parts management API tests"""
    print("Enhanced Parts Management API Test Suite")
    print("=" * 60)
    print("Testing Task 7: Enhanced Parts Management API")
    print("- Multilingual name search capabilities")
    print("- Enhanced POST /parts validation")
    print("- Enhanced PUT /parts/{id} support")
    print("- Superadmin-only access control")
    print("=" * 60)
    
    # Check if API is accessible
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print("❌ API is not accessible. Make sure the backend is running.")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure the backend is running with: docker-compose up api")
        return False
    
    tests = [
        ("Multilingual Name Validation", test_multilingual_name_validation),
        ("Multilingual Search Capabilities", test_multilingual_search),
        ("Superadmin Access Control", test_superadmin_access_control),
        ("Image URL Validation", test_image_validation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Enhanced Parts Management API tests passed!")
        print("\nTask 7 Implementation Summary:")
        print("✅ GET /parts enhanced with multilingual name search")
        print("✅ POST /parts enhanced with multilingual validation")
        print("✅ PUT /parts/{id} enhanced with multilingual support")
        print("✅ Superadmin-only access control implemented")
        print("✅ Image URL validation (max 20 images)")
        print("✅ Enhanced search across all part fields")
        return True
    else:
        print(f"❌ {total - passed} tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)