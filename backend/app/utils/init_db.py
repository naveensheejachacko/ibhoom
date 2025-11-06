from sqlalchemy.orm import Session
from ..core.database import SessionLocal, engine
from ..core.security import get_password_hash
from ..models import User, UserRole, CommissionSetting, CommissionType
from ..core.config import settings


def init_db():
    """Initialize database with default data"""
    db = SessionLocal()
    
    try:
        # Check if tables exist first
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if "users" not in tables:
            print("⚠️  Tables not found. Skipping initialization. Run migrations first.")
            return
        
        # Create default admin user
        admin_user = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not admin_user:
            admin_user = User(
                email=settings.ADMIN_EMAIL,
                password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                first_name="Admin",
                last_name="User",
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            print(f"Created admin user: {settings.ADMIN_EMAIL}")
        
        # Create default global commission setting
        global_commission = db.query(CommissionSetting).filter(
            CommissionSetting.type == CommissionType.GLOBAL
        ).first()
        if not global_commission:
            global_commission = CommissionSetting(
                type=CommissionType.GLOBAL,
                commission_rate=settings.DEFAULT_COMMISSION_RATE,
                is_active=True
            )
            db.add(global_commission)
            print(f"Created global commission rate: {settings.DEFAULT_COMMISSION_RATE}%")
        
        db.commit()
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db() 