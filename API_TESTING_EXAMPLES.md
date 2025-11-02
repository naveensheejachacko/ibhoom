# 🧪 API Testing Examples - Location-Based Filtering

Quick reference for testing the location-based product filtering endpoints.

## 🔑 **Setup**

Replace these placeholders with your actual values:
- `YOUR_API_URL` - Your backend URL (e.g., `http://localhost:8000` or `https://api.ibhoom.com`)
- `YOUR_TOKEN` - Customer access token from login

---

## 📍 **1. Get Products by Latitude & Longitude**

### **Products within 25km of Trivandrum**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products?latitude=8.5241&longitude=76.9366&radius_km=25" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### **Products within 50km of Kochi**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products?latitude=9.9312&longitude=76.2673&radius_km=50" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### **Products within 10km of Kozhikode**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products?latitude=11.2588&longitude=75.7804&radius_km=10" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

---

## 🏙️ **2. Get Products by City Name**

### **Products in Thiruvananthapuram area (50km)**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products?city=Thiruvananthapuram&radius_km=50" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### **Products in Kochi area (30km)**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products?city=Kochi&radius_km=30" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### **Products in Thrissur area (40km)**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products?city=Thrissur&radius_km=40" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

---

## 🆕 **3. Get Newly Arrived Products**

### **New products within 25km (last 7 days)**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products/newly-arrived?latitude=8.5241&longitude=76.9366&radius_km=25&days=7" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### **New products by city (last 14 days)**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products/newly-arrived?city=Kochi&radius_km=50&days=14" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

---

## 📂 **4. Get Products by Category**

### **Electronics within 30km**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products/category/CATEGORY_ID?latitude=8.5241&longitude=76.9366&radius_km=30" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

Replace `CATEGORY_ID` with actual category ID from your database.

---

## 🎯 **5. Combined Filters**

### **Electronics, ₹1000-5000, within 50km, sorted by price**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products?latitude=8.5241&longitude=76.9366&radius_km=50&category_id=CATEGORY_ID&min_price=1000&max_price=5000&sort_by=price&sort_order=asc" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### **Search "laptop" within 100km**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products?latitude=8.5241&longitude=76.9366&radius_km=100&search=laptop" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

---

## 🌍 **6. All Products (No Location Filter)**

### **Get all products (original behavior)**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

This returns all products without location filtering.

---

## 📊 **7. Different Radius Options**

### **Very Local (10km)**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products?latitude=8.5241&longitude=76.9366&radius_km=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **City-level (25km)**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products?latitude=8.5241&longitude=76.9366&radius_km=25" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Regional (50km)**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products?latitude=8.5241&longitude=76.9366&radius_km=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **State-level (100km)**
```bash
curl -X GET "YOUR_API_URL/api/v1/customer/products?latitude=8.5241&longitude=76.9366&radius_km=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🧑‍💼 **8. Register Seller with Location**

### **Register new seller (auto-geocodes pincode)**
```bash
curl -X POST "YOUR_API_URL/api/v1/auth/register/seller" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newseller@example.com",
    "password": "SecurePass123",
    "first_name": "Ravi",
    "last_name": "Kumar",
    "phone": "9876543210",
    "business_name": "Ravi Electronics",
    "business_type": "Retail",
    "address": "MG Road, Trivandrum",
    "city": "Thiruvananthapuram",
    "state": "Kerala",
    "pincode": "695001"
  }'
```

Backend will automatically:
1. Geocode pincode `695001` → `(8.5241, 76.9366)`
2. Store coordinates in seller profile
3. Products from this seller will appear in Trivandrum area searches

---

## 🗺️ **9. Kerala Major Cities Coordinates**

Use these coordinates for testing:

```bash
# Thiruvananthapuram
latitude=8.5241&longitude=76.9366

# Kochi (Ernakulam)
latitude=9.9312&longitude=76.2673

# Kozhikode (Calicut)
latitude=11.2588&longitude=75.7804

# Thrissur
latitude=10.5276&longitude=76.2144

