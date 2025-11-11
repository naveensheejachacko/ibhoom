from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.notification import NotificationType


class NotificationBase(BaseModel):
    notification_type: NotificationType
    title: str
    message: str
    order_id: Optional[str] = None


class NotificationCreate(NotificationBase):
    user_id: str


class NotificationResponse(NotificationBase):
    id: str
    user_id: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    total_unread: int
    total_count: int


