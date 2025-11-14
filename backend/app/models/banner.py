from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..core.database import Base


class BannerPosition(str, enum.Enum):
    """Banner display positions"""
    HOME_TOP = "home_top"
    HOME_MIDDLE = "home_middle"
    HOME_BOTTOM = "home_bottom"
    CATEGORY_TOP = "category_top"
    PRODUCT_TOP = "product_top"
    CART_TOP = "cart_top"
    CHECKOUT_TOP = "checkout_top"


class BannerStatus(str, enum.Enum):
    """Banner status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class Banner(Base):
    __tablename__ = "banners"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    image_url = Column(String(500), nullable=False)
    link_url = Column(String(500))  # Optional link when banner is clicked
    position = Column(Enum(BannerPosition), nullable=False, default=BannerPosition.HOME_TOP)
    status = Column(Enum(BannerStatus), default=BannerStatus.DRAFT)
    sort_order = Column(Integer, default=0)  # For ordering banners in same position
    start_date = Column(DateTime)  # Optional: when banner should start showing
    end_date = Column(DateTime)  # Optional: when banner should stop showing
    click_count = Column(Integer, default=0)  # Track banner clicks
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Banner {self.title} - {self.position.value}>"



