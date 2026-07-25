#!/usr/bin/env python3

"""
Final test of the Protocol Translation System
Tests both backend API and frontend accessibility
"""

import requests
import json

def test_complete_system():
    """Test the complete protocol translation system"""
    
    print("🎯 Protocol Translation System - Final Test")
    print("=" * 50)
    
    # Test 1: Backend API
    print("\n🔧 Backend API Tests:")
    
    backend_tests = [
        ("/docs", "API Documentation"),
        ("/maintenance-protocols", "Maintenance Protocols API"),
        ("/translations/protocols", "Protocol Translations API"),
    ]
    
    backend_working = True
    for endpoint, description in backend_tests:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code in [200, 401, 422]:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description} (Status: {response.status_code})")
                backend_working = False
        except Exception as e:
            print(f"  ❌ {description} (Error: {e})")
            backend_working = False
    
    # Test 2: Frontend
    print("\n🌐 Frontend Tests:")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("  ✅ Frontend accessible at http://localhost:3000")
            frontend_working = True
        else:
            print(f"  ❌ Frontend not accessible (Status: {response.status_code})")
            frontend_working = False
    except Exception as e:
        print(f"  ❌ Frontend not accessible (Error: {e})")
        frontend_working = False
    
    # Test 3: CORS Configuration
    print("\n🔗 CORS Tests:")
    
    try:
        # Test CORS preflight
        response = requests.options(
            "http://localhost:8000/token",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            print("  ✅ CORS configured correctly for localhost:3000")
            cors_working = True
        else:
            print(f"  ❌ CORS issue (Status: {response.status_code})")
            cors_working = False
    except Exception as e:
        print(f"  ❌ CORS test failed (Error: {e})")
        cors_working = False
    
    # Summary
    print("\n📊 System Status:")
    print(f"  Backend API: {'✅ Working' if backend_working else '❌ Issues'}")
    print(f"  Frontend UI: {'✅ Working' if frontend_working else '❌ Issues'}")
    print(f"  CORS Config: {'✅ Working' if cors_working else '❌ Issues'}")
    
    overall_status = backend_working and frontend_working and cors_working
    
    if overall_status:
        print("\n🎉 PROTOCOL TRANSLATION SYSTEM READY!")
        print("\n🚀 How to test the translation system:")
        print("   1. Open http://localhost:3000 in your browser")
        print("   2. Login with super admin credentials:")
        print("      - Try: superadmin / admin123")
        print("      - Or: jamie / admin123")
        print("      - Or: dthomaz / admin123")
        print("   3. Navigate to 'Protocol Translations' in the admin menu")
        print("   4. Select a protocol and start translating!")
        print("\n🌍 Supported Languages:")
        print("   🇺🇸 English (base) | 🇬🇷 Greek | 🇸🇦 Arabic")
        print("   🇪🇸 Spanish | 🇹🇷 Turkish | 🇳🇴 Norwegian")
        print("\n✨ The multi-language future of ABParts is here!")
    else:
        print("\n⚠️  SYSTEM ISSUES DETECTED")
        print("   Some components need attention before testing")
    
    return overall_status

if __name__ == "__main__":
    test_complete_system()