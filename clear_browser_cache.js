// Clear Browser Cache - Run this in browser console
// Copy and paste this entire script into the browser console at https://abparts.oraseas.com

(async function clearAllCaches() {
  console.log('🧹 Starting cache cleanup...');
  console.log('');
  
  // Step 1: Unregister service workers
  console.log('1️⃣ Unregistering service workers...');
  try {
    const registrations = await navigator.serviceWorker.getRegistrations();
    for (let registration of registrations) {
      await registration.unregister();
      console.log('   ✓ Unregistered:', registration.scope);
    }
    if (registrations.length === 0) {
      console.log('   ℹ️  No service workers registered');
    } else {
      console.log('   ✅ Unregistered', registrations.length, 'service worker(s)');
    }
  } catch (error) {
    console.error('   ❌ Error unregistering service workers:', error);
  }
  
  console.log('');
  
  // Step 2: Clear all caches
  console.log('2️⃣ Clearing cache storage...');
  try {
    const cacheNames = await caches.keys();
    for (let name of cacheNames) {
      await caches.delete(name);
      console.log('   ✓ Deleted cache:', name);
    }
    if (cacheNames.length === 0) {
      console.log('   ℹ️  No caches found');
    } else {
      console.log('   ✅ Deleted', cacheNames.length, 'cache(s)');
    }
  } catch (error) {
    console.error('   ❌ Error clearing caches:', error);
  }
  
  console.log('');
  
  // Step 3: Clear IndexedDB
  console.log('3️⃣ Clearing IndexedDB...');
  try {
    const deleteRequest = indexedDB.deleteDatabase('ABPartsOfflineDB');
    
    deleteRequest.onsuccess = function() {
      console.log('   ✅ IndexedDB deleted successfully');
    };
    
    deleteRequest.onerror = function() {
      console.error('   ❌ Error deleting IndexedDB');
    };
    
    deleteRequest.onblocked = function() {
      console.warn('   ⚠️  IndexedDB deletion blocked (close other tabs)');
    };
  } catch (error) {
    console.error('   ❌ Error clearing IndexedDB:', error);
  }
  
  console.log('');
  
  // Step 4: Clear localStorage (optional - preserves auth token)
  console.log('4️⃣ Clearing localStorage (except auth token)...');
  try {
    const token = localStorage.getItem('token');
    const itemCount = localStorage.length;
    localStorage.clear();
    if (token) {
      localStorage.setItem('token', token);
      console.log('   ✓ Preserved auth token');
    }
    console.log('   ✅ Cleared', itemCount, 'localStorage item(s)');
  } catch (error) {
    console.error('   ❌ Error clearing localStorage:', error);
  }
  
  console.log('');
  console.log('========================================');
  console.log('✅ Cache cleanup complete!');
  console.log('========================================');
  console.log('');
  console.log('🔄 Reloading page in 3 seconds...');
  console.log('');
  console.log('After reload, you should see:');
  console.log('  [OfflinePreloader] Module loaded, STORES = ...');
  console.log('  [OfflinePreloader] ✓ Cached X protocols');
  console.log('');
  
  // Reload after 3 seconds
  setTimeout(() => {
    console.log('🔄 Reloading now...');
    location.reload(true);
  }, 3000);
})();

