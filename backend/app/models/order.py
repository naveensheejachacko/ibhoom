from sqlalchemy import Column, String, Text, DECIMAL, Boolean, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from decimal import Decimal
from ..core.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"                      # Initial status when order placed
    REJECTED = "rejected"                    # Seller rejected the order
    PROCESSING = "processing"                # Seller accepted, preparing order
    READY_FOR_DISPATCH = "ready for dispatch" # Seller packed, ready to dispatch
    DISPATCHED = "dispatched"                # Admin dispatched the order
    DELIVERED = "delivered"                   # Admin marked as delivered
    CANCELLED = "cancelled"                  # Cancelled by seller or admin
    RETURN_REQUESTED = "return requested"    # Customer requested return
    RETURN_APPROVED = "return approved"      # Admin approved return
    RETURN_REJECTED = "return rejected"      # Admin rejected return
    RETURN_PICKED_UP = "return picked up"    # Return item picked up
    RETURN_RECEIVED = "return received"      # Return item received and verified
    REFUND_PROCESSING = "refund processing"  # Refund being processed
    REFUND_COMPLETED = "refund completed"    # Refund completed successfully


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
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.COD_PENDING)
    delivery_address = Column(Text, nullable=False)
    delivery_city = Column(String(100), nullable=False)
    delivery_state = Column(String(100), nullable=False) 
    delivery_pincode = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=False)
    notes = Column(Text)
    admin_notes = Column(Text)
    seller_notes = Column(Text)  # Seller's notes (for rejections, etc.)
    return_reason = Column(Text)  # Customer's reason for return
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