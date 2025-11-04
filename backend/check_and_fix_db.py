"""Check and fix database schema"""
import sqlite3
from pathlib import Path

# Check both possible database locations
db_paths = [
    Path(__file__).parent / "marketplace.db",
    Path(__file__).parent.parent / "marketplace.db"
]

for db_path in db_paths:
    if db_path.exists():
        print(f"\nFound database at: {db_path.absolute()}")
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(sellers)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"\nCurrent columns in sellers table:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Check if latitude/longitude exist
        has_lat = 'latitude' in column_names
        has_lon = 'longitude' in column_names
        
        print(f"\nLocation columns status:")
        print(f"  Latitude: {'✅ EXISTS' if has_lat else '❌ MISSING'}")
        print(f"  Longitude: {'✅ EXISTS' if has_lon else '❌ MISSING'}")
        
        # Add missing columns
        if not has_lat:
            print("\nAdding latitude column...")
            cursor.execute("ALTER TABLE sellers ADD COLUMN latitude REAL")
            conn.commit()
            print("✅ Added latitude column")
        
        if not has_lon:
            print("\nAdding longitude column...")
            cursor.execute("ALTER TABLE sellers ADD COLUMN longitude REAL")
            conn.commit()
            print("✅ Added longitude column")
        
        # Verify after adding
        if not has_lat or not has_lon:
            cursor.execute("PRAGMA table_info(sellers)")
            columns = cursor.fetchall()
            print(f"\nUpdated columns in sellers table:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        print("\n✅ Database check complete!")
        break
else:
    print("❌ Database file not found in expected locations")
    print("Searched locations:")
    for db_path in db_paths:
        print(f"  - {db_path.absolute()}")

