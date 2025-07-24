"""
Unit tests for user CRUD functions, specifically focusing on the set_user_active_status fix.
Tests requirements 1.1, 2.1, 2.2, 2.3 from the user reactivation fix specification.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import User, UserStatus, UserRole, Organization, OrganizationType
from app.crud.users import (
    set_user_active_status, 
    get_user, 
    create_user
)
from app.schemas import UserCreate
from app.auth import get_password_hash


class TestSetUserActiveStatus:
    """Test suite for the set_user_active_status function."""
    
    def test_reactivate_user_success(self, db_session: Session, test_organizations):
        """
        Test successful user reactivation (is_active=True scenario).
        Requirements: 1.1, 2.1, 2.2
        """
        # Create an inactive user
        user = User(
            username="inactive_user",
            email="inactive@test.com",
            password_hash=get_password_hash("password123"),
            name="Inactive User",
            role=UserRole.user,
            user_status=UserStatus.inactive,
            organization_id=test_organizations["customer1"].id,
            is_active=False
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Verify initial state
        assert user.is_active is False
        assert user.user_status == UserStatus.inactive
        
        # Reactivate the user
        result = set_user_active_status(db_session, user.id, True)
        
        # Verify the function returns the updated user
        assert result is not None
        assert result.id == user.id
        
        # Verify both status fields are synchronized correctly
        assert result.is_active is True
        assert result.user_status == UserStatus.active
        
        # Verify updated_at timestamp was updated
        assert result.updated_at > user.created_at
        
        # Verify changes are persisted in database
        db_user = get_user(db_session, user.id)
        assert db_user.is_active is True
        assert db_user.user_status == UserStatus.active

    def test_deactivate_user_success(self, db_session: Session, test_organizations):
        """
        Test successful user deactivation (is_active=False scenario).
        Requirements: 1.1, 2.1, 2.2
        """
        # Create an active user
        user = User(
            username="active_user",
            email="active@test.com",
            password_hash=get_password_hash("password123"),
            name="Active User",
            role=UserRole.user,
            user_status=UserStatus.active,
            organization_id=test_organizations["customer1"].id,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Verify initial state
        assert user.is_active is True
        assert user.user_status == UserStatus.active
        
        # Deactivate the user
        result = set_user_active_status(db_session, user.id, False)
        
        # Verify the function returns the updated user
        assert result is not None
        assert result.id == user.id
        
        # Verify both status fields are synchronized correctly
        assert result.is_active is False
        assert result.user_status == UserStatus.inactive
        
        # Verify updated_at timestamp was updated
        assert result.updated_at > user.created_at
        
        # Verify changes are persisted in database
        db_user = get_user(db_session, user.id)
        assert db_user.is_active is False
        assert db_user.user_status == UserStatus.inactive

    def test_user_not_found_error(self, db_session: Session):
        """
        Test error condition when user is not found.
        Requirements: 1.1, 2.1
        """
        # Generate a random UUID that doesn't exist
        non_existent_user_id = uuid.uuid4()
        
        # Attempt to set status for non-existent user
        result = set_user_active_status(db_session, non_existent_user_id, True)
        
        # Verify function returns None for non-existent user
        assert result is None

    def test_reactivate_already_active_user(self, db_session: Session, test_organizations):
        """
        Test reactivating a user who is already active.
        Requirements: 2.1, 2.2
        """
        # Create an already active user
        user = User(
            username="already_active",
            email="already_active@test.com",
            password_hash=get_password_hash("password123"),
            name="Already Active User",
            role=UserRole.user,
            user_status=UserStatus.active,
            organization_id=test_organizations["customer1"].id,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        original_updated_at = user.updated_at
        
        # Reactivate the already active user
        result = set_user_active_status(db_session, user.id, True)
        
        # Verify the function still works correctly
        assert result is not None
        assert result.is_active is True
        assert result.user_status == UserStatus.active
        
        # Verify updated_at timestamp was still updated
        assert result.updated_at > original_updated_at

    def test_deactivate_already_inactive_user(self, db_session: Session, test_organizations):
        """
        Test deactivating a user who is already inactive.
        Requirements: 2.1, 2.2
        """
        # Create an already inactive user
        user = User(
            username="already_inactive",
            email="already_inactive@test.com",
            password_hash=get_password_hash("password123"),
            name="Already Inactive User",
            role=UserRole.user,
            user_status=UserStatus.inactive,
            organization_id=test_organizations["customer1"].id,
            is_active=False
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        original_updated_at = user.updated_at
        
        # Deactivate the already inactive user
        result = set_user_active_status(db_session, user.id, False)
        
        # Verify the function still works correctly
        assert result is not None
        assert result.is_active is False
        assert result.user_status == UserStatus.inactive
        
        # Verify updated_at timestamp was still updated
        assert result.updated_at > original_updated_at

    def test_status_field_synchronization_consistency(self, db_session: Session, test_organizations):
        """
        Test that both status fields are always synchronized correctly.
        Requirements: 2.1, 2.2, 2.3
        """
        # Create a user with inconsistent initial state (simulating the bug)
        user = User(
            username="inconsistent_user",
            email="inconsistent@test.com",
            password_hash=get_password_hash("password123"),
            name="Inconsistent User",
            role=UserRole.user,
            user_status=UserStatus.inactive,  # This is inactive
            organization_id=test_organizations["customer1"].id,
            is_active=True  # But this is True (inconsistent state)
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Verify initial inconsistent state
        assert user.is_active is True
        assert user.user_status == UserStatus.inactive
        
        # Fix the inconsistency by setting to active
        result = set_user_active_status(db_session, user.id, True)
        
        # Verify both fields are now consistent
        assert result.is_active is True
        assert result.user_status == UserStatus.active
        
        # Now set to inactive
        result = set_user_active_status(db_session, user.id, False)
        
        # Verify both fields are consistent for inactive state
        assert result.is_active is False
        assert result.user_status == UserStatus.inactive

    def test_transaction_integrity_on_success(self, db_session: Session, test_organizations):
        """
        Test that database transaction is committed properly on success.
        Requirements: 2.3
        """
        # Create a user
        user = User(
            username="transaction_user",
            email="transaction@test.com",
            password_hash=get_password_hash("password123"),
            name="Transaction User",
            role=UserRole.user,
            user_status=UserStatus.inactive,
            organization_id=test_organizations["customer1"].id,
            is_active=False
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Update status
        result = set_user_active_status(db_session, user.id, True)
        
        # Verify changes are committed by querying again in the same session
        fresh_user = get_user(db_session, user.id)
        assert fresh_user is not None
        assert fresh_user.is_active is True
        assert fresh_user.user_status == UserStatus.active

    def test_database_error_handling(self, db_session: Session, test_organizations):
        """
        Test that database errors are properly handled and exceptions are raised.
        Requirements: 2.3
        """
        # Create a user
        user = User(
            username="error_test_user",
            email="error@test.com",
            password_hash=get_password_hash("password123"),
            name="Error Test User",
            role=UserRole.user,
            user_status=UserStatus.inactive,
            organization_id=test_organizations["customer1"].id,
            is_active=False
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        
        # Mock a database error by replacing the commit method
        original_commit = db_session.commit
        
        def mock_commit():
            raise SQLAlchemyError("Simulated database error")
        
        db_session.commit = mock_commit
        
        # Attempt to update status - should raise an exception
        with pytest.raises(SQLAlchemyError, match="Simulated database error"):
            set_user_active_status(db_session, user_id, True)
        
        # Restore original commit method
        db_session.commit = original_commit
        
        # The function should properly propagate database errors
        # This test verifies that the function doesn't silently fail

    def test_multiple_status_changes(self, db_session: Session, test_organizations):
        """
        Test multiple consecutive status changes to ensure consistency.
        Requirements: 2.1, 2.2, 2.3
        """
        # Create a user
        user = User(
            username="multi_change_user",
            email="multichange@test.com",
            password_hash=get_password_hash("password123"),
            name="Multi Change User",
            role=UserRole.user,
            user_status=UserStatus.inactive,
            organization_id=test_organizations["customer1"].id,
            is_active=False
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Activate user
        result1 = set_user_active_status(db_session, user.id, True)
        assert result1.is_active is True
        assert result1.user_status == UserStatus.active
        
        # Deactivate user
        result2 = set_user_active_status(db_session, user.id, False)
        assert result2.is_active is False
        assert result2.user_status == UserStatus.inactive
        
        # Reactivate user again
        result3 = set_user_active_status(db_session, user.id, True)
        assert result3.is_active is True
        assert result3.user_status == UserStatus.active
        
        # Verify final state in database
        final_user = get_user(db_session, user.id)
        assert final_user.is_active is True
        assert final_user.user_status == UserStatus.active

    def test_different_user_roles_and_statuses(self, db_session: Session, test_organizations):
        """
        Test that the function works correctly for users with different roles.
        Requirements: 1.1, 2.1, 2.2
        """
        # Test with admin user
        admin_user = User(
            username="admin_test",
            email="admin@test.com",
            password_hash=get_password_hash("password123"),
            name="Admin User",
            role=UserRole.admin,
            user_status=UserStatus.inactive,
            organization_id=test_organizations["customer1"].id,
            is_active=False
        )
        db_session.add(admin_user)
        
        # Test with super_admin user
        super_admin_user = User(
            username="superadmin_test",
            email="superadmin@test.com",
            password_hash=get_password_hash("password123"),
            name="Super Admin User",
            role=UserRole.super_admin,
            user_status=UserStatus.inactive,
            organization_id=test_organizations["oraseas"].id,
            is_active=False
        )
        db_session.add(super_admin_user)
        
        db_session.commit()
        
        # Test reactivation for admin user
        admin_result = set_user_active_status(db_session, admin_user.id, True)
        assert admin_result.is_active is True
        assert admin_result.user_status == UserStatus.active
        assert admin_result.role == UserRole.admin  # Role should remain unchanged
        
        # Test reactivation for super admin user
        super_admin_result = set_user_active_status(db_session, super_admin_user.id, True)
        assert super_admin_result.is_active is True
        assert super_admin_result.user_status == UserStatus.active
        assert super_admin_result.role == UserRole.super_admin  # Role should remain unchanged