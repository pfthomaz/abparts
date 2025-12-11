# Part Usage Fix - Deployment Checklist

## Issue
Part usage records created via PartUsageRecorder show in Transactions but not in Machine Details "Parts Usage" tab.

## Root Cause
1. `create_transaction()` wasn't creating PartUsage records for consumption transactions
2. `get_machine_usage_history()` was hardcoded to return empty list

## Files Changed
- `backend/app/crud/transaction.py` - Added PartUsage record creation
- `backend/app/crud/machines.py` - Enabled usage history query

## Deployment Steps

### 1. Verify Code is Committed
```bash
git status
git log --oneline -3
```

### 2. Pull Latest Code on Production
```bash
cd ~/abparts
git pull
```

### 3. Rebuild and Restart API Container
```bash
sudo docker compose -f docker-compose.prod.yml build api
sudo docker compose -f docker-compose.prod.yml up -d api
```

### 4. Check API Logs for Errors
```bash
sudo docker compose -f docker-compose.prod.yml logs api --tail=100
```

Look for:
- ✅ "Application startup complete"
- ❌ Any Python errors or import failures

### 5. Test with New Part Usage Record
1. Go to Machines page
2. Click "Use Part" on a machine
3. Select warehouse, part, quantity
4. Submit

### 6. Verify in Database
```bash
sudo docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod
```

Then run:
```sql
-- Check if PartUsage record was created
SELECT COUNT(*) FROM part_usage WHERE created_at > NOW() - INTERVAL '5 minutes';

-- Check the latest PartUsage record
SELECT 
    pu.*,
    m.name as machine_name,
    p.part_number
FROM part_usage pu
LEFT JOIN machines m ON pu.machine_id = m.id
LEFT JOIN parts p ON pu.part_id = p.id
ORDER BY pu.created_at DESC
LIMIT 1;
```

### 7. Verify in UI
1. Go to Machine Details for the machine you used
2. Click "Parts Usage" tab
3. Should see the usage record

## Troubleshooting

### If PartUsage records still not created:
```bash
# Check API logs for errors during transaction creation
sudo docker compose -f docker-compose.prod.yml logs api | grep -i "error\|exception" | tail -20

# Verify the code changes are in the container
sudo docker compose -f docker-compose.prod.yml exec api cat /app/app/crud/transaction.py | grep -A 5 "create_part_usage_from_transaction"
```

### If records exist but not showing in UI:
```bash
# Check API logs for errors during GET request
sudo docker compose -f docker-compose.prod.yml logs api | grep "usage-history" | tail -20

# Test the endpoint directly
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://abparts.oraseas.com/api/machines/MACHINE_ID/usage-history
```

### Common Issues:

**1. Old code still running**
- Solution: Force rebuild with `--no-cache`
```bash
sudo docker compose -f docker-compose.prod.yml build api --no-cache
sudo docker compose -f docker-compose.prod.yml up -d api
```

**2. Database trigger interfering**
- Check if there's a database trigger that might be preventing inserts
```sql
SELECT * FROM information_schema.triggers WHERE event_object_table = 'part_usage';
```

**3. Schema mismatch**
- The PartUsage model uses `quantity` field
- The schema expects `quantity_used` field
- This might cause serialization issues

## Expected Behavior After Fix

### When recording part usage:
1. ✅ Transaction record created (type: consumption)
2. ✅ PartUsage record created (linked to machine)
3. ✅ Inventory decreased in warehouse
4. ✅ Shows in Transactions page
5. ✅ Shows in Machine Details "Parts Usage" tab

### API Response:
```json
{
  "id": "uuid",
  "customer_organization_id": "uuid",
  "part_id": "uuid",
  "machine_id": "uuid",
  "quantity": 2.0,
  "usage_date": "2024-11-24T10:30:00Z",
  "warehouse_id": "uuid",
  "recorded_by_user_id": "uuid",
  "notes": "Regular maintenance",
  "part_number": "AB-001",
  "part_name": "Filter Cartridge",
  "recorded_by_username": "john.doe",
  "machine_name": "KEF-5"
}
```
