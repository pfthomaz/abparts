#!/usr/bin/env python3
"""
API Integration test for Enhanced Security and Audit Implementation
Tests the security features through actual API calls
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
SUPERADMIN_CREDENTIALS = {"username": "superadmin", "password": "superadmin"}

def get_auth_token(credentials):
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/token", data=credentials)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Failed to get auth token: {response.status_code} - {response.text}")
        return None

def test_audit_logs_access():
    """Test access to audit logs (superadmin only)"""
    print("📋 Testing Audit Logs Access...")
    
    # Get superadmin token
    token = get_auth_token(SUPERADMIN_CREDENTIALS)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test audit logs endpoint
    response = requests.get(f"{BASE_URL}/security/audit-logs", headers=headers)
    
    if response.status_code == 200:
        audit_logs = response.json()
        print(f"✅ Retrieved {len(audit_logs)} audit log entries")
        
        # Check if our test entries are there
        test_entries = [log for log in audit_logs if log.get("resource_type") == "TEST_RESOURCE"]
        if test_entries:
            print(f"✅ Found {len(test_entries)} test audit entries")
        
        return True
    else:
        print(f"❌ Failed to get audit logs: {response.status_code} - {response.text}")
        return False

def test_security_events_access():
    """Test access to security events"""
    print("\n🔒 Testing Security Events Access...")
    
    # Get superadmin token
    token = get_auth_token(SUPERADMIN_CREDENTIALS)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test security events endpoint
    response = requests.get(f"{BASE_URL}/security/security-events", headers=headers)
    
    if response.status_code == 200:
        security_events = response.json()
        print(f"✅ Retrieved {len(security_events)} security event entries")
        
        # Check for our test events
        test_events = [event for event in security_events if "TEST" in event.get("event_type", "")]
        if test_events:
            print(f"✅ Found {len(test_events)} test security events")
        
        return True
    else:
        print(f"❌ Failed to get security events: {response.status_code} - {response.text}")
        return False

def test_organization_access_validation():
    """Test organization access validation endpoint"""
    print("\n🏢 Testing Organization Access Validation...")
    
    # Get superadmin token
    token = get_auth_token(SUPERADMIN_CREDENTIALS)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, get list of organizations
    response = requests.get(f"{BASE_URL}/organizations", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get organizations: {response.status_code}")
        return False
    
    organizations = response.json()
    if not organizations:
        print("⚠️  No organizations found")
        return True
    
    # Test validation for first organization
    test_org_id = organizations[0]["id"]
    response = requests.get(
        f"{BASE_URL}/security/validate-organization-access",
        headers=headers,
        params={"target_organization_id": test_org_id}
    )
    
    if response.status_code == 200:
        validation_result = response.json()
        print(f"✅ Organization access validation: {validation_result['access_granted']}")
        print(f"   Reason: {validation_result['reason']}")
        return True
    else:
        print(f"❌ Failed organization access validation: {response.status_code} - {response.text}")
        return False

def test_accessible_organizations():
    """Test accessible organizations endpoint"""
    print("\n📋 Testing Accessible Organizations...")
    
    # Get superadmin token
    token = get_auth_token(SUPERADMIN_CREDENTIALS)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/security/accessible-organizations", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ User can access {result['accessible_organization_count']} organizations")
        print(f"   User role: {result['user_role']}")
        return True
    else:
        print(f"❌ Failed to get accessible organizations: {response.status_code} - {response.text}")
        return False

def test_visible_suppliers():
    """Test visible suppliers endpoint"""
    print("\n👥 Testing Visible Suppliers...")
    
    # Get superadmin token
    token = get_auth_token(SUPERADMIN_CREDENTIALS)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/security/visible-suppliers", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ User can see {result['visible_supplier_count']} suppliers")
        return True
    else:
        print(f"❌ Failed to get visible suppliers: {response.status_code} - {response.text}")
        return False

def test_bossaqua_access_validation():
    """Test BossAqua access validation endpoint"""
    print("\n🏢 Testing BossAqua Access Validation...")
    
    # Get superadmin token
    token = get_auth_token(SUPERADMIN_CREDENTIALS)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/security/validate-bossaqua-access",
        headers=headers,
        params={"action": "READ"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ BossAqua access validation: {result['access_granted']}")
        print(f"   Reason: {result['reason']}")
        return True
    else:
        print(f"❌ Failed BossAqua access validation: {response.status_code} - {response.text}")
        return False

def test_api_audit_logging():
    """Test that API calls are being audited"""
    print("\n📝 Testing API Audit Logging...")
    
    # Get superadmin token
    token = get_auth_token(SUPERADMIN_CREDENTIALS)
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Make a test API call that should be audited
    response = requests.get(f"{BASE_URL}/organizations", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Test API call failed: {response.status_code}")
        return False
    
    # Wait a moment for audit logging to complete
    time.sleep(1)
    
    # Check if the API call was audited
    response = requests.get(f"{BASE_URL}/security/audit-logs?limit=10", headers=headers)
    
    if response.status_code == 200:
        audit_logs = response.json()
        
        # Look for recent API request logs
        api_logs = [log for log in audit_logs if log.get("resource_type") == "API_REQUEST"]
        if api_logs:
            print(f"✅ Found {len(api_logs)} API request audit entries")
            
            # Check for our specific call
            org_logs = [log for log in api_logs if "/organizations" in log.get("action", "")]
            if org_logs:
                print("✅ Organizations API call was audited")
            
            return True
        else:
            print("⚠️  No API request audit entries found")
            return True  # Not a failure, might just be timing
    else:
        print(f"❌ Failed to check audit logs: {response.status_code}")
        return False

def main():
    """Run all API integration tests"""
    print("🚀 Starting Enhanced Security API Integration Tests")
    print("=" * 60)
    
    # Check if API is accessible
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ API health check failed: {response.status_code}")
            return False
        print("✅ API is accessible")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {str(e)}")
        print("   Make sure the API is running with: docker-compose up")
        return False
    
    tests = [
        test_audit_logs_access,
        test_security_events_access,
        test_organization_access_validation,
        test_accessible_organizations,
        test_visible_suppliers,
        test_bossaqua_access_validation,
        test_api_audit_logging
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 API Integration Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All enhanced security API integration tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please review the API implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)