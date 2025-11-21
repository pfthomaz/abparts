# Profile Photos and Organization Logos Feature

## Overview

Added functionality for users to upload profile photos and organization admins to upload organization logos. These images are displayed in the application header.

## Changes Made

### Backend Changes

1. **Database Schema Updates** (`backend/app/models.py`):
   - Added `logo_url` field to `Organization` model
   - Added `profile_photo_url` field to `User` model

2. **Schema Updates**:
   - Updated `OrganizationBase`, `OrganizationUpdate` schemas to include `logo_url`
   - Updated `UserBase`, `UserUpdate`, `UserProfileUpdate` schemas to include `profile_photo_url`

3. **New Upload Router** (`backend/app/routers/uploads.py`):
   - `POST /uploads/users/profile-photo` - Upload user profile photo
   - `DELETE /uploads/users/profile-photo` - Remove user profile photo
   - `POST /uploads/organizations/{id}/logo` - Upload organization logo (admin only)
   - `DELETE /uploads/organizations/{id}/logo` - Remove organization logo (admin only)

4. **Registered Router** in `backend/app/main.py`

### Frontend Changes

1. **Header Updates** (`frontend/src/components/Layout.js`):
   - Shows organization name and logo (if available) next to user menu
   - Displays user profile photo instead of initials circle (if available)
   - Profile photo shown in both header button and dropdown menu

2. **New Components**:
   - `ProfilePhotoUpload.js` - Component for users to upload/remove their profile photo
   - `OrganizationLogoUpload.js` - Component for admins to upload/remove organization logo

## Database Migration

Run this SQL to add the new columns:

```sql
-- Add logo_url to organizations table
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);

-- Add profile_photo_url to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(500);
```

Or use the provided migration file:
```bash
docker-compose exec db psql -U abparts_user -d abparts_dev -f /path/to/add_images_migration.sql
```

## How to Use

### For Users - Upload Profile Photo

1. Go to your Profile page (click user menu > My Profile)
2. Look for the "Profile Photo" section
3. Click "Upload Photo" and select an image
4. Your photo will appear in the header immediately

### For Organization Admins - Upload Organization Logo

1. Go to Organization Management page
2. Edit your organization
3. Look for the "Organization Logo" section
4. Click "Upload Logo" and select an image
5. The logo will appear next to the organization name in the header

## Features

### Profile Photos
- **Who can upload**: Any authenticated user (for their own profile)
- **File types**: JPG, JPEG, PNG, GIF, WEBP
- **Max size**: 5MB
- **Display**: Circular avatar in header and user menu
- **Fallback**: Shows initials in colored circle if no photo

### Organization Logos
- **Who can upload**: Organization admins and super admins
- **File types**: JPG, JPEG, PNG, GIF, WEBP
- **Max size**: 5MB
- **Display**: Small logo next to organization name in header
- **Fallback**: Shows only organization name if no logo

## Header Display

The header now shows (from left to right):
1. ABParts logo
2. Navigation menus
3. **Organization name + logo** (new!)
4. Mobile menu button
5. **User photo/initials + name** (enhanced!)

## Technical Details

### Image Storage
- Images are stored in `/app/static/images/` directory
- Filenames are prefixed with type (`profile_`, `org_logo_`) and UUID
- URLs are stored as relative paths in database (`/static/images/filename.jpg`)

### Permissions
- **Profile photos**: Users can only upload/remove their own photos
- **Organization logos**: Only admins of the organization or super admins can upload/remove

### API Endpoints

**Upload User Profile Photo:**
```
POST /uploads/users/profile-photo
Authorization: Bearer {token}
Content-Type: multipart/form-data
Body: file (image file)

Response: { "url": "/static/images/profile_uuid.jpg" }
```

**Remove User Profile Photo:**
```
DELETE /uploads/users/profile-photo
Authorization: Bearer {token}

Response: { "message": "Profile photo removed successfully" }
```

**Upload Organization Logo:**
```
POST /uploads/organizations/{organization_id}/logo
Authorization: Bearer {token}
Content-Type: multipart/form-data
Body: file (image file)

Response: { "url": "/static/images/org_logo_uuid.jpg" }
```

**Remove Organization Logo:**
```
DELETE /uploads/organizations/{organization_id}/logo
Authorization: Bearer {token}

Response: { "message": "Organization logo removed successfully" }
```

## Testing

1. **Run the database migration**:
   ```bash
   docker-compose exec db psql -U abparts_user -d abparts_dev < add_images_migration.sql
   ```

2. **Restart the backend** to load new code:
   ```bash
   docker-compose restart api
   ```

3. **Test profile photo upload**:
   - Login as any user
   - The header should show your organization name
   - Upload a profile photo (you'll need to integrate the component into the profile page)
   - Refresh the page - your photo should appear in the header

4. **Test organization logo upload**:
   - Login as an admin
   - Upload an organization logo (you'll need to integrate the component into the organization management page)
   - Refresh the page - the logo should appear next to the organization name

## Next Steps

To complete the integration, you need to:

1. Add `ProfilePhotoUpload` component to the User Profile page
2. Add `OrganizationLogoUpload` component to the Organization Management/Edit page
3. Ensure the AuthContext refreshes user data after photo upload to update the header immediately

## Files Modified

**Backend:**
- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/schemas/organization.py`
- `backend/app/routers/uploads.py` (new)
- `backend/app/main.py`

**Frontend:**
- `frontend/src/components/Layout.js`
- `frontend/src/components/ProfilePhotoUpload.js` (new)
- `frontend/src/components/OrganizationLogoUpload.js` (new)

**Database:**
- `add_images_migration.sql` (new)
