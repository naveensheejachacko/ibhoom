"""
Database migration script to add order tracking columns to orders table
Adds: seller_notes, return_reason, return_notes
"""
import sqlite3
import sys
from pathlib import Path

def add_order_tracking_columns():
    """Add seller_notes, return_reason, return_notes columns to orders table"""
    
    db_path = Path(__file__).parent / "marketplace.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(orders)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add seller_notes column if it doesn't exist
        if 'seller_notes' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN seller_notes TEXT")
            print("Added 'seller_notes' column to orders table")
        else:
            print("'seller_notes' column already exists")
        
        # Add return_reason column if it doesn't exist
        if 'return_reason' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN return_reason TEXT")
            print("Added 'return_reason' column to orders table")
        else:
            print("'return_reason' column already exists")
        
        # Add return_notes column if it doesn't exist
        if 'return_notes' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN return_notes TEXT")
            print("Added 'return_notes' column to orders table")
        else:
            print("'return_notes' column already exists")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Order tracking columns migration completed successfully!")
        print("\nNote: OrderStatus enum values have been updated. Restart your application to use the new statuses:")
        print("  - REJECTED")
        print("  - READY_FOR_DISPATCH")
        print("  - DISPATCHED")
        print("  - RETURN_REQUESTED")
        print("  - RETURN_APPROVED")
        print("  - RETURN_REJECTED")
        print("  - RETURNED")
        
        return True
        
    except Exception as e:
        print(f"Error adding columns: {str(e)}")
        return False


if __name__ == "__main__":
    success = add_order_tracking_columns()
    sys.exit(0 if success else 1)




