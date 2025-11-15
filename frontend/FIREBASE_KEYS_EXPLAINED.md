# Firebase Keys: What Goes Where?

## 🔑 Key Types Explained

### **VAPID Key (Web Push Certificate)**
- **Type**: Public Key (safe to expose)
- **Location**: Frontend `.env` file
- **Where to get**: Firebase Console → Project Settings → Cloud Messaging → Web Push certificates
- **What it's called**: "Key pair" (but you only need the public key)

### **Service Account JSON**
- **Type**: Contains Private Keys (NEVER expose)
- **Location**: Backend `.env` file ONLY
- **Where to get**: Firebase Console → Project Settings → Service Accounts
- **What it contains**: Private keys for server-side operations

---

## ✅ What Goes in Frontend `.env`

**Add the VAPID KEY (public key)** - This is safe to use in frontend code.

```env
# Firebase VAPID Key (Public Key - Safe for Frontend)
VITE_FIREBASE_VAPID_KEY=BGabcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

**This is the PUBLIC key from the VAPID key pair. It's safe to expose in frontend code.**

---

## ❌ What NEVER Goes in Frontend

**DO NOT add**:
- Service Account JSON (contains private keys)
- Private key from VAPID pair
- Any credentials with "private" in the name

---

## 📍 Where to Find VAPID Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to **Project Settings** (gear icon)
4. Click **Cloud Messaging** tab
5. Scroll to **Web Push certificates** section
6. Click **Generate key pair** (if not already generated)
7. **Copy the key** that appears (this is the public VAPID key)

**Example of what it looks like**:
```
BGabcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

---

## 🔐 Backend vs Frontend Keys

### **Backend `.env`** (Server-side):
```env
# Service Account JSON file path (contains private keys)
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase-service-account.json
```

### **Frontend `.env`** (Client-side):
```env
# VAPID Key (public key - safe to expose)
VITE_FIREBASE_VAPID_KEY=BGabcdefghijklmnopqrstuvwxyz...
```

---

## 🎯 Quick Answer

**For React frontend `.env`, add:**
- ✅ **VAPID Key** (the public key from Web Push certificates)
- ✅ **Firebase Config** (apiKey, projectId, etc.)

**Do NOT add:**
- ❌ Private keys
- ❌ Service Account JSON
- ❌ Any credentials marked as "private"

---

## 📝 Complete Frontend `.env` Example

```env
# API Configuration
VITE_API_URL=http://localhost:8000

# Firebase Configuration (from Project Settings → General)
VITE_FIREBASE_API_KEY=AIzaSyC1234567890abcdefghijklmnopqrstuv
VITE_FIREBASE_AUTH_DOMAIN=myproject.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=myproject-12345
VITE_FIREBASE_STORAGE_BUCKET=myproject-12345.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
VITE_FIREBASE_APP_ID=1:123456789012:web:abcdef1234567890

# Firebase VAPID Key (Public Key - from Cloud Messaging → Web Push certificates)
VITE_FIREBASE_VAPID_KEY=BGabcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

---

## 🔍 How to Verify

After adding to `.env`:

1. **Restart dev server**: `npm run dev`
2. **Check browser console** when you log in:
   - Should see: `✅ Firebase initialized successfully`
   - Should see: `✅ FCM token obtained`
3. **If you see errors**:
   - Check that VAPID key is correct (no extra spaces)
   - Check that all Firebase config values are correct
   - Restart server after changing `.env`

---

## ⚠️ Security Notes

- **VAPID Key (Public)**: Safe to commit to version control (it's public)
- **Service Account JSON**: NEVER commit to version control (contains private keys)
- **Firebase Config**: Safe to commit (these are public identifiers)

---

## Summary

**For React frontend `.env`:**
- ✅ Use **VAPID Key** (public key from Web Push certificates)
- ✅ This is the key you generate in Firebase Console → Cloud Messaging → Web Push certificates
- ✅ It's safe to use in frontend code
- ❌ Do NOT use private keys or service account JSON

