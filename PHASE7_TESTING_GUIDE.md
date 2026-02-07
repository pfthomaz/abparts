# Phase 7: Offline Mode Testing Guide

## ✅ Status: Ready to Test!

**Frontend**: Running on http://localhost:3000 ✅  
**Backend API**: Running on http://localhost:8000 ✅  
**Database**: Running ✅

---

## 🧪 Step-by-Step Testing Instructions

### **Step 1: Open the App in Chrome**

1. Open **Google Chrome** (or Chromium-based browser)
2. Navigate to: **http://localhost:3000**
3. Log in with your credentials
4. Open **Chrome DevTools** (Press `F12` or `Cmd+Option+I` on Mac)

---

### **Step 2: Verify You Have Net Cleaning Permissions**

Before testing, make sure you have access to Net Cleaning features:

1. Check the left navigation menu
2. You should see **"Net Cleaning Records"** under Operations
3. If not visible, you may need to log in as a user with proper permissions

---

### **Step 3: Go Offline**

1. In DevTools, click the **Network** tab
2. Find the dropdown that says **"No throttling"** (near the top)
3. Click it and select **"Offline"**
4. **Expected Result**: You should see a **yellow banner** at the top saying:
   - "Offline Mode - You are currently offline"
   - Shows offline duration
   - Shows pending operations count (should be 0 initially)

**Screenshot what you see!**

---

### **Step 4: Navigate to Net Cleaning Records**

1. Click **"Net Cleaning Records"** in the left menu
2. **Expected Result**: Page should load with cached data
3. You should see existing records (if any)
4. The yellow offline banner should still be visible

---

### **Step 5: Create an Offline Net Cleaning Record**

**IMPORTANT**: Before going offline, you need to cache users first:

1. While still **ONLINE**, click the **"Add Record"** button
2. Select a **Farm Site** (this will fetch and cache users for that organization)
3. You should see the operator dropdown populate with users
4. Click **Cancel** to close the form (users are now cached)
5. **NOW go offline** (DevTools Network tab → Offline)
6. Click **"Add Record"** again

**Expected Result**: The operator dropdown should still show users even though you're offline!

Now fill in the form:
   - **Farm Site**: Select any farm site (from cached list)
   - **Net/Cage**: Select any net (from cached list)
   - **Operator**: Select an operator from the dropdown (from cached users)
   - **Cleaning Mode**: Select Mode 1, 2, or 3
   - **Depth 1**: Enter a number (e.g., 10.5)
   - **Start Time**: Select a date/time
   - **End Time**: Select a date/time (after start time)
   - **Notes**: Type anything (e.g., "Test offline record")

4. **Add Photos** (optional but recommended):
   - Click the photo input
   - Select 1-2 test images from your computer
   - **Expected Result**: Photo previews appear below the input
   - Each photo should have a small × button to remove it

5. Click **"Create"** button

6. **Expected Results**:
   - Alert appears: "Saved offline. Will sync when connection restored."
   - Form closes
   - You return to the Net Cleaning Records list

---

### **Step 6: Verify Pending Record Display**

1. Look at the Net Cleaning Records list
2. **Expected Results**:
   - Your new record appears at the top
   - It has a **blue background** (`bg-blue-50`)
   - It has a **blue "Pending Sync" badge**
   - Instead of Edit/Delete buttons, it shows **"Waiting Sync"**
   - The page header shows: **"1 record pending sync"** (or more if you created multiple)

3. The yellow offline banner should now show:
   - "1 pending operation" (or more with photos)

**Screenshot this!**

---

### **Step 7: Check IndexedDB Storage**

1. In DevTools, click the **Application** tab
2. In the left sidebar, expand **IndexedDB**
3. Expand **ABPartsOfflineDB**
4. Click on **netCleaningRecords** store
5. **Expected Result**: You should see your record with:
   - `id`: Starts with `temp_`
   - `synced`: `false`
   - All your form data

6. If you added photos, click on **netCleaningPhotos** store
7. **Expected Result**: You should see your photos with:
   - `id`: Starts with `temp_photo_`
   - `record_id`: Matches your record's temp ID
   - `photo_data`: Base64 encoded image
   - `synced`: `false`

8. Click on **syncQueue** store
9. **Expected Result**: You should see queued operations:
   - Type: `NET_CLEANING_RECORD`
   - Type: `NET_CLEANING_PHOTO` (if you added photos)
   - Status: `pending`
   - Priority: 1 for record, 2 for photos

**Screenshot the IndexedDB contents!**

---

### **Step 8: Check Sync Status Page**

1. Navigate to **Sync Status** (in Operations menu)
2. **Expected Results**:
   - **Connection Status**: Shows "Offline" in red
   - **Pending Operations**: Shows count (1+ depending on photos)
   - **Queue Statistics**: Shows pending count
   - **Offline Records** section shows your record with:
     - Operator name
     - Cleaning mode
     - Timestamp
     - Blue "Waiting Sync" badge
   - **Sync Now** button is disabled (grayed out)

**Screenshot this page!**

---

### **Step 9: Go Back Online**

