"""
Admin Setup Endpoint - Hidden endpoint for initial admin account creation
This endpoint is protected by a secret key and should not be publicly documented
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from ....core.database import get_db
from ....core.config import settings
from ....models.user import User, UserRole
from ....schemas.user import UserCreate, UserResponse
from ....core.security import get_password_hash

router = APIRouter()


@router.post("/setup", response_model=UserResponse)
async def setup_admin(
    user_data: UserCreate,
    secret: Optional[str] = Header(None, alias="X-Admin-Setup-Secret"),
    db: Session = Depends(get_db)
):
    """
    Setup initial admin account (Protected by secret key)
    
    This endpoint is hidden and requires a secret key in the header:
    X-Admin-Setup-Secret: <your-secret-key>
    
    Set ADMIN_SETUP_SECRET in your .env file to enable this endpoint.
    """
    # Check if secret key is configured
    if not settings.ADMIN_SETUP_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin setup is not configured. Contact system administrator."
        )
    
    # Verify secret key
    if not secret or secret != settings.ADMIN_SETUP_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing setup secret"
        )
    
    # Check if user already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if admin already exists (optional - can be removed if you want multiple admins)
    existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin account already exists. Use login instead."
        )
    
    # Create admin user
    db_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role=UserRole.ADMIN,
        is_verified=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

