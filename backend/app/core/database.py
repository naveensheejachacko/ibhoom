from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

def normalize_database_url(db_url: str) -> str:
    """Normalize database URL to ensure proper driver specification"""
    # Convert postgres:// to postgresql:// for better compatibility
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return db_url

def get_connect_args():
    """Get connection arguments based on database type"""
    db_url = settings.DATABASE_URL
    
    if "sqlite" in db_url:
        return {"check_same_thread": False}
    elif "postgres" in db_url.lower():
        # Handle SSL for PostgreSQL (Aiven requires SSL)
        connect_args = {}
        # Extract sslmode from URL if present
        if "sslmode=require" in db_url.lower():
            connect_args["sslmode"] = "require"
        return connect_args
    return {}

# Normalize database URL
normalized_db_url = normalize_database_url(settings.DATABASE_URL)

# Create database engine
# For PostgreSQL: Use connection pooling and SSL support
# For SQLite: Use thread-safe configuration
is_postgres = "postgres" in normalized_db_url.lower()

engine = create_engine(
    normalized_db_url,
    connect_args=get_connect_args(),
    pool_pre_ping=True if is_postgres else False,  # Verify connections before using them (PostgreSQL)
    pool_size=5 if is_postgres else None,  # Connection pool for PostgreSQL
    max_overflow=10 if is_postgres else None  # Max overflow for PostgreSQL
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

