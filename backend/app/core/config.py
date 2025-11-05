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
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Commission Settings
    DEFAULT_COMMISSION_RATE: float = 8.0  # 8%
    MIN_COMMISSION_RATE: float = 0.0
    MAX_COMMISSION_RATE: float = 30.0
    
    # Admin Configuration
    ADMIN_EMAIL: str = "admin@marketplace.com"
    ADMIN_PASSWORD: str = "admin123"  # Change this!
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

