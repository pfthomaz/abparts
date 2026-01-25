# Dashboard & Net Cleaning Enhancements

## Requirements

### 1. Dashboard Updates

**Quick Actions (Middle Column):**
- Add "Record Net Cleaning" button as **second from top** (after "Let's Wash Nets")
- Should link to net cleaning records page with modal open

**Entities (Left Column):**
- Add "Farms" card showing count of farm sites
- Add "Cages" card showing count of nets/cages

### 2. Farm Sites Page Enhancement
- Add "Add Cage" button on each farm site card
- When clicked, open Net form modal with farm site pre-selected
- User cannot change the farm site in the modal

### 3. Net Cleaning Record Form Improvements

**Operator Field:**
- Change from text input to dropdown
- Populate with users from the organization
- Show user's full name

**Material Field (in NetForm):**
- Change from text input to dropdown
- Options based on image:
  - Polyester
  - Polypropylene
  - Polyethylene
  - Galvanized steel
  - Spectra
  - Copper
  - Thorn d
  - Dyneema
  - Other

### 4. Localization
All new text must be translated to 6 languages:
- English (en)
- Greek (el)
- Arabic (ar)
- Spanish (es)
- Norwegian (no)
- Turkish (tr)

## Implementation Plan

1. Add dashboard translations
2. Update Dashboard.js with new cards and actions
3. Update FarmSites.js to add "Add Cage" button
4. Create material constants
5. Update NetForm.js with material dropdown
6. Update NetCleaningRecordForm.js with user dropdown
7. Add backend endpoint to fetch organization users (if needed)
8. Test all changes

## Files to Modify

- `frontend/src/pages/Dashboard.js` - Add cards and action button
- `frontend/src/pages/FarmSites.js` - Add "Add Cage" button
- `frontend/src/components/NetForm.js` - Add material dropdown
- `frontend/src/components/NetCleaningRecordForm.js` - Add user dropdown
- `frontend/src/locales/*.json` - Add translations (6 files)
- Create translation script for new keys
