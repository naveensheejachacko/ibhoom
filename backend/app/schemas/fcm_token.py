from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FCMTokenCreate(BaseModel):
    token: str
    device_type: Optional[str] = "web"  # 'web', 'android', 'ios'
    device_id: Optional[str] = None


class FCMTokenResponse(BaseModel):
    id: str
    user_id: str
    token: str
    device_type: Optional[str]
    device_id: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_used_at: datetime
    
    class Config:
        from_attributes = True


class FCMTokenUpdate(BaseModel):
    token: Optional[str] = None
    device_type: Optional[str] = None
    is_active: Optional[bool] = None

