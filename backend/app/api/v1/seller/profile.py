from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from ....core.database import get_db
from ....core.dependencies import get_seller_user
from ....models.user import User
from ....schemas.profile import ProfileUpdate, PasswordUpdate, ProfileResponse
from ....services import profile_service

router = APIRouter()


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_seller_user)
):
    """Get current seller's profile information"""
    return current_user


@router.put("/", response_model=ProfileResponse)
async def update_profile(
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    pincode: Optional[str] = Form(None),
    profile_picture: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Update seller's profile information"""
    try:
        # Prepare profile data
        profile_data = ProfileUpdate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            pincode=pincode
        )
        
        # Handle profile picture upload
        if profile_picture:
            # Validate file type
            if not profile_picture.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only image files are allowed"
                )
            
            # Validate file size (2MB limit)
            file_content = await profile_picture.read()
            if len(file_content) > 2 * 1024 * 1024:  # 2MB
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File size must be less than 2MB"
                )
            
            # Save the image
            file_path = profile_service.save_profile_image(
                file_content, 
                profile_picture.filename
            )
            profile_data.profile_picture = file_path
            
            # Delete old profile picture if exists
            if current_user.profile_picture:
                profile_service.delete_profile_image(current_user.profile_picture)
        
        # Update profile
        updated_user = profile_service.update_profile(db, current_user.id, profile_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return updated_user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.put("/password")
async def update_password(
    password_data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Update seller's password"""
    try:
        success = profile_service.update_password(db, current_user.id, password_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"message": "Password updated successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )


@router.delete("/profile-picture")
async def delete_profile_picture(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Delete seller's profile picture"""
    try:
        if not current_user.profile_picture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No profile picture found"
            )
        
        # Delete the file
        profile_service.delete_profile_image(current_user.profile_picture)
        
        # Update user record
        current_user.profile_picture = None
        db.commit()
        
        return {"message": "Profile picture deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete profile picture"
        )
