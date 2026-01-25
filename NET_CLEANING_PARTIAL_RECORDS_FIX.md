# Net Cleaning Records - Operator Dropdown & Partial Records Fix

## Issues Fixed

### 1. Operator Dropdown Showing No Names
**Problem:** The operator dropdown in the net cleaning record form was empty - no user names were showing.

**Root Cause:** 
- The endpoint `/users/organization/{organization_id}/users` required admin or super_admin role
- Regular users couldn't access it to see their organization's users

**Solution:**
- Modified `backend/app/routers/users.py` to allow all authenticated users to fetch users from their own organization
- Regular users and admins can only view users in their own organization
- Super admins can view users in any organization

**Files Modified:**
- `backend/app/routers/users.py` - Changed permission from `has_roles(["super_admin", "admin"])` to `get_current_user` with organization-based access control

### 2. Allow Partial/Incomplete Records
**Problem:** Users had to fill in both start and end times, making it impossible to record the start of a cleaning and complete it later.

**Solution:** Implemented partial record support with the following changes:

#### Backend Changes:
1. **Model Update** (`backend/app/models.py`):
   - Made `end_time` nullable
   - Added `status` column (varchar(20)) with values: 'in_progress' or 'completed'
   - Updated validation logic to handle null end_time
   - Updated duration calculation to handle incomplete records

2. **Schema Update** (`backend/app/schemas/net_cleaning.py`):
   - Made `end_time` optional in `NetCleaningRecordBase`
   - Added `status` field with default 'completed'
   - Updated validator to only check end_time if it's provided

3. **Database Migration**:
   - Created migration `7b3899138d40_add_status_to_net_cleaning_records_and_make_end_time_nullable.py`
   - Added `status` column with default value 'completed'
   - Made `end_time` nullable
   - Migration applied successfully

#### Frontend Changes:
1. **Form Update** (`frontend/src/components/NetCleaningRecordForm.js`):
   - Removed `required` attribute from end_time field
   - Added help text: "Leave empty to save as in-progress and complete later"
   - Updated submit logic to set status based on whether end_time is provided
   - Status automatically set to 'in_progress' if end_time is null, 'completed' if provided

2. **Records List Update** (`frontend/src/pages/NetCleaningRecords.js`):
   - Added visual indicator for incomplete records (yellow background)
   - Added "In Progress" badge for incomplete records
   - Duration shows "-" for incomplete records instead of null
   - Users can edit incomplete records to add end_time and complete them

3. **Translation Updates**:
   - Added `optional` key: "optional" / "opcional"
   - Added `endTimeHelp` key with instructions
   - Added `inProgress` key: "In Progress" / "En Progreso"
   - Updated both English and Spanish translation files

## User Workflow

### Recording a Partial Cleaning:
1. User opens "Add Cleaning Record"
2. Fills in all required fields (farm site, net, operator, mode, depths, start time)
3. Leaves "End Time" empty
4. Clicks "Create"
5. Record is saved with status='in_progress'
6. Record appears in list with yellow background and "In Progress" badge

### Completing a Partial Cleaning:
1. User finds the incomplete record in the list (yellow background)
2. Clicks "Edit"
3. Adds the end time
4. Clicks "Update"
5. Record is updated with status='completed'
6. Duration is automatically calculated
7. Record appears normal (white background, no badge)

## Files Modified

### Backend:
1. `backend/app/models.py` - Updated NetCleaningRecord model
2. `backend/app/schemas/net_cleaning.py` - Made end_time optional, added status
3. `backend/app/routers/users.py` - Fixed permissions for organization users endpoint
4. `backend/alembic/versions/7b3899138d40_add_status_to_net_cleaning_records_and_.py` - New migration

### Frontend:
1. `frontend/src/components/NetCleaningRecordForm.js` - Made end_time optional, added status logic
2. `frontend/src/pages/NetCleaningRecords.js` - Added visual indicators for incomplete records
3. `frontend/src/locales/en.json` - Added new translation keys
4. `frontend/src/locales/es.json` - Added new translation keys

## Testing

To verify the fixes:
1. **Operator Dropdown**: Open the net cleaning form - should see list of users from your organization
2. **Partial Record**: Create a record without end time - should save successfully
3. **Visual Indicator**: Incomplete records should have yellow background and "In Progress" badge
4. **Complete Record**: Edit an incomplete record and add end time - should update to completed status

## Status

✅ Operator dropdown now shows organization users
✅ Regular users can access the users endpoint for their organization
✅ End time is now optional
✅ Status field added to track incomplete records
✅ Visual indicators show incomplete records
✅ Users can edit incomplete records to complete them
✅ Database migration applied successfully
✅ All translations updated (English & Spanish)
