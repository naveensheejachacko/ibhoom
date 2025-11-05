# How Customer Location Filtering Works

## Current Implementation

### How It Works Now:

1. **Customer sends location in request** (not from stored pincode):
   - Customer must provide `latitude` and `longitude` in query parameters
   - OR provide `city` name (which gets geocoded)
   - **Customer's stored pincode is NOT used automatically**

2. **Every request process**:
   ```
   Customer Request → Extract lat/long from query params → Filter products by distance → Return results
   ```

3. **No automatic conversion from stored pincode**:
   - The `User` model has a `pincode` field
   - But it's NOT automatically converted to lat/long for product queries
   - Customer must send lat/long in every request

### Current Flow:

```
GET /api/v1/customer/products?latitude=10.54&longitude=76.02&radius_km=5
              ↓
     Extract lat/long from query params
              ↓
     Load all products from database
              ↓
     For each product:
       - Get seller's lat/long (already stored)
       - Calculate distance using Haversine formula
       - If distance ≤ radius_km → include in results
              ↓
     Return filtered products
```

## Problems with Current Approach:

1. **Customer must send location every time** - inconvenient
2. **Stored pincode is not used** - wasted data
3. **No caching** - location is recalculated on every request

## Recommended Improvement:

### Option 1: Auto-use Customer's Stored Pincode

If customer has pincode in profile, convert it to lat/long automatically:

```python
# In get_all_products endpoint:
if not latitude or not longitude:
    # Try to use customer's stored pincode
    if current_user.pincode:
        coords = geocode_pincode_kerala(current_user.pincode, db_session=None)
        if coords:
            customer_lat, customer_lon = coords
    else:
        raise HTTPException(...)  # Location required
```

### Option 2: Store Customer's Coordinates

Store lat/long in User model when pincode is set:

```python
# Add to User model:
latitude = Column(Float)
longitude = Column(Float)

# When user updates pincode, auto-geocode:
if user.pincode:
    coords = geocode_pincode_kerala(user.pincode)
    if coords:
        user.latitude, user.longitude = coords
```

### Option 3: Use GPS Location (Recommended for Mobile Apps)

For Flutter/mobile apps, get GPS coordinates directly:

```dart
// Flutter example
Position position = await Geolocator.getCurrentPosition();
// Send lat/long to API
```

## Current Code Flow:

1. **Customer Request**: `GET /api/v1/customer/products?latitude=X&longitude=Y`
2. **Backend extracts**: lat/long from query parameters
3. **Loads products**: Gets all approved products with seller relationships
4. **Filters by distance**: For each product, calculates distance to customer
5. **Returns**: Only products within radius_km

## Performance:

- ✅ **Good**: Seller coordinates are stored once (not recalculated)
- ❌ **Bad**: Distance calculation happens for every product on every request
- ❌ **Bad**: No caching of customer location

## Suggested Improvements:

1. **Store customer coordinates** when pincode is set
2. **Cache location** in session/token
3. **Use database-level geospatial queries** (PostGIS) for better performance
4. **Add pagination** to limit distance calculations

