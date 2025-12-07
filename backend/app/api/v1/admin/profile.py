from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ....core.database import get_db
from ....core.dependencies import get_admin_user
from ....models.user import User
from ....schemas.profile import PasswordUpdate
from ....services import profile_service

router = APIRouter()


@router.put("/password")
async def update_password(
    password_data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update admin's password"""
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

