#!/usr/bin/env python3
"""
Test script for Enhanced Security and Audit Implementation
Tests the four main components of task 19:
1. Organizational data isolation validation
2. Audit trail tracking for all data access and modifications
3. Supplier visibility restriction enforcement
4. BossAqua data access restrictions for non-superadmin users
"""

import asyncio
import uuid
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import the modules we're testing
import sys
import os
sys.path.append('/app')

from app.database import get_db, SessionLocal
from app.models import User, Organization, AuditLog, SecurityEventLog, OrganizationType, UserRole
from app.enhanced_organizational_isolation import (
    EnhancedOrganizationalDataFilter,
    EnhancedBossAquaAccessControl,
    EnhancedSupplierVisibilityControl
)
from app.enhanced_audit_system import EnhancedAuditSystem, AuditContext

def test_organizational_data_isolation():
    """Test organizational data isolation validation"""
    print("🔒 Testing Organizational Data Isolation...")
    
    db = SessionLocal()
    try:
        # Get test users from different organizations
        superadmin = db.query(User).filter(User.role == UserRole.super_admin).first()
        admin_user = db.query(User).filter(User.role == UserRole.admin).first()
        regular_user = db.query(User).filter(User.role == UserRole.user).first()
        
        if not superadmin:
            print("❌ No superadmin user found")
            return False
        
        print(f"✅ Found superadmin: {superadmin.username}")
        
        # Test 1: Superadmin should have access to all organizations
        all_orgs = db.query(Organization).all()
        if all_orgs:
            test_org = all_orgs[0]
            validation_result = EnhancedOrganizationalDataFilter.validate_organization_access(
                superadmin, test_org.id, db
            )
            assert validation_result["allowed"], "Superadmin should have access to all organizations"
            print(f"✅ Superadmin access validation: {validation_result['reason']}")
        
        # Test 2: Regular user should only access their own organization
        if admin_user:
            # Try to access a different organization
            other_org = None
            for org in all_orgs:
                if org.id != admin_user.organization_id:
                    other_org = org
                    break
            
            if other_org:
                validation_result = EnhancedOrganizationalDataFilter.validate_organization_access(
                    admin_user, other_org.id, db
                )
                assert not validation_result["allowed"], "Admin should not access other organizations"
                print(f"✅ Admin isolation validation: {validation_result['reason']}")
        
        # Test 3: Get accessible organization IDs
        accessible_orgs = EnhancedOrganizationalDataFilter.get_accessible_organization_ids(
            superadmin, db
        )
        print(f"✅ Superadmin accessible organizations: {len(accessible_orgs)}")
        
        if admin_user:
            accessible_orgs = EnhancedOrganizationalDataFilter.get_accessible_organization_ids(
                admin_user, db
            )
            print(f"✅ Admin accessible organizations: {len(accessible_orgs)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Organizational isolation test failed: {str(e)}")
        return False
    finally:
        db.close()

