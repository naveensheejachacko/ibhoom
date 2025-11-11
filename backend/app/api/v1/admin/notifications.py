from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....core.dependencies import get_admin_user
from ....models.user import User
from ....schemas.notification import NotificationResponse, NotificationListResponse, NotificationUpdate
from ....services import notification_service

router = APIRouter()


@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get admin notifications (Admin only)"""
    notifications = notification_service.get_user_notifications(
        db, current_user.id, skip=skip, limit=limit, unread_only=unread_only
    )
    
    total_unread = notification_service.get_unread_count(db, current_user.id)
    total_count = len(notifications)
    
    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        total_unread=total_unread,
        total_count=total_count
    )


@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get count of unread notifications (Admin only)"""
    count = notification_service.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.put("/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Mark a notification as read (Admin only)"""
    success = notification_service.mark_as_read(db, notification_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    return {"message": "Notification marked as read"}


@router.put("/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Mark all notifications as read (Admin only)"""
    count = notification_service.mark_all_as_read(db, current_user.id)
    return {"message": f"{count} notification(s) marked as read"}

