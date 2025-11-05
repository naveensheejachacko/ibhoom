# 📱 Flutter Integration Example - Location-Based Product Filtering

This document provides ready-to-use Flutter code examples for implementing location-based product filtering.

## 📦 **Required Packages**

Add to your `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  geolocator: ^10.1.0
  permission_handler: ^11.0.1  # For better permission handling
  shared_preferences: ^2.2.2   # For caching location
```

## 🔧 **1. Location Service**

Create `lib/services/location_service.dart`:

```dart
import 'package:geolocator/geolocator.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LocationService {
  static const String _latKey = 'cached_latitude';
  static const String _lonKey = 'cached_longitude';
  
  /// Get user's current location
  Future<Position?> getCurrentLocation() async {
    try {
      // Check if location services are enabled
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        print('Location services are disabled.');
        return null;
      }

      // Check permissions
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          print('Location permissions are denied');
          return null;
        }
      }
      
      if (permission == LocationPermission.deniedForever) {
        print('Location permissions are permanently denied');
        return null;
      }

      // Get current position
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: Duration(seconds: 10),
      );
      
      // Cache the location
      await _cacheLocation(position);
      
      return position;
    } catch (e) {
      print('Error getting location: $e');
      return null;
    }
  }
  
  /// Get cached location (for faster loading)
  Future<Position?> getCachedLocation() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final lat = prefs.getDouble(_latKey);
      final lon = prefs.getDouble(_lonKey);
      
      if (lat != null && lon != null) {
        return Position(
          latitude: lat,
          longitude: lon,
          timestamp: DateTime.now(),
          accuracy: 0,
          altitude: 0,
          heading: 0,
          speed: 0,
          speedAccuracy: 0,
          altitudeAccuracy: 0,
          headingAccuracy: 0,
        );
      }
      return null;
    } catch (e) {
      print('Error getting cached location: $e');
      return null;
    }
  }
  
  /// Cache location for faster access
  Future<void> _cacheLocation(Position position) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setDouble(_latKey, position.latitude);
      await prefs.setDouble(_lonKey, position.longitude);
    } catch (e) {
      print('Error caching location: $e');
    }
  }
  
  /// Calculate distance between two points (in km)
  double calculateDistance(
    double lat1, double lon1,
    double lat2, double lon2,
  ) {
    return Geolocator.distanceBetween(lat1, lon1, lat2, lon2) / 1000;
  }
}
```

## 🛍️ **2. Product Service with Location**

Create `lib/services/product_service.dart`:

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';
import '../models/product.dart';

class ProductService {
  final String baseUrl;
  final String? accessToken;
  
  ProductService({
    required this.baseUrl,
    this.accessToken,
  });
  
  /// Get products near user's location
  Future<List<Product>> getNearbyProducts({
    Position? position,
    String? city,
    double radiusKm = 50,
    String? categoryId,
    double? minPrice,
    double? maxPrice,
    String? search,
    String sortBy = 'created_at',
    String sortOrder = 'desc',
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      // Build query parameters
      Map<String, String> queryParams = {
        'radius_km': radiusKm.toString(),
        'sort_by': sortBy,
        'sort_order': sortOrder,
        'skip': skip.toString(),
        'limit': limit.toString(),
      };
      
      // Add location parameters
      if (position != null) {
        queryParams['latitude'] = position.latitude.toString();
        queryParams['longitude'] = position.longitude.toString();
      } else if (city != null && city.isNotEmpty) {
        queryParams['city'] = city;
      }
      
      // Add optional filters
      if (categoryId != null) queryParams['category_id'] = categoryId;
      if (minPrice != null) queryParams['min_price'] = minPrice.toString();
      if (maxPrice != null) queryParams['max_price'] = maxPrice.toString();
      if (search != null && search.isNotEmpty) queryParams['search'] = search;
      
      // Build URL
      final uri = Uri.parse('$baseUrl/api/v1/customer/products')
          .replace(queryParameters: queryParams);
      
      // Make request
      final response = await http.get(
        uri,
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Product.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load products: ${response.statusCode}');
      }
    } catch (e) {
      print('Error fetching products: $e');
      rethrow;
    }
  }
  
