# Maintenance Protocols API Quick Start

## Overview

Quick guide to testing the new Maintenance Protocols API endpoints after running the migration.

## Prerequisites

- Migration completed successfully
- API container restarted
- Super admin user credentials

## Get Your Auth Token

```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=YOUR_EMAIL&password=YOUR_PASSWORD"
```

Save the `access_token` from the response.

## API Endpoints Overview

Base URL: `http://localhost:8000/maintenance-protocols`

### Super Admin Endpoints (Protocol Management)
- `GET /` - List all protocols
- `POST /` - Create protocol
- `GET /{id}` - Get protocol details
- `PUT /{id}` - Update protocol
- `DELETE /{id}` - Delete protocol
- `POST /{id}/duplicate` - Duplicate protocol
- `GET /{id}/checklist-items` - List checklist items
- `POST /{id}/checklist-items` - Add checklist item
- `PUT /{id}/checklist-items/{item_id}` - Update item
- `DELETE /{id}/checklist-items/{item_id}` - Delete item
- `POST /{id}/checklist-items/reorder` - Reorder items

### User Endpoints (Maintenance Recording)
- `GET /for-machine/{machine_id}` - Get protocols for machine
- `POST /executions` - Record maintenance
- `GET /executions/machine/{machine_id}` - Get history
- `GET /reminders/pending` - Get pending reminders
- `PUT /reminders/{id}/acknowledge` - Acknowledge reminder

## Example 1: Create a Daily Protocol

```bash
curl -X POST "http://localhost:8000/maintenance-protocols" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Start of Day",
    "protocol_type": "daily",
    "description": "Morning checklist before starting operations",
    "is_active": true,
    "display_order": 1
  }'
```

Response:
```json
{
  "id": "uuid-here",
  "name": "Daily Start of Day",
  "protocol_type": "daily",
  "service_interval_hours": null,
  "machine_model": null,
  "description": "Morning checklist before starting operations",
  "is_active": true,
  "display_order": 1,
  "checklist_items": [],
  "created_at": "2025-12-04T...",
  "updated_at": "2025-12-04T..."
}
```

## Example 2: Add Checklist Items

```bash
# Add first item
curl -X POST "http://localhost:8000/maintenance-protocols/{PROTOCOL_ID}/checklist-items" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_order": 1,
    "item_description": "Check water level in tank",
    "item_type": "check",
    "item_category": "Pre-operation",
    "is_critical": true,
    "estimated_duration_minutes": 2
  }'

# Add second item
curl -X POST "http://localhost:8000/maintenance-protocols/{PROTOCOL_ID}/checklist-items" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_order": 2,
    "item_description": "Inspect nets for damage",
    "item_type": "check",
    "item_category": "Pre-operation",
    "is_critical": true,
    "estimated_duration_minutes": 5
  }'

# Add item with part
curl -X POST "http://localhost:8000/maintenance-protocols/{PROTOCOL_ID}/checklist-items" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_order": 3,
    "item_description": "Replace filter if needed",
    "item_type": "replacement",
    "item_category": "Maintenance",
    "part_id": "PART_UUID_HERE",
    "estimated_quantity": 1.0,
    "is_critical": false,
    "estimated_duration_minutes": 10
  }'
```

## Example 3: Create a Scheduled Service Protocol

```bash
curl -X POST "http://localhost:8000/maintenance-protocols" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "50 Hour Service",
    "protocol_type": "scheduled",
    "service_interval_hours": 50.0,
    "machine_model": "V3.1B",
    "description": "First scheduled service at 50 operating hours",
    "is_active": true,
    "display_order": 10
  }'
```

## Example 4: List All Protocols

```bash
# List all protocols
curl -X GET "http://localhost:8000/maintenance-protocols" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by type
curl -X GET "http://localhost:8000/maintenance-protocols?protocol_type=daily" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by machine model
curl -X GET "http://localhost:8000/maintenance-protocols?machine_model=V3.1B" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search
curl -X GET "http://localhost:8000/maintenance-protocols?search=daily" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Example 5: Get Protocols for a Machine

```bash
curl -X GET "http://localhost:8000/maintenance-protocols/for-machine/{MACHINE_ID}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

This returns all active protocols applicable to the machine's model.

