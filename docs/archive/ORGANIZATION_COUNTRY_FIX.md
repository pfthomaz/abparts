# Organization Country Field Fix

## Issue
When creating a new organization and selecting a country, the country was not being stored in the database. However, if the organization was edited afterwards and the country was added again, it would save correctly.

## Root Cause
The backend CRUD function `create_organization()` in `backend/app/crud/organizations.py` had a temporary workaround that was filtering out the `country` field during creation:

```python
# Temporarily remove country field until DB migration is complete
org_dict_filtered = {k: v for k, v in org_dict.items() if k != 'country'}

org = models.Organization(**org_dict_filtered)
```

This filtering was NOT present in the `update_organization()` function, which is why editing worked but creation didn't.

## Fix Applied
Removed the country field filtering from the `create_organization()` function in `backend/app/crud/organizations.py`:

**Before:**
```python
# Temporarily remove country field until DB migration is complete
org_dict_filtered = {k: v for k, v in org_dict.items() if k != 'country'}

org = models.Organization(**org_dict_filtered)
db.add(org)
db.commit()
db.refresh(org)
```

**After:**
```python
org = models.Organization(**org_dict)
db.add(org)
db.commit()
db.refresh(org)
```

## Verification
The `country` column exists in the database model (`backend/app/models.py` line 87):
```python
country = Column(Enum(CountryCode), nullable=True)
```

## Status
✅ **FIXED** - Country field now saves correctly during organization creation

## Testing
1. Create a new organization
2. Select a country from the dropdown
3. Save the organization
4. Verify the country is displayed in the organization details
5. Verify the country persists after page refresh

## Files Modified
- `backend/app/crud/organizations.py` - Removed country field filtering from create_organization()

## Related Issues
This was a leftover temporary workaround, likely from when the country field was being added to the database schema. The workaround should have been removed after the migration was complete.