1. Go back to the **Network** tab in DevTools
2. Change from **"Offline"** to **"No throttling"**
3. **Expected Results** (should happen automatically within 2-3 seconds):
   - **Green banner** appears briefly: "Back online - Syncing pending operations..."
   - Yellow offline banner changes to show **"Syncing..."** with a spinning icon
   - After a few seconds, the banner disappears or shows "All synced!"

**Watch carefully and note what happens!**

---

### **Step 10: Verify Sync Completed**

1. Go back to **Net Cleaning Records** page
2. **Expected Results**:
   - The record should **automatically refresh** after sync completes
   - The **blue "Pending Sync" badge** is GONE
   - The record now has a normal white background
   - **Edit** and **Delete** buttons now appear
   - The header no longer shows "pending sync" message
   - **No manual page refresh needed!**

3. Check the **Sync Status** page again:
   - Should show **"All Synced!"** with a green checkmark
   - Pending Operations: 0
   - Offline Records section should be empty or show "No offline records"

---

### **Step 11: Verify Record in Backend**

1. Open a new tab and go to: **http://localhost:8000/docs**
2. Find the **GET /net-cleaning-records** endpoint
3. Click "Try it out" → "Execute"
4. **Expected Result**: Your record should appear in the response with:
   - A real UUID (not temp_)
   - All your form data
   - Photos should have URLs (not base64)

Alternatively, check the database directly:
```bash
docker-compose exec db psql -U abparts_user -d abparts_dev -c "SELECT id, operator_name, notes, created_at FROM net_cleaning_records ORDER BY created_at DESC LIMIT 5;"
```

---

### **Step 12: Verify Photos Synced**

1. Click on your synced record to view details
2. **Expected Result**: Photos should be visible as images (not base64)
3. Photos should load from the backend server

---

## ✅ Testing Checklist

Mark each item as you test:

- [ ] Offline indicator appears when going offline
- [ ] Can navigate to Net Cleaning Records while offline
- [ ] "Add Record" button works offline
- [ ] Form shows offline warning banner
- [ ] Can select farm site from cached list
- [ ] Can select net from cached list
- [ ] Can add photos offline
- [ ] Photo previews work
- [ ] Can submit form offline
- [ ] "Saved offline" alert appears
- [ ] Record appears in list with "Pending Sync" badge
- [ ] Record has blue background
- [ ] Edit/Delete buttons hidden (shows "Waiting Sync")
- [ ] Pending count shows in header
- [ ] Offline indicator shows pending count
- [ ] Record stored in IndexedDB
- [ ] Photos stored in IndexedDB as base64
- [ ] Operations queued in syncQueue
- [ ] Sync Status page shows offline status
- [ ] Sync Status page shows pending operations
- [ ] Auto-sync triggers when back online
- [ ] "Back online" message appears
- [ ] Syncing indicator shows
- [ ] Pending badge disappears after sync
- [ ] Record shows Edit/Delete buttons after sync
- [ ] Record appears in backend API
- [ ] Photos uploaded to backend
- [ ] Photos display correctly after sync

---

## 🐛 Common Issues & Solutions

### Issue: Operator dropdown is empty when offline
**Solution**: You need to load users while online first. Go online, open the form, select a farm site (this caches users), then go offline. The dropdown will now work.

### Issue: Offline indicator doesn't appear
**Solution**: Check browser console for errors. Service worker may not be registered.

### Issue: Can't create record offline
**Solution**: Check that farm sites and nets are cached. Try refreshing the page while online first.

### Issue: Photos don't save
**Solution**: Check browser console. File size may be too large. Try smaller images.

### Issue: Auto-sync doesn't trigger
**Solution**: Wait 2-3 seconds after going online. Check Sync Status page and click "Sync Now" manually.

### Issue: Record doesn't appear in backend
**Solution**: Check browser console for sync errors. Check backend logs: `docker-compose logs api`

---

## 📊 What to Report

After testing, please report:

1. **Screenshots** of:
   - Offline indicator
   - Pending record with blue badge
   - IndexedDB contents
   - Sync Status page
   - Synced record (no badge)

2. **Any errors** from:
   - Browser console
   - Network tab
   - Backend logs

3. **Timing**:
   - How long did sync take?
   - Did auto-sync work or did you need manual sync?

4. **Overall experience**:
   - Was it intuitive?
   - Any confusing parts?
   - Suggestions for improvement?

---

## 🎉 Success Criteria

The test is **SUCCESSFUL** if:

✅ You can create a net cleaning record while offline  
✅ Record appears with "Pending Sync" badge  
✅ Auto-sync triggers when back online  
✅ Record syncs to backend successfully  
✅ Photos sync correctly  
✅ No errors in console  

---

## 📝 Next Steps After Testing

Once testing is complete:

1. **If successful**: Move to Task 24 (Mobile Testing)
2. **If issues found**: Document them and we'll fix before mobile testing
3. **Update IMPLEMENTATION.md**: Mark Task 23 as complete

---

**Ready to start? Follow the steps above and let me know what you see at each step!** 🚀
