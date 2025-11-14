from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
from ....core.database import get_db
from ....core.dependencies import get_admin_user
from ....models.user import User
from ....models.banner import Banner, BannerPosition, BannerStatus
from ....schemas.banner import BannerCreate, BannerUpdate, BannerResponse, BannerListResponse
from ....schemas.pagination import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=BannerResponse, status_code=status.HTTP_201_CREATED)
async def create_banner(
    banner: BannerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new banner (Admin only)"""
    db_banner = Banner(
        id=str(uuid.uuid4()),
        title=banner.title,
        description=banner.description,
        image_url=banner.image_url,
        link_url=banner.link_url,
        position=banner.position,
        status=banner.status,
        sort_order=banner.sort_order,
        start_date=banner.start_date,
        end_date=banner.end_date
    )
    
    db.add(db_banner)
    db.commit()
    db.refresh(db_banner)
    
    return db_banner


@router.get("/", response_model=PaginatedResponse[BannerListResponse])
async def get_all_banners(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=1000, description="Items per page"),
    position: Optional[BannerPosition] = Query(None),
    status: Optional[BannerStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all banners with filtering (Admin only)"""
    # Calculate skip from page
    skip = (page - 1) * limit
    
    # Build query
    query = db.query(Banner)
    
    if position:
        query = query.filter(Banner.position == position)
    if status:
        query = query.filter(Banner.status == status)
    
    # Get total count
    total = query.count()
    
    # Get banners
    banners = query.order_by(Banner.sort_order.asc(), Banner.created_at.desc()).offset(skip).limit(limit).all()
    
    # Calculate pagination metadata
    current_page = page
    pages = (total + limit - 1) // limit if total > 0 else 1
    
    return PaginatedResponse(
        items=banners,
        total=total,
        page=current_page,
        size=limit,
        pages=pages
    )


@router.get("/{banner_id}", response_model=BannerResponse)
async def get_banner(
    banner_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get banner by ID (Admin only)"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
    return banner


@router.put("/{banner_id}", response_model=BannerResponse)
async def update_banner(
    banner_id: str,
    banner_update: BannerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update banner (Admin only)"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
    
    # Update fields
    update_data = banner_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(banner, field, value)
    
    banner.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(banner)
    
    return banner


@router.delete("/{banner_id}")
async def delete_banner(
    banner_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete banner (Admin only)"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
    
    db.delete(banner)
    db.commit()
    
    return {"message": "Banner deleted successfully"}


@router.post("/{banner_id}/track-click")
async def track_banner_click(
    banner_id: str,
    db: Session = Depends(get_db)
):
    """Track banner click (Public endpoint)"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
    
    banner.click_count += 1
    db.commit()
    
    return {"message": "Click tracked successfully"}

