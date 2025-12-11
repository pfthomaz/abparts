#!/usr/bin/env python3

"""
Test script for Protocol Translation API
Tests the new translation endpoints and functionality
"""

import requests
import json
from uuid import uuid4

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USERNAME = "superadmin"  # Replace with your admin user
TEST_PASSWORD = "admin123"  # Replace with your admin password

class TranslationAPITester:
    def __init__(self):
        self.token = None
        self.headers = {}
        self.protocol_id = None
        
    def authenticate(self):
        """Authenticate and get access token"""
        print("🔐 Authenticating...")
        
        auth_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        
        response = requests.post(f"{BASE_URL}/token", data=auth_data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print("✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(response.text)
            return False
    
    def get_first_protocol(self):
        """Get the first available protocol for testing"""
        print("📋 Getting first protocol...")
        
        response = requests.get(
            f"{BASE_URL}/maintenance-protocols",
            headers=self.headers
        )
        
        if response.status_code == 200:
            protocols = response.json()
            if protocols:
                self.protocol_id = protocols[0]["id"]
                print(f"✅ Found protocol: {protocols[0]['name']} (ID: {self.protocol_id})")
                return True
            else:
                print("❌ No protocols found")
                return False
        else:
            print(f"❌ Failed to get protocols: {response.status_code}")
            return False
    
    def test_create_protocol_translation(self):
        """Test creating a protocol translation"""
        print("🌍 Testing protocol translation creation...")
        
        translation_data = {
            "language_code": "el",
            "name": "Ημερήσια Έναρξη Ημέρας",
            "description": "Ολοκληρώστε αυτές τις εργασίες στην αρχή κάθε ημέρας"
        }
        
        response = requests.post(
            f"{BASE_URL}/translations/protocols/{self.protocol_id}/translations",
            headers=self.headers,
            json=translation_data
        )
        
        if response.status_code == 200:
            translation = response.json()
            print(f"✅ Created Greek translation: {translation['name']}")
            return True
        else:
            print(f"❌ Failed to create translation: {response.status_code}")
            print(response.text)
            return False
    
    def test_get_localized_protocol(self):
        """Test getting localized protocol"""
        print("🔍 Testing localized protocol retrieval...")
        
        # Test Greek localization
        response = requests.get(
            f"{BASE_URL}/translations/protocols/{self.protocol_id}/localized?language=el",
            headers=self.headers
        )
        
        if response.status_code == 200:
            protocol = response.json()
            print(f"✅ Got localized protocol: {protocol['name']}")
            print(f"   Language: {protocol['display_language']}")
            print(f"   Translated: {protocol['is_translated']}")
            return True
        else:
            print(f"❌ Failed to get localized protocol: {response.status_code}")
            print(response.text)
            return False
    
    def test_translation_status(self):
        """Test getting translation status"""
        print("📊 Testing translation status...")
        
        response = requests.get(
            f"{BASE_URL}/translations/protocols/{self.protocol_id}/translation-status",
            headers=self.headers
        )
        
        if response.status_code == 200:
            status = response.json()
            print("✅ Translation status:")
            print(f"   Total items: {status['total_items']}")
            print(f"   Base language: {status['base_language']}")
            
            for lang, percentage in status['completion_percentage'].items():
                print(f"   {lang}: {percentage:.1f}%")
            
            return True
        else:
            print(f"❌ Failed to get translation status: {response.status_code}")
            print(response.text)
            return False
    
    def test_checklist_item_translation(self):
        """Test checklist item translation"""
        print("📝 Testing checklist item translation...")
        
        # First get checklist items
        response = requests.get(
            f"{BASE_URL}/maintenance-protocols/{self.protocol_id}/checklist-items",
            headers=self.headers
        )
        
        if response.status_code != 200:
            print("❌ Failed to get checklist items")
            return False
        
        items = response.json()
        if not items:
            print("⚠️  No checklist items found")
            return True
        
        item_id = items[0]["id"]
        
        # Create translation for first item
        translation_data = {
            "language_code": "el",
            "item_description": "Έλεγχος στάθμης λαδιού και συμπλήρωση εάν χρειάζεται",
            "notes": "Χρησιμοποιήστε το κατάλληλο λάδι",
            "item_category": "Μηχανικά"
        }
        
        response = requests.post(
            f"{BASE_URL}/translations/checklist-items/{item_id}/translations",
            headers=self.headers,
            json=translation_data
        )
        
        if response.status_code == 200:
            translation = response.json()
            print(f"✅ Created checklist item translation: {translation['item_description']}")
            return True
        else:
            print(f"❌ Failed to create checklist item translation: {response.status_code}")
            print(response.text)
            return False
    
    def run_all_tests(self):
        """Run all translation tests"""
        print("🧪 Starting Protocol Translation API Tests")
        print("=" * 50)
        
        tests = [
            ("Authentication", self.authenticate),
            ("Get Protocol", self.get_first_protocol),
            ("Create Protocol Translation", self.test_create_protocol_translation),
            ("Get Localized Protocol", self.test_get_localized_protocol),
            ("Translation Status", self.test_translation_status),
            ("Checklist Item Translation", self.test_checklist_item_translation)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔬 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"💥 {test_name} ERROR: {str(e)}")
        
        print(f"\n📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Translation system is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the errors above.")
        
        return passed == total


if __name__ == "__main__":
    tester = TranslationAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Next steps:")
        print("1. Start creating translations for your protocols")
        print("2. Test the frontend translation management interface")
        print("3. Verify language-aware protocol display")
    else:
        print("\n🔧 Please fix the issues and run the tests again")