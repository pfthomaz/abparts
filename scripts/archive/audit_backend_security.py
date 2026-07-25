#!/usr/bin/env python3
"""
Comprehensive Backend Security Audit
Checks ALL endpoints for proper organization-scoped filtering
"""

import os
import re
from pathlib import Path

# Endpoints that MUST have organization filtering
CRITICAL_ENDPOINTS = {
    'machines': {
        'file': 'backend/app/routers/machines.py',
        'crud': 'backend/app/crud/machines.py',
        'org_field': 'customer_organization_id'
    },
    'parts': {
        'file': 'backend/app/routers/parts.py',
        'crud': 'backend/app/crud/parts.py',
        'org_field': 'organization_id'
    },
    'warehouses': {
        'file': 'backend/app/routers/warehouses.py',
        'crud': 'backend/app/crud/warehouses.py',
        'org_field': 'organization_id'
    },
    'inventory': {
        'file': 'backend/app/routers/inventory.py',
        'crud': 'backend/app/crud/inventory.py',
        'org_field': 'organization_id'
    },
    'customer_orders': {
        'file': 'backend/app/routers/customer_orders.py',
        'crud': 'backend/app/crud/customer_orders.py',
        'org_field': 'customer_organization_id'
    },
    'supplier_orders': {
        'file': 'backend/app/routers/supplier_orders.py',
        'crud': 'backend/app/crud/supplier_orders.py',
        'org_field': 'ordering_organization_id'
    },
    'stock_adjustments': {
        'file': 'backend/app/routers/stock_adjustments.py',
        'crud': 'backend/app/crud/stock_adjustments.py',
        'org_field': 'organization_id'
    },
    'transactions': {
        'file': 'backend/app/routers/transactions.py',
        'crud': 'backend/app/crud/transactions.py',
        'org_field': 'organization_id'
    },
    'maintenance_protocols': {
        'file': 'backend/app/routers/maintenance_protocols.py',
        'crud': 'backend/app/crud/maintenance_protocols.py',
        'org_field': 'organization_id'
    },
    'maintenance_executions': {
        'file': 'backend/app/routers/maintenance_executions.py',
        'crud': 'backend/app/crud/maintenance_executions.py',
        'org_field': 'organization_id'
    },
    'net_cleaning_records': {
        'file': 'backend/app/routers/net_cleaning_records.py',
        'crud': 'backend/app/crud/net_cleaning_records.py',
        'org_field': 'organization_id'
    },
    'farm_sites': {
        'file': 'backend/app/routers/farm_sites.py',
        'crud': 'backend/app/crud/farm_sites.py',
        'org_field': 'organization_id'
    },
    'nets': {
        'file': 'backend/app/routers/nets.py',
        'crud': 'backend/app/crud/nets.py',
        'org_field': 'organization_id'
    }
}

def check_file_exists(filepath):
    """Check if file exists"""
    return os.path.exists(filepath)

def check_super_admin_check(content):
    """Check if file has super_admin permission checking"""
    patterns = [
        r'is_super_admin\(.*?\)',
        r'permission_checker\.is_super_admin',
        r'current_user\.role\s*==\s*["\']super_admin["\']'
    ]
    for pattern in patterns:
        if re.search(pattern, content):
            return True
    return False

def check_org_filtering(content, org_field):
    """Check if file filters by organization_id"""
    patterns = [
        rf'{org_field}\s*==\s*.*?organization_id',
        rf'filter.*?{org_field}',
        rf'\.organization_id\)',
        r'current_user\.organization_id'
    ]
    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False

def check_get_endpoint(content):
    """Check if file has GET endpoint for listing"""
    patterns = [
        r'@router\.get\(["\']\/["\']',
        r'def\s+get_\w+\(',
        r'async\s+def\s+get_\w+\('
    ]
    for pattern in patterns:
        if re.search(pattern, content):
            return True
    return False

