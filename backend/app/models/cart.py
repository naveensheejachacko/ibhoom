from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, DECIMAL, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..core.database import Base


class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    product_variant_id = Column(String, ForeignKey("product_variants.id"), nullable=True)  # Optional - for variant-based products
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")
    variant = relationship("ProductVariant", back_populates="cart_items")
    
    # Note: Unique constraint handled at application level for SQLite compatibility
    # SQLite doesn't handle NULL in UNIQUE constraints well
    
    def __repr__(self):
        return f"<Cart {self.customer_id}-{self.product_id}-{self.product_variant_id}>"


class Wishlist(Base):
    __tablename__ = "wishlists"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = relationship("User", back_populates="wishlist_items")
    product = relationship("Product", back_populates="wishlist_items")
    
    # Unique constraint: one wishlist item per customer per product
    __table_args__ = (
        UniqueConstraint('customer_id', 'product_id', name='unique_wishlist_item'),
    )
    
    def __repr__(self):
        return f"<Wishlist {self.customer_id}-{self.product_id}>"

