# 📍 Location-Based Product Filtering Guide

This guide explains the implementation of location-based product filtering for the Ibhoom marketplace, specifically designed for Kerala, India.

## 🎯 **Feature Overview**

Customers can now see only products from sellers near their location. The system:
1. Stores seller location (geocoded from pincode during registration)
2. Receives customer location (lat/long or city name) from Flutter app
3. Filters products to show only those from sellers within a specified radius
4. Uses Haversine formula for accurate distance calculations

---

## 🏗️ **Architecture**

### **Database Changes**
- Added `latitude` and `longitude` columns to `sellers` table
- Automatically geocoded from pincode during seller registration

### **New Components**
1. **Location Utilities** (`backend/app/utils/location.py`)
   - Geocoding functions (pincode → coordinates)
   - Distance calculation (Haversine formula)
   - City name → coordinates lookup
   - Kerala pincode database for faster lookups

2. **Updated API Endpoints**
   - All customer product endpoints now support location filtering
   - Optional parameters: `latitude`, `longitude`, `city`, `radius_km`

---

## 🚀 **How It Works**

### **1. Seller Registration**
When a seller registers with a pincode:
```python
# In auth.py
coords = geocode_pincode_kerala("695001")  # Trivandrum
# Returns: (8.5241, 76.9366)
# Stored in seller.latitude, seller.longitude
```

### **2. Customer Requests Products**
Flutter app sends customer location:

**Option A: Using Latitude & Longitude**
```
GET /api/v1/customer/products?latitude=8.5241&longitude=76.9366&radius_km=25
```

**Option B: Using City Name**
```
GET /api/v1/customer/products?city=Thiruvananthapuram&radius_km=50
```

**Option C: No Location (shows all products)**
```
GET /api/v1/customer/products
```

### **3. Backend Filters Products**
```python
# Calculate distance between customer and each seller
distance = haversine_distance(
    seller_lat, seller_lon,
    customer_lat, customer_lon
)

# Only include if within radius
if distance <= radius_km:
    include_product()
```

---

## 📡 **API Endpoints**

All customer product endpoints support location filtering:

### **1. Get All Products**
```
GET /api/v1/customer/products
```

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `latitude` | float | No | - | Customer's latitude |
| `longitude` | float | No | - | Customer's longitude |
| `city` | string | No | - | Customer's city name |
| `radius_km` | float | No | 50 | Search radius (1-500 km) |
| `category_id` | string | No | - | Filter by category |
| `min_price` | float | No | - | Minimum price |
| `max_price` | float | No | - | Maximum price |
| `search` | string | No | - | Search query |
| `sort_by` | string | No | created_at | Sort by: `created_at`, `price`, `name` |
| `sort_order` | string | No | desc | `asc` or `desc` |
| `skip` | int | No | 0 | Pagination offset |
| `limit` | int | No | 100 | Results per page |

**Example Request:**
```bash
curl -X GET "https://api.ibhoom.com/api/v1/customer/products?latitude=8.5241&longitude=76.9366&radius_km=25" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### **2. Get Newly Arrived Products**
```
GET /api/v1/customer/products/newly-arrived
```

**Query Parameters:**
Same location parameters as above, plus:
- `days`: Number of days to look back (default: 7, max: 30)
- `limit`: Max results (default: 20, max: 100)

### **3. Get Products by Category**
```
GET /api/v1/customer/products/category/{category_id}
```

**Query Parameters:**
Same as "Get All Products" endpoint

---

## 🔧 **Setup & Installation**

### **Step 1: Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### **Step 2: Run Database Migration**
```bash
cd backend
python add_seller_location_columns.py
```

This will:
- Add `latitude` and `longitude` columns to sellers table
- Geocode existing sellers' pincodes automatically

### **Step 3: Restart Backend**
```bash
cd backend
uvicorn app.main:app --reload
```

---

## 📱 **Flutter Integration**

### **1. Get User Location**

#### **Using Geolocator Package**
Add to `pubspec.yaml`:
```yaml
dependencies:
  geolocator: ^10.1.0
```

Get location in Flutter:
```dart
import 'package:geolocator/geolocator.dart';

