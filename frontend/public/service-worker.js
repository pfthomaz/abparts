// ABParts Offline Service Worker
// Enables offline functionality for field operations

const CACHE_VERSION = 'abparts-offline-v2';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;
const IMAGE_CACHE = `${CACHE_VERSION}-images`;

// Assets to cache immediately on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/static/css/main.css',
  '/static/js/main.js',
  '/manifest.json',
  '/favicon.ico'
];

// API endpoints that should NEVER be cached (always fetch fresh)
const NO_CACHE_PATTERNS = [
  /\/api\/auth\//,
  /\/api\/users\/me/,
  /\/api\/.*\/sync/
];

// API endpoints that can be cached for offline use
const CACHEABLE_API_PATTERNS = [
  /\/api\/farm-sites/,
  /\/api\/nets/,
  /\/api\/machines/,
  /\/api\/maintenance-protocols/,
  /\/api\/parts/
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[Service Worker] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('[Service Worker] Installation complete');
        return self.skipWaiting(); // Activate immediately
      })
      .catch((error) => {
        console.error('[Service Worker] Installation failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              // Delete old version caches
              return cacheName.startsWith('abparts-offline-') && 
                     cacheName !== STATIC_CACHE &&
                     cacheName !== DYNAMIC_CACHE &&
                     cacheName !== IMAGE_CACHE;
            })
            .map((cacheName) => {
              console.log('[Service Worker] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            })
        );
      })
      .then(() => {
        console.log('[Service Worker] Activation complete');
        return self.clients.claim(); // Take control immediately
      })
  );
});

// Fetch event - handle network requests with caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests (POST, PUT, DELETE handled by sync queue)
  if (request.method !== 'GET') {
    return;
  }

  // Skip chrome extensions and other protocols
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // Check if this is an API request
  const isApiRequest = url.pathname.startsWith('/api/');

  if (isApiRequest) {
    // Check if API should never be cached
    const shouldNotCache = NO_CACHE_PATTERNS.some(pattern => pattern.test(url.pathname));
    
    if (shouldNotCache) {
      // Network only - no caching
      event.respondWith(fetch(request));
      return;
    }

    // Check if API can be cached
    const isCacheable = CACHEABLE_API_PATTERNS.some(pattern => pattern.test(url.pathname));
    
    if (isCacheable) {
      // Network first, fallback to cache (for offline)
      event.respondWith(networkFirstStrategy(request, DYNAMIC_CACHE));
      return;
    }

    // Default for other API requests - network only
    event.respondWith(fetch(request));
    return;
  }

  // Handle image requests
  if (request.destination === 'image') {
    event.respondWith(cacheFirstStrategy(request, IMAGE_CACHE));
    return;
  }

  // Handle static assets (JS, CSS, fonts)
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(cacheFirstStrategy(request, STATIC_CACHE));
    return;
  }

  // Default strategy for other requests
  event.respondWith(networkFirstStrategy(request, DYNAMIC_CACHE));
});

// Network First Strategy - try network, fallback to cache
async function networkFirstStrategy(request, cacheName) {
  try {
    // Try to fetch from network
    const networkResponse = await fetch(request);
    
    // If successful, update cache and return response
    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // Network failed, try cache
    console.log('[Service Worker] Network failed, trying cache:', request.url);
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      console.log('[Service Worker] Serving from cache:', request.url);
      return cachedResponse;
    }
    
    // No cache available, return offline page or error
    console.error('[Service Worker] No cache available for:', request.url);
    
    // For HTML requests, could return offline page
    if (request.destination === 'document') {
      return new Response(
        '<html><body><h1>Offline</h1><p>You are currently offline. Please check your connection.</p></body></html>',
        { headers: { 'Content-Type': 'text/html' } }
      );
    }
    
    // For other requests, return error
    return new Response('Network error', {
      status: 408,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

// Cache First Strategy - try cache, fallback to network
async function cacheFirstStrategy(request, cacheName) {
  // Try cache first
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    console.log('[Service Worker] Serving from cache:', request.url);
    return cachedResponse;
  }
  
  // Cache miss, fetch from network
  try {
    const networkResponse = await fetch(request);
    
    // Cache the response for future use
    if (networkResponse && networkResponse.status === 200) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('[Service Worker] Network and cache failed:', request.url);
    return new Response('Resource not available', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

// Listen for messages from the app
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => caches.delete(cacheName))
        );
      })
    );
  }
});

console.log('[Service Worker] Loaded and ready');
