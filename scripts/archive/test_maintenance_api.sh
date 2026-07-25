#!/bin/bash

# Test script for Maintenance Protocols API
# Make sure you have a super admin user created

BASE_URL="http://localhost:8000"
EMAIL="your-super-admin-email@example.com"
PASSWORD="your-password"

echo "🔐 Getting authentication token..."
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD")

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token. Response:"
    echo $TOKEN_RESPONSE
    echo ""
    echo "Please update EMAIL and PASSWORD in this script with your super admin credentials."
    exit 1
fi

echo "✅ Token obtained!"
echo ""

# Create Daily Start of Day Protocol
echo "📋 Creating 'Daily Start of Day' protocol..."
DAILY_START=$(curl -s -X POST "$BASE_URL/maintenance-protocols" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Start of Day",
    "protocol_type": "daily",
    "description": "Morning checklist before starting operations",
    "is_active": true,
    "display_order": 1
  }')

DAILY_START_ID=$(echo $DAILY_START | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo "✅ Created protocol: $DAILY_START_ID"
echo ""

# Add checklist items to Daily Start
echo "📝 Adding checklist items to Daily Start of Day..."

curl -s -X POST "$BASE_URL/maintenance-protocols/$DAILY_START_ID/checklist-items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_order": 1,
    "item_description": "Check water level in tank",
    "item_type": "check",
    "item_category": "Pre-operation",
    "is_critical": true,
    "estimated_duration_minutes": 2
  }' > /dev/null

curl -s -X POST "$BASE_URL/maintenance-protocols/$DAILY_START_ID/checklist-items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_order": 2,
    "item_description": "Inspect nets for damage or wear",
    "item_type": "check",
    "item_category": "Pre-operation",
    "is_critical": true,
    "estimated_duration_minutes": 5
  }' > /dev/null

curl -s -X POST "$BASE_URL/maintenance-protocols/$DAILY_START_ID/checklist-items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_order": 3,
    "item_description": "Check pump operation",
    "item_type": "check",
    "item_category": "Pre-operation",
    "is_critical": true,
    "estimated_duration_minutes": 3
  }' > /dev/null

echo "✅ Added 3 checklist items"
echo ""

# Create Daily End of Day Protocol
echo "📋 Creating 'Daily End of Day' protocol..."
DAILY_END=$(curl -s -X POST "$BASE_URL/maintenance-protocols" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily End of Day",
    "protocol_type": "daily",
    "description": "Evening shutdown checklist",
    "is_active": true,
    "display_order": 2
  }')

DAILY_END_ID=$(echo $DAILY_END | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo "✅ Created protocol: $DAILY_END_ID"
echo ""

# Add checklist items to Daily End
echo "📝 Adding checklist items to Daily End of Day..."

curl -s -X POST "$BASE_URL/maintenance-protocols/$DAILY_END_ID/checklist-items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_order": 1,
    "item_description": "Clean nets thoroughly",
    "item_type": "service",
    "item_category": "Cleaning",
    "is_critical": true,
    "estimated_duration_minutes": 15
  }' > /dev/null

curl -s -X POST "$BASE_URL/maintenance-protocols/$DAILY_END_ID/checklist-items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_order": 2,
    "item_description": "Drain and clean water tank",
    "item_type": "service",
    "item_category": "Cleaning",
    "is_critical": true,
    "estimated_duration_minutes": 10
  }' > /dev/null

curl -s -X POST "$BASE_URL/maintenance-protocols/$DAILY_END_ID/checklist-items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_order": 3,
    "item_description": "Record machine hours",
    "item_type": "check",
    "item_category": "Documentation",
    "is_critical": true,
    "estimated_duration_minutes": 2
  }' > /dev/null

echo "✅ Added 3 checklist items"
echo ""

# Create 50h Service Protocol
echo "📋 Creating '50 Hour Service' protocol..."
SERVICE_50=$(curl -s -X POST "$BASE_URL/maintenance-protocols" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "50 Hour Service",
    "protocol_type": "scheduled",
    "service_interval_hours": 50.0,
    "machine_model": "V3.1B",
    "description": "First scheduled service at 50 operating hours",
    "is_active": true,
    "display_order": 10
  }')

SERVICE_50_ID=$(echo $SERVICE_50 | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo "✅ Created protocol: $SERVICE_50_ID"
echo ""

# Add checklist items to 50h Service
echo "📝 Adding checklist items to 50h Service..."

curl -s -X POST "$BASE_URL/maintenance-protocols/$SERVICE_50_ID/checklist-items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_order": 1,
    "item_description": "Inspect and clean pump filter",
    "item_type": "service",
    "item_category": "Pump Maintenance",
    "is_critical": true,
    "estimated_duration_minutes": 20
  }' > /dev/null

curl -s -X POST "$BASE_URL/maintenance-protocols/$SERVICE_50_ID/checklist-items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_order": 2,
    "item_description": "Check all hose connections",
    "item_type": "check",
    "item_category": "Safety Check",
    "is_critical": true,
    "estimated_duration_minutes": 10
  }' > /dev/null

curl -s -X POST "$BASE_URL/maintenance-protocols/$SERVICE_50_ID/checklist-items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_order": 3,
    "item_description": "Lubricate moving parts",
    "item_type": "service",
    "item_category": "Lubrication",
    "is_critical": false,
    "estimated_duration_minutes": 15
  }' > /dev/null

echo "✅ Added 3 checklist items"
echo ""

# List all protocols
echo "📋 Listing all protocols..."
curl -s -X GET "$BASE_URL/maintenance-protocols" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo "🎉 Sample data created successfully!"
echo ""
echo "You can now:"
echo "  1. View protocols at: http://localhost:8000/docs"
echo "  2. Test the endpoints in the Swagger UI"
echo "  3. Start building the frontend UI"
