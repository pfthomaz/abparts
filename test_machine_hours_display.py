#!/usr/bin/env python3
"""
Test script to verify machine hours are being returned in the API response
"""
import requests
import json

API_BASE_URL = "http://localhost:8000"

# You'll need to get a valid token first
# For now, this script shows what to check

print("=" * 60)
print("Machine Hours Display Test")
print("=" * 60)

print("\n1. First, login to get a token:")
print("   curl -X POST http://localhost:8000/token \\")
print("     -d 'username=YOUR_USERNAME&password=YOUR_PASSWORD'")

print("\n2. Then, get machines with the token:")
print("   curl -X GET http://localhost:8000/machines/ \\")
print("     -H 'Authorization: Bearer YOUR_TOKEN' | jq")

print("\n3. Check the response for these fields:")
print("   - latest_hours: should have a number value")
print("   - latest_hours_date: should have a timestamp")
print("   - total_hours_records: should be > 0 for machines with hours")

print("\n4. Example expected response:")
print(json.dumps({
    "id": "machine-uuid",
    "name": "KEF-1",
    "model_type": "V4.0",
    "serial_number": "ABC123",
    "customer_organization_id": "org-uuid",
    "latest_hours": 5000.0,
    "latest_hours_date": "2025-11-17T14:00:00+00:00",
    "days_since_last_hours_record": 0,
    "total_hours_records": 1,
    "customer_organization_name": "Customer Org"
}, indent=2))

print("\n" + "=" * 60)
print("If latest_hours is null, check:")
print("1. Database has machine_hours records")
print("2. machine_id matches between tables")
print("3. Backend logs for any errors")
print("=" * 60)
