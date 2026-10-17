/**
 * UKIS Mountain Disaster Early-Warning Service Worker
 * Offline Resilience & Web Push for iOS & Android
 * Works during complete data failure & cellular packet blackout
 */

const CACHE_NAME = 'ukis-emergency-offline-v1';
const CRITICAL_OFFLINE_ASSETS = [
  '/',
  '/guidebook',
  '/shelters',
  '/manifest.json',
];

// Offline emergency fallback payload
const OFFLINE_EMERGENCY_STATE = {
  status: 'OFFLINE_SURVIVAL_MODE',
  message: 'Cellular data or grid power unreachable. Serving cached mountain disaster survival protocols.',
  emergency_helplines: {
    police_disaster: '112',
    state_control_seoc: '1070',
    district_eoc: '1077',
    ambulance: '108',
  },
  evacuation_rules: [
    'Move immediately to designated high ground above 1900m contour line.',
    'Vacate all riverbed transit corridors (Alaknanda, Bhagirathi, Mandakini, Dhauliganga, Kali).',
    'Do not attempt to cross flooded causeways or swollen mountain torrents.',
    'Conserve mobile battery: switch to 2G plain-text SMS mode.',
  ],
};

// Install Event: Cache critical emergency pages and offline assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[UKIS SW] Pre-caching critical disaster assets for offline iOS/Android use');
      return cache.addAll(CRITICAL_OFFLINE_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// Activate Event: Clean up stale caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[UKIS SW] Removing stale cache:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event: Network-first with aggressive offline cache fallback
self.addEventListener('fetch', (event) => {
  // Pass through non-GET requests
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        // Cache successful responses for offline use
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(async () => {
        // Network failed (no mobile data, power failure, or airplane mode)
        const cachedResponse = await caches.match(event.request);
        if (cachedResponse) {
          return cachedResponse;
        }

        // Return offline JSON for API requests
        if (event.request.url.includes('/api/')) {
          return new Response(JSON.stringify(OFFLINE_EMERGENCY_STATE), {
            headers: { 'Content-Type': 'application/json' },
            status: 200,
          });
        }

        // Return fallback to offline guidebook
        return caches.match('/guidebook');
      })
  );
});

// Push Notification Event: High-Priority Emergency Alert for iOS & Android
self.addEventListener('push', (event) => {
  let alertData = {
    title: '🚨 CRITICAL FLASH FLOOD WARNING (USDMA)',
    body: 'Evacuate riverbed settlements immediately to designated high-ground shelters. Dial 112 for rescue.',
    url: '/',
    tag: 'critical-emergency-warning',
  };

  try {
    if (event.data) {
      alertData = Object.assign(alertData, event.data.json());
    }
  } catch (e) {
    if (event.data) alertData.body = event.data.text();
  }

  const notificationOptions = {
    body: alertData.body,
    icon: '/icon-192.png',
    badge: '/icon-192.png',
    tag: alertData.tag || 'disaster-alert',
    renotify: true,
    requireInteraction: true, // Remains on screen until user interacts
    vibrate: [500, 200, 500, 200, 1000], // Statutory emergency vibration pattern
    data: { url: alertData.url || '/' },
    actions: [
      { action: 'shelter', title: 'Find Safe Shelter' },
      { action: 'call112', title: 'Call SOS 112' },
    ],
  };

  event.waitUntil(
    self.registration.showNotification(alertData.title, notificationOptions)
  );
});

// Notification Click Event
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  if (event.action === 'call112') {
    clients.openWindow('tel:112');
  } else if (event.action === 'shelter') {
    clients.openWindow('/shelters');
  } else {
    clients.openWindow(event.notification.data?.url || '/');
  }
});
