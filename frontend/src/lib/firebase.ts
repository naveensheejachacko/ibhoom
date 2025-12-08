/**
 * Firebase Cloud Messaging (FCM) configuration and utilities
 * 
 * Setup:
 * 1. Install Firebase: npm install firebase
 * 2. Get your Firebase config from Firebase Console → Project Settings → General
 * 3. Get VAPID key from Firebase Console → Project Settings → Cloud Messaging → Web Push certificates
 * 4. Add these to your .env file (see below)
 */

import { initializeApp, getApps, FirebaseApp } from 'firebase/app';
import { getMessaging, getToken, onMessage, Messaging } from 'firebase/messaging';
import { api } from './api';

// Firebase configuration from environment variables
// Get these from Firebase Console → Project Settings → General → Your apps
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || '',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || '',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || '',
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || '',
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '',
  appId: import.meta.env.VITE_FIREBASE_APP_ID || '',
};

// VAPID key from Firebase Console → Project Settings → Cloud Messaging → Web Push certificates
const VAPID_KEY = import.meta.env.VITE_FIREBASE_VAPID_KEY || '';

// Initialize Firebase app
let app: FirebaseApp | null = null;
let messaging: Messaging | null = null;

export const initializeFirebase = (): FirebaseApp | null => {
  if (getApps().length === 0) {
    try {
      app = initializeApp(firebaseConfig);
      console.log('✅ Firebase initialized successfully');
      return app;
    } catch (error) {
      console.error('❌ Firebase initialization error:', error);
      return null;
    }
  }
  return getApps()[0];
};

export const getFirebaseMessaging = (): Messaging | null => {
  if (!app) {
    app = initializeFirebase();
  }
  
  if (!app) {
    console.error('Firebase app not initialized');
    return null;
  }

  if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
    try {
      // Register service worker for background notifications
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/firebase-messaging-sw.js')
          .then((registration) => {
            console.log('✅ Service Worker registered:', registration.scope);
            
            // Send Firebase config to service worker
            if (registration.active) {
              registration.active.postMessage({
                type: 'FIREBASE_CONFIG',
                config: firebaseConfig
              });
            } else if (registration.installing) {
              registration.installing.addEventListener('statechange', () => {
                if (registration.active) {
                  registration.active.postMessage({
                    type: 'FIREBASE_CONFIG',
                    config: firebaseConfig
                  });
                }
              });
            } else if (registration.waiting) {
              registration.waiting.postMessage({
                type: 'FIREBASE_CONFIG',
                config: firebaseConfig
              });
            }
          })
          .catch((error) => {
            console.error('❌ Service Worker registration failed:', error);
          });
      }
      
      messaging = getMessaging(app);
      return messaging;
    } catch (error) {
      console.error('Error getting Firebase messaging:', error);
      return null;
    }
  }
  
  console.warn('Service Worker not supported in this browser');
  return null;
};

/**
 * Request notification permission and get FCM token
 * Call this when user logs in
 */
export const requestNotificationPermission = async (userRole: 'admin' | 'seller' | 'customer'): Promise<string | null> => {
  try {
    // Check if browser supports notifications
    if (!('Notification' in window)) {
      console.warn('This browser does not support notifications');
      return null;
    }

    // Request permission
    const permission = await Notification.requestPermission();
    
    if (permission !== 'granted') {
      console.warn('Notification permission denied');
      return null;
    }

    // Get messaging instance
    const messagingInstance = getFirebaseMessaging();
    if (!messagingInstance) {
      console.error('Firebase messaging not available');
      return null;
    }

    // Check if VAPID key is configured
    if (!VAPID_KEY) {
      console.error('VAPID key not configured. Add VITE_FIREBASE_VAPID_KEY to .env file');
      return null;
    }

    // Get FCM token
    const token = await getToken(messagingInstance, {
      vapidKey: VAPID_KEY,
    });

    if (!token) {
      console.warn('No FCM token available');
      return null;
    }

    console.log('FCM token obtained:', token.substring(0, 20) + '...');

    // Register token with backend
    try {
      await api.post(`/api/v1/${userRole}/fcm-token/register`, {
        token: token,
        device_type: 'web',
      });
      console.log('✅ FCM token registered with backend');
      // Store token in localStorage for logout cleanup
      localStorage.setItem('fcm_token', token);
    } catch (error: any) {
      console.error('Failed to register FCM token with backend:', error);
      // Don't fail if backend registration fails, token is still valid
    }

    return token;
  } catch (error) {
    console.error('Error requesting notification permission:', error);
    return null;
  }
};

/**
 * Delete FCM token
 * Call this when user logs out
 */
export const deleteFCMToken = async (token: string, userRole: 'admin' | 'seller' | 'customer'): Promise<void> => {
  try {
    await api.delete(`/api/v1/${userRole}/fcm-token/${token}`);
    console.log('✅ FCM token deleted');
  } catch (error: any) {
    console.error('Failed to delete FCM token:', error);
  }
};

/**
 * Listen for foreground messages (when app is open)
 */
export const setupForegroundMessageListener = (onMessageReceived?: (payload: unknown) => void) => {
  const messagingInstance = getFirebaseMessaging();
  
  if (!messagingInstance) {
    console.warn('Firebase messaging not available for foreground listener');
    return;
  }

  onMessage(messagingInstance, (payload) => {
    console.log('📬 Foreground message received:', payload);
    
    // Show browser notification
    if (payload.notification) {
      const notification = new Notification(payload.notification.title || 'New Notification', {
        body: payload.notification.body,
        icon: payload.notification.image || '/ibhoom-logo.png',
        badge: '/ibhoom-logo.png',
      });

      // Handle notification click
      notification.onclick = () => {
        window.focus();
        notification.close();
        
        // Navigate to relevant page based on notification data
        if (payload.data?.order_id) {
          const role = payload.data.type === 'new_order' ? 'admin' : 'seller';
          window.location.href = `/${role}/orders`;
        }
      };
    }

    // Call custom handler if provided
    if (onMessageReceived) {
      onMessageReceived(payload);
    }
  });
};

/**
 * Initialize Firebase notifications
 * Call this in your App component or AuthContext after login
 */
export const initializeFirebaseNotifications = async (
  userRole: 'admin' | 'seller' | 'customer',
  onMessageReceived?: (payload: any) => void
) => {
  // Initialize Firebase
  initializeFirebase();
  
  // Request permission and get token
  const token = await requestNotificationPermission(userRole);
  
  if (token) {
    // Setup foreground message listener
    // When a push notification is received, trigger a custom event to refresh notifications
    setupForegroundMessageListener((payload) => {
      // Dispatch custom event to refresh notifications in UI
      window.dispatchEvent(new CustomEvent('notification-received', { detail: payload }));
      
      // Call custom handler if provided
      if (onMessageReceived) {
        onMessageReceived(payload);
      }
    });
    console.log('✅ Firebase notifications initialized');
  } else {
    console.warn('⚠️ Firebase notifications not initialized (permission denied or token unavailable)');
  }
};

