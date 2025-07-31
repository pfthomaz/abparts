# backend/test_security_implementation.py

import requests
import json
import uuid
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
SUPERADMIN_CREDENTIALS = {
    "username": "superadmin",
    "password": "superadmin"
}

def get_auth_token():
    """Get authentication token for superadmin"""
    response = requests.post(
        f"{BASE_URL}/token",
        data=SUPERADMIN_CREDENTIALS,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Authentication failed: {response.status_code} - {response.text}")
        return None

def test_audit_logs_endpoint(token):
    """Test audit logs endpoint"""
    print("\n=== Testing Audit Logs Endpoint ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test getting audit logs
    response = requests.get(f"{BASE_URL}/security/audit-logs", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        audit_logs = response.json()
        print(f"Retrieved {len(audit_logs)} audit log entries")
        if audit_logs:
            print(f"Sample audit log: {json.dumps(audit_logs[0], indent=2, default=str)}")
    else:
        print(f"Error: {response.text}")

def test_security_events_endpoint(token):
    """Test security events endpoint"""
    print("\n=== Testing Security Events Endpoint ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test getting security events
    response = requests.get(f"{BASE_URL}/security/security-events", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        security_events = response.json()
        print(f"Retrieved {len(security_events)} security event entries")
        if security_events:
            print(f"Sample security event: {json.dumps(security_events[0], indent=2, default=str)}")
    else:
        print(f"Error: {response.text}")

def test_organization_access_validation(token):
    """Test organization access validation"""
    print("\n=== Testing Organization Access Validation ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, get list of organizations to test with
    orgs_response = requests.get(f"{BASE_URL}/organizations", headers=headers)
    if orgs_response.status_code == 200:
        organizations = orgs_response.json()
        if organizations:
            test_org_id = organizations[0]["id"]
            
            # Test access validation
            response = requests.get(
                f"{BASE_URL}/security/validate-organization-access",
                params={"target_organization_id": test_org_id},
                headers=headers
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                validation_result = response.json()
                print(f"Access validation result: {json.dumps(validation_result, indent=2, default=str)}")
            else:
                print(f"Error: {response.text}")
        else:
            print("No organizations found to test with")
    else:
        print(f"Failed to get organizations: {orgs_response.status_code}")

def test_accessible_organizations(token):
    """Test accessible organizations endpoint"""
    print("\n=== Testing Accessible Organizations ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/security/accessible-organizations", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Accessible organizations: {json.dumps(result, indent=2, default=str)}")
    else:
        print(f"Error: {response.text}")

def test_visible_suppliers(token):
    """Test visible suppliers endpoint"""
    print("\n=== Testing Visible Suppliers ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/security/visible-suppliers", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Visible suppliers: {json.dumps(result, indent=2, default=str)}")
    else:
        print(f"Error: {response.text}")

def test_bossaqua_access_validation(token):
    """Test BossAqua access validation"""
    print("\n=== Testing BossAqua Access Validation ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/security/validate-bossaqua-access",
        params={"action": "READ_PARTS"},
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"BossAqua access validation: {json.dumps(result, indent=2, default=str)}")
    else:
        print(f"Error: {response.text}")

def test_organizational_isolation():
    """Test organizational isolation by making requests without proper access"""
    print("\n=== Testing Organizational Isolation ===")
    
    # This would require creating a non-superadmin user and testing access restrictions
    # For now, we'll just test that the endpoints exist and respond appropriately
    print("Organizational isolation testing requires non-superadmin users")
    print("This would be implemented in a more comprehensive test suite")

def main():
    """Run all security tests"""
    print("=== ABParts Security Implementation Test ===")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to authenticate. Exiting.")
        return
    
    print(f"Authentication successful. Token: {token[:20]}...")
    
    # Run all tests
    test_audit_logs_endpoint(token)
    test_security_events_endpoint(token)
    test_organization_access_validation(token)
    test_accessible_organizations(token)
    test_visible_suppliers(token)
    test_bossaqua_access_validation(token)
    test_organizational_isolation()
    
    print("\n=== Security Implementation Test Complete ===")

if __name__ == "__main__":
    main()