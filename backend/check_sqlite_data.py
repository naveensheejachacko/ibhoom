"""Quick script to check what data exists in SQLite database"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "marketplace.db"

if not db_path.exists():
    print(f"❌ SQLite database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print(f"Found {len(tables)} tables in SQLite database:")
print("=" * 60)

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  {table}: {count} records")

conn.close()

