"""Script to check distance between customer and seller locations"""
from app.utils.location import haversine_distance, geocode_pincode_kerala
from app.core.database import SessionLocal
from app.models.seller import Seller
from app.models.product import Product, ProductStatus

# Customer location
customer_lat = 10.54
customer_lon = 76.02
radius_km = 5

print("=" * 60)
print("Checking Seller Locations and Distance")
print("=" * 60)

# Get database session
db = SessionLocal()

try:
    # Get all sellers with pincode 680512
    sellers = db.query(Seller).filter(Seller.pincode == '680512').all()
    
    print(f"\nFound {len(sellers)} seller(s) with pincode 680512:")
    
    for seller in sellers:
        print(f"\nSeller ID: {seller.id}")
        print(f"Business Name: {seller.business_name}")
        print(f"Pincode: {seller.pincode}")
        print(f"Latitude: {seller.latitude}")
        print(f"Longitude: {seller.longitude}")
        
        if seller.latitude and seller.longitude:
            distance = haversine_distance(
                seller.latitude, seller.longitude,
                customer_lat, customer_lon
            )
            print(f"Distance from customer: {distance:.2f} km")
            print(f"Within {radius_km}km radius: {'YES' if distance <= radius_km else 'NO'}")
            
            # Check products
            products = db.query(Product).filter(
                Product.seller_id == seller.id,
                Product.status == ProductStatus.APPROVED
            ).all()
            print(f"Approved products: {len(products)}")
        else:
            print("WARNING: Seller has no coordinates stored!")
            print("   Geocoding pincode now...")
            coords = geocode_pincode_kerala('680512', db_session=None)
            if coords:
                lat, lon = coords
                distance = haversine_distance(lat, lon, customer_lat, customer_lon)
                print(f"   Pincode coordinates: ({lat}, {lon})")
                print(f"   Distance from customer: {distance:.2f} km")
                print(f"   Within {radius_km}km radius: {'YES' if distance <= radius_km else 'NO'}")
            else:
                print("   ERROR: Failed to geocode pincode")
    
    print("\n" + "=" * 60)
    print("Customer Location:", f"({customer_lat}, {customer_lon})")
    print("Search Radius:", f"{radius_km} km")
    print("=" * 60)
    
finally:
    db.close()

