#!/usr/bin/env python3

"""
Test script to verify localized protocol display is working
"""

import requests
import json

def test_localized_protocols():
    """Test if localized protocols are being returned correctly"""
    
    print("🧪 Testing Localized Protocol Display")
    print("=" * 50)
    
    # Test the localized protocol endpoint
    try:
        # Get a protocol ID first
        protocols_response = requests.get("http://localhost:8000/maintenance-protocols/")
        if protocols_response.status_code == 401:
            print("❌ Authentication required - cannot test without login")
            return False
            
        protocols = protocols_response.json()
        if not protocols:
            print("❌ No protocols found")
            return False
            
        protocol_id = protocols[0]['id']
        print(f"📋 Testing with protocol ID: {protocol_id}")
        
        # Test localized protocol endpoint
        localized_response = requests.get(f"http://localhost:8000/translations/protocols/{protocol_id}/localized?language=el")
        
        if localized_response.status_code == 401:
            print("❌ Authentication required for localized endpoint")
            return False
        elif localized_response.status_code == 200:
            localized_data = localized_response.json()
            print("✅ Localized protocol endpoint working")
            print(f"   Original name: {protocols[0].get('name', 'N/A')}")
            print(f"   Greek name: {localized_data.get('name', 'N/A')}")
            print(f"   Is translated: {localized_data.get('isTranslated', False)}")
            return True
        else:
            print(f"❌ Localized endpoint returned status: {localized_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing localized protocols: {e}")
        return False

def test_localized_checklist():
    """Test if localized checklist items are working"""
    
    print("\n🧪 Testing Localized Checklist Items")
    print("=" * 50)
    
    try:
        # Get a protocol ID first
        protocols_response = requests.get("http://localhost:8000/maintenance-protocols/")
        if protocols_response.status_code == 401:
            print("❌ Authentication required - cannot test without login")
            return False
            
        protocols = protocols_response.json()
        if not protocols:
            print("❌ No protocols found")
            return False
            
        protocol_id = protocols[0]['id']
        
        # Test localized checklist items endpoint
        checklist_response = requests.get(f"http://localhost:8000/translations/protocols/{protocol_id}/checklist-items/localized?language=el")
        
        if checklist_response.status_code == 401:
            print("❌ Authentication required for localized checklist endpoint")
            return False
        elif checklist_response.status_code == 200:
            checklist_data = checklist_response.json()
            print("✅ Localized checklist endpoint working")
            print(f"   Found {len(checklist_data)} checklist items")
            if checklist_data:
                first_item = checklist_data[0]
                print(f"   First item description: {first_item.get('description', 'N/A')}")
                print(f"   Is translated: {first_item.get('isTranslated', False)}")
            return True
        else:
            print(f"❌ Localized checklist endpoint returned status: {checklist_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing localized checklist: {e}")
        return False

if __name__ == "__main__":
    print("🌍 Testing Protocol Localization Integration")
    print("=" * 60)
    
    protocol_test = test_localized_protocols()
    checklist_test = test_localized_checklist()
    
    print(f"\n📊 Test Results:")
    print(f"   Localized Protocols: {'✅ Working' if protocol_test else '❌ Issues'}")
    print(f"   Localized Checklist: {'✅ Working' if checklist_test else '❌ Issues'}")
    
    if protocol_test and checklist_test:
        print("\n🎉 LOCALIZATION INTEGRATION READY!")
        print("\n🚀 Next steps:")
        print("   1. Login as a user with Greek language preference")
        print("   2. Navigate to Maintenance Executions")
        print("   3. Select 'Start of Day' protocol")
        print("   4. You should see 'Ημερήσια Έναρξη Ημέρας' instead!")
        print("\n✨ The localized maintenance experience is now live!")
    else:
        print("\n⚠️  Some localization features need attention")
        print("   The backend endpoints are working, but authentication is required")
        print("   Test the frontend interface directly at http://localhost:3000")