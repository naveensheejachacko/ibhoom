"""
Script to migrate data from SQLite (marketplace.db) to PostgreSQL
Run this script to transfer all data while preserving relationships.
"""
import sqlite3
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.database import normalize_database_url, get_connect_args
from app.models import (
    User, UserRole, Category, Seller, Product, ProductVariant,
    ProductImage, Order, OrderItem, Cart, Wishlist, ProductReview,
    Attribute, AttributeValue, CategoryAttribute, CommissionSetting
)

# Path to SQLite database
SQLITE_DB_PATH = Path(__file__).parent / "marketplace.db"

def get_sqlite_connection():
    """Get SQLite connection"""
    if not SQLITE_DB_PATH.exists():
        print(f"Error: SQLite database not found at {SQLITE_DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(str(SQLITE_DB_PATH))

def get_postgres_session():
    """Get PostgreSQL session"""
    db_url = normalize_database_url(settings.DATABASE_URL)
    connect_args = get_connect_args()
    
    engine = create_engine(db_url, connect_args=connect_args)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()

def migrate_table(sqlite_conn, postgres_session, table_name, model_class, order_key=None):
    """Migrate data from SQLite to PostgreSQL for a specific table"""
    print(f"\n📦 Migrating {table_name}...")
    
    sqlite_cursor = sqlite_conn.cursor()
    
    # Check if table exists in SQLite
    sqlite_cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    if not sqlite_cursor.fetchone():
        print(f"   ⚠️  Table {table_name} doesn't exist in SQLite, skipping...")
        return 0
    
    # Get all columns from SQLite
    sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in sqlite_cursor.fetchall()]
    
    if not columns:
        print(f"   ⚠️  No columns found in {table_name}, skipping...")
        return 0
    
    # Get all rows
    columns_str = ", ".join(columns)
    query = f"SELECT {columns_str} FROM {table_name}"
    if order_key:
        query += f" ORDER BY {order_key}"
    
    sqlite_cursor.execute(query)
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f"   ℹ️  No data in {table_name}")
        return 0
    
    # Create column mapping
    column_map = dict(zip(columns, range(len(columns))))
    
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    # Process in batches for better performance
    batch_size = 100
    batch = []
    
    for row_idx, row in enumerate(rows, 1):
        try:
            # Create dictionary from row
            row_dict = {}
            for col, idx in column_map.items():
                value = row[idx] if idx < len(row) else None
                row_dict[col] = value
            
            # Handle enum conversions
            if 'role' in row_dict and isinstance(row_dict['role'], str):
                try:
                    row_dict['role'] = UserRole(row_dict['role'])
                except ValueError:
                    print(f"   ⚠️  Invalid role '{row_dict['role']}' in row {row_idx}, skipping...")
                    skipped_count += 1
                    continue
            
            # Handle status enums for products and orders
            if 'status' in row_dict and isinstance(row_dict['status'], str):
                # Let SQLAlchemy handle the enum conversion
                pass
            
            # Check if record already exists (by id)
            if 'id' in row_dict and row_dict['id']:
                existing = postgres_session.query(model_class).filter_by(id=row_dict['id']).first()
                if existing:
                    skipped_count += 1
                    if row_idx % 50 == 0:  # Print progress every 50 records
                        print(f"   ⏭️  Skipped {skipped_count} existing records...")
                    continue
            
            # Remove None values for optional fields to avoid issues
            row_dict = {k: v for k, v in row_dict.items() if v is not None or k in ['id']}
            
            # Create model instance
            instance = model_class(**row_dict)
            batch.append(instance)
            
            # Commit in batches
            if len(batch) >= batch_size:
                try:
                    for item in batch:
                        postgres_session.add(item)
                    postgres_session.commit()
                    migrated_count += len(batch)
                    print(f"   ✅ Migrated batch of {len(batch)} records (total: {migrated_count})...")
                    batch = []
                except Exception as e:
                    postgres_session.rollback()
                    print(f"   ❌ Error in batch: {e}")
                    # Try individual inserts for this batch
                    for item in batch:
                        try:
                            postgres_session.add(item)
                            postgres_session.commit()
                            migrated_count += 1
                        except Exception as err:
                            postgres_session.rollback()
                            error_count += 1
                            if error_count <= 5:  # Show first 5 errors
                                print(f"   ❌ Error inserting individual record: {err}")
                    batch = []
            
        except Exception as e:
            error_count += 1
            if row_idx <= 10:  # Show first 10 errors
                print(f"   ❌ Error migrating row {row_idx}: {e}")
            continue
    
    # Commit remaining batch
    if batch:
        try:
            for item in batch:
                postgres_session.add(item)
            postgres_session.commit()
            migrated_count += len(batch)
        except Exception as e:
            postgres_session.rollback()
            print(f"   ❌ Error committing final batch: {e}")
            # Try individual inserts
            for item in batch:
                try:
                    postgres_session.add(item)
                    postgres_session.commit()
                    migrated_count += 1
                except Exception as err:
                    postgres_session.rollback()
                    error_count += 1
                    if error_count <= 5:  # Show first 5 errors
                        print(f"   ❌ Error inserting final record: {err}")
    
    print(f"   ✅ Completed: {migrated_count} migrated, {skipped_count} skipped, {error_count} errors")
    return migrated_count

def main():
    """Main migration function"""
    print("🚀 Starting SQLite to PostgreSQL Migration")
    print("=" * 60)
    
    # Check SQLite database exists
    if not SQLITE_DB_PATH.exists():
        print(f"❌ SQLite database not found at {SQLITE_DB_PATH}")
        print("   Please ensure marketplace.db exists in the backend directory")
        sys.exit(1)
    
    sqlite_conn = get_sqlite_connection()
    postgres_session = get_postgres_session()
    
    try:
        # Migration order is important due to foreign key constraints
        # 1. Users (no dependencies)
        # 2. Categories (no dependencies, but self-referential)
        # 3. Attributes (no dependencies)
        # 4. Sellers (depends on Users)
        # 5. Products (depends on Sellers, Categories)
        # 6. Product Variants, Images (depends on Products)
        # 7. Orders (depends on Users)
        # 8. Order Items (depends on Orders, Products)
        # 9. Cart, Wishlist (depends on Users, Products)
        # 10. Reviews (depends on Users, Products)
        # 11. Commission Settings (depends on Categories)
        
        migration_order = [
            ("users", User),
            ("categories", Category),
            ("attributes", Attribute),
            ("attribute_values", AttributeValue),
            ("category_attributes", CategoryAttribute),
            ("sellers", Seller),
            ("products", Product),
            ("product_variants", ProductVariant),
            ("product_images", ProductImage),
            ("orders", Order),
            ("order_items", OrderItem),
            ("carts", Cart),
            ("wishlists", Wishlist),
            ("product_reviews", ProductReview),
            ("commission_settings", CommissionSetting),
        ]
        
        total_migrated = 0
        
        for table_name, model_class in migration_order:
            count = migrate_table(sqlite_conn, postgres_session, table_name, model_class)
            total_migrated += count
        
        print("\n" + "=" * 60)
        print(f"✅ Migration Complete!")
        print(f"   Total records migrated: {total_migrated}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        postgres_session.rollback()
        sys.exit(1)
    finally:
        sqlite_conn.close()
        postgres_session.close()

if __name__ == "__main__":
    main()