  /// Get newly arrived products near user
  Future<List<Product>> getNewlyArrivedProducts({
    Position? position,
    String? city,
    double radiusKm = 50,
    int days = 7,
    int limit = 20,
  }) async {
    try {
      Map<String, String> queryParams = {
        'days': days.toString(),
        'limit': limit.toString(),
        'radius_km': radiusKm.toString(),
      };
      
      if (position != null) {
        queryParams['latitude'] = position.latitude.toString();
        queryParams['longitude'] = position.longitude.toString();
      } else if (city != null && city.isNotEmpty) {
        queryParams['city'] = city;
      }
      
      final uri = Uri.parse('$baseUrl/api/v1/customer/products/newly-arrived')
          .replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Product.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load products: ${response.statusCode}');
      }
    } catch (e) {
      print('Error fetching newly arrived products: $e');
      rethrow;
    }
  }
  
  /// Get products by category with location filter
  Future<List<Product>> getProductsByCategory({
    required String categoryId,
    Position? position,
    String? city,
    double radiusKm = 50,
    double? minPrice,
    double? maxPrice,
    String? search,
    String sortBy = 'created_at',
    String sortOrder = 'desc',
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      Map<String, String> queryParams = {
        'radius_km': radiusKm.toString(),
        'sort_by': sortBy,
        'sort_order': sortOrder,
        'skip': skip.toString(),
        'limit': limit.toString(),
      };
      
      if (position != null) {
        queryParams['latitude'] = position.latitude.toString();
        queryParams['longitude'] = position.longitude.toString();
      } else if (city != null && city.isNotEmpty) {
        queryParams['city'] = city;
      }
      
      if (minPrice != null) queryParams['min_price'] = minPrice.toString();
      if (maxPrice != null) queryParams['max_price'] = maxPrice.toString();
      if (search != null && search.isNotEmpty) queryParams['search'] = search;
      
      final uri = Uri.parse('$baseUrl/api/v1/customer/products/category/$categoryId')
          .replace(queryParameters: queryParams);
      
      final response = await http.get(
        uri,
        headers: {
          'Authorization': 'Bearer $accessToken',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Product.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load products: ${response.statusCode}');
      }
    } catch (e) {
      print('Error fetching category products: $e');
      rethrow;
    }
  }
}
```

## 🎨 **3. Products Screen UI**

Create `lib/screens/products_screen.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../services/location_service.dart';
import '../services/product_service.dart';
import '../models/product.dart';
import '../widgets/product_card.dart';

class ProductsScreen extends StatefulWidget {
  @override
  _ProductsScreenState createState() => _ProductsScreenState();
}

class _ProductsScreenState extends State<ProductsScreen> {
  final LocationService _locationService = LocationService();
  late ProductService _productService;
  
  Position? _currentPosition;
  List<Product> _products = [];
  bool _isLoading = true;
  bool _isLoadingLocation = false;
  double _radiusKm = 50.0;
  String _errorMessage = '';
  
  // Filter options
  final List<double> _radiusOptions = [10, 25, 50, 100, 200];
  
  @override
  void initState() {
    super.initState();
    _productService = ProductService(
      baseUrl: 'https://your-api-url.com',
      accessToken: 'YOUR_ACCESS_TOKEN', // Get from auth state
    );
    _initializeLocation();
  }
  
  Future<void> _initializeLocation() async {
    setState(() => _isLoadingLocation = true);
    
    // Try to get cached location first
    _currentPosition = await _locationService.getCachedLocation();
    if (_currentPosition != null) {
      _loadProducts();
    }
    
    // Then get fresh location
    Position? freshPosition = await _locationService.getCurrentLocation();
    if (freshPosition != null) {
      setState(() => _currentPosition = freshPosition);
      _loadProducts();
    }
    
    setState(() => _isLoadingLocation = false);
  }
  
  Future<void> _loadProducts() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });
    
    try {
      final products = await _productService.getNearbyProducts(
        position: _currentPosition,
        radiusKm: _radiusKm,
      );
      
      setState(() {
        _products = products;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load products: $e';
        _isLoading = false;
      });
    }
  }
  
  void _changeRadius(double newRadius) {
    setState(() => _radiusKm = newRadius);
    _loadProducts();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Nearby Products'),
            if (_currentPosition != null)
              Text(
                'Within ${_radiusKm.toInt()} km',
                style: TextStyle(fontSize: 12),
              ),
          ],
        ),
        actions: [
          // Radius selector
          PopupMenuButton<double>(
            icon: Icon(Icons.tune),
            initialValue: _radiusKm,
            onSelected: _changeRadius,
            itemBuilder: (context) => _radiusOptions.map((radius) {
              return PopupMenuItem(
                value: radius,
                child: Row(
                  children: [
                    Icon(
                      Icons.location_on,
                      color: radius == _radiusKm ? Colors.blue : Colors.grey,
                    ),
                    SizedBox(width: 8),
                    Text('Within ${radius.toInt()} km'),
                  ],
                ),
              );
            }).toList(),
          ),
          // Refresh location
          IconButton(
            icon: _isLoadingLocation
                ? SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : Icon(Icons.my_location),
            onPressed: _isLoadingLocation ? null : _initializeLocation,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadProducts,
        child: _buildBody(),
      ),
    );
  }
  
  Widget _buildBody() {
    if (_errorMessage.isNotEmpty) {
      return _buildErrorView();
    }
    
    if (_isLoading) {
      return Center(child: CircularProgressIndicator());
    }
    
    if (_products.isEmpty) {
      return _buildEmptyView();
    }
    
    return ListView.builder(
      padding: EdgeInsets.all(16),
      itemCount: _products.length,
      itemBuilder: (context, index) {
        return ProductCard(product: _products[index]);
      },
    );
  }
  
  Widget _buildErrorView() {
    return Center(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.red),
            SizedBox(height: 16),
            Text(
              'Oops! Something went wrong',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text(
              _errorMessage,
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
            SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _loadProducts,
              icon: Icon(Icons.refresh),
              label: Text('Try Again'),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildEmptyView() {
    return Center(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.location_off, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No products found nearby',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text(
              _currentPosition == null
                  ? 'Enable location to find products near you'
                  : 'Try increasing the search radius',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
            SizedBox(height: 24),
            if (_currentPosition == null)
              ElevatedButton.icon(
                onPressed: _initializeLocation,
                icon: Icon(Icons.location_on),
                label: Text('Enable Location'),
              )
            else
              ElevatedButton.icon(
                onPressed: () => _changeRadius(_radiusKm + 25),
                icon: Icon(Icons.zoom_out_map),
                label: Text('Increase Radius'),
              ),
          ],
        ),
      ),
    );
  }
}
```

## 🏗️ **4. Product Model**

Create `lib/models/product.dart`:

```dart
class Product {
  final String id;
  final String name;
  final String slug;
  final String sellerId;
  final String categoryId;
  final double sellerPrice;
  final double customerPrice;
  final double commissionRate;
  final int stockQuantity;
  final String status;
  final DateTime createdAt;
  final List<ProductImage> images;
  final String? sellerName;
  final String? sellerEmail;
  
