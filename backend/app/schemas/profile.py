from pydantic import BaseModel, EmailStr
from typing import Optional


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    pincode: Optional[str] = None
    profile_picture: Optional[str] = None


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


class ProfileResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    pincode: Optional[str]
    profile_picture: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    full_name: str
    
    class Config:
        from_attributes = True
