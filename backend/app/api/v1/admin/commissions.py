from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....core.dependencies import get_admin_user
from ....models.user import User
from ....models.commission import CommissionType
from ....schemas.commission import (
    CommissionSettingCreate, 
    CommissionSettingUpdate, 
    CommissionSettingResponse,
    CommissionCalculation
)
from ....services import commission_service

router = APIRouter()


@router.post("/", response_model=CommissionSettingResponse, status_code=status.HTTP_201_CREATED)
async def create_commission_setting(
    commission: CommissionSettingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new commission setting (Admin only)"""
    try:
        db_commission = commission_service.create_commission_setting(db, commission)
        return db_commission
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[CommissionSettingResponse])
async def get_commission_settings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    commission_type: Optional[CommissionType] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get commission settings with optional filtering (Admin only)"""
    commissions = commission_service.get_commission_settings(
        db, skip=skip, limit=limit, commission_type=commission_type, active_only=active_only
    )
    return commissions


@router.get("/{commission_id}", response_model=CommissionSettingResponse)
async def get_commission_setting(
    commission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get commission setting by ID (Admin only)"""
    commission = commission_service.get_commission_setting(db, commission_id)
    if not commission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commission setting not found")
    return commission


@router.put("/{commission_id}", response_model=CommissionSettingResponse)
async def update_commission_setting(
    commission_id: str,
    commission_update: CommissionSettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update commission setting (Admin only)"""
    updated_commission = commission_service.update_commission_setting(db, commission_id, commission_update)
    if not updated_commission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commission setting not found")
    return updated_commission


@router.delete("/{commission_id}")
async def delete_commission_setting(
    commission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete commission setting (Admin only)"""
    deleted = commission_service.delete_commission_setting(db, commission_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commission setting not found")
    return {"message": "Commission setting deleted successfully"}


@router.post("/calculate", response_model=CommissionCalculation)
async def calculate_commission(
    seller_price: float = Query(..., gt=0),
    commission_rate: float = Query(..., ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Calculate commission for a given price and rate (Admin only)"""
    calculation = commission_service.calculate_commission(seller_price, commission_rate)
    return calculation


@router.get("/rate/calculate", response_model=dict)
async def get_applicable_commission_rate(
    category_id: str = Query(...),
    product_id: Optional[str] = Query(None),
    seller_price: float = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get applicable commission rate for a product/category (Admin only)"""
    commission_rate = commission_service.get_commission_rate(
        db, category_id=category_id, product_id=product_id, seller_price=seller_price
    )
    calculation = commission_service.calculate_commission(seller_price, commission_rate)
    
    return {
        "commission_rate": commission_rate,
        "calculation": calculation
    }


@router.get("/global/rate")
async def get_global_commission_rate(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get current global commission rate (Admin only)"""
    rate = commission_service.get_global_commission_rate(db)
    return {"global_commission_rate": rate} 