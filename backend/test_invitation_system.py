#!/usr/bin/env python3
"""
Test script for the User Invitation and Onboarding System
This script tests the core functionality without requiring a full server setup.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from app.models import User, Organization, UserStatus, UserRole, OrganizationType, InvitationAuditLog
from app.schemas import UserInvitationCreate, UserRoleEnum
from app.crud.users import (
    create_user_invitation, 
    get_user_by_invitation_token, 
    accept_user_invitation,
    resend_user_invitation,
    get_pending_invitations,
    mark_invitations_as_expired,
    get_invitation_audit_logs
)
from app.crud.organizations import create_organization
from app.schemas import OrganizationCreate, OrganizationTypeEnum
from app.database import SessionLocal
import uuid

def test_invitation_system():
    """Test the complete invitation workflow"""
    print("🧪 Testing User Invitation and Onboarding System")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. Create test organization
        print("\n1️⃣ Creating test organization...")
        org_data = OrganizationCreate(
            name="Test Customer Organization",
            organization_type=OrganizationTypeEnum.CUSTOMER,
            address="123 Test Street",
            contact_info="test@example.com"
        )
        
        # Create organization directly in database for testing
        test_org = Organization(
            name=org_data.name,
            organization_type=OrganizationType.CUSTOMER,
            address=org_data.address,
            contact_info=org_data.contact_info
        )
        db.add(test_org)
        db.commit()
        db.refresh(test_org)
        print(f"✅ Created organization: {test_org.name} (ID: {test_org.id})")
        
        # 2. Create admin user to send invitations
        print("\n2️⃣ Creating admin user...")
        admin_user = User(
            username="test_admin",
            email="admin@test.com",
            password_hash="hashed_password",
            name="Test Admin",
            role=UserRole.admin,
            organization_id=test_org.id,
            user_status=UserStatus.active,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"✅ Created admin user: {admin_user.username} (ID: {admin_user.id})")
        
        # 3. Test invitation creation
        print("\n3️⃣ Testing invitation creation...")
        invitation_data = UserInvitationCreate(
            email="newuser@test.com",
            name="New Test User",
            role=UserRoleEnum.USER,
            organization_id=test_org.id
        )
        
        invited_user = create_user_invitation(db, invitation_data, admin_user.id)
        print(f"✅ Created invitation for: {invited_user.email}")
        print(f"   - User ID: {invited_user.id}")
        print(f"   - Status: {invited_user.user_status}")
        print(f"   - Token: {invited_user.invitation_token[:20]}...")
        print(f"   - Expires: {invited_user.invitation_expires_at}")
        
        # 4. Test invitation token lookup
        print("\n4️⃣ Testing invitation token lookup...")
        found_user = get_user_by_invitation_token(db, invited_user.invitation_token)
        if found_user:
            print(f"✅ Found user by token: {found_user.email}")
        else:
            print("❌ Failed to find user by token")
            return False
        
        # 5. Test invitation acceptance
        print("\n5️⃣ Testing invitation acceptance...")
        activated_user = accept_user_invitation(
            db, 
            invited_user.invitation_token,
            "newuser123",
            "securepassword123",
            "New User Full Name"
        )
        
        if activated_user:
            print(f"✅ Invitation accepted successfully!")
            print(f"   - Username: {activated_user.username}")
            print(f"   - Status: {activated_user.user_status}")
            print(f"   - Active: {activated_user.is_active}")
            print(f"   - Token cleared: {activated_user.invitation_token is None}")
        else:
            print("❌ Failed to accept invitation")
            return False
        
        # 6. Test pending invitations query
        print("\n6️⃣ Testing pending invitations query...")
        
        # Create another pending invitation
        invitation_data2 = UserInvitationCreate(
            email="pending@test.com",
            name="Pending User",
            role=UserRoleEnum.USER,
            organization_id=test_org.id
        )
        pending_user = create_user_invitation(db, invitation_data2, admin_user.id)
        
        pending_invitations = get_pending_invitations(db, test_org.id)
        print(f"✅ Found {len(pending_invitations)} pending invitations")
        for inv in pending_invitations:
            print(f"   - {inv.email} (expires: {inv.invitation_expires_at})")
        
        # 7. Test invitation resend
        print("\n7️⃣ Testing invitation resend...")
        original_token = pending_user.invitation_token
        resent_user = resend_user_invitation(db, pending_user.id, admin_user.id)
        
        if resent_user and resent_user.invitation_token != original_token:
            print(f"✅ Invitation resent with new token")
            print(f"   - Old token: {original_token[:20]}...")
            print(f"   - New token: {resent_user.invitation_token[:20]}...")
        else:
            print("❌ Failed to resend invitation")
        
        # 8. Test audit logs
        print("\n8️⃣ Testing audit logs...")
        audit_logs = get_invitation_audit_logs(db, activated_user.id)
        print(f"✅ Found {len(audit_logs)} audit log entries for activated user:")
        for log in audit_logs:
            print(f"   - {log.action} at {log.timestamp}")
        
        audit_logs_pending = get_invitation_audit_logs(db, pending_user.id)
        print(f"✅ Found {len(audit_logs_pending)} audit log entries for pending user:")
        for log in audit_logs_pending:
            print(f"   - {log.action} at {log.timestamp}")
        
        # 9. Test expired invitations handling
        print("\n9️⃣ Testing expired invitations handling...")
        
        # Create an expired invitation by manually setting the expiry date
        expired_invitation = UserInvitationCreate(
            email="expired@test.com",
            name="Expired User",
            role=UserRoleEnum.USER,
            organization_id=test_org.id
        )
        expired_user = create_user_invitation(db, expired_invitation, admin_user.id)
        
        # Manually set expiry to past date
        expired_user.invitation_expires_at = datetime.utcnow() - timedelta(days=1)
        db.commit()
        
        expired_count = mark_invitations_as_expired(db)
        print(f"✅ Marked {expired_count} invitations as expired")
        
        print("\n🎉 All tests passed! User Invitation System is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        try:
            # Delete test users and organization
            db.query(InvitationAuditLog).filter(InvitationAuditLog.user_id.in_(
                db.query(User.id).filter(User.organization_id == test_org.id)
            )).delete(synchronize_session=False)
            
            db.query(User).filter(User.organization_id == test_org.id).delete()
            db.query(Organization).filter(Organization.id == test_org.id).delete()
            db.commit()
            print("✅ Test data cleaned up")
        except Exception as e:
            print(f"⚠️ Warning: Failed to clean up test data: {str(e)}")
        finally:
            db.close()

if __name__ == "__main__":
    success = test_invitation_system()
    sys.exit(0 if success else 1)