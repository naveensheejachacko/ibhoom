"""
Create pincode_cache table for caching geocoded pincodes
"""
import sqlite3
from pathlib import Path

def create_pincode_cache_table():
    """Create pincode_cache table"""
    
    db_path = Path(__file__).parent / "marketplace.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='pincode_cache'
        """)
        
        if cursor.fetchone():
            print("✅ pincode_cache table already exists")
            return True
        
        # Create table
        cursor.execute("""
            CREATE TABLE pincode_cache (
                pincode VARCHAR(10) PRIMARY KEY,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                district VARCHAR(100),
                state VARCHAR(100),
                country VARCHAR(100) DEFAULT 'India',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Successfully created pincode_cache table!")
        print("\nTable Schema:")
        print("  - pincode (PRIMARY KEY)")
        print("  - latitude (REAL)")
        print("  - longitude (REAL)")
        print("  - district (VARCHAR)")
        print("  - state (VARCHAR)")
        print("  - country (VARCHAR)")
        print("  - created_at (DATETIME)")
        print("\nThis table will automatically cache geocoded pincodes to avoid repeated API calls.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {str(e)}")
        return False


if __name__ == "__main__":
    print("Creating pincode_cache table...\n")
    success = create_pincode_cache_table()
    
    if success:
        print("\n🎉 Setup complete! The system will now:")
        print("  1. Check cache for pincodes (fastest)")
        print("  2. Check static database (fast)")
        print("  3. Call API and cache result (for new pincodes)")
        print("\nNo need to manually add pincodes - they're cached automatically!")














