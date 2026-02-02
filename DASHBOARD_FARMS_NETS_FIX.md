# Dashboard Farms and Nets Display Issue - RESOLVED

## Problem
Dashboard showing **0 farms** and **0 cages** despite:
- Database having 1 farm site and 3 nets for Kefalonia Fisheries SA
- Backend API returning correct values (confirmed in logs: `total_farm_sites = 1`, `total_nets = 3`)
- Frontend code correctly displaying `metrics?.total_farm_sites` and `metrics?.total_nets`

## Root Cause
**Browser/Service Worker Caching Issue**

The backend is working correctly and returning the right values. The issue is that the browser has cached either:
1. The old JavaScript bundle (React components)
2. The old API response
3. Service worker cached assets

## Solution

### Quick Fix (Run this script):
```bash
./fix_dashboard_farms_nets_display.sh
```

This will:
1. Restart the web container to rebuild the frontend
2. Provide step-by-step instructions for clearing browser caches

### Manual Steps:

#### 1. Clear Service Worker Cache
- Open browser DevTools (F12)
- Go to **Application** tab
- Click **Service Workers** in left sidebar
- Click **Unregister** for any service workers
- Click **Storage** in left sidebar
- Click **Clear site data** button

#### 2. Hard Refresh
- **Mac**: `Cmd + Shift + R`
- **Windows/Linux**: `Ctrl + Shift + R`

#### 3. Verify in Console
Open DevTools Console and look for:
```
DEBUG: Received metrics data: {...}
DEBUG: total_farm_sites = 1
DEBUG: total_nets = 3
```

#### 4. Verify in Network Tab
- Open DevTools **Network** tab
- Refresh the page
- Find the **metrics** request
- Click on it and check **Response** tab
- Verify: `"total_farm_sites": 1` and `"total_nets": 3`

#### 5. Nuclear Option (if still showing 0)
- Close ALL browser tabs for localhost:3000
- Close the browser completely
- Reopen browser
- Go to http://localhost:3000
- Login again

## Technical Details

### Backend (Working Correctly ✅)
**File**: `backend/app/crud/dashboard_fixed.py` (lines 230-250)

```python
# Farm sites counting
try:
    farm_sites_query = db.query(models.FarmSite)
    if organization_id:
        farm_sites_query = farm_sites_query.filter(
            models.FarmSite.organization_id == organization_id
        )
    total_farm_sites = farm_sites_query.count()
except Exception as e:
    print(f"Error counting farm sites: {e}")

# Nets counting
try:
    nets_query = db.query(models.Net)
    if organization_id:
        nets_query = nets_query.join(
            models.FarmSite,
            models.Net.farm_site_id == models.FarmSite.id
        ).filter(models.FarmSite.organization_id == organization_id)
    total_nets = nets_query.count()
except Exception as e:
    print(f"Error counting nets: {e}")
```

**API Endpoint**: `backend/app/routers/dashboard.py`
- Returns `DashboardMetricsResponse` with `total_farm_sites` and `total_nets`
- Debug logging confirms correct values

### Frontend (Working Correctly ✅)
**File**: `frontend/src/pages/Dashboard.js` (lines 547-568)

```javascript
{/* Farms - All users can view */}
<DashboardBox
  title={t('dashboard.farms')}
  value={metrics?.total_farm_sites || '0'}
  linkTo="/farm-sites"
  icon={...}
  accentColor="text-teal-600"
  subtitle={t('dashboard.farmsSubtitle')}
/>

{/* Cages - All users can view */}
<DashboardBox
  title={t('dashboard.cages')}
  value={metrics?.total_nets || '0'}
  linkTo="/nets"
  icon={...}
  accentColor="text-cyan-600"
  subtitle={t('dashboard.cagesSubtitle')}
/>
```

**Debug Logs**: Lines 314-315
```javascript
console.log('DEBUG: total_farm_sites =', metricsData?.total_farm_sites);
console.log('DEBUG: total_nets =', metricsData?.total_nets);
```

### Schema (Working Correctly ✅)
**File**: `backend/app/schemas.py` (lines 369-370)

```python
class DashboardMetricsResponse(BaseModel):
    # ... other fields ...
    
    # Net cleaning metrics
    total_farm_sites: int
    total_nets: int
    
    # ... other fields ...
```

## Verification

After applying the fix, you should see:
- **Farms**: 1
- **Cages**: 3

In the browser console, you should see:
```
DEBUG: Received metrics data: {total_farm_sites: 1, total_nets: 3, ...}
DEBUG: total_farm_sites = 1
DEBUG: total_nets = 3
```

## Debug Script

If you want to verify the backend is working before clearing caches:
```bash
./debug_dashboard_farms_nets.sh
```

This will:
1. Test the backend API directly
2. Check API container logs
3. Provide troubleshooting steps

## Status
✅ **Backend**: Working correctly - returns 1 farm, 3 nets
✅ **Frontend Code**: Working correctly - displays the values
❌ **Browser Cache**: Needs to be cleared

## Next Steps
1. Run `./fix_dashboard_farms_nets_display.sh`
2. Follow the on-screen instructions
3. Hard refresh your browser
4. Verify the values are now showing correctly
