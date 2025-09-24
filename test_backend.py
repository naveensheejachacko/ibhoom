#!/usr/bin/env python3
"""
Simple test script to verify the backend is working
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.core.database import create_database
    from app.models import User, UserRole
    from app.utils.init_db import init_db
    
    print("✅ All imports successful!")
    
    # Create database tables
    print("Creating database tables...")
    create_database()
    print("✅ Database tables created!")
    
    # Initialize database with default data
    print("Initializing database...")
    init_db()
    print("✅ Database initialized!")
    
    print("\n🎉 Backend setup completed successfully!")
    print("\nYou can now run the server with:")
    print("cd backend && python -m app.main")
    print("\nOr with uvicorn:")
    print("cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    
    print("\n📚 API Documentation will be available at:")
    print("http://localhost:8000/docs")
    
    print("\n🔑 Default Admin Credentials:")
    print("Email: admin@marketplace.com")
    print("Password: admin123")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 