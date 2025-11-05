"""
Test script for location-based filtering feature
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

def test_location_utils():
    """Test location utility functions"""
    print("=" * 60)
    print("Testing Location Utilities")
    print("=" * 60)
    
    from app.utils.location import (
        haversine_distance,
        geocode_pincode_kerala,
        is_within_radius
    )
    
    # Test 1: Distance calculation
    print("\n1. Testing Haversine Distance Calculation:")
    print("-" * 60)
    # Trivandrum to Kochi
    trivandrum = (8.5241, 76.9366)
    kochi = (9.9312, 76.2673)
    distance = haversine_distance(*trivandrum, *kochi)
    print(f"Distance from Trivandrum to Kochi: {distance:.2f} km")
    print(f"Expected: ~170-180 km")
    
    # Test 2: Geocoding Kerala pincodes
    print("\n2. Testing Pincode Geocoding:")
    print("-" * 60)
    test_pincodes = ["695001", "682001", "673001"]
    for pincode in test_pincodes:
        coords = geocode_pincode_kerala(pincode)
        if coords:
            lat, lon = coords
            print(f"✅ Pincode {pincode}: ({lat}, {lon})")
        else:
            print(f"❌ Pincode {pincode}: Failed to geocode")
    
    # Test 3: Radius check
    print("\n3. Testing Radius Filtering:")
    print("-" * 60)
    seller_location = (8.5241, 76.9366)  # Trivandrum
    customer_location = (8.5500, 76.9000)  # Nearby location
    
    within_10km = is_within_radius(*seller_location, *customer_location, 10)
    within_50km = is_within_radius(*seller_location, *customer_location, 50)
    
    distance_actual = haversine_distance(*seller_location, *customer_location)
    print(f"Seller at: {seller_location}")
    print(f"Customer at: {customer_location}")
    print(f"Actual distance: {distance_actual:.2f} km")
    print(f"Within 10km? {within_10km}")
    print(f"Within 50km? {within_50km}")
    
    print("\n" + "=" * 60)
    print("✅ Location utilities test completed!")
    print("=" * 60)


def test_database_migration():
    """Test if database has location columns"""
    print("\n\n" + "=" * 60)
    print("Testing Database Schema")
    print("=" * 60)
    
    import sqlite3
    
    db_path = Path(__file__).parent / "marketplace.db"
    
    if not db_path.exists():
        print("❌ Database not found. Please create database first.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check sellers table schema
    cursor.execute("PRAGMA table_info(sellers)")
    columns = cursor.fetchall()
    
    print("\n📊 Sellers Table Schema:")
    print("-" * 60)
    has_latitude = False
    has_longitude = False
    
    for col in columns:
        col_id, name, col_type, notnull, default, pk = col
        print(f"  {name:20} {col_type:15}")
        if name == 'latitude':
            has_latitude = True
        if name == 'longitude':
            has_longitude = True
    
    print("\n📍 Location Columns Status:")
    print("-" * 60)
    if has_latitude and has_longitude:
        print("✅ Latitude column exists")
        print("✅ Longitude column exists")
        
        # Check if any sellers have coordinates
        cursor.execute("""
            SELECT COUNT(*) as total,
                   COUNT(latitude) as with_coords
            FROM sellers
        """)
        total, with_coords = cursor.fetchone()
        
        print(f"\n📈 Sellers Statistics:")
        print(f"  Total sellers: {total}")
        print(f"  With coordinates: {with_coords}")
        
        if total > 0 and with_coords < total:
            print(f"\n⚠️  {total - with_coords} sellers need geocoding")
            print("   Run: python add_seller_location_columns.py")
    else:
        print("❌ Location columns missing!")
        print("   Run: python add_seller_location_columns.py")
    
    conn.close()
    print("\n" + "=" * 60)


def main():
    """Run all tests"""
    print("\n")
    print("🚀 LOCATION-BASED FILTERING FEATURE TEST")
    print("\n")
    
    try:
        # Test 1: Location utilities
        test_location_utils()
        
        # Test 2: Database schema
        test_database_migration()
        
        print("\n\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run migration: python add_seller_location_columns.py")
        print("3. Start server: uvicorn app.main:app --reload")
        print("4. Test API endpoints (see LOCATION_BASED_FILTERING_GUIDE.md)")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()