Future<Position?> getUserLocation() async {
  bool serviceEnabled;
  LocationPermission permission;

  // Check if location services are enabled
  serviceEnabled = await Geolocator.isLocationServiceEnabled();
  if (!serviceEnabled) {
    return null;
  }

  permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied) {
      return null;
    }
  }

  if (permission == LocationPermission.deniedForever) {
    return null;
  }

  // Get current position
  return await Geolocator.getCurrentPosition(
    desiredAccuracy: LocationAccuracy.high
  );
}
```

### **2. Fetch Products with Location**

```dart
Future<List<Product>> fetchNearbyProducts({
  required Position position,
  double radiusKm = 50.0,
}) async {
  final response = await http.get(
    Uri.parse(
      '$apiUrl/api/v1/customer/products'
      '?latitude=${position.latitude}'
      '&longitude=${position.longitude}'
      '&radius_km=$radiusKm'
    ),
    headers: {
      'Authorization': 'Bearer $accessToken',
    },
  );

  if (response.statusCode == 200) {
    final List<dynamic> data = json.decode(response.body);
    return data.map((json) => Product.fromJson(json)).toList();
  } else {
    throw Exception('Failed to load products');
  }
}
```

### **3. Alternative: Fetch by City Name**

```dart
Future<List<Product>> fetchProductsByCity({
  required String cityName,
  double radiusKm = 50.0,
}) async {
  final response = await http.get(
    Uri.parse(
      '$apiUrl/api/v1/customer/products'
      '?city=${Uri.encodeComponent(cityName)}'
      '&radius_km=$radiusKm'
    ),
    headers: {
      'Authorization': 'Bearer $accessToken',
    },
  );

  if (response.statusCode == 200) {
    final List<dynamic> data = json.decode(response.body);
    return data.map((json) => Product.fromJson(json)).toList();
  } else {
    throw Exception('Failed to load products');
  }
}
```

### **4. Example: Products Screen with Location**

```dart
class ProductsScreen extends StatefulWidget {
  @override
  _ProductsScreenState createState() => _ProductsScreenState();
}

class _ProductsScreenState extends State<ProductsScreen> {
  Position? _currentPosition;
  List<Product> _products = [];
  double _radiusKm = 50.0;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProducts();
  }

  Future<void> _loadProducts() async {
    setState(() => _isLoading = true);

    // Get user location
    _currentPosition = await getUserLocation();

    // Fetch nearby products
    if (_currentPosition != null) {
      _products = await fetchNearbyProducts(
        position: _currentPosition!,
        radiusKm: _radiusKm,
      );
    } else {
      // Fallback: show all products if location not available
      _products = await fetchAllProducts();
    }

    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Nearby Products'),
        actions: [
          // Radius selector
          PopupMenuButton<double>(
            initialValue: _radiusKm,
            onSelected: (radius) {
              setState(() => _radiusKm = radius);
              _loadProducts();
            },
            itemBuilder: (context) => [
              PopupMenuItem(value: 10, child: Text('Within 10 km')),
              PopupMenuItem(value: 25, child: Text('Within 25 km')),
              PopupMenuItem(value: 50, child: Text('Within 50 km')),
              PopupMenuItem(value: 100, child: Text('Within 100 km')),
            ],
          ),
        ],
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: _products.length,
              itemBuilder: (context, index) {
                return ProductCard(product: _products[index]);
              },
            ),
    );
  }
}
```

---

## 🗺️ **Kerala Pincode Database**

The system includes a built-in database of major Kerala pincodes for faster geocoding:

```python
KERALA_PINCODE_DB = {
    "695001": (8.5241, 76.9366, "Thiruvananthapuram"),
    "682001": (9.9312, 76.2673, "Ernakulam"),
    "673001": (11.2588, 75.7804, "Kozhikode"),
    "680001": (10.5276, 76.2144, "Thrissur"),
    # ... more pincodes
}
```

**To add more pincodes:**
1. Edit `backend/app/utils/location.py`
2. Add entries to `KERALA_PINCODE_DB` dictionary
3. Format: `"pincode": (latitude, longitude, "city_name")`

---

## ⚙️ **Configuration**

### **Default Radius**
Change default search radius in the API:
```python
# In backend/app/api/v1/customer/products.py
radius_km: Optional[float] = Query(
    50,  # Change this value (in kilometers)
    ge=1, 
    le=500, 
    description="Search radius in kilometers"
)
```

### **Geocoding Service**
The system uses OpenStreetMap Nominatim by default. To use a different service:

1. Edit `backend/app/utils/location.py`
2. Modify the `geocode_pincode()` function
3. Options:
   - Google Maps Geocoding API
   - MapMyIndia API (India-specific)
   - Local pincode database

### **Rate Limiting**
Nominatim has rate limits (1 request/second). For production:
- Use the Kerala pincode database for common pincodes
- Consider caching geocoded results
- Use a paid geocoding service for high traffic

---

## 🧪 **Testing**

### **Test with Postman**

1. **Register a Seller with Pincode:**
```json
POST /api/v1/auth/register/seller
{
  "email": "seller@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "1234567890",
  "business_name": "John's Store",
  "address": "123 Main St",
  "city": "Thiruvananthapuram",
  "state": "Kerala",
  "pincode": "695001"
}
```

2. **Check Seller Coordinates:**
```sql
-- Query the database
SELECT id, business_name, pincode, latitude, longitude 
FROM sellers;
```

3. **Fetch Products by Location:**
```
GET /api/v1/customer/products?latitude=8.5241&longitude=76.9366&radius_km=25
```

### **Test Different Scenarios**

```bash
# 1. Products within 10km of Trivandrum
GET /api/v1/customer/products?latitude=8.5241&longitude=76.9366&radius_km=10

