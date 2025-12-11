# Commit Message

## Feature: Profile Photos, Organization Logos, and Part Usage Improvements

### Summary
Implemented user profile photos and organization logos with upload functionality, fixed and enhanced the part usage workflow, and improved transaction history display. Added comprehensive production deployment documentation.

---

## Changes Made

### 🖼️ Profile Photos & Organization Logos

**Backend:**
- Added `profile_photo_url` column to `users` table
- Added `logo_url` column to `organizations` table
- Created `/uploads/users/profile-photo` endpoint (POST/DELETE)
- Created `/uploads/organizations/{org_id}/logo` endpoint (POST/DELETE)
- Fixed `/users/me/` endpoint to return `profile_photo_url` and full organization object
- Removed `response_model` constraint to allow custom response structure
- Added static file serving for uploaded images

**Frontend:**
- Created `ProfilePhotoUpload` component for user photo management
- Created `OrganizationLogoUpload` component for org logo management
- Integrated photo upload in User Profile page
- Integrated logo upload in Organization edit form
- Updated `Layout` component to display profile photos and org logos in header
- Increased header photo/logo sizes from 32px to 48px for better visibility
- Fixed `userService.getMyProfile()` to use `/users/me/` endpoint
- Added proper error handling and loading states

**Database:**
- `users.profile_photo_url` VARCHAR(500) - stores image path
- `organizations.logo_url` VARCHAR(500) - stores image path

---

### 🔧 Part Usage Feature Improvements

**Backend:**
- Fixed transaction CRUD functions to include `machine_name` in responses
- Updated `search_transactions()`, `get_transactions()`, and `get_transaction()` to return machine names
- Changed `machine_serial` field to return machine name (with fallback to serial number)

**Frontend:**
- Fixed `PartUsageRecorder` component data format issues (parts.find error)
- Reordered workflow: Warehouse → Part → Machine (more logical flow)
- Implemented auto-select for single options (better UX)
- Added warehouse inventory filtering (only shows parts with stock > 0)
- Enhanced parts dropdown: "Part Code - Part Name (X available)"
- Fixed organization validation to use `customer_organization_id`
- Added "Use Part" button to machine cards on Machines page
- Added required `unit_of_measure` field to transaction creation
- Implemented auto-close modal after successful submission
- Updated `TransactionHistory` to show machine names in "TO" column for consumption transactions

**Workflow:**
1. Select warehouse (auto-selected if only one)
2. Select part from available inventory (filtered by warehouse, stock > 0)
3. Select destination machine (pre-selected when opened from machine card)
4. Enter quantity and submit

---

### 📊 Transaction History Enhancements

**Changes:**
- "TO" column now displays "Machine: KEF-1" for consumption transactions
- Shows destination warehouse for transfer transactions
- Backend returns machine name instead of serial number for better clarity

---

### 🌍 Country Support

**Added Countries:**
- 🇬🇧 United Kingdom (UK)
- 🇳🇴 Norway (NO)
- 🇨🇦 Canada (CA)
- 🇳🇿 New Zealand (NZ)
- 🇹🇷 Turkey (TR)

**Note:** Countries are defined in frontend code (`frontend/src/utils/countryFlags.js`), no database changes required.

---

### 📚 Documentation

**Created:**
- `PRODUCTION_DATABASE_MIGRATION.sql` - SQL script for production deployment
- `PRODUCTION_DEPLOYMENT_GUIDE.md` - Complete deployment instructions
- Includes backup procedures, rollback steps, and troubleshooting guide

---

## Database Schema Changes

```sql
-- New columns (backward compatible)
ALTER TABLE users ADD COLUMN profile_photo_url VARCHAR(500);
ALTER TABLE organizations ADD COLUMN logo_url VARCHAR(500);
ALTER TABLE customer_orders ADD COLUMN shipped_by_user_id UUID REFERENCES users(id);
```

**Migration:** Run `PRODUCTION_DATABASE_MIGRATION.sql` on production database

---

## Files Changed

### Backend
- `backend/app/main.py` - Removed response_model from /users/me/
- `backend/app/models.py` - Added profile_photo_url and logo_url columns
- `backend/app/schemas.py` - Added profile_photo_url to UserProfileResponse
- `backend/app/crud/users.py` - Added profile_photo_url to user profile response
- `backend/app/crud/transaction.py` - Added machine_name to transaction responses
- `backend/app/routers/uploads.py` - Created image upload endpoints
- `backend/app/auth.py` - Updated read_users_me to return full user data

### Frontend
- `frontend/src/components/ProfilePhotoUpload.js` - New component
- `frontend/src/components/OrganizationLogoUpload.js` - New component
- `frontend/src/components/PartUsageRecorder.js` - Major improvements
- `frontend/src/components/TransactionHistory.js` - Show machine names
- `frontend/src/components/Layout.js` - Display photos/logos, increased sizes
- `frontend/src/pages/UserProfile.js` - Integrated photo upload
- `frontend/src/pages/Machines.js` - Added "Use Part" button
- `frontend/src/services/userService.js` - Fixed getMyProfile endpoint
- `frontend/src/services/authService.js` - No changes (context only)
- `frontend/src/utils/countryFlags.js` - Added new countries

### Documentation
- `PRODUCTION_DATABASE_MIGRATION.sql` - New
- `PRODUCTION_DEPLOYMENT_GUIDE.md` - New

---

## Testing Performed

✅ Profile photo upload and display in header
✅ Organization logo upload and display in header  
✅ Part usage workflow from machine card
✅ Part usage workflow from transactions page
✅ Warehouse inventory filtering
✅ Auto-select single options
✅ Transaction history displays machine names
✅ Image file validation (type and size)
✅ Error handling and user feedback
✅ Modal auto-close after success

---

## Breaking Changes

**None** - All changes are backward compatible. Existing functionality remains unchanged.

---

## Deployment Notes

1. **Backup database before deployment**
2. Run `PRODUCTION_DATABASE_MIGRATION.sql`
3. Create `backend/static/images` directory with proper permissions
4. Deploy backend code and restart API
5. Build and deploy frontend
6. Verify image uploads work correctly

See `PRODUCTION_DEPLOYMENT_GUIDE.md` for detailed instructions.

---

## Known Issues

None

---

## Future Improvements

- Image compression/optimization before upload
- Image cropping tool for profile photos
- Bulk part usage recording
- Part usage history per machine
- Export transaction history to CSV/Excel

---

## Contributors

- Development and implementation of all features
- Testing and bug fixes
- Documentation

---

## Related Issues

- Fixes profile photo display issue
- Fixes part usage workflow UX issues
- Improves transaction history clarity
- Adds missing image upload functionality
