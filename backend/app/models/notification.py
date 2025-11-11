from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..core.database import Base


class NotificationType(str, enum.Enum):
    """Types of notifications"""
    NEW_ORDER = "new_order"
    ORDER_STATUS_CHANGED = "order_status_changed"
    PAYMENT_RECEIVED = "payment_received"
    ORDER_CANCELLED = "order_cancelled"
    PRODUCT_APPROVED = "product_approved"
    PRODUCT_REJECTED = "product_rejected"


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)  # Admin or Seller user ID
    notification_type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    order_id = Column(String, ForeignKey("orders.id"), nullable=True)  # Related order if applicable
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    order = relationship("Order", foreign_keys=[order_id])
    
    def __repr__(self):
        return f"<Notification {self.notification_type.value} for {self.user_id}>"


