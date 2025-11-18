from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime
from ..models.banner import BannerPosition, BannerStatus


class BannerBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    image_url: str = Field(..., min_length=1)
    link_url: Optional[str] = None
    position: BannerPosition = BannerPosition.HOME_TOP
    status: BannerStatus = BannerStatus.DRAFT
    sort_order: int = Field(0, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category_id: Optional[str] = None
    product_id: Optional[str] = None


class BannerCreate(BannerBase):
    pass


class BannerUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, min_length=1)
    link_url: Optional[str] = None
    position: Optional[BannerPosition] = None
    status: Optional[BannerStatus] = None
    sort_order: Optional[int] = Field(None, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    category_id: Optional[str] = None
    product_id: Optional[str] = None


class BannerResponse(BannerBase):
    id: str
    click_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BannerListResponse(BaseModel):
    """Simplified banner response for list views"""
    id: str
    title: str
    image_url: str
    link_url: Optional[str] = None
    position: BannerPosition
    status: BannerStatus
    sort_order: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True






