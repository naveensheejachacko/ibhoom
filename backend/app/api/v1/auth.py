from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.security import create_access_token, create_refresh_token, verify_password, get_password_hash
from ...models import User, Seller, UserRole
from ...schemas.auth import UserLogin, UserCreate, SellerRegister, Token, UserResponse
from ...core.config import settings

router = APIRouter()
security = HTTPBearer()


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login endpoint for all user types"""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.id, "role": user.role})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/register/customer", response_model=UserResponse)
async def register_customer(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new customer"""
    # Check if user already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Role is automatically set to customer
    
    # Create user
    db_user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        role=UserRole.CUSTOMER,
        is_verified=True  # Auto-verify for demo
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/register/seller", response_model=UserResponse)
async def register_seller(seller_data: SellerRegister, db: Session = Depends(get_db)):
    """Register a new seller"""
    # Check if user already exists
    if db.query(User).filter(User.email == seller_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Role is automatically set to seller (no need to modify seller_data)
    
    # Create user
    db_user = User(
        email=seller_data.email,
        password_hash=get_password_hash(seller_data.password),
        first_name=seller_data.first_name,
        last_name=seller_data.last_name,
        phone=seller_data.phone,
        role=UserRole.SELLER,
        is_verified=True  # Auto-verify for demo
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create seller profile
    db_seller = Seller(
        user_id=db_user.id,
        business_name=seller_data.business_name,
        business_type=seller_data.business_type,
        address=seller_data.address,
        city=seller_data.city,
        state=seller_data.state,
        pincode=seller_data.pincode,
        is_approved=False  # Requires admin approval
    )
    
    db.add(db_seller)
    db.commit()
    
    return db_user


@router.post("/register/admin", response_model=UserResponse)
async def register_admin(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register admin (for development only - should be protected in production)"""
    # Check if user already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Role is automatically set to admin
    
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


# Import here to avoid circular imports
from ...core.dependencies import get_current_user

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user 