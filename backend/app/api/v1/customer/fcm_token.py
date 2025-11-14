from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....core.database import get_db
from ....core.dependencies import get_customer_user
from ....models.user import User
from ....schemas.fcm_token import FCMTokenCreate, FCMTokenResponse, FCMTokenUpdate
from ....services import fcm_token_service

router = APIRouter()


@router.post("/register", response_model=FCMTokenResponse, status_code=status.HTTP_201_CREATED)
async def register_fcm_token(
    token_data: FCMTokenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Register or update FCM token for customer (Customer only)"""
    token = fcm_token_service.register_fcm_token(db, current_user.id, token_data)
    return token


@router.delete("/{token}", status_code=status.HTTP_200_OK)
async def delete_fcm_token(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Delete FCM token (Customer only)"""
    success = fcm_token_service.delete_token(db, current_user.id, token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FCM token not found"
        )
    return {"message": "FCM token deleted successfully"}


@router.put("/{token}/deactivate", status_code=status.HTTP_200_OK)
async def deactivate_fcm_token(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Deactivate FCM token (Customer only)"""
    success = fcm_token_service.deactivate_token(db, current_user.id, token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FCM token not found"
        )
    return {"message": "FCM token deactivated successfully"}

