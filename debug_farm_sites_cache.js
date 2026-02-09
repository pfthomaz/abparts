// Debug script to check farm sites in IndexedDB
// Run this in browser console

(async function debugFarmSitesCache() {
  console.log('=== DEBUGGING FARM SITES CACHE ===');
  
  // Open IndexedDB
  const request = indexedDB.open('ABPartsOfflineDB', 3);
  
  request.onsuccess = function(event) {
    const db = event.target.result;
    console.log('✅ Database opened successfully');
    console.log('Available stores:', Array.from(db.objectStoreNames));
    
    // Check if farmSites store exists
    if (!db.objectStoreNames.contains('farmSites')) {
      console.error('❌ farmSites store does NOT exist!');
      return;
    }
    
    console.log('✅ farmSites store exists');
    
    // Read all farm sites
    const transaction = db.transaction(['farmSites'], 'readonly');
    const store = transaction.objectStore('farmSites');
    const getAllRequest = store.getAll();
    
    getAllRequest.onsuccess = function() {
      const farmSites = getAllRequest.result;
      console.log(`\n📊 Found ${farmSites.length} farm sites in cache:`);
      
      if (farmSites.length === 0) {
        console.warn('⚠️  No farm sites in cache!');
        console.log('This means either:');
        console.log('1. Data preload failed');
        console.log('2. User context was missing during preload');
        console.log('3. API returned no farm sites');
      } else {
        console.table(farmSites.map(fs => ({
          id: fs.id,
          name: fs.name,
          organization_id: fs.organization_id,
          active: fs.active,
          location: fs.location
        })));
        
        // Check for missing organization_id
        const missingOrgId = farmSites.filter(fs => !fs.organization_id);
        if (missingOrgId.length > 0) {
          console.error(`❌ ${missingOrgId.length} farm sites missing organization_id:`, missingOrgId);
        }
      }
    };
    
    getAllRequest.onerror = function() {
      console.error('❌ Failed to read farm sites:', getAllRequest.error);
    };
  };
  
  request.onerror = function() {
    console.error('❌ Failed to open database:', request.error);
  };
})();

console.log('Debug script loaded. Check results above.');
