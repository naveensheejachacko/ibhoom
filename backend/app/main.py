from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .core.database import create_database
from .api.v1 import auth
import os

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS middleware - Must be before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600  # Cache preflight requests for 1 hour
)

# Create upload directory
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)

# Mount static files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

# Import and include admin router
from .api.v1.admin.router import router as admin_router
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])

# Import and include seller router
from .api.v1.seller.router import router as seller_router
app.include_router(seller_router, prefix="/api/v1/seller", tags=["Seller"])

# Import and include customer router
from .api.v1.customer.router import router as customer_router
app.include_router(customer_router, prefix="/api/v1/customer", tags=["Customer"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and create default admin user on startup"""
    try:
        # Initialize Cloudinary if configured
        if settings.CLOUDINARY_URL:
            from .utils.cloudinary_service import configure_cloudinary
            configure_cloudinary(settings.CLOUDINARY_URL)
            print("✅ Cloudinary configured successfully")
            print(f"   Cloudinary URL: {settings.CLOUDINARY_URL[:30]}...")
        else:
            print("⚠️  WARNING: CLOUDINARY_URL not set! Product images will be stored as base64 in database.")
        
        # Initialize Firebase if configured
        if settings.FIREBASE_ENABLED:
            try:
                from .services.firebase_service import initialize_firebase
                firebase_app = initialize_firebase()
                if firebase_app:
                    print("✅ Firebase Cloud Messaging initialized successfully")
                else:
                    print("⚠️  WARNING: Firebase enabled but initialization failed. Check your configuration.")
            except Exception as e:
                print(f"⚠️  Firebase initialization warning: {e}")
        else:
            print("ℹ️  Firebase notifications are disabled (set FIREBASE_ENABLED=true to enable)")
        
        # Initialize default data (admin user, etc.)
        # Note: Migrations should run in startCommand before app starts
        from .utils.init_db import init_db
        init_db()
        print("✅ Database initialization completed successfully")
    except Exception as e:
        print(f"⚠️  Database initialization warning: {e}")
        # Don't fail the startup - this is non-critical

@app.get("/debug/cloudinary")
async def check_cloudinary():
    """Debug endpoint to check Cloudinary configuration"""
    return {
        "cloudinary_configured": settings.CLOUDINARY_URL is not None,
        "cloudinary_url_set": bool(settings.CLOUDINARY_URL),
        "cloudinary_url_preview": settings.CLOUDINARY_URL[:30] + "..." if settings.CLOUDINARY_URL else None
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
