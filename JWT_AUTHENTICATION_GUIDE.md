# JWT Authentication Guide

## 🔐 How JWT Works in Your System

Your FastAPI backend uses **JSON Web Tokens (JWT)** for authentication. Here's how it works:

### 1. **Token Types**

Your system uses **two types of tokens**:

- **Access Token**: Short-lived token for API requests
  - **Expires in**: 30 minutes (configurable)
  - **Used for**: All authenticated API requests
  - **Contains**: User ID (`sub`) and Role (`role`)

- **Refresh Token**: Long-lived token for getting new access tokens
  - **Expires in**: 7 days (configurable)
  - **Used for**: Refreshing expired access tokens
  - **Contains**: User ID (`sub`) and Role (`role`)

### 2. **Token Structure**

Each JWT token contains:
```json
{
  "sub": "user-uuid-here",      // User ID
  "role": "customer",            // User role (customer/seller/admin)
  "exp": 1234567890,             // Expiration timestamp
  "type": "access" or "refresh"  // Token type
}
```

### 3. **Token Expiration**

✅ **Yes, tokens DO expire!**

- **Access Token**: Expires after **30 minutes**
- **Refresh Token**: Expires after **7 days**

When a token expires:
- Access token expiration → API returns `401 Unauthorized`
- You need to use the refresh token to get a new access token
- If refresh token also expires → User must login again

---

## 🔄 How Authentication Flow Works

### **Step 1: Login/Register**
```
User → POST /api/v1/auth/login
      Body: { email, password }
      
Backend → Validates credentials
        → Creates access_token (30 min)
        → Creates refresh_token (7 days)
        → Returns both tokens
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "customer@example.com",
    "role": "customer",
    ...
  }
}
```

### **Step 2: Making API Requests**
```
Flutter App → GET /api/v1/customer/products
           → Header: Authorization: Bearer {access_token}
           
Backend → Validates token
        → Extracts user ID and role
        → Returns data
```

### **Step 3: Token Expiration Handling**
```
Access Token Expires → API returns 401
                    → Flutter app detects 401
                    → Uses refresh_token to get new access_token
                    → Retries original request
```

---

## 📱 Flutter Integration Guide

### **1. Store Tokens Securely**

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  final _storage = FlutterSecureStorage();
  
  // Save tokens after login
  Future<void> saveTokens(String accessToken, String refreshToken) async {
    await _storage.write(key: 'access_token', value: accessToken);
    await _storage.write(key: 'refresh_token', value: refreshToken);
  }
  
  // Get access token
  Future<String?> getAccessToken() async {
    return await _storage.read(key: 'access_token');
  }
  
  // Get refresh token
  Future<String?> getRefreshToken() async {
    return await _storage.read(key: 'refresh_token');
  }
  
  // Clear tokens on logout
  Future<void> clearTokens() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
  }
}
```

### **2. Make Authenticated API Requests**

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  final AuthService _authService = AuthService();
  final String baseUrl = 'http://your-api-url.com/api/v1';
  
  Future<Map<String, dynamic>> getProducts({
    required double latitude,
    required double longitude,
    double radiusKm = 5.0,
  }) async {
    final accessToken = await _authService.getAccessToken();
    
    final url = Uri.parse('$baseUrl/customer/products')
        .replace(queryParameters: {
          'latitude': latitude.toString(),
          'longitude': longitude.toString(),
          'radius_km': radiusKm.toString(),
        });
    
    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $accessToken',
        'Content-Type': 'application/json',
      },
    );
    
    // Handle 401 - Token expired
    if (response.statusCode == 401) {
      // Try to refresh token
      final refreshed = await refreshAccessToken();
      if (refreshed) {
        // Retry the request
        return getProducts(
          latitude: latitude,
          longitude: longitude,
          radiusKm: radiusKm,
        );
      } else {
        // Refresh failed - redirect to login
        throw Exception('Session expired. Please login again.');
      }
    }
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load products');
    }
  }
}
```

### **3. Implement Token Refresh**

```dart
class ApiService {
  // ... previous code ...
  
  Future<bool> refreshAccessToken() async {
    final refreshToken = await _authService.getRefreshToken();
    
    if (refreshToken == null) {
      return false;
    }
    
    try {
      final url = Uri.parse('$baseUrl/auth/refresh');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'refresh_token': refreshToken}),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        // Save new tokens (both access and refresh tokens are returned)
        await _authService.saveTokens(
          data['access_token'],
          data['refresh_token'], // New refresh token (also returned)
        );
        return true;
      } else if (response.statusCode == 401) {
        // Refresh token expired - user needs to login again
        await _authService.clearTokens();
        return false;
      }
    } catch (e) {
      print('Token refresh failed: $e');
    }
    
    return false;
  }
}
```

