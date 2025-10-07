from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class ProductReview(Base):
    __tablename__ = "product_reviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    customer_id = Column(String, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text)
    is_approved = Column(Boolean, default=True)  # Admin can moderate reviews
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="reviews")
    customer = relationship("User", foreign_keys=[customer_id])

    def __repr__(self):
        return f"<ProductReview {self.rating} stars>"