# Kollam
latitude=8.8932&longitude=76.6141

# Kannur
latitude=11.8745&longitude=75.3704

# Kottayam
latitude=9.5916&longitude=76.5222

# Palakkad
latitude=10.7905&longitude=76.6545

# Alappuzha
latitude=9.4981&longitude=76.3388

# Malappuram
latitude=10.9446&longitude=76.2552
```

---

## 📝 **10. Expected Response Format**

```json
[
  {
    "id": "product-uuid-1234",
    "name": "iPhone 13",
    "slug": "iphone-13",
    "seller_id": "seller-uuid-5678",
    "category_id": "category-uuid-9012",
    "seller_price": 45000.00,
    "customer_price": 47250.00,
    "commission_rate": 5.00,
    "stock_quantity": 10,
    "status": "approved",
    "created_at": "2024-01-15T10:30:00",
    "images": [
      {
        "id": "image-uuid-3456",
        "image_url": "/uploads/iphone-13.jpg",
        "alt_text": "iPhone 13",
        "sort_order": 0
      }
    ],
    "seller_name": "Ravi Kumar",
    "seller_email": "ravi@example.com"
  }
]
```

---

## ✅ **11. Testing Checklist**

- [ ] Test with valid lat/long
- [ ] Test with city name
- [ ] Test with different radius values (10, 25, 50, 100km)
- [ ] Test without location (should return all products)
- [ ] Test combined with category filter
- [ ] Test combined with price range
- [ ] Test combined with search query
- [ ] Test newly arrived endpoint
- [ ] Test with invalid coordinates (should return empty or error)
- [ ] Register new seller and verify auto-geocoding

---

## 🔍 **12. Verify Database**

### **Check if sellers have coordinates:**
```bash
# Connect to database
sqlite3 backend/marketplace.db

# Query seller locations
SELECT id, business_name, pincode, latitude, longitude 
FROM sellers 
LIMIT 10;
```

### **Expected output:**
```
id                  | business_name      | pincode | latitude | longitude
abc-123-def-456     | Ravi Electronics   | 695001  | 8.5241   | 76.9366
xyz-789-ghi-012     | Tech Store Kochi   | 682001  | 9.9312   | 76.2673
```

---

## 🐛 **13. Common Issues & Solutions**

### **Issue: "401 Unauthorized"**
```
Solution: Check your access token. Get fresh token from login endpoint.
```

### **Issue: Empty array returned**
```
Solutions:
1. Increase radius_km (try 100 or 200)
2. Check if sellers have coordinates in database
3. Run migration: python add_seller_location_columns.py
```

### **Issue: "No products found"**
```
Solutions:
1. Verify sellers exist in that area
2. Check if products are approved
3. Try without location filter to see all products
```

---

## 🎯 **Quick Test Script**

Save as `test_api.sh`:

```bash
#!/bin/bash

API_URL="http://localhost:8000"
TOKEN="your-token-here"

echo "Testing location-based product filtering..."

echo "\n1. Products within 25km of Trivandrum:"
curl -s "$API_URL/api/v1/customer/products?latitude=8.5241&longitude=76.9366&radius_km=25" \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {name, seller_name}'

echo "\n2. Products in Kochi area:"
curl -s "$API_URL/api/v1/customer/products?city=Kochi&radius_km=50" \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {name, seller_name}'

echo "\n3. Newly arrived products:"
curl -s "$API_URL/api/v1/customer/products/newly-arrived?latitude=8.5241&longitude=76.9366&radius_km=50" \
  -H "Authorization: Bearer $TOKEN" | jq '.[] | {name, created_at}'
```

Make executable and run:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## 📚 **Additional Resources**

- **Complete Guide:** See `LOCATION_BASED_FILTERING_GUIDE.md`
- **Flutter Integration:** See `FLUTTER_INTEGRATION_EXAMPLE.md`
- **Implementation Details:** See `IMPLEMENTATION_SUMMARY.md`

---

Happy testing! 🚀









