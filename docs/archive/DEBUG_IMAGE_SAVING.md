# Debug Guide: Image Saving Issue

## Problem
Images are not being saved when creating or updating parts.

## Changes Made to Debug

### 1. Enhanced PartPhotoGallery Component
- Added `onImagesChange` callback notification to parent
- Added console logging for image upload and state changes
- Fixed image state management to notify parent component

### 2. Enhanced PartForm Component  
- Added `onImagesChange` callback to update form data when images change
- Added extensive console logging to track image URLs through the submission process
- Form now updates its `image_urls` state when gallery changes

## How to Test

1. **Open Browser Developer Tools** (F12)
2. **Go to Console tab** to see debug messages
3. **Create or Edit a Part**
4. **Upload an image** - you should see:
   ```
   PartPhotoGallery: Successfully uploaded images: [...]
   PartPhotoGallery: New images list: [...]
   PartPhotoGallery: Images changed, notifying parent [...]
   PartForm: Received image URLs from gallery: [...]
   ```

5. **Submit the form** - you should see:
   ```
   PartForm: Retrieved image URLs from gallery: [...]
   PartForm: Current formData.image_urls: [...]
   PartForm: Final data being sent: {...}
   PartForm: Final image URLs being sent: [...]
   ```

## What to Look For

### If images upload but don't save:
- Check if `getCurrentImageUrls()` returns the correct URLs
- Check if the form submission includes the image URLs
- Check backend logs for validation errors

### If images don't upload:
- Check network tab for failed upload requests
- Check console for upload errors
- Verify the upload endpoint is working: `POST /api/parts/upload-image`

### If images upload and submit but don't persist:
- Check backend part creation/update endpoints
- Check database schema for `image_urls` field
- Check if validation is rejecting the image URLs

## Backend Verification

Check if the backend is receiving and storing the images:

1. **Check API logs** for part creation/update requests
2. **Check database** for the `image_urls` field in the parts table
3. **Test the upload endpoint directly** with a tool like Postman

## Quick Fix Commands

If you need to restart the services:
```bash
# Restart backend
docker-compose restart api

# Restart frontend  
docker-compose restart web

# Check logs
docker-compose logs api
docker-compose logs web
```

## Expected Behavior

1. User uploads image → Image appears in gallery
2. User submits form → Form includes image URLs in submission
3. Backend receives data → Saves part with image URLs
4. Part is created/updated with images visible in the UI

## Next Steps

After testing with the debug logs, we can identify exactly where the issue occurs and fix it accordingly.