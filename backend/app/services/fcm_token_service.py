"""
Service for managing FCM tokens (register, update, delete)
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime
import uuid

from ..models.fcm_token import FCMToken
from ..schemas.fcm_token import FCMTokenCreate, FCMTokenUpdate


def register_fcm_token(
    db: Session,
    user_id: str,
    token_data: FCMTokenCreate
) -> FCMToken:
    """
    Register or update an FCM token for a user.
    If token already exists, update it. Otherwise, create new.
    
    Args:
        db: Database session
        user_id: User ID
        token_data: FCM token data
        
    Returns:
        FCMToken object
    """
    # Check if token already exists (for any user)
    existing_token = db.query(FCMToken).filter(
        FCMToken.token == token_data.token
    ).first()
    
    if existing_token:
        # If token exists for different user, deactivate it
        if existing_token.user_id != user_id:
            existing_token.is_active = False
            db.commit()
            # Create new token for this user
            new_token = FCMToken(
                id=str(uuid.uuid4()),
                user_id=user_id,
                token=token_data.token,
                device_type=token_data.device_type,
                device_id=token_data.device_id,
                is_active=True
            )
            db.add(new_token)
            db.commit()
            db.refresh(new_token)
            return new_token
        else:
            # Update existing token
            existing_token.device_type = token_data.device_type or existing_token.device_type
            existing_token.device_id = token_data.device_id or existing_token.device_id
            existing_token.is_active = True
            existing_token.last_used_at = datetime.utcnow()
            existing_token.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_token)
            return existing_token
    
    # Create new token
    new_token = FCMToken(
        id=str(uuid.uuid4()),
        user_id=user_id,
        token=token_data.token,
        device_type=token_data.device_type,
        device_id=token_data.device_id,
        is_active=True
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    return new_token


def get_user_tokens(
    db: Session,
    user_id: str,
    active_only: bool = True
) -> List[FCMToken]:
    """
    Get all FCM tokens for a user.
    
    Args:
        db: Database session
        user_id: User ID
        active_only: If True, only return active tokens
        
    Returns:
        List of FCM tokens
    """
    query = db.query(FCMToken).filter(FCMToken.user_id == user_id)
    
    if active_only:
        query = query.filter(FCMToken.is_active == True)
    
    return query.order_by(FCMToken.last_used_at.desc()).all()


def deactivate_token(
    db: Session,
    user_id: str,
    token: str
) -> bool:
    """
    Deactivate an FCM token.
    
    Args:
        db: Database session
        user_id: User ID
        token: FCM token to deactivate
        
    Returns:
        True if deactivated, False if not found
    """
    fcm_token = db.query(FCMToken).filter(
        and_(
            FCMToken.user_id == user_id,
            FCMToken.token == token
        )
    ).first()
    
    if not fcm_token:
        return False
    
    fcm_token.is_active = False
    fcm_token.updated_at = datetime.utcnow()
    db.commit()
    return True


def delete_token(
    db: Session,
    user_id: str,
    token: str
) -> bool:
    """
    Delete an FCM token.
    
    Args:
        db: Database session
        user_id: User ID
        token: FCM token to delete
        
    Returns:
        True if deleted, False if not found
    """
    fcm_token = db.query(FCMToken).filter(
        and_(
            FCMToken.user_id == user_id,
            FCMToken.token == token
        )
    ).first()
    
    if not fcm_token:
        return False
    
    db.delete(fcm_token)
    db.commit()
    return True

