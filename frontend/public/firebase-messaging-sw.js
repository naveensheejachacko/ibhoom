// Firebase Cloud Messaging Service Worker
// This file must be in the public directory and will be served at the root URL

// Import Firebase SDK
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// Initialize Firebase
// The Firebase SDK will automatically use the same configuration as your main app
// Make sure your main app initializes Firebase before this service worker runs
firebase.initializeApp({
  // Firebase config is automatically shared from the main app
  // If you need explicit config, uncomment and add your values:
  /*
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef123456"
  */
});

// Retrieve Firebase Messaging instance
const messaging = firebase.messaging();

// Handle background messages (when app is closed)
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
