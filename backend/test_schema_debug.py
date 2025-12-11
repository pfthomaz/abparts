#!/usr/bin/env python3
"""
Debug script to test schema field definitions
"""

import sys
sys.path.append('/app')

# Import directly from the file
import importlib.util
spec = importlib.util.spec_from_file_location("schemas", "/app/app/schemas.py")
schemas_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schemas_module)

print("Direct import test:")
print("PartBase fields:", list(schemas_module.PartBase.model_fields.keys()))
print("PartCreate fields:", list(schemas_module.PartCreate.model_fields.keys()))

# Test creating a part
data = {
    'part_number': 'test',
    'name': 'test',
    'manufacturer': 'Test Manufacturer',
    'part_code': 'TEST-001',
    'serial_number': 'SN123'
}

try:
    part = schemas_module.PartCreate(**data)
    print("Part created successfully")
    print("Part data:", part.model_dump())
except Exception as e:
    print("Error creating part:", e)