def test_audit_trail_tracking():
    """Test audit trail tracking for data access and modifications"""
    print("\n📝 Testing Audit Trail Tracking...")
    
    db = SessionLocal()
    try:
        # Get a test user
        test_user = db.query(User).filter(User.role == UserRole.super_admin).first()
        if not test_user:
            print("❌ No test user found")
            return False
        
        # Test 1: Log data access
        test_resource_id = uuid.uuid4()
        success = EnhancedAuditSystem.log_data_access(
            user_id=test_user.id,
            organization_id=test_user.organization_id,
            resource_type="TEST_RESOURCE",
            resource_id=test_resource_id,
            action="READ",
            details={"test": "data_access"},
            ip_address="127.0.0.1",
            user_agent="test-agent",
            endpoint="/test",
            http_method="GET",
            db=db
        )
        assert success, "Data access logging should succeed"
        print("✅ Data access logging successful")
        
        # Test 2: Log data modification
        success = EnhancedAuditSystem.log_data_modification(
            user_id=test_user.id,
            organization_id=test_user.organization_id,
            resource_type="TEST_RESOURCE",
            resource_id=test_resource_id,
            action="UPDATE",
            old_values={"field": "old_value"},
            new_values={"field": "new_value"},
            ip_address="127.0.0.1",
            user_agent="test-agent",
            endpoint="/test",
            http_method="PUT",
            db=db
        )
        assert success, "Data modification logging should succeed"
        print("✅ Data modification logging successful")
        
        # Test 3: Log security event
        success = EnhancedAuditSystem.log_security_event(
            event_type="TEST_SECURITY_EVENT",
            severity="LOW",
            description="Test security event",
            user_id=test_user.id,
            organization_id=test_user.organization_id,
            details={"test": "security_event"},
            ip_address="127.0.0.1",
            user_agent="test-agent",
            endpoint="/test",
            db=db
        )
        assert success, "Security event logging should succeed"
        print("✅ Security event logging successful")
        
        # Test 4: Verify audit entries were created
        audit_count = db.query(AuditLog).filter(
            AuditLog.user_id == test_user.id,
            AuditLog.resource_type == "TEST_RESOURCE"
        ).count()
        assert audit_count >= 2, "Audit entries should be created"
        print(f"✅ Found {audit_count} audit entries")
        
        security_count = db.query(SecurityEventLog).filter(
            SecurityEventLog.event_type == "TEST_SECURITY_EVENT"
        ).count()
        assert security_count >= 1, "Security event entries should be created"
        print(f"✅ Found {security_count} security event entries")
        
        return True
        
    except Exception as e:
        print(f"❌ Audit trail test failed: {str(e)}")
        return False
    finally:
        db.close()

def test_supplier_visibility_restrictions():
    """Test supplier visibility restriction enforcement"""
    print("\n👥 Testing Supplier Visibility Restrictions...")
    
    db = SessionLocal()
    try:
        # Get test users
        superadmin = db.query(User).filter(User.role == UserRole.super_admin).first()
        admin_user = db.query(User).filter(User.role == UserRole.admin).first()
        
        if not superadmin:
            print("❌ No superadmin user found")
            return False
        
        # Test 1: Superadmin should see all suppliers
        visible_suppliers = EnhancedSupplierVisibilityControl.get_visible_suppliers(
            superadmin, db
        )
        print(f"✅ Superadmin can see {len(visible_suppliers)} suppliers")
        
        # Test 2: Admin should only see suppliers from their organization
        if admin_user:
            visible_suppliers = EnhancedSupplierVisibilityControl.get_visible_suppliers(
                admin_user, db
            )
            print(f"✅ Admin can see {len(visible_suppliers)} suppliers")
            
            # Test 3: Validate supplier access
            if visible_suppliers:
                supplier = visible_suppliers[0]
                access_granted = EnhancedSupplierVisibilityControl.validate_supplier_access(
                    admin_user, supplier.id, "READ", db
                )
                assert access_granted, "Admin should have access to their organization's suppliers"
                print("✅ Admin supplier access validation successful")
        
        # Test 4: Test supplier visibility violation logging
        fake_supplier_id = uuid.uuid4()
        if admin_user:
            success = EnhancedAuditSystem.log_supplier_visibility_violation(
                user_id=admin_user.id,
                user_organization_id=admin_user.organization_id,
                attempted_supplier_id=fake_supplier_id,
                action="READ",
                ip_address="127.0.0.1",
                db=db
            )
            assert success, "Supplier visibility violation logging should succeed"
            print("✅ Supplier visibility violation logging successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Supplier visibility test failed: {str(e)}")
        return False
    finally:
        db.close()