## Example 6: Record Maintenance Execution

```bash
curl -X POST "http://localhost:8000/maintenance-protocols/executions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "machine_id": "MACHINE_UUID",
    "protocol_id": "PROTOCOL_UUID",
    "performed_date": "2025-12-04T08:00:00",
    "machine_hours_at_service": 125.5,
    "next_service_due_hours": 175.5,
    "status": "completed",
    "notes": "All checks completed successfully",
    "checklist_completions": [
      {
        "checklist_item_id": "ITEM_UUID_1",
        "is_completed": true,
        "completed_at": "2025-12-04T08:05:00"
      },
      {
        "checklist_item_id": "ITEM_UUID_2",
        "is_completed": true,
        "completed_at": "2025-12-04T08:10:00"
      }
    ]
  }'
```

## Example 7: Get Maintenance History

```bash
curl -X GET "http://localhost:8000/maintenance-protocols/executions/machine/{MACHINE_ID}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Example 8: Duplicate a Protocol

```bash
curl -X POST "http://localhost:8000/maintenance-protocols/{PROTOCOL_ID}/duplicate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "new_name": "Daily Start of Day - V4.0",
    "new_machine_model": "V4.0",
    "copy_checklist_items": true
  }'
```

## Example 9: Reorder Checklist Items

```bash
curl -X POST "http://localhost:8000/maintenance-protocols/{PROTOCOL_ID}/checklist-items/reorder" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_orders": [
      {"id": "ITEM_UUID_1", "order": 2},
      {"id": "ITEM_UUID_2", "order": 1},
      {"id": "ITEM_UUID_3", "order": 3}
    ]
  }'
```

## Testing with Swagger UI

The easiest way to test is using the interactive API docs:

1. Go to: `http://localhost:8000/docs`
2. Click "Authorize" button
3. Enter your token: `Bearer YOUR_TOKEN`
4. Navigate to "Maintenance Protocols" section
5. Try out the endpoints interactively

## Sample Data Setup Script

Create a file `setup_maintenance_data.sh`:

```bash
#!/bin/bash

TOKEN="YOUR_TOKEN_HERE"
BASE_URL="http://localhost:8000/maintenance-protocols"

# Create Daily Start of Day protocol
DAILY_START=$(curl -s -X POST "$BASE_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Start of Day",
    "protocol_type": "daily",
    "description": "Morning checklist",
    "is_active": true,
    "display_order": 1
  }' | jq -r '.id')

echo "Created Daily Start protocol: $DAILY_START"

# Add checklist items
curl -s -X POST "$BASE_URL/$DAILY_START/checklist-items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_order": 1,
    "item_description": "Check water level",
    "item_type": "check",
    "is_critical": true
  }' > /dev/null

curl -s -X POST "$BASE_URL/$DAILY_START/checklist-items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_order": 2,
    "item_description": "Inspect nets",
    "item_type": "check",
    "is_critical": true
  }' > /dev/null

echo "Added checklist items"

# Create Daily End of Day protocol
DAILY_END=$(curl -s -X POST "$BASE_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily End of Day",
    "protocol_type": "daily",
    "description": "Evening shutdown checklist",
    "is_active": true,
    "display_order": 2
  }' | jq -r '.id')

echo "Created Daily End protocol: $DAILY_END"

# Create 50h service
SERVICE_50=$(curl -s -X POST "$BASE_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "50 Hour Service",
    "protocol_type": "scheduled",
    "service_interval_hours": 50.0,
    "description": "First scheduled service",
    "is_active": true,
    "display_order": 10
  }' | jq -r '.id')

echo "Created 50h Service protocol: $SERVICE_50"

echo "✅ Sample data created successfully!"
```

## Common Issues

### 403 Forbidden
- Make sure you're using a super admin account for protocol management
- Regular users can only view protocols and record executions

### 404 Not Found
- Check that the protocol/item ID is correct
- Verify the migration ran successfully

### 400 Bad Request
- Check the request body matches the schema
- Verify required fields are included
- Check data types (UUIDs, decimals, etc.)

## Next Steps

1. Create your daily protocols
2. Add checklist items
3. Create scheduled service protocols
4. Test recording maintenance executions
5. Build the frontend UI

## API Documentation

Full interactive documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