# 2. Products in Kochi area
GET /api/v1/customer/products?city=Kochi&radius_km=30

# 3. Newly arrived products near customer
GET /api/v1/customer/products/newly-arrived?latitude=8.5241&longitude=76.9366&radius_km=50

# 4. Category products with location filter
GET /api/v1/customer/products/category/{category_id}?latitude=8.5241&longitude=76.9366&radius_km=25
```

---

## 📊 **Performance Considerations**

### **Current Implementation**
- ✅ Simple and works for small to medium scale
- ✅ No additional database dependencies
- ❌ Filters in application layer (not database)

### **For Large Scale (>10,000 products)**

Consider using PostGIS for database-level geospatial queries:

1. **Migrate to PostgreSQL with PostGIS**
2. **Create spatial index:**
```sql
CREATE INDEX idx_seller_location 
ON sellers USING GIST(ST_MakePoint(longitude, latitude));
```

3. **Query within radius:**
```sql
SELECT p.* FROM products p
JOIN sellers s ON p.seller_id = s.id
WHERE ST_DWithin(
  ST_MakePoint(s.longitude, s.latitude)::geography,
  ST_MakePoint(:customer_lon, :customer_lat)::geography,
  :radius_meters
);
```

---

## 🔐 **Privacy Considerations**

1. **Location Permissions**: Always request user permission in Flutter
2. **Optional Feature**: Location filtering is optional (if not provided, shows all products)
3. **Seller Privacy**: Only store city-level precision (from pincode), not exact address coordinates
4. **Customer Privacy**: Don't store customer locations on backend

---

## 🐛 **Troubleshooting**

### **Problem: Geocoding Fails**
**Solution:**
- Check internet connection
- Verify pincode is valid Kerala pincode
- Add pincode to local database in `location.py`

### **Problem: No Products Returned**
**Solution:**
- Increase `radius_km` parameter
- Check if sellers have latitude/longitude in database
- Run migration script: `python add_seller_location_columns.py`

### **Problem: Sellers Missing Coordinates**
**Solution:**
```python
# Run this script to geocode existing sellers
python add_seller_location_columns.py
```

### **Problem: Rate Limit Errors**
**Solution:**
- Use the Kerala pincode database for common pincodes
- Add delays between geocoding requests
- Use a paid geocoding service

---

## 📝 **Summary**

### **What Was Implemented:**
✅ Added latitude/longitude to Seller model
✅ Created geocoding utilities for Kerala pincodes
✅ Updated customer product APIs with location filtering
✅ Implemented Haversine distance calculation
✅ Created database migration script
✅ Added comprehensive documentation

### **How to Use:**
1. Run database migration
2. Sellers register with pincode → auto-geocoded
3. Flutter app sends customer location (lat/long or city)
4. Backend filters products within radius
5. Customer sees only nearby sellers' products

### **Next Steps:**
1. Test with real Kerala pincodes
2. Populate Kerala pincode database with more entries
3. Implement in Flutter frontend
4. Consider caching for performance
5. Add distance display on product cards

---

## 🎓 **Resources**

- **Geolocator Package**: https://pub.dev/packages/geolocator
- **Nominatim API**: https://nominatim.org/release-docs/develop/api/Overview/
- **India Post Pincode**: https://www.indiapost.gov.in/
- **Haversine Formula**: https://en.wikipedia.org/wiki/Haversine_formula

---

Need help? Feel free to reach out! 🚀









