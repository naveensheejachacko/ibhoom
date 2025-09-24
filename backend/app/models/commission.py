from sqlalchemy import Column, String, DECIMAL, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..core.database import Base


class CommissionType(str, enum.Enum):
    GLOBAL = "global"
    CATEGORY = "category"
    PRODUCT = "product"


class CommissionSetting(Base):
    __tablename__ = "commission_settings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(Enum(CommissionType), nullable=False)
    entity_id = Column(String)  # category_id or product_id
    commission_rate = Column(DECIMAL(5, 2), nullable=False)
    min_seller_price = Column(DECIMAL(10, 2), default=0.00)
    max_seller_price = Column(DECIMAL(10, 2))
    is_active = Column(Boolean, default=True)
    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Note: Relationships will be handled in application logic due to flexible entity_id
    
    def __repr__(self):
        return f"<CommissionSetting {self.type}-{self.commission_rate}%>" 