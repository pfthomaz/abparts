#!/usr/bin/env python3

"""
Debug script to check localization issues
"""

import requests
import json

def debug_localization():
    """Debug the localization system"""
    
    print("🔍 Debugging Protocol Localization")
    print("=" * 50)
    
    # First, let's check if we have any protocols
    try:
        protocols_response = requests.get("http://localhost:8000/maintenance-protocols/")
        if protocols_response.status_code == 401:
            print("❌ Authentication required - cannot debug without login")
            print("💡 Please test directly in the browser at http://localhost:3000")
            return
            
        protocols = protocols_response.json()
        print(f"✅ Found {len(protocols)} protocols in the system")
        
        if protocols:
            protocol = protocols[0]
            protocol_id = protocol['id']
            print(f"📋 Testing with protocol: '{protocol['name']}' (ID: {protocol_id})")
            
            # Test the localized endpoint
            print(f"\n🌍 Testing localized protocol endpoint...")
            localized_url = f"http://localhost:8000/translations/protocols/{protocol_id}/localized?language=el"
            print(f"   URL: {localized_url}")
            
            localized_response = requests.get(localized_url)
            print(f"   Status: {localized_response.status_code}")
            
            if localized_response.status_code == 200:
                localized_data = localized_response.json()
                print(f"   ✅ Localized response received")
                print(f"   Original name: '{protocol['name']}'")
                print(f"   Greek name: '{localized_data.get('name', 'NOT FOUND')}'")
                print(f"   Is translated: {localized_data.get('isTranslated', False)}")
                
                if localized_data.get('name') != protocol['name']:
                    print(f"   🎉 Translation is working! Greek name is different from English")
                else:
                    print(f"   ⚠️  Translation might not exist - names are the same")
            else:
                print(f"   ❌ Error: {localized_response.text}")
                
            # Test checklist items
            print(f"\n📝 Testing localized checklist items...")
            checklist_url = f"http://localhost:8000/translations/protocols/{protocol_id}/checklist-items/localized?language=el"
            print(f"   URL: {checklist_url}")
            
            checklist_response = requests.get(checklist_url)
            print(f"   Status: {checklist_response.status_code}")
            
            if checklist_response.status_code == 200:
                checklist_data = checklist_response.json()
                print(f"   ✅ Found {len(checklist_data)} checklist items")
                if checklist_data:
                    first_item = checklist_data[0]
                    print(f"   First item: '{first_item.get('description', 'NO DESCRIPTION')}'")
                    print(f"   Is translated: {first_item.get('isTranslated', False)}")
            else:
                print(f"   ❌ Error: {checklist_response.text}")
                
    except Exception as e:
        print(f"❌ Error during debugging: {e}")

def check_sample_translations():
    """Check if sample translations exist"""
    
    print(f"\n🗄️  Checking sample translations in database...")
    
    try:
        # This would require database access, so let's just check the API
        print("   (Database check requires direct access - testing via API instead)")
        
        # Test if translation endpoints exist
        endpoints = [
            "/translations/protocols",
            "/docs"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"http://localhost:8000{endpoint}")
            status = "✅ Available" if response.status_code in [200, 401, 422] else f"❌ Status {response.status_code}"
            print(f"   {endpoint}: {status}")
            
    except Exception as e:
        print(f"   ❌ Error checking translations: {e}")

if __name__ == "__main__":
    debug_localization()
    check_sample_translations()
    
    print(f"\n💡 Debugging Tips:")
    print(f"   1. Check browser console for JavaScript errors")
    print(f"   2. Verify user's preferred_language is set to 'el'")
    print(f"   3. Check Network tab to see API calls being made")
    print(f"   4. Ensure translations exist for the protocols you're testing")
    print(f"   5. Test with a fresh browser session")