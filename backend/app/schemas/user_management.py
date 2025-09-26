from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.user import UserRole


class UserListResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SellerListResponse(BaseModel):
    id: str
    business_name: str
    business_type: str
    address: str
    city: str
    state: str
    pincode: str
    is_verified: bool
    user: UserListResponse
    
    class Config:
        from_attributes = True


class UserStatusUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class SellerStatusUpdate(BaseModel):
    is_verified: Optional[bool] = None


class UserStats(BaseModel):
    total_users: int
    active_users: int
    verified_users: int
    total_sellers: int
    active_sellers: int
    verified_sellers: int
    total_customers: int
    active_customers: int 