def audit_endpoint(name, config):
    """Audit a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Auditing: {name}")
    print(f"{'='*60}")
    
    results = {
        'name': name,
        'router_exists': False,
        'crud_exists': False,
        'has_get_endpoint': False,
        'has_super_admin_check': False,
        'has_org_filtering': False,
        'status': 'UNKNOWN'
    }
    
    # Check router file
    router_file = config['file']
    if check_file_exists(router_file):
        results['router_exists'] = True
        print(f"✅ Router file exists: {router_file}")
        
        with open(router_file, 'r') as f:
            router_content = f.read()
        
        results['has_get_endpoint'] = check_get_endpoint(router_content)
        results['has_super_admin_check'] = check_super_admin_check(router_content)
        results['has_org_filtering'] = check_org_filtering(router_content, config['org_field'])
        
        if results['has_get_endpoint']:
            print(f"✅ Has GET endpoint")
        else:
            print(f"⚠️  No GET endpoint found")
        
        if results['has_super_admin_check']:
            print(f"✅ Has super_admin check")
        else:
            print(f"❌ MISSING super_admin check")
        
        if results['has_org_filtering']:
            print(f"✅ Has organization filtering")
        else:
            print(f"❌ MISSING organization filtering")
    else:
        print(f"❌ Router file NOT FOUND: {router_file}")
    
    # Check CRUD file
    crud_file = config['crud']
    if check_file_exists(crud_file):
        results['crud_exists'] = True
        print(f"✅ CRUD file exists: {crud_file}")
        
        with open(crud_file, 'r') as f:
            crud_content = f.read()
        
        crud_has_org_filter = check_org_filtering(crud_content, config['org_field'])
        if crud_has_org_filter:
            print(f"✅ CRUD has organization filtering")
        else:
            print(f"⚠️  CRUD may not have organization filtering")
    else:
        print(f"⚠️  CRUD file NOT FOUND: {crud_file}")
    
    # Determine status
    if results['router_exists'] and results['has_get_endpoint']:
        if results['has_super_admin_check'] and results['has_org_filtering']:
            results['status'] = 'SECURE'
        elif results['has_super_admin_check'] or results['has_org_filtering']:
            results['status'] = 'PARTIAL'
        else:
            results['status'] = 'VULNERABLE'
    else:
        results['status'] = 'N/A'
    
    return results

def main():
    print("\n" + "="*60)
    print("BACKEND SECURITY AUDIT")
    print("="*60)
    print("\nChecking organization-scoped filtering on ALL endpoints...")
    
    all_results = []
    
    for name, config in CRITICAL_ENDPOINTS.items():
        results = audit_endpoint(name, config)
        all_results.append(results)
    
    # Summary
    print("\n" + "="*60)
    print("AUDIT SUMMARY")
    print("="*60)
    
    secure = [r for r in all_results if r['status'] == 'SECURE']
    partial = [r for r in all_results if r['status'] == 'PARTIAL']
    vulnerable = [r for r in all_results if r['status'] == 'VULNERABLE']
    na = [r for r in all_results if r['status'] == 'N/A']
    
    print(f"\n✅ SECURE: {len(secure)}")
    for r in secure:
        print(f"   - {r['name']}")
    
    if partial:
        print(f"\n⚠️  PARTIAL SECURITY: {len(partial)}")
        for r in partial:
            print(f"   - {r['name']}")
    
    if vulnerable:
        print(f"\n❌ VULNERABLE: {len(vulnerable)}")
        for r in vulnerable:
            print(f"   - {r['name']}")
    
    if na:
        print(f"\n⚪ NOT APPLICABLE: {len(na)}")
        for r in na:
            print(f"   - {r['name']}")
    
    # Recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    if vulnerable:
        print("\n🚨 CRITICAL: Fix vulnerable endpoints immediately!")
        for r in vulnerable:
            print(f"\n{r['name']}:")
            if not r['has_super_admin_check']:
                print("  - Add super_admin permission check")
            if not r['has_org_filtering']:
                print("  - Add organization_id filtering")
    
    if partial:
        print("\n⚠️  WARNING: Review partial security endpoints")
        for r in partial:
            print(f"\n{r['name']}:")
            if not r['has_super_admin_check']:
                print("  - Add super_admin permission check")
            if not r['has_org_filtering']:
                print("  - Add organization_id filtering")
    
    print("\n" + "="*60)
    
    # Return exit code
    if vulnerable:
        return 1
    elif partial:
        return 2
    else:
        return 0

if __name__ == "__main__":
    exit(main())
