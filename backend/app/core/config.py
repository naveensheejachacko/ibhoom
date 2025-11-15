from pydantic_settings import BaseSettings
from typing import Optional, Union
from pydantic import field_validator


class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = "Local Vendor Marketplace"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database Configuration
    # DATABASE_URL must be set in .env file or environment variable
    # For PostgreSQL: postgresql://user:password@host:port/database?sslmode=require
    DATABASE_URL: str  # Required - must be set in .env file (no SQLite fallback)
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Configuration - Accept string or list
    BACKEND_CORS_ORIGINS: Union[str, list] = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173,http://127.0.0.1:3000"
    
    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # Split comma-separated string and strip whitespace
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # File Upload Configuration
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: list = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    
    # Cloudinary Configuration
    CLOUDINARY_URL: Optional[str] = None  # cloudinary://api_key:api_secret@cloud_name
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Commission Settings
    DEFAULT_COMMISSION_RATE: float = 8.0  # 8%
    MIN_COMMISSION_RATE: float = 0.0
    MAX_COMMISSION_RATE: float = 30.0
    
    # Delivery Settings
    MAX_DELIVERY_RADIUS_KM: float = 50.0  # Maximum delivery radius in kilometers (default: 50km)
    DELIVERY_VALIDATION_STRICT: bool = True  # If True, block orders when location validation fails
    
    # Mapbox Geocoding
    MAPBOX_ACCESS_TOKEN: Optional[str] = None
    MAPBOX_GEOCODING_TIMEOUT: float = 5.0
    
    # Admin Configuration
    ADMIN_EMAIL: str = "admin@marketplace.com"
    ADMIN_PASSWORD: str = "admin123"  # Change this!
    ADMIN_SETUP_SECRET: Optional[str] = None  # Secret key for admin setup endpoint (set in .env)
    
    # Email/SMTP Configuration for Notifications
    SMTP_ENABLED: bool = False  # Set to True to enable email notifications
    SMTP_HOST: str = "smtp.gmail.com"  # SMTP server host
    SMTP_PORT: int = 587  # SMTP server port (587 for TLS, 465 for SSL)
    SMTP_USE_TLS: bool = True  # Use TLS encryption
    SMTP_USERNAME: Optional[str] = None  # SMTP username (usually your email)
    SMTP_PASSWORD: Optional[str] = None  # SMTP password or app password
    SMTP_FROM_EMAIL: str = "noreply@marketplace.com"  # From email address
    
    # Firebase Cloud Messaging (FCM) Configuration
    FIREBASE_ENABLED: bool = False  # Set to True to enable Firebase push notifications
    FIREBASE_SERVICE_ACCOUNT_PATH: Optional[str] = None  # Path to Firebase service account JSON file
    FIREBASE_SERVICE_ACCOUNT_JSON: Optional[str] = None  # Firebase service account JSON as string (alternative to file path)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

