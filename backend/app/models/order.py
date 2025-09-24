from sqlalchemy import Column, String, Text, DECIMAL, Boolean, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..core.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COLLECTED = "collected"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(String, ForeignKey("users.id"), nullable=False)
    total_customer_amount = Column(DECIMAL(10, 2), nullable=False)  # Total amount customer pays
    total_seller_amount = Column(DECIMAL(10, 2), nullable=False)  # Total amount sellers get
    total_commission_amount = Column(DECIMAL(10, 2), nullable=False)  # Total commission admin gets
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    delivery_address = Column(Text, nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_name = Column(String(255), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    
    def __repr__(self):
        return f"<Order {self.order_number}>"


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    variant_id = Column(String, ForeignKey("product_variants.id"))
    seller_id = Column(String, ForeignKey("sellers.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    variant_details = Column(Text)
    quantity = Column(Integer, nullable=False)
    seller_unit_price = Column(DECIMAL(10, 2), nullable=False)  # Price seller gets per unit
    customer_unit_price = Column(DECIMAL(10, 2), nullable=False)  # Price customer pays per unit
    commission_unit_rate = Column(DECIMAL(5, 2), nullable=False)  # Commission rate per unit
    commission_unit_amount = Column(DECIMAL(10, 2), nullable=False)  # Commission amount per unit
    total_seller_amount = Column(DECIMAL(10, 2), nullable=False)  # Total seller amount for this item
    total_customer_amount = Column(DECIMAL(10, 2), nullable=False)  # Total customer amount for this item
    total_commission_amount = Column(DECIMAL(10, 2), nullable=False)  # Total commission for this item
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
    variant = relationship("ProductVariant", back_populates="order_items")
    seller = relationship("Seller", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem {self.order_id}-{self.product_name}>" 