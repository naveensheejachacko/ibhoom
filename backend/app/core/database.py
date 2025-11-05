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
    """Get connection arguments for PostgreSQL (SSL required for Aiven)"""
    db_url = settings.DATABASE_URL
    
    # PostgreSQL SSL configuration
    connect_args = {}
    if "sslmode=require" in db_url.lower():
        connect_args["sslmode"] = "require"
    
    return connect_args

# Normalize database URL
normalized_db_url = normalize_database_url(settings.DATABASE_URL)

# Create database engine
# PostgreSQL with connection pooling and SSL support
engine = create_engine(
    normalized_db_url,
    connect_args=get_connect_args(),
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Connection pool size
    max_overflow=10  # Max overflow connections
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

