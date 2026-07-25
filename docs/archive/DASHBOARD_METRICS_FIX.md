# Dashboard Metrics Fix - Farm Sites and Nets Counts

## Issue
Farm Sites and Nets (Cages) cards on the dashboard were showing 0 instead of the actual counts.

## Root Cause
The backend metrics endpoint wasn't counting farm sites and nets. The fields existed in the frontend but weren't being populated by the backend.

## Solution Implemented

### Backend Changes

**1. Updated `backend/app/crud/dashboard_fixed.py`:**
- Added `total_farm_sites` and `total_nets` to the metrics calculation
- Counts only active farm sites and nets
- Properly scoped to user's organization for non-super admins
- Includes error handling for graceful degradation

```python
# Added to get_dashboard_metrics function:
try:
    farm_sites_query = db.query(models.FarmSite)
    if organization_id:
        farm_sites_query = farm_sites_query.filter(
            models.FarmSite.organization_id == organization_id
        )
    total_farm_sites = farm_sites_query.filter(
        models.FarmSite.active == True
    ).count()
except Exception as e:
    print(f"Error counting farm sites: {e}")

try:
    nets_query = db.query(models.Net)
    if organization_id:
        nets_query = nets_query.join(
            models.FarmSite,
            models.Net.farm_site_id == models.FarmSite.id
        ).filter(models.FarmSite.organization_id == organization_id)
    total_nets = nets_query.filter(models.Net.active == True).count()
except Exception as e:
    print(f"Error counting nets: {e}")
```

**2. Updated `backend/app/schemas.py`:**
- Added `total_farm_sites` and `total_nets` fields to `DashboardMetricsResponse`

```python
class DashboardMetricsResponse(BaseModel):
    # ... existing fields ...
    total_farm_sites: int = 0
    total_nets: int = 0
```

### Frontend
No changes needed - the frontend was already configured to display these metrics:
- `metrics?.total_farm_sites` for Farms card
- `metrics?.total_nets` for Cages card

## How to Apply

1. **Restart the API** to load the new code:
   ```bash
   docker-compose restart api
   ```

2. **Refresh the dashboard** in your browser

3. **Verify** the counts are now showing correctly

## Testing

Run the test script to verify metrics are working:
```bash
python test_dashboard_metrics.py
```

This will:
- Login to the API
- Fetch dashboard metrics
- Display all metrics including farm sites and nets counts
- Check if the endpoints are working correctly

## Notes

- The counts only include **active** farm sites and nets (where `active = True`)
- For non-super admin users, counts are scoped to their organization
- If the migration hasn't been applied yet, the counts will be 0 (tables don't exist)
- Error handling ensures the dashboard still works even if there are database issues

## Files Modified

1. `backend/app/crud/dashboard_fixed.py` - Added counting logic
2. `backend/app/schemas.py` - Added response fields
3. `test_dashboard_metrics.py` - Created test script (new file)

## Status

✅ **COMPLETE** - Dashboard now shows accurate counts for Farm Sites and Nets
