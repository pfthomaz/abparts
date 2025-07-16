#!/usr/bin/env python3
"""
Test script for user profile and self-service management functionality.
This script can be run inside the Docker container to verify the implementation.
"""

import sys
import os
import json

def test_imports():
    """Test that all required modules can be imported."""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        
        # Test core imports
        from app import schemas, models, crud
        from app.routers import users
        from app import tasks
        
        print("✅ All core modules imported successfully")
        
        # Test specific schema classes
        required_schemas = [
            'UserProfileUpdate',
            'UserPasswordChange', 
            'UserProfileResponse',
            'PasswordResetRequest',
            'PasswordResetConfirm',
            'EmailVerificationRequest',
            'EmailVerificationConfirm',
            'UserAccountStatusUpdate'
        ]
        
        for schema_name in required_schemas:
            if hasattr(schemas, schema_name):
                print(f"✅ Schema {schema_name} is available")
            else:
                print(f"❌ Schema {schema_name} is missing")
                return False
        
        # Test CRUD functions
        required_crud_functions = [
            'update_user_profile',
            'change_user_password',
            'request_password_reset',
            'confirm_password_reset',
            'request_email_verification',
            'confirm_email_verification',
            'get_user_profile_with_organization',
            'update_user_status'
        ]
        
        for func_name in required_crud_functions:
            if hasattr(crud.users, func_name):
                print(f"✅ CRUD function {func_name} is available")
            else:
                print(f"❌ CRUD function {func_name} is missing")
                return False
        
        # Test email tasks
        required_tasks = [
            'send_password_reset_email',
            'send_email_verification_email'
        ]
        
        for task_name in required_tasks:
            if hasattr(tasks, task_name):
                print(f"✅ Email task {task_name} is available")
            else:
                print(f"❌ Email task {task_name} is missing")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_model_fields():
    """Test that the User model has the required new fields."""
    try:
        from app.models import User
        
        # Check if User model has new fields
        required_fields = [
            'email_verification_token',
            'email_verification_expires_at',
            'pending_email'
        ]
        
        user_columns = [column.name for column in User.__table__.columns]
        
        for field in required_fields:
            if field in user_columns:
                print(f"✅ User model has field: {field}")
            else:
                print(f"❌ User model missing field: {field}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking model fields: {e}")
        return False

def test_docker_environment():
    """Test Docker-specific environment variables and configurations."""
    
    # Check for required environment variables
    required_env_vars = [
        'DATABASE_URL',
        'REDIS_URL'
    ]
    
    optional_env_vars = [
        'SMTP_SERVER',
        'SMTP_USERNAME', 
        'SMTP_PASSWORD',
        'BASE_URL'
    ]
    
    print("Checking environment variables...")
    
    for var in required_env_vars:
        if os.getenv(var):
            print(f"✅ Required env var {var} is set")
        else:
            print(f"⚠️  Required env var {var} is not set")
    
    for var in optional_env_vars:
        if os.getenv(var):
            print(f"✅ Optional env var {var} is set")
        else:
            print(f"ℹ️  Optional env var {var} is not set (needed for email functionality)")

def test_api_structure():
    """Test that the API structure is correct without making actual HTTP calls."""
    try:
        from app.main import app
        from fastapi.openapi.utils import get_openapi
        
        # Generate OpenAPI schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        paths = openapi_schema.get("paths", {})
        
        # Check that our new endpoints are defined
        expected_endpoints = [
            "/users/me/profile",
            "/users/me/change-password", 
            "/users/request-password-reset",
            "/users/confirm-password-reset",
            "/users/me/request-email-verification",
            "/users/confirm-email-verification"
        ]
        
        for endpoint in expected_endpoints:
            if endpoint in paths:
                print(f"✅ Endpoint {endpoint} is properly defined")
            else:
                print(f"❌ Endpoint {endpoint} not found in API schema")
                return False
        
        # Check specific HTTP methods
        method_checks = [
            ("/users/me/profile", "get"),
            ("/users/me/profile", "put"),
            ("/users/me/change-password", "post"),
            ("/users/request-password-reset", "post")
        ]
        
        for endpoint, method in method_checks:
            if endpoint in paths and method in paths[endpoint]:
                print(f"✅ {method.upper()} method available for {endpoint}")
            else:
                print(f"❌ {method.upper()} method missing for {endpoint}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API structure: {e}")
        return False

if __name__ == "__main__":
    print("🐳 Docker User Profile Implementation Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    print("\n1. Testing imports...")
    if not test_imports():
        all_tests_passed = False
    
    print("\n2. Testing model fields...")
    if not test_model_fields():
        all_tests_passed = False
    
    print("\n3. Testing Docker environment...")
    test_docker_environment()  # This is informational, doesn't fail
    
    print("\n4. Testing API structure...")
    if not test_api_structure():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    
    if all_tests_passed:
        print("✅ All tests passed! User profile functionality is properly implemented.")
        print("\n📋 Next steps:")
        print("1. Run database migration: docker-compose exec backend alembic upgrade head")
        print("2. Configure email environment variables")
        print("3. Ensure Celery worker is running for email tasks")
        print("4. Test endpoints with actual HTTP requests")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the implementation.")
        sys.exit(1)