### **4. Login Implementation**

```dart
class AuthService {
  // ... previous code ...
  
  Future<bool> login(String email, String password) async {
    try {
      final url = Uri.parse('$baseUrl/auth/login');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        // Save tokens
        await saveTokens(
          data['access_token'],
          data['refresh_token'],
        );
        
        // Save user data if needed
        // await _storage.write(key: 'user', value: json.encode(data['user']));
        
        return true;
      }
    } catch (e) {
      print('Login failed: $e');
    }
    
    return false;
  }
}
```

### **5. Auto-login After Registration**

Your customer registration endpoint already returns tokens, so you can use the same flow:

```dart
Future<bool> registerCustomer({
  required String email,
  required String password,
  required String firstName,
  required String lastName,
  required String phone,
}) async {
  try {
    final url = Uri.parse('$baseUrl/auth/register/customer');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'email': email,
        'password': password,
        'first_name': firstName,
        'last_name': lastName,
        'phone': phone,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      
      // Auto-login: Save tokens immediately
      await saveTokens(
        data['access_token'],
        data['refresh_token'],
      );
      
      return true;
    }
  } catch (e) {
    print('Registration failed: $e');
  }
  
  return false;
}
```

---

## 🔧 Configuration

### **Current Settings** (`backend/app/core/config.py`)

```python
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Access token expires in 30 minutes
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7     # Refresh token expires in 7 days
JWT_SECRET_KEY = "your-secret-key"    # ⚠️ Change in production!
JWT_ALGORITHM = "HS256"               # HMAC SHA-256
```

### **To Change Token Expiration:**

1. Edit `backend/app/core/config.py`:
   ```python
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Change to 1 hour
   JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30     # Change to 30 days
   ```

2. Or set environment variables:
   ```bash
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
   JWT_REFRESH_TOKEN_EXPIRE_DAYS=30
   ```

---

## 🔐 Security Best Practices

### **1. Change JWT Secret Key in Production**

**⚠️ CRITICAL**: Change the default secret key!

```python
# In .env file or environment variables
JWT_SECRET_KEY=your-super-secret-random-key-minimum-32-characters-long
```

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### **2. Use HTTPS in Production**

Never send tokens over HTTP in production!

### **3. Store Tokens Securely**

- ✅ Use `flutter_secure_storage` for Flutter
- ✅ Use `Keychain` for iOS
- ✅ Use `Keystore` for Android
- ❌ Never store in SharedPreferences or plain text

### **4. Handle Token Expiration Gracefully**

- Automatically refresh tokens when expired
- Show user-friendly messages
- Redirect to login if refresh fails

---

## 📝 API Endpoints Reference

### **Login**
```
POST /api/v1/auth/login
Body: { "email": "...", "password": "..." }
Response: { "access_token": "...", "refresh_token": "...", "user": {...} }
```

### **Register Customer (Auto-login)**
```
POST /api/v1/auth/register/customer
Body: { "email": "...", "password": "...", "first_name": "...", "last_name": "...", "phone": "..." }
Response: { "access_token": "...", "refresh_token": "...", "user": {...} }
```

### **Get Current User**
```
GET /api/v1/auth/me
Header: Authorization: Bearer {access_token}
Response: { "id": "...", "email": "...", "role": "...", ... }
```

### **Using Tokens in API Requests**
```
GET /api/v1/customer/products?latitude=19.0760&longitude=72.8777&radius_km=5
Header: Authorization: Bearer {access_token}
```

---

## 🐛 Troubleshooting

### **Error: 401 Unauthorized**
- Token expired → Use refresh token to get new access token
- Invalid token → User needs to login again
- Token not sent → Check Authorization header

### **Error: 403 Forbidden**
- User doesn't have required role
- User account is inactive

### **Token Not Working**
1. Check if token is being sent in Authorization header
2. Verify token hasn't expired
3. Check if user account is active
4. Verify JWT_SECRET_KEY matches between requests

---

## 📚 Additional Resources

