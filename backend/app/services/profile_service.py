from sqlalchemy.orm import Session
from typing import Optional
from ..models.user import User
from ..core.security import verify_password, get_password_hash
from ..schemas.profile import ProfileUpdate, PasswordUpdate
import os
import uuid
from datetime import datetime


def update_profile(db: Session, user_id: str, profile_data: ProfileUpdate) -> Optional[User]:
    """Update user profile information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Update fields if provided
    if profile_data.first_name is not None:
        user.first_name = profile_data.first_name
    if profile_data.last_name is not None:
        user.last_name = profile_data.last_name
    if profile_data.email is not None:
        user.email = profile_data.email
    if profile_data.pincode is not None:
        user.pincode = profile_data.pincode
    if profile_data.profile_picture is not None:
        user.profile_picture = profile_data.profile_picture
    
    user.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise e


def update_password(db: Session, user_id: str, password_data: PasswordUpdate) -> bool:
    """Update user password"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    # Verify current password
    if not verify_password(password_data.current_password, user.password_hash):
        raise ValueError("Current password is incorrect")
    
    # Update password
    user.password_hash = get_password_hash(password_data.new_password)
    user.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e


def save_profile_image(file_content: bytes, filename: str) -> str:
    """Save profile image and return the file path"""
    from ..core.config import settings
    
    # Create uploads directory if it doesn't exist
    upload_dir = settings.UPLOAD_DIR
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # Generate unique filename
    file_extension = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return file_path


def delete_profile_image(file_path: str) -> bool:
    """Delete profile image file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception:
        return False