  Product({
    required this.id,
    required this.name,
    required this.slug,
    required this.sellerId,
    required this.categoryId,
    required this.sellerPrice,
    required this.customerPrice,
    required this.commissionRate,
    required this.stockQuantity,
    required this.status,
    required this.createdAt,
    required this.images,
    this.sellerName,
    this.sellerEmail,
  });
  
  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'],
      name: json['name'],
      slug: json['slug'],
      sellerId: json['seller_id'],
      categoryId: json['category_id'],
      sellerPrice: (json['seller_price'] as num).toDouble(),
      customerPrice: (json['customer_price'] as num).toDouble(),
      commissionRate: (json['commission_rate'] as num).toDouble(),
      stockQuantity: json['stock_quantity'],
      status: json['status'],
      createdAt: DateTime.parse(json['created_at']),
      images: (json['images'] as List)
          .map((img) => ProductImage.fromJson(img))
          .toList(),
      sellerName: json['seller_name'],
      sellerEmail: json['seller_email'],
    );
  }
}

class ProductImage {
  final String id;
  final String imageUrl;
  final String? altText;
  final int sortOrder;
  
  ProductImage({
    required this.id,
    required this.imageUrl,
    this.altText,
    required this.sortOrder,
  });
  
  factory ProductImage.fromJson(Map<String, dynamic> json) {
    return ProductImage(
      id: json['id'],
      imageUrl: json['image_url'],
      altText: json['alt_text'],
      sortOrder: json['sort_order'],
    );
  }
}
```

## 🎯 **5. Usage Example**

```dart
import 'package:flutter/material.dart';
import 'screens/products_screen.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Ibhoom Marketplace',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: ProductsScreen(),
    );
  }
}
```

## 🔒 **6. Permissions Configuration**

### **Android** (`android/app/src/main/AndroidManifest.xml`)

```xml
<manifest ...>
    <!-- Add permissions -->
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    
    <application ...>
        ...
    </application>
</manifest>
```

### **iOS** (`ios/Runner/Info.plist`)

```xml
<dict>
    <!-- Add location usage descriptions -->
    <key>NSLocationWhenInUseUsageDescription</key>
    <string>We need your location to show nearby products from local sellers</string>
    <key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
    <string>We need your location to show nearby products from local sellers</string>
</dict>
```

## 🎨 **7. Optional: Distance Badge Widget**

Show distance from seller on product cards:

```dart
class DistanceBadge extends StatelessWidget {
  final double distanceKm;
  
  const DistanceBadge({required this.distanceKm});
  
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: _getColorForDistance(distanceKm),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.location_on, size: 14, color: Colors.white),
          SizedBox(width: 4),
          Text(
            '${distanceKm.toStringAsFixed(1)} km',
            style: TextStyle(
              color: Colors.white,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
  
  Color _getColorForDistance(double km) {
    if (km < 5) return Colors.green;
    if (km < 15) return Colors.orange;
    return Colors.red;
  }
}
```

---

## ✅ **Quick Setup Checklist**

- [ ] Add packages to `pubspec.yaml`
- [ ] Configure Android permissions
- [ ] Configure iOS permissions
- [ ] Copy `LocationService` class
- [ ] Copy `ProductService` class
- [ ] Update API base URL and auth token
- [ ] Test location permission flow
- [ ] Test fetching nearby products

---

## 🚀 **Ready to Go!**

Your Flutter app is now ready to show location-based products! The backend will automatically filter products based on the customer's location and the specified radius.

Happy coding! 🎉














