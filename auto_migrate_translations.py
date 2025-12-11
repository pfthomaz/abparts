#!/usr/bin/env python3
"""
Automatic translation migration script
This script will add translation support to React components
"""

import re
import os
from pathlib import Path

# Translation mappings - common English strings to translation keys
TRANSLATIONS = {
    # Common buttons
    '"Save"': "t('common.save')",
    '"Cancel"': "t('common.cancel')",
    '"Delete"': "t('common.delete')",
    '"Edit"': "t('common.edit')",
    '"Add"': "t('common.add')",
    '"Create"': "t('common.create')",
    '"Update"': "t('common.update')",
    '"Search"': "t('common.search')",
    '"Filter"': "t('common.filter')",
    '"Export"': "t('common.export')",
    '"Close"': "t('common.close')",
    '"Submit"': "t('common.submit')",
    '"Reset"': "t('common.reset')",
    '"Loading..."': "t('common.loading')",
    '"Active"': "t('common.active')",
    '"Inactive"': "t('common.inactive')",
    
    # Navigation
    '"Dashboard"': "t('navigation.dashboard')",
    '"Organizations"': "t('navigation.organizations')",
    '"Users"': "t('navigation.users')",
    '"Parts"': "t('navigation.parts')",
    '"Inventory"': "t('navigation.inventory')",
    '"Warehouses"': "t('navigation.warehouses')",
    '"Machines"': "t('navigation.machines')",
    '"Orders"': "t('navigation.orders')",
    '"Stock Adjustments"': "t('navigation.stockAdjustments')",
    '"Maintenance"': "t('navigation.maintenance')",
    '"Reports"': "t('navigation.reports')",
    '"Settings"': "t('navigation.settings')",
    '"Profile"': "t('navigation.profile')",
    
    # User management
    '"Username"': "t('users.username')",
    '"Email"': "t('users.email')",
    '"Name"': "t('users.name')",
    '"Role"': "t('users.role')",
    '"Organization"': "t('users.organization')",
}

def add_translation_import(content):
    """Add useTranslation import if not present"""
    if "useTranslation" in content:
        return content
    
    # Find the last import statement
    import_pattern = r"(import .+ from .+;)\n"
    imports = list(re.finditer(import_pattern, content))
    
    if imports:
        last_import = imports[-1]
        insert_pos = last_import.end()
        new_import = "import { useTranslation } from '../hooks/useTranslation';\n"
        content = content[:insert_pos] + new_import + content[insert_pos:]
    
    return content

def add_translation_hook(content):
    """Add const { t } = useTranslation(); if not present"""
    if "const { t } = useTranslation()" in content:
        return content
    
    # Find function component declaration
    component_pattern = r"(const \w+ = \([^)]*\) => \{)"
    match = re.search(component_pattern, content)
    
    if match:
        insert_pos = match.end()
        hook_line = "\n  const { t } = useTranslation();\n"
        content = content[:insert_pos] + hook_line + content[insert_pos:]
    
    return content

def replace_strings(content):
    """Replace hardcoded strings with translation calls"""
    for english, translation in TRANSLATIONS.items():
        # Replace in JSX context (between > and <)
        content = re.sub(
            r'>' + english + r'<',
            '>{' + translation + '}<',
            content
        )
        # Replace in button text
        content = re.sub(
            r'(className="[^"]*">)' + english + r'(<)',
            r'\1{' + translation + r'}\2',
            content
        )
    
    return content

def migrate_file(filepath):
    """Migrate a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Add import
        content = add_translation_import(content)
        
        # Add hook
        content = add_translation_hook(content)
        
        # Replace strings
        content = replace_strings(content)
        
        # Only write if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Main migration function"""
    print("🌍 Automatic Translation Migration")
    print("=" * 50)
    
    # Directories to process
    directories = [
        'frontend/src/pages',
        'frontend/src/components'
    ]
    
    migrated_files = []
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.js') or file.endswith('.jsx'):
                    filepath = os.path.join(root, file)
                    
                    # Skip test files and demo
                    if 'test' in file.lower() or 'demo' in file.lower():
                        continue
                    
                    if migrate_file(filepath):
                        migrated_files.append(filepath)
                        print(f"✅ Migrated: {filepath}")
    
    print("\n" + "=" * 50)
    print(f"✅ Migration complete! {len(migrated_files)} files updated")
    print("\nMigrated files:")
    for f in migrated_files:
        print(f"  - {f}")
    
    print("\n⚠️  IMPORTANT: Review the changes and test thoroughly!")
    print("Some strings may need manual adjustment.")

if __name__ == "__main__":
    main()
