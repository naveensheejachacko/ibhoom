"""
Database migration script to add cart and wishlist tables
"""
import sqlite3
import sys
from pathlib import Path

def add_cart_wishlist_tables():
    """Add cart and wishlist tables to database"""
    
    db_path = Path(__file__).parent / "marketplace.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables already exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='carts'")
        carts_exists = cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wishlists'")
        wishlists_exists = cursor.fetchone() is not None
        
        if carts_exists and wishlists_exists:
            print("Cart and wishlist tables already exist")
            return True
        
        # Create carts table
        if not carts_exists:
            cursor.execute("""
                CREATE TABLE carts (
                    id VARCHAR PRIMARY KEY,
                    customer_id VARCHAR NOT NULL,
                    product_id VARCHAR NOT NULL,
                    product_variant_id VARCHAR,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES users(id),
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    FOREIGN KEY (product_variant_id) REFERENCES product_variants(id)
                )
            """)
            # Create unique index for non-NULL variant_id
            # Note: SQLite doesn't handle NULL in UNIQUE constraints well
            # We handle uniqueness at application level
            print("✅ Created 'carts' table")
            
            # Create index on customer_id for faster queries
            cursor.execute("CREATE INDEX idx_carts_customer_id ON carts(customer_id)")
            print("✅ Created index on carts.customer_id")
        else:
            print("Carts table already exists")
        
        # Create wishlists table
        if not wishlists_exists:
            cursor.execute("""
                CREATE TABLE wishlists (
                    id VARCHAR PRIMARY KEY,
                    customer_id VARCHAR NOT NULL,
                    product_id VARCHAR NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES users(id),
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    UNIQUE(customer_id, product_id)
                )
            """)
            print("✅ Created 'wishlists' table")
            
            # Create index on customer_id for faster queries
            cursor.execute("CREATE INDEX idx_wishlists_customer_id ON wishlists(customer_id)")
            print("✅ Created index on wishlists.customer_id")
        else:
            print("Wishlists table already exists")
        
        conn.commit()
        conn.close()
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting database migration...")
    print("Adding cart and wishlist tables...\n")
    success = add_cart_wishlist_tables()
    sys.exit(0 if success else 1)

