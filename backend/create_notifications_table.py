"""
Script to create notifications table in the database.
Run this script to add the notifications table to your existing database.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import Base, engine
from app.models.notification import Notification

def create_notifications_table():
    """Create notifications table"""
    print("Creating notifications table...")
    try:
        Notification.__table__.create(engine, checkfirst=True)
        print("✅ Notifications table created successfully!")
    except Exception as e:
        print(f"❌ Error creating notifications table: {e}")
        raise

if __name__ == "__main__":
    create_notifications_table()


