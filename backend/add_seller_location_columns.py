"""
Database migration script to add latitude and longitude columns to sellers table
"""
import sqlite3
import sys
from pathlib import Path

def add_location_columns():
    """Add latitude and longitude columns to sellers table"""
    
    db_path = Path(__file__).parent / "marketplace.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(sellers)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'latitude' in columns and 'longitude' in columns:
            print("Latitude and longitude columns already exist in sellers table")
            return True
        
        # Add latitude column if it doesn't exist
        if 'latitude' not in columns:
            cursor.execute("ALTER TABLE sellers ADD COLUMN latitude REAL")
            print("Added 'latitude' column to sellers table")
        
        # Add longitude column if it doesn't exist
        if 'longitude' not in columns:
            cursor.execute("ALTER TABLE sellers ADD COLUMN longitude REAL")
            print("Added 'longitude' column to sellers table")
        
        conn.commit()
        
        # Now geocode existing sellers' pincodes
        cursor.execute("SELECT id, pincode FROM sellers WHERE latitude IS NULL OR longitude IS NULL")
        sellers = cursor.fetchall()
        
        if sellers:
            print(f"\nGeocoding {len(sellers)} sellers...")
            
            # Import geocoding function
            sys.path.insert(0, str(Path(__file__).parent))
            from app.utils.location import geocode_pincode_kerala
            
            updated_count = 0
            for seller_id, pincode in sellers:
                if pincode:
                    coords = geocode_pincode_kerala(pincode)
                    if coords:
                        lat, lon = coords
                        cursor.execute(
                            "UPDATE sellers SET latitude = ?, longitude = ? WHERE id = ?",
                            (lat, lon, seller_id)
                        )
                        updated_count += 1
                        print(f"  Geocoded seller {seller_id}: {pincode} -> ({lat}, {lon})")
            
            conn.commit()
            print(f"\nSuccessfully geocoded {updated_count} out of {len(sellers)} sellers")
        else:
            print("No sellers need geocoding")
        
        conn.close()
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        return False


if __name__ == "__main__":
    print("Starting database migration...")
    print("Adding latitude and longitude columns to sellers table...\n")
    success = add_location_columns()
    sys.exit(0 if success else 1)