def test_bossaqua_access_restrictions():
    """Test BossAqua data access restrictions for non-superadmin users"""
    print("\n🏢 Testing BossAqua Access Restrictions...")
    
    db = SessionLocal()
    try:
        # Get test users
        superadmin = db.query(User).filter(User.role == UserRole.super_admin).first()
        admin_user = db.query(User).filter(User.role == UserRole.admin).first()
        regular_user = db.query(User).filter(User.role == UserRole.user).first()
        
        if not superadmin:
            print("❌ No superadmin user found")
            return False
        
        # Test 1: Superadmin should have BossAqua access
        access_granted = EnhancedBossAquaAccessControl.validate_bossaqua_access(
            superadmin, "READ", db=db
        )
        assert access_granted, "Superadmin should have BossAqua access"
        print("✅ Superadmin BossAqua access granted")
        
        # Test 2: Admin should NOT have BossAqua access
        if admin_user:
            access_granted = EnhancedBossAquaAccessControl.validate_bossaqua_access(
                admin_user, "READ", db=db
            )
            assert not access_granted, "Admin should not have BossAqua access"
            print("✅ Admin BossAqua access denied")
        
        # Test 3: Regular user should NOT have BossAqua access
        if regular_user:
            access_granted = EnhancedBossAquaAccessControl.validate_bossaqua_access(
                regular_user, "READ", db=db
            )
            assert not access_granted, "Regular user should not have BossAqua access"
            print("✅ Regular user BossAqua access denied")
        
        # Test 4: Test BossAqua access violation logging
        if admin_user:
            success = EnhancedAuditSystem.log_bossaqua_access_violation(
                user_id=admin_user.id,
                user_organization_id=admin_user.organization_id,
                user_role="admin",
                action="READ",
                ip_address="127.0.0.1",
                db=db
            )
            assert success, "BossAqua access violation logging should succeed"
            print("✅ BossAqua access violation logging successful")
        
        # Test 5: Check if BossAqua organization exists
        bossaqua_org = db.query(Organization).filter(
            Organization.organization_type == OrganizationType.bossaqua
        ).first()
        
        if bossaqua_org:
            is_bossaqua = EnhancedBossAquaAccessControl.is_bossaqua_organization(
                bossaqua_org.id, db
            )
            assert is_bossaqua, "BossAqua organization should be identified correctly"
            print("✅ BossAqua organization identification successful")
        else:
            print("⚠️  No BossAqua organization found in database")
        
        return True
        
    except Exception as e:
        print(f"❌ BossAqua access test failed: {str(e)}")
        return False
    finally:
        db.close()

def test_audit_context():
    """Test AuditContext functionality"""
    print("\n🔍 Testing Audit Context...")
    
    db = SessionLocal()
    try:
        # Get a test user
        test_user = db.query(User).filter(User.role == UserRole.super_admin).first()
        if not test_user:
            print("❌ No test user found")
            return False
        
        # Create audit context
        audit_context = AuditContext(test_user)
        
        # Test logging through context
        test_resource_id = uuid.uuid4()
        
        # Test access logging
        success = audit_context.log_access(
            "TEST_CONTEXT_RESOURCE",
            test_resource_id,
            "READ",
            details={"context_test": True},
            db=db
        )
        assert success, "Context access logging should succeed"
        print("✅ Audit context access logging successful")
        
        # Test modification logging
        success = audit_context.log_modification(
            "TEST_CONTEXT_RESOURCE",
            test_resource_id,
            "UPDATE",
            old_values={"field": "old"},
            new_values={"field": "new"},
            db=db
        )
        assert success, "Context modification logging should succeed"
        print("✅ Audit context modification logging successful")
        
        # Test security event logging
        success = audit_context.log_security_event(
            "TEST_CONTEXT_SECURITY",
            "LOW",
            "Test context security event",
            details={"context_test": True},
            db=db
        )
        assert success, "Context security event logging should succeed"
        print("✅ Audit context security event logging successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Audit context test failed: {str(e)}")
        return False
    finally:
        db.close()

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Security and Audit Implementation Tests")
    print("=" * 60)
    
    tests = [
        test_organizational_data_isolation,
        test_audit_trail_tracking,
        test_supplier_visibility_restrictions,
        test_bossaqua_access_restrictions,
        test_audit_context
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
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All enhanced security and audit tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)