#!/usr/bin/env python3
"""
Automated script to add translation support to all React components.
This script will:
1. Add useTranslation import if missing
2. Add const { t } = useTranslation() if missing
3. Replace common hardcoded strings with t() calls
"""

import os
import re
from pathlib import Path

# Common text patterns to translate
TRANSLATIONS = {
    # Common buttons and actions
    r'"Save"': 't("common.save")',
    r'"Cancel"': 't("common.cancel")',
    r'"Delete"': 't("common.delete")',
    r'"Edit"': 't("common.edit")',
    r'"Add"': 't("common.add")',
    r'"Create"': 't("common.create")',
    r'"Update"': 't("common.update")',
    r'"Search"': 't("common.search")',
    r'"Filter"': 't("common.filter")',
    r'"Export"': 't("common.export")',
    r'"Loading\.\.\."': 't("common.loading")',
    r'"Error"': 't("common.error")',
    r'"Success"': 't("common.success")',
    r'"Close"': 't("common.close")',
    r'"Submit"': 't("common.submit")',
    r'"Reset"': 't("common.reset")',
    r'"Clear"': 't("common.clear")',
    r'"Select"': 't("common.select")',
    r'"Actions"': 't("common.actions")',
    r'"Details"': 't("common.details")',
    r'"View"': 't("common.view")',
    r'"Refresh"': 't("common.refresh")',
    r'"Back"': 't("common.back")',
    r'"Next"': 't("common.next")',
    r'"Previous"': 't("common.previous")',
    
    # Navigation
    r'"Dashboard"': 't("navigation.dashboard")',
    r'"Organizations"': 't("navigation.organizations")',
    r'"Users"': 't("navigation.users")',
    r'"Parts"': 't("navigation.parts")',
    r'"Inventory"': 't("navigation.inventory")',
    r'"Warehouses"': 't("navigation.warehouses")',
    r'"Machines"': 't("navigation.machines")',
    r'"Orders"': 't("navigation.orders")',
    r'"Stock Adjustments"': 't("navigation.stockAdjustments")',
    r'"Daily Operations"': 't("navigation.dailyOperations")',
    r'"Maintenance"': 't("navigation.maintenance")',
    
    # Status
    r'"Active"': 't("common.active")',
    r'"Inactive"': 't("common.inactive")',
    r'"Status"': 't("common.status")',
}

def has_use_translation_import(content):
    """Check if file already imports useTranslation"""
    return "useTranslation" in content and "from '../hooks/useTranslation'" in content

def has_use_translation_hook(content):
    """Check if file already uses the useTranslation hook"""
    return re.search(r'const\s+{\s*t\s*}\s*=\s*useTranslation\(\)', content) is not None

def add_use_translation_import(content):
    """Add useTranslation import after other imports"""
    # Find the last import statement
    import_pattern = r"(import\s+.*?from\s+['\"].*?['\"];?\n)"
    imports = list(re.finditer(import_pattern, content))
    
    if imports:
        last_import = imports[-1]
        insert_pos = last_import.end()
        
        # Check if we need to add the import
        if not has_use_translation_import(content):
            new_import = "import { useTranslation } from '../hooks/useTranslation';\n"
            content = content[:insert_pos] + new_import + content[insert_pos:]
    
    return content

def add_use_translation_hook(content):
    """Add const { t } = useTranslation() inside component"""
    # Find function component definition
    component_pattern = r'((?:function|const)\s+\w+\s*(?:=\s*\(.*?\)\s*=>|)\s*(?:\(.*?\))?\s*{)'
    
    match = re.search(component_pattern, content)
    if match and not has_use_translation_hook(content):
        insert_pos = match.end()
        # Add the hook declaration
        hook_code = "\n  const { t } = useTranslation();\n"
        content = content[:insert_pos] + hook_code + content[insert_pos:]
    
    return content

def translate_strings(content):
    """Replace hardcoded strings with t() calls"""
    for pattern, replacement in TRANSLATIONS.items():
        content = re.sub(pattern, replacement, content)
    return content

def process_file(file_path):
    """Process a single React component file"""
    print(f"Processing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Skip if file already heavily uses translations
    if content.count('t("') > 10:
        print(f"  ✓ Already translated")
        return False
    
    # Add import if needed
    if not has_use_translation_import(content):
        content = add_use_translation_import(content)
    
    # Add hook if needed
    if not has_use_translation_hook(content):
        content = add_use_translation_hook(content)
    
    # Translate strings
    content = translate_strings(content)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Updated")
        return True
    else:
        print(f"  - No changes needed")
        return False

def main():
    """Main function to process all React components"""
    frontend_dir = Path('frontend/src')
    
    # Find all .js and .jsx files
    component_files = []
    for ext in ['*.js', '*.jsx']:
        component_files.extend(frontend_dir.rglob(ext))
    
    # Filter to only component files (exclude tests, configs, etc.)
    component_files = [
        f for f in component_files 
        if not any(x in str(f) for x in ['test', 'spec', 'config', 'setupTests'])
    ]
    
    print(f"Found {len(component_files)} component files\n")
    
    updated_count = 0
    for file_path in sorted(component_files):
        if process_file(file_path):
            updated_count += 1
    
    print(f"\n✅ Complete! Updated {updated_count} files")

if __name__ == '__main__':
    main()
