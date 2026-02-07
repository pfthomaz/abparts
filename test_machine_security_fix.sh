#!/bin/bash

# Test script to verify machine security fix
# This script tests that admin users only see their organization's machines

echo "=========================================="
echo "Machine Security Fix - Verification Test"
echo "=========================================="
echo ""

# Get Kefalonia organization ID
echo "1. Getting Kefalonia Fisheries organization ID..."
KEF_ORG_ID=$(docker-compose exec -T db psql -U abparts_user -d abparts_dev -t -c "SELECT id FROM organizations WHERE name LIKE '%Kefalonia%' LIMIT 1;" | tr -d ' ')
echo "   Kefalonia Org ID: $KEF_ORG_ID"
echo ""

# Count total machines in database
echo "2. Counting total machines in database..."
TOTAL_MACHINES=$(docker-compose exec -T db psql -U abparts_user -d abparts_dev -t -c "SELECT COUNT(*) FROM machines;" | tr -d ' ')
echo "   Total machines: $TOTAL_MACHINES"
echo ""

# Count Kefalonia machines
echo "3. Counting Kefalonia machines..."
KEF_MACHINES=$(docker-compose exec -T db psql -U abparts_user -d abparts_dev -t -c "SELECT COUNT(*) FROM machines WHERE customer_organization_id = '$KEF_ORG_ID';" | tr -d ' ')
echo "   Kefalonia machines: $KEF_MACHINES"
echo ""

# List Kefalonia machines
echo "4. Listing Kefalonia machines:"
docker-compose exec -T db psql -U abparts_user -d abparts_dev -c "SELECT name, serial_number, model_type FROM machines WHERE customer_organization_id = '$KEF_ORG_ID' ORDER BY name;"
echo ""

# List Kefalonia admin users
echo "5. Listing Kefalonia admin users:"
docker-compose exec -T db psql -U abparts_user -d abparts_dev -c "SELECT username, role FROM users WHERE organization_id = '$KEF_ORG_ID' ORDER BY username;"
echo ""

echo "=========================================="
echo "Test Instructions:"
echo "=========================================="
echo ""
echo "1. Log out from the application completely"
echo "2. Close the browser tab"
echo "3. Open a new browser tab and go to http://localhost:3000"
echo "4. Log in as one of these Kefalonia admin users:"
echo "   - lefteris"
echo "   - thomas"
echo "   - Zisis"
echo "5. Navigate to the Machines page"
echo "6. Verify you see ONLY $KEF_MACHINES machines (not $TOTAL_MACHINES)"
echo ""
echo "Expected: $KEF_MACHINES machines from Kefalonia Fisheries"
echo "Bug behavior: $TOTAL_MACHINES machines from all organizations"
echo ""
echo "=========================================="
