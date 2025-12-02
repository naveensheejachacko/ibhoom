from sqlalchemy import Column, String, Text, DECIMAL, Boolean, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from decimal import Decimal
from ..core.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"                      # Initial status when order placed
    REJECTED = "REJECTED"                    # Seller rejected the order
    PROCESSING = "PROCESSING"                # Seller accepted, preparing order
    READY_FOR_DISPATCH = "READY_FOR_DISPATCH" # Seller packed, ready to dispatch
    DISPATCHED = "DISPATCHED"                # Admin dispatched the order
    DELIVERED = "DELIVERED"                   # Admin marked as delivered
    CANCELLED = "CANCELLED"                  # Cancelled by seller or admin
    RETURN_REQUESTED = "RETURN_REQUESTED"    # Customer requested return
    RETURN_APPROVED = "RETURN_APPROVED"      # Admin approved return
    RETURN_REJECTED = "RETURN_REJECTED"      # Admin rejected return
    RETURN_PICKED_UP = "RETURN_PICKED_UP"    # Return item picked up
    RETURN_RECEIVED = "RETURN_RECEIVED"      # Return item received and verified
    REFUND_PROCESSING = "REFUND_PROCESSING"  # Refund being processed
    REFUND_COMPLETED = "REFUND_COMPLETED"    # Refund completed successfully


class PaymentStatus(str, enum.Enum):
    COD_PENDING = "cod_pending"
    COD_COLLECTED = "cod_collected"
    PAID = "paid"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(String, ForeignKey("users.id"), nullable=False)
    total_customer_amount = Column(DECIMAL(10, 2), nullable=False)  # Subtotal before tax
    total_tax_amount = Column(DECIMAL(10, 2), nullable=False, default=Decimal('0.00'))  # Total tax collected
    grand_total_amount = Column(DECIMAL(10, 2), nullable=False, default=Decimal('0.00'))  # Total amount customer pays (subtotal + tax)
    total_seller_amount = Column(DECIMAL(10, 2), nullable=False)  # Total amount sellers get
    total_commission_amount = Column(DECIMAL(10, 2), nullable=False)  # Total commission admin gets
    status = Column(Enum(OrderStatus, name='orderstatus', native_enum=True, create_type=False), default=OrderStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus, name='paymentstatus', native_enum=True, create_type=False), default=PaymentStatus.COD_PENDING)
    delivery_address = Column(Text, nullable=False)
    delivery_city = Column(String(100), nullable=False)
    delivery_state = Column(String(100), nullable=False) 
    delivery_pincode = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=False)
    notes = Column(Text)
    admin_notes = Column(Text)
    seller_notes = Column(Text)  # Seller's notes (for rejections, etc.)
    return_reason = Column(Text)  # Customer's reason for return
    return_images = Column(Text, nullable=True)  # JSON array of return image URLs
    return_notes = Column(Text)   # Admin's notes for return processing
    return_requested_at = Column(DateTime)  # When return was requested
    refund_amount = Column(DECIMAL(10, 2))  # Amount refunded
    refund_date = Column(DateTime)  # When refund was completed
    refund_notes = Column(Text)  # Notes about refund
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    
    @property
    def total_items(self) -> int:
        """Calculate total number of items in order"""
        return sum(item.quantity for item in self.items)
    
    def __repr__(self):
        return f"<Order {self.order_number}>"


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    product_variant_id = Column(String, ForeignKey("product_variants.id"))
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    seller_unit_price = Column(DECIMAL(10, 2), nullable=False)  # Price seller gets per unit
    customer_unit_price = Column(DECIMAL(10, 2), nullable=False)  # Price customer pays per unit
    commission_unit_rate = Column(DECIMAL(5, 2), nullable=False)  # Commission rate per unit
    commission_unit_amount = Column(DECIMAL(10, 2), nullable=False)  # Commission amount per unit
    total_seller_amount = Column(DECIMAL(10, 2), nullable=False)  # Total seller amount for this item
    total_customer_amount = Column(DECIMAL(10, 2), nullable=False)  # Total customer amount for this item (before tax)
    total_commission_amount = Column(DECIMAL(10, 2), nullable=False)  # Total commission for this item
    tax_rate = Column(DECIMAL(5, 2), nullable=False, default=Decimal('18.00'))  # Tax rate applied to this item
    tax_unit_amount = Column(DECIMAL(10, 2), nullable=False, default=Decimal('0.00'))  # Tax per unit
    total_tax_amount = Column(DECIMAL(10, 2), nullable=False, default=Decimal('0.00'))  # Total tax for this item
    final_unit_price = Column(DECIMAL(10, 2), nullable=False, default=Decimal('0.00'))  # Unit price including tax
    total_final_amount = Column(DECIMAL(10, 2), nullable=False, default=Decimal('0.00'))  # Total including tax
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")
    
    def __repr__(self):
        return f"<OrderItem {self.order_id}-{self.product_name}>" 