- [JWT.io](https://jwt.io/) - Decode and verify JWT tokens
- [Flutter Secure Storage](https://pub.dev/packages/flutter_secure_storage)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

## 💡 Quick Integration Checklist

- [ ] Install `flutter_secure_storage` package
- [ ] Create `AuthService` class for token management
- [ ] Implement login/register functions
- [ ] Add token refresh logic
- [ ] Add Authorization header to all API requests
- [ ] Handle 401 errors with automatic token refresh
- [ ] Test token expiration handling
- [ ] Change JWT_SECRET_KEY in production
- [ ] Enable HTTPS in production

---

### **Refresh Token Endpoint**
```
POST /api/v1/auth/refresh
Body: { "refresh_token": "..." }
Response: { "access_token": "...", "refresh_token": "...", "user": {...} }
```

✅ **Refresh endpoint is available!** Use this when your access token expires.

---

## 🔄 How to Get New Access Token Using Refresh Token

### **Step-by-Step Process:**

1. **Your access token expires** (after 30 minutes)
2. **API returns 401 Unauthorized**
3. **Call refresh endpoint** with your refresh token
4. **Get new access token** (and optionally new refresh token)
5. **Retry your original request** with new access token

### **Example: Flutter/Dart**

```dart
Future<String?> refreshAndGetAccessToken() async {
  final refreshToken = await _authService.getRefreshToken();
  
  if (refreshToken == null) {
    throw Exception('No refresh token available');
  }
  
  final url = Uri.parse('https://your-api.com/api/v1/auth/refresh');
  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
    body: json.encode({'refresh_token': refreshToken}),
  );
  
  if (response.statusCode == 200) {
    final data = json.decode(response.body);
    
    // Save new tokens
    await _authService.saveTokens(
      data['access_token'],
      data['refresh_token'],
    );
    
    // Return the new access token
    return data['access_token'];
  } else {
    throw Exception('Failed to refresh token');
  }
}
```

### **Example: JavaScript/Fetch**

```javascript
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }
  
  const response = await fetch('https://your-api.com/api/v1/auth/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh_token: refreshToken
    })
  });
  
  if (response.ok) {
    const data = await response.json();
    
    // Save new tokens
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    
    return data.access_token;
  } else {
    throw new Error('Failed to refresh token');
  }
}
```

### **Example: cURL/Command Line**

```bash
curl -X POST "https://your-api.com/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your-refresh-token-here"
  }'
```

### **Example: Python/Requests**

```python
import requests

def refresh_access_token(refresh_token):
    url = "https://your-api.com/api/v1/auth/refresh"
    payload = {"refresh_token": refresh_token}
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        return data['access_token'], data['refresh_token']
    else:
        raise Exception("Failed to refresh token")

# Usage
new_access_token, new_refresh_token = refresh_access_token(old_refresh_token)
```

### **Example: Postman**

1. **Method**: POST
2. **URL**: `{{baseUrl}}/api/v1/auth/refresh`
3. **Headers**: 
   - `Content-Type: application/json`
4. **Body** (raw JSON):
   ```json
   {
     "refresh_token": "{{refreshToken}}"
   }
   ```
5. **Response**: 
   ```json
   {
     "access_token": "new-access-token-here",
     "refresh_token": "new-refresh-token-here",
     "token_type": "bearer",
     "user": {...}
   }
   ```

### **Automatic Token Refresh in API Calls**

Here's a complete example that automatically refreshes tokens when expired:

```dart
class ApiService {
  Future<http.Response> makeAuthenticatedRequest(
    String method,
    String endpoint, {
    Map<String, dynamic>? body,
  }) async {
    String? accessToken = await _authService.getAccessToken();
    
    // Make the request
    var response = await _makeRequest(
      method,
      endpoint,
      accessToken: accessToken,
      body: body,
    );
    
    // If 401, try to refresh token and retry
    if (response.statusCode == 401) {
      final refreshed = await refreshAccessToken();
      if (refreshed) {
        // Get new access token
        accessToken = await _authService.getAccessToken();
        // Retry the original request
        response = await _makeRequest(
          method,
          endpoint,
          accessToken: accessToken,
          body: body,
        );
      } else {
        // Refresh failed - redirect to login
        throw Exception('Session expired');
      }
    }
    
    return response;
  }
  
  Future<http.Response> _makeRequest(
    String method,
    String endpoint, {
    String? accessToken,
    Map<String, dynamic>? body,
  }) async {
    final url = Uri.parse('$baseUrl$endpoint');
    final headers = {
      'Content-Type': 'application/json',
      if (accessToken != null) 'Authorization': 'Bearer $accessToken',
    };
    
    switch (method.toUpperCase()) {
      case 'GET':
        return await http.get(url, headers: headers);
      case 'POST':
        return await http.post(
          url,
          headers: headers,
          body: body != null ? json.encode(body) : null,
        );
      case 'PUT':
        return await http.put(
          url,
          headers: headers,
          body: body != null ? json.encode(body) : null,
        );
      case 'DELETE':
        return await http.delete(url, headers: headers);
      default:
        throw Exception('Unsupported HTTP method');
    }
  }
}
```

### **Response Format**

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "customer@example.com",
    "role": "customer",
    ...
  }
}
```

**Error Responses:**

- **400 Bad Request**: Missing refresh token
  ```json
  {
    "detail": "Refresh token is required"
  }
  ```

- **401 Unauthorized**: Invalid or expired refresh token
  ```json
  {
    "detail": "Invalid or expired refresh token"
  }
  ```

