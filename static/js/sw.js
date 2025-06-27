// Enhanced Service Worker for Rhiz PWA
const CACHE_NAME = 'rhiz-pwa-v2';
const STATIC_CACHE = 'rhiz-static-v2';
const DYNAMIC_CACHE = 'rhiz-dynamic-v2';
const OFFLINE_CACHE = 'rhiz-offline-v1';

const STATIC_FILES = [
  '/',
  '/offline.html',
  '/static/manifest.json',
  '/static/js/app.js',
  '/static/js/background-gamification.js',
  '/static/css/mobile.css',
  '/static/css/root-membership-theme.css',
  '/static/images/ourhizome-logo.png',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
];

const OFFLINE_FALLBACKS = {
  '/contacts': '/offline.html',
  '/goals': '/offline.html',
  '/crm/pipeline': '/offline.html',
  '/analytics': '/offline.html'
};

const CACHE_STRATEGIES = {
  // Network first for API calls and dynamic content
  networkFirst: [
    '/api/',
    '/analytics/',
    '/crm/',
    '/integrations/',
    '/network/'
  ],
  
  // Cache first for static assets
  cacheFirst: [
    '/static/',
    'https://cdn.',
    '.css',
    '.js',
    '.png',
    '.jpg',
    '.svg'
  ],
  
  // Stale while revalidate for main pages
  staleWhileRevalidate: [
    '/',
    '/contacts',
    '/goals'
  ]
};

// Install event - cache static files
self.addEventListener('install', event => {
  console.log('[SW] Installing service worker');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('[SW] Caching static files');
        return cache.addAll(STATIC_FILES);
      })
      .catch(err => {
        console.log('[SW] Cache installation failed', err);
      })
  );
  
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[SW] Activating service worker');
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  
  self.clients.claim();
});

// Fetch event - handle network requests
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Determine cache strategy
  const strategy = getCacheStrategy(request.url);
  
  event.respondWith(
    handleRequest(request, strategy)
  );
});

function getCacheStrategy(url) {
  for (const [strategy, patterns] of Object.entries(CACHE_STRATEGIES)) {
    if (patterns.some(pattern => url.includes(pattern))) {
      return strategy;
    }
  }
  return 'networkFirst'; // Default strategy
}

async function handleRequest(request, strategy) {
  switch (strategy) {
    case 'cacheFirst':
      return cacheFirst(request);
    case 'networkFirst':
      return networkFirst(request);
    case 'staleWhileRevalidate':
      return staleWhileRevalidate(request);
    default:
      return networkFirst(request);
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(STATIC_CACHE);
  const cached = await cache.match(request);
  
  if (cached) {
    return cached;
  }
  
  try {
    const response = await fetch(request);
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    return new Response('Offline', { status: 503 });
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    const cache = await caches.open(DYNAMIC_CACHE);
    const cached = await cache.match(request);
    
    if (cached) {
      return cached;
    }
    
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      return caches.match('/offline.html') || 
             new Response('Offline', { status: 503 });
    }
    
    return new Response('Offline', { status: 503 });
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(DYNAMIC_CACHE);
  const cached = await cache.match(request);
  
  // Fetch in background
  const fetchPromise = fetch(request).then(response => {
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  });
  
  // Return cached version immediately if available
  return cached || fetchPromise;
}

// Enhanced background sync for offline actions
self.addEventListener('sync', event => {
  console.log('[SW] Background sync:', event.tag);
  
  if (event.tag === 'contact-sync') {
    event.waitUntil(syncOfflineContacts());
  } else if (event.tag === 'interaction-sync') {
    event.waitUntil(syncOfflineInteractions());
  } else if (event.tag === 'email-sync') {
    event.waitUntil(syncOfflineEmails());
  } else if (event.tag === 'goal-sync') {
    event.waitUntil(syncOfflineGoals());
  }
});

// Push notification handler
self.addEventListener('push', event => {
  console.log('[SW] Push notification received:', event);
  
  const options = {
    body: event.data ? event.data.text() : 'New notification from Rhiz',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      url: '/'
    },
    actions: [
      {
        action: 'open',
        title: 'Open Rhiz',
        icon: '/static/icons/icon-72x72.png'
      },
      {
        action: 'dismiss',
        title: 'Dismiss'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('Rhiz', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  console.log('[SW] Notification clicked:', event);
  
  event.notification.close();
  
  if (event.action === 'open' || !event.action) {
    event.waitUntil(
      clients.openWindow(event.notification.data.url || '/')
    );
  }
});

// Periodic background sync for updates
self.addEventListener('periodicsync', event => {
  console.log('[SW] Periodic sync:', event.tag);
  
  if (event.tag === 'content-sync') {
    event.waitUntil(syncPeriodicContent());
  }
});

async function syncOfflineContacts() {
  try {
    const db = await openOfflineDB();
    const contacts = await getOfflineContacts(db);
    
    for (const contact of contacts) {
      try {
        await fetch('/api/contacts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(contact)
        });
        
        // Remove from offline storage on success
        await removeOfflineContact(db, contact.id);
      } catch (error) {
        console.log('[SW] Failed to sync contact:', contact.name);
      }
    }
  } catch (error) {
    console.log('[SW] Contact sync failed:', error);
  }
}

async function syncOfflineInteractions() {
  try {
    const db = await openOfflineDB();
    const interactions = await getOfflineInteractions(db);
    
    for (const interaction of interactions) {
      try {
        await fetch('/api/interactions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(interaction)
        });
        
        await removeOfflineInteraction(db, interaction.id);
      } catch (error) {
        console.log('[SW] Failed to sync interaction');
      }
    }
  } catch (error) {
    console.log('[SW] Interaction sync failed:', error);
  }
}

// Push notifications
self.addEventListener('push', event => {
  console.log('[SW] Push notification received');
  
  const options = {
    body: 'You have networking follow-ups due',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      url: '/crm/pipeline'
    },
    actions: [
      {
        action: 'view',
        title: 'View Follow-ups',
        icon: '/static/icons/icon-72x72.png'
      },
      {
        action: 'dismiss',
        title: 'Dismiss',
        icon: '/static/icons/icon-72x72.png'
      }
    ]
  };
  
  if (event.data) {
    const data = event.data.json();
    options.body = data.body || options.body;
    options.data.url = data.url || options.data.url;
  }
  
  event.waitUntil(
    self.registration.showNotification('Founder Network AI', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  console.log('[SW] Notification clicked');
  
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow(event.notification.data.url)
    );
  } else if (event.action === 'dismiss') {
    // Just close the notification
    return;
  } else {
    // Default action - open the app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// IndexedDB helpers for offline storage
function openOfflineDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('FounderNetworkOffline', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      
      if (!db.objectStoreNames.contains('contacts')) {
        db.createObjectStore('contacts', { keyPath: 'id' });
      }
      
      if (!db.objectStoreNames.contains('interactions')) {
        db.createObjectStore('interactions', { keyPath: 'id' });
      }
    };
  });
}

function getOfflineContacts(db) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['contacts'], 'readonly');
    const store = transaction.objectStore('contacts');
    const request = store.getAll();
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
}

function removeOfflineContact(db, id) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['contacts'], 'readwrite');
    const store = transaction.objectStore('contacts');
    const request = store.delete(id);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve();
  });
}

function getOfflineInteractions(db) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['interactions'], 'readonly');
    const store = transaction.objectStore('interactions');
    const request = store.getAll();
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
}

function removeOfflineInteraction(db, id) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['interactions'], 'readwrite');
    const store = transaction.objectStore('interactions');
    const request = store.delete(id);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve();
  });
}