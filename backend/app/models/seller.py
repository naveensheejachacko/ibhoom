from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..core.database import Base


class Seller(Base):
    __tablename__ = "sellers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    business_name = Column(String(255), nullable=False)
    business_type = Column(String(100))
    address = Column(Text, nullable=False)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    is_approved = Column(Boolean, default=False)
    approval_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="seller")
    products = relationship("Product", back_populates="seller")
    order_items = relationship("OrderItem", back_populates="seller")
    
    def __repr__(self):
        return f"<Seller {self.business_name}>" 