"""Script to fix seller coordinates for pincode 680512"""
from app.core.database import SessionLocal
from app.models.seller import Seller
from app.utils.location import geocode_pincode_kerala

db = SessionLocal()

try:
    # Find sellers with pincode 680512 that don't have coordinates
    sellers = db.query(Seller).filter(
        Seller.pincode == '680512',
        (Seller.latitude == None) | (Seller.longitude == None)
    ).all()
    
    print(f"Found {len(sellers)} seller(s) without coordinates")
    
    # Geocode pincode 680512
    print("\nGeocoding pincode 680512...")
    coords = geocode_pincode_kerala('680512', db_session=None)
    
    if not coords:
        print("ERROR: Failed to geocode pincode. Trying alternative method...")
        # Try to get approximate coordinates for Thrissur area (680512 is in Thrissur)
        # Thrissur approximate coordinates
        coords = (10.5167, 76.2167)  # Thrissur city center
        print(f"Using approximate coordinates for Thrissur: {coords}")
    else:
        print(f"Geocoded coordinates: {coords}")
    
    lat, lon = coords
    
    # Update sellers
    for seller in sellers:
        print(f"\nUpdating seller: {seller.business_name} (ID: {seller.id})")
        seller.latitude = lat
        seller.longitude = lon
        print(f"  Set coordinates: ({lat}, {lon})")
    
    db.commit()
    print(f"\nSuccessfully updated {len(sellers)} seller(s)")
    
    # Verify distance from customer location
    customer_lat = 10.54
    customer_lon = 76.02
    from app.utils.location import haversine_distance
    distance = haversine_distance(lat, lon, customer_lat, customer_lon)
    print(f"\nDistance from customer location ({customer_lat}, {customer_lon}): {distance:.2f} km")
    print(f"Within 5km radius: {'YES' if distance <= 5 else 'NO'}")
    
    if distance > 5:
        print(f"\nNOTE: Distance is {distance:.2f} km, which is more than 5km.")
        print("You may need to increase radius_km or check if customer location is correct.")
    
finally:
    db.close()

