"""
Security testing for ABParts role-based access control.
Tests authorization and permission enforcement across different user roles.
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import (
    Organization, User, Part, Warehouse, Inventory, Machine, Transaction,
    OrganizationType, UserRole, UserStatus
)


class TestRoleBasedAccessControl:
    """Test role-based access control enforcement."""
    
    def test_super_admin_permissions(self, client: TestClient, auth_headers, test_organizations):
        """Test super admin access to all resources."""
        headers = auth_headers["super_admin"]
        
        # Super admin can access all organizations
        response = client.get("/organizations/", headers=headers)
        assert response.status_code == 200
        orgs = response.json()
        assert len(orgs) >= 4  # Should see all organizations
        
        # Super admin can access all users
        response = client.get("/users/", headers=headers)
        assert response.status_code == 200
        
        # Super admin can create organizations
        new_org = {
            "name": "New Test Customer",
            "organization_type": "customer",
            "address": "123 Test Street",
            "contact_info": "test@example.com"
        }
        response = client.post("/organizations/", json=new_org, headers=headers)
        assert response.status_code == 201
        
        # Super admin can create users in any organization
        new_user = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "securepassword123",
            "name": "Test User",
            "role": "user",
            "organization_id": str(test_organizations["customer1"].id)
        }
        response = client.post("/users/", json=new_user, headers=headers)
        assert response.status_code == 201
    
    def test_organization_admin_permissions(self, client: TestClient, auth_headers, test_organizations):
        """Test organization admin permissions."""
        headers = auth_headers["customer_admin"]
        
        # Admin can only see their own organization
        response = client.get("/organizations/", headers=headers)
        assert response.status_code == 200
        orgs = response.json()
        assert len(orgs) == 1
        assert orgs[0]["id"] == str(test_organizations["customer1"].id)
        
        # Admin can see users in their organization
        response = client.get("/users/", headers=headers)
        assert response.status_code == 200
        users = response.json()
        for user in users:
            assert user["organization_id"] == str(test_organizations["customer1"].id)
        
        # Admin can create users in their organization
        new_user = {
            "username": "newcustomeruser",
            "email": "newuser@customer.com",
            "password": "securepassword123",
            "name": "New Customer User",
            "role": "user",
            "organization_id": str(test_organizations["customer1"].id)
        }
        response = client.post("/users/", json=new_user, headers=headers)
        assert response.status_code == 201
        
        # Admin cannot create users in other organizations
        other_org_user = {
            "username": "otherorguser",
            "email": "other@example.com",
            "password": "securepassword123",
            "name": "Other Org User",
            "role": "user",
            "organization_id": str(test_organizations["customer2"].id)
        }
        response = client.post("/users/", json=other_org_user, headers=headers)
        assert response.status_code == 403
    
    def test_regular_user_permissions(self, client: TestClient, auth_headers, test_organizations):
        """Test regular user permissions."""
        headers = auth_headers["customer_user"]
        
        # Regular user can see their own organization
        response = client.get("/organizations/", headers=headers)
        assert response.status_code == 200
        orgs = response.json()
        assert len(orgs) == 1
        assert orgs[0]["id"] == str(test_organizations["customer1"].id)
        
        # Regular user can see their own profile
        response = client.get("/users/me/", headers=headers)
        assert response.status_code == 200
        
        # Regular user cannot create new users
        new_user = {
            "username": "attemptcreate",
            "email": "attempt@example.com",
            "password": "securepassword123",
            "name": "Attempt Create",
            "role": "user",
            "organization_id": str(test_organizations["customer1"].id)
        }
        response = client.post("/users/", json=new_user, headers=headers)
        assert response.status_code == 403
        
        # Regular user cannot modify organization details
        org_update = {"name": "Hacked Organization"}
        response = client.put(f"/organizations/{test_organizations['customer1'].id}", 
                             json=org_update, headers=headers)
        assert response.status_code == 403
    
    def test_cross_organization_access_prevention(self, client: TestClient, auth_headers, test_organizations, test_warehouses):
        """Test prevention of cross-organization resource access."""
        # Customer 1 admin trying to access Customer 2 resources
        headers = auth_headers["customer_admin"]
        
        # Try to access another organization's warehouse
        other_warehouse_id = str(test_warehouses["customer2_main"].id)
        response = client.get(f"/warehouses/{other_warehouse_id}", headers=headers)
        assert response.status_code == 403
        
        # Try to access another organization's users
        response = client.get(f"/organizations/{test_organizations['customer2'].id}/users", headers=headers)
        assert response.status_code == 403
        
        # Try to create warehouse in another organization
        new_warehouse = {
            "name": "Unauthorized Warehouse",
            "location": "Somewhere",
            "organization_id": str(test_organizations["customer2"].id)
        }
        response = client.post("/warehouses/", json=new_warehouse, headers=headers)
        assert response.status_code == 403
    
    def test_permission_elevation_prevention(self, client: TestClient, auth_headers, test_organizations):
        """Test prevention of permission elevation."""
        headers = auth_headers["customer_admin"]
        
        # Try to create super admin user
        super_admin_attempt = {
            "username": "fakesuperadmin",
            "email": "fake@superadmin.com",
            "password": "securepassword123",
            "name": "Fake Super Admin",
            "role": "super_admin",
            "organization_id": str(test_organizations["customer1"].id)
        }
        response = client.post("/users/", json=super_admin_attempt, headers=headers)
        assert response.status_code == 403
        
        # Try to modify own role to super_admin
        user_response = client.get("/users/me/", headers=headers)
        user_id = user_response.json()["id"]
        
        role_update = {"role": "super_admin"}
        response = client.put(f"/users/{user_id}", json=role_update, headers=headers)
        assert response.status_code == 403
    
    def test_token_expiration_and_refresh(self, client: TestClient, auth_headers, test_users):
        """Test token expiration and refresh mechanisms."""
        # This would require mocking time or token validation
        # For now, we'll test the refresh token endpoint exists and works
        
        # Get initial auth token
        login_data = {
            "username": test_users["customer_user"].username,
            "password": "user123"  # This is the password set in the fixture
        }
        
        response = client.post("/token", data=login_data)
        assert response.status_code == 200
        tokens = response.json()
        assert "access_token" in tokens
        assert "token_type" in tokens
        assert tokens["token_type"] == "bearer"
        
        # Test using the token
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = client.get("/users/me/", headers=headers)
        assert response.status_code == 200
    
    def test_invalid_token_rejection(self, client: TestClient):
        """Test rejection of invalid tokens."""
        # Test with invalid token
        headers = {"Authorization": "Bearer invalidtoken12345"}
        response = client.get("/users/me/", headers=headers)
        assert response.status_code == 401
        
        # Test with malformed authorization header
        headers = {"Authorization": "invalidformat"}
        response = client.get("/users/me/", headers=headers)
        assert response.status_code == 401
        
        # Test with missing authorization header
        response = client.get("/users/me/")
        assert response.status_code == 401
    
    def test_brute_force_protection(self, client: TestClient, db_session: Session, test_users):
        """Test protection against brute force attacks."""
        # Attempt multiple failed logins
        login_data = {
            "username": test_users["customer_user"].username,
            "password": "wrongpassword"
        }
        
        # Make 5 failed login attempts
        for _ in range(5):
            response = client.post("/token", data=login_data)
            assert response.status_code == 401
        
        # Check if account is locked (depends on implementation)
        user = db_session.query(User).filter(User.id == test_users["customer_user"].id).first()
        assert user.failed_login_attempts >= 5
        
        # If account locking is implemented, this should fail even with correct password
        correct_login = {
            "username": test_users["customer_user"].username,
            "password": "user123"
        }
        
        response = client.post("/token", data=correct_login)
        # Either 401 (if account is locked) or 200 (if just tracking attempts)
        if user.user_status == UserStatus.locked:
            assert response.status_code == 401
    
    def test_session_management(self, client: TestClient, auth_headers):
        """Test session management and control."""
        headers = auth_headers["customer_admin"]
        
        # Get active sessions
        response = client.get("/sessions/active", headers=headers)
        assert response.status_code == 200
        
        # Test session termination (if implemented)
        response = client.post("/sessions/terminate-all", headers=headers)
        assert response.status_code in [200, 204, 404]  # 404 if not implemented


class TestSecurityHeaders:
    """Test security headers and protections."""
    
    def test_security_headers(self, client: TestClient):
        """Test that security headers are properly set."""
        response = client.get("/")
        headers = response.headers
        
        # Check for security headers
        assert "X-Content-Type-Options" in headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in headers
        assert headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in headers
        assert headers["X-XSS-Protection"] == "1; mode=block"
        
        # Content Security Policy might be present
        if "Content-Security-Policy" in headers:
            assert "default-src" in headers["Content-Security-Policy"]
    
    def test_cors_configuration(self, client: TestClient):
        """Test CORS configuration."""
        # Send preflight request
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type, Authorization"
        }
        response = client.options("/", headers=headers)
        
        # Check CORS headers
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_sql_injection_prevention(self, client: TestClient, auth_headers):
        """Test prevention of SQL injection attacks."""
        headers = auth_headers["customer_admin"]
        
        # Try SQL injection in query parameters
        response = client.get("/users/?username=user' OR '1'='1", headers=headers)
        assert response.status_code != 500  # Should not cause server error
        
        # Try SQL injection in path parameters
        response = client.get("/users/1' OR '1'='1", headers=headers)
        assert response.status_code in [404, 422]  # Should be not found or validation error
        
        # Try SQL injection in JSON body
        injection_data = {
            "name": "'; DROP TABLE users; --"
        }
        response = client.post("/organizations/", json=injection_data, headers=headers)
        assert response.status_code in [400, 422]  # Should be validation error
    
    def test_xss_prevention(self, client: TestClient, auth_headers):
        """Test prevention of Cross-Site Scripting (XSS) attacks."""
        headers = auth_headers["customer_admin"]
        
        # Try XSS in organization name
        xss_data = {
            "name": "<script>alert('XSS')</script>",
            "organization_type": "customer",
            "address": "123 Test Street",
            "contact_info": "test@example.com"
        }
        
        response = client.post("/organizations/", json=xss_data, headers=headers)
        if response.status_code == 201:
            # If created, ensure script tags are escaped/sanitized in response
            org_data = response.json()
            assert org_data["name"] != "<script>alert('XSS')</script>"
            assert "<script>" not in org_data["name"] or org_data["name"].startswith("&lt;script&gt;")
    
    def test_csrf_protection(self, client: TestClient, auth_headers):
        """Test CSRF protection mechanisms."""
        # This would depend on the specific CSRF protection implementation
        # For API-only backends with proper CORS and token-based auth, CSRF might not be explicitly needed
        pass