from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....core.dependencies import get_admin_user
from ....models.user import User, UserRole
from ....models.seller import Seller
from ....schemas.user_management import (
    UserListResponse, 
    SellerListResponse, 
    UserStatusUpdate, 
    SellerStatusUpdate,
    UserStats
)

router = APIRouter()


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get user statistics (Admin only)"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    verified_users = db.query(User).filter(User.is_verified == True).count()
    
    total_sellers = db.query(User).filter(User.role == UserRole.SELLER).count()
    active_sellers = db.query(User).filter(
        User.role == UserRole.SELLER, User.is_active == True
    ).count()
    verified_sellers = db.query(User).join(Seller).filter(
        User.role == UserRole.SELLER, Seller.is_verified == True
    ).count()
    
    total_customers = db.query(User).filter(User.role == UserRole.CUSTOMER).count()
    active_customers = db.query(User).filter(
        User.role == UserRole.CUSTOMER, User.is_active == True
    ).count()
    
    return UserStats(
        total_users=total_users,
        active_users=active_users,
        verified_users=verified_users,
        total_sellers=total_sellers,
        active_sellers=active_sellers,
        verified_sellers=verified_sellers,
        total_customers=total_customers,
        active_customers=active_customers
    )


@router.get("/", response_model=List[UserListResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get users with filtering (Admin only)"""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    
    if search:
        query = query.filter(
            User.first_name.contains(search) |
            User.last_name.contains(search) |
            User.email.contains(search)
        )
    
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users


@router.get("/sellers", response_model=List[SellerListResponse])
async def get_sellers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_verified: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get sellers with filtering (Admin only)"""
    query = db.query(Seller).join(User)
    
    if is_verified is not None:
        query = query.filter(Seller.is_verified == is_verified)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if search:
        query = query.filter(
            Seller.business_name.contains(search) |
            User.first_name.contains(search) |
            User.last_name.contains(search) |
            User.email.contains(search)
        )
    
    sellers = query.order_by(Seller.created_at.desc()).offset(skip).limit(limit).all()
    return sellers


@router.get("/{user_id}", response_model=UserListResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get user by ID (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}/status", response_model=UserListResponse)
async def update_user_status(
    user_id: str,
    status_update: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update user status (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id and status_update.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate yourself")
    
    update_data = status_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.put("/sellers/{seller_id}/status", response_model=SellerListResponse)
async def update_seller_status(
    seller_id: str,
    status_update: SellerStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update seller verification status (Admin only)"""
    seller = db.query(Seller).filter(Seller.id == seller_id).first()
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")
    
    update_data = status_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(seller, field, value)
    
    db.commit()
    db.refresh(seller)
    return seller


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete user (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself")
    
    # Soft delete
    user.is_active = False
    db.commit()
    
    return {"message": "User deleted successfully"} 