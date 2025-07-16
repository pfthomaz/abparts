#!/usr/bin/env python3
"""
Simple script to validate the updated models file syntax without requiring database connection.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    # Try to import the models to check for syntax errors
    from backend.app import models
    print("✅ Models file syntax is valid")
    
    # Check if all expected models exist
    expected_models = [
        'Organization', 'User', 'Machine', 'Part', 'Warehouse', 'Inventory',
        'SupplierOrder', 'SupplierOrderItem', 'CustomerOrder', 'CustomerOrderItem',
        'PartUsage', 'Transaction', 'StockAdjustment'
    ]
    
    expected_enums = [
        'OrganizationType', 'PartType', 'UserRole', 'UserStatus', 
        'TransactionType', 'StockAdjustmentReason'
    ]
    
    missing_models = []
    for model_name in expected_models:
        if not hasattr(models, model_name):
            missing_models.append(model_name)
    
    missing_enums = []
    for enum_name in expected_enums:
        if not hasattr(models, enum_name):
            missing_enums.append(enum_name)
    
    if missing_models:
        print(f"❌ Missing models: {', '.join(missing_models)}")
    else:
        print("✅ All expected models found")
        
    if missing_enums:
        print(f"❌ Missing enums: {', '.join(missing_enums)}")
    else:
        print("✅ All expected enums found")
    
    # Test enum values
    print("\n📋 Enum Values:")
    print(f"OrganizationType: {[e.value for e in models.OrganizationType]}")
    print(f"PartType: {[e.value for e in models.PartType]}")
    print(f"UserRole: {[e.value for e in models.UserRole]}")
    print(f"UserStatus: {[e.value for e in models.UserStatus]}")
    print(f"TransactionType: {[e.value for e in models.TransactionType]}")
    
    # Test hybrid properties
    print("\n🔧 Testing hybrid properties...")
    org = models.Organization()
    org.organization_type = models.OrganizationType.ORASEAS_EE
    print(f"✅ Organization.is_oraseas_ee works: {org.is_oraseas_ee}")
    
    user = models.User()
    user.role = models.UserRole.SUPER_ADMIN
    print(f"✅ User.is_super_admin works: {user.is_super_admin}")
    
    print("\n✅ Models validation completed successfully")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except SyntaxError as e:
    print(f"❌ Syntax error in models file: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)