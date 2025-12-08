// Firebase Cloud Messaging Service Worker
// This file must be in the public directory and will be served at the root URL

// Import Firebase SDK
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// Initialize Firebase - Service workers need explicit config
// The config will be passed from the main app via postMessage
let firebaseInitialized = false;
let messaging = null;

// Function to initialize messaging after we have full config
function initializeMessaging() {
  if (!firebaseInitialized || messaging) {
    return; // Don't initialize if Firebase isn't ready or messaging already exists
  }
  
  try {
    // Verify Firebase app exists and has config
    const app = firebase.app();
    if (!app || !app.options || !app.options.projectId) {
      console.warn('[firebase-messaging-sw.js] Firebase app not fully configured yet');
      return;
    }
    
    messaging = firebase.messaging();
    console.log('[firebase-messaging-sw.js] ✅ Firebase messaging initialized');
    
    // Set up background message handler after messaging is initialized
    messaging.onBackgroundMessage((payload) => {
      console.log('[firebase-messaging-sw.js] Received background message:', payload);
      
      const notificationTitle = payload.notification?.title || 'New Notification';
      const notificationOptions = {
        body: payload.notification?.body || '',
        icon: payload.notification?.image || '/ibhoom-logo.png',
        badge: '/ibhoom-logo.png',
        image: payload.notification?.image,
        data: payload.data || {},
        tag: payload.data?.notification_id || payload.data?.order_id || 'default',
        requireInteraction: false,
        silent: false,
      };

      return self.registration.showNotification(notificationTitle, notificationOptions);
    });
  } catch (e) {
    console.error('[firebase-messaging-sw.js] Failed to get messaging instance:', e);
  }
}

// Listen for Firebase config from main app
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'FIREBASE_CONFIG') {
    try {
      const config = event.data.config;
      
      // Validate config has required fields
      if (!config || !config.apiKey || !config.projectId) {
        console.error('[firebase-messaging-sw.js] Invalid Firebase config - missing required fields');
        return;
      }
      
      // Check if Firebase is already initialized
      try {
        const existingApp = firebase.app();
        // App already exists - check if it has the same projectId
        if (existingApp.options.projectId === config.projectId) {
          firebaseInitialized = true;
          console.log('[firebase-messaging-sw.js] Firebase already initialized with same config');
          initializeMessaging();
        } else {
          console.warn('[firebase-messaging-sw.js] Firebase app exists with different projectId');
        }
      } catch (e) {
        // No app exists, initialize with config from main app
        firebase.initializeApp(config);
        firebaseInitialized = true;
        console.log('[firebase-messaging-sw.js] ✅ Firebase initialized with config from main app');
        
        // Initialize messaging after Firebase is ready
        initializeMessaging();
      }
    } catch (error) {
      console.error('[firebase-messaging-sw.js] Failed to initialize Firebase:', error);
    }
  }
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('[firebase-messaging-sw.js] Notification clicked:', event.notification);
  
  event.notification.close();

  const data = event.notification.data || {};
  
  // Determine URL based on notification type
  let url = '/';
  
  if (data.order_id) {
    if (data.type === 'new_order' || data.type === 'order_created') {
      url = '/admin/orders';
    } else if (data.type === 'order_status_update' || data.type === 'order_updated') {
      url = '/seller/orders';
    } else {
      url = '/customer/orders';
    }
  } else if (data.product_id) {
    url = `/products/${data.product_id}`;
  } else if (data.notification_id) {
    // Navigate to notifications page
    if (data.user_role === 'admin') {
      url = '/admin/notifications';
    } else if (data.user_role === 'seller') {
      url = '/seller/notifications';
    } else {
      url = '/customer/notifications';
    }
  }

  // Open or focus the window
  event.waitUntil(
    clients.matchAll({ 
      type: 'window', 
      includeUncontrolled: true 
    }).then((clientList) => {
      // Check if there's already a window/tab open with this URL
      for (let i = 0; i < clientList.length; i++) {
        const client = clientList[i];
        if (client.url.includes(url.split('/')[1]) && 'focus' in client) {
          return client.focus();
        }
      }
      // If no window is open, open a new one
      if (clients.openWindow) {
        return clients.openWindow(url);
      }
    })
  );
});

// Handle service worker installation
self.addEventListener('install', (event) => {
  console.log('[firebase-messaging-sw.js] Service Worker installing...');
  self.skipWaiting(); // Activate immediately
});

// Handle service worker activation
self.addEventListener('activate', (event) => {
  console.log('[firebase-messaging-sw.js] Service Worker activating...');
  event.waitUntil(clients.claim()); // Take control of all pages immediately
});
