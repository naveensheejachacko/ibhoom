from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ....core.database import get_db
from ....core.dependencies import get_customer_user
from ....models.user import User
from ....models.banner import Banner, BannerPosition, BannerStatus

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_active_banners(
    position: Optional[BannerPosition] = Query(None, description="Filter by banner position"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get active banners for customer (Customer only)"""
    # Build query for active banners
    query = db.query(Banner).filter(
        Banner.status == BannerStatus.ACTIVE,
        Banner.is_active == True
    )
    
    # Filter by position if provided
    if position:
        query = query.filter(Banner.position == position)
    
    # Check date range if specified
    now = datetime.utcnow()
    query = query.filter(
        (Banner.start_date.is_(None) | (Banner.start_date <= now)),
        (Banner.end_date.is_(None) | (Banner.end_date >= now))
    )
    
    # Get banners ordered by sort_order
    banners = query.order_by(Banner.sort_order.asc(), Banner.created_at.desc()).all()
    
    # Return simplified response
    result = []
    for banner in banners:
        result.append({
            "id": banner.id,
            "title": banner.title,
            "description": banner.description,
            "image_url": banner.image_url,
            "link_url": banner.link_url,
            "position": banner.position.value,
            "sort_order": banner.sort_order
        })
    
    return result


@router.post("/{banner_id}/click")
async def track_banner_click(
    banner_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Track banner click (Customer only)"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
    
    banner.click_count += 1
    db.commit()
    
    return {"message": "Click tracked successfully"}






