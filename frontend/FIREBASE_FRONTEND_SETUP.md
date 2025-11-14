# Firebase Frontend Setup Guide

This guide shows you exactly where to add the VAPID key and Firebase configuration in your frontend.

## Step 1: Install Firebase SDK

```bash
cd frontend
npm install firebase
```

## Step 2: Get Firebase Configuration

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to **Project Settings** (gear icon) → **General** tab
4. Scroll down to **Your apps** section
5. If you don't have a web app, click **Add app** → **Web** (</> icon)
6. Copy the Firebase configuration values

## Step 3: Get VAPID Key

1. In Firebase Console, go to **Project Settings** → **Cloud Messaging** tab
2. Scroll down to **Web Push certificates** section
3. Click **Generate key pair** button
4. Copy the generated key (this is your VAPID key)

## Step 4: Create .env File

Create a `.env` file in the `frontend` directory:

```env
# API Configuration
VITE_API_URL=http://localhost:8000

# Firebase Configuration (from Step 2)
VITE_FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
VITE_FIREBASE_APP_ID=1:123456789012:web:abcdef123456

# Firebase VAPID Key (from Step 3)
VITE_FIREBASE_VAPID_KEY=BGXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## Step 5: Add .env to .gitignore

Make sure your `.env` file is in `.gitignore`:

```gitignore
# Environment variables
.env
.env.local
.env.production
```

## Step 6: Restart Development Server

After creating/updating `.env`, restart your dev server:

```bash
npm run dev
```

## How It Works

The Firebase service (`src/lib/firebase.ts`) automatically:
1. Reads configuration from `.env` file
2. Initializes Firebase when user logs in
3. Requests notification permission
4. Gets FCM token using the VAPID key
5. Registers token with backend
6. Listens for incoming push notifications

## File Structure

```
frontend/
├── .env                    ← Add your VAPID key here
├── .env.example            ← Template (already created)
├── src/
│   ├── lib/
│   │   ├── firebase.ts     ← Firebase service (already created)
│   │   └── api.ts
│   └── contexts/
│       └── AuthContext.tsx ← Auto-initializes Firebase on login
```

## Testing

1. Make sure `.env` file has all Firebase config values
2. Start the app: `npm run dev`
3. Log in as admin or seller
4. Check browser console for:
   - ✅ Firebase initialized successfully
   - ✅ FCM token obtained
   - ✅ FCM token registered with backend

## Troubleshooting

### "VAPID key not configured"
- Make sure `VITE_FIREBASE_VAPID_KEY` is set in `.env`
- Restart dev server after adding to `.env`

### "Firebase initialization error"
- Check all `VITE_FIREBASE_*` values in `.env`
- Verify values match Firebase Console

### "Notification permission denied"
- User must grant notification permission
- Check browser settings if permission was previously denied

### Notifications not received
- Verify FCM token is registered (check backend database)
- Check browser console for errors
- Make sure Firebase is enabled in backend `.env`

## Example .env File

```env
VITE_API_URL=http://localhost:8000

VITE_FIREBASE_API_KEY=AIzaSyC1234567890abcdefghijklmnopqrstuv
VITE_FIREBASE_AUTH_DOMAIN=myproject.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=myproject-12345
VITE_FIREBASE_STORAGE_BUCKET=myproject-12345.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789012
VITE_FIREBASE_APP_ID=1:123456789012:web:abcdef1234567890

VITE_FIREBASE_VAPID_KEY=BGabcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

**Important**: Replace all placeholder values with your actual Firebase configuration!

