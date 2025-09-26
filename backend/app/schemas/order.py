from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime
from ..models.order import OrderStatus, PaymentStatus


class OrderItemBase(BaseModel):
    product_variant_id: Optional[str] = None
    product_id: str  # Can order main product or variant
    quantity: int
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: str
    seller_unit_price: float
    customer_unit_price: float
    commission_unit_rate: float
    commission_unit_amount: float
    total_seller_amount: float
    total_customer_amount: float
    total_commission_amount: float
    product_name: str
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    delivery_address: str
    delivery_city: str
    delivery_state: str
    delivery_pincode: str
    phone: str
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Order must have at least one item')
        return v


class OrderResponse(OrderBase):
    id: str
    customer_id: str
    total_customer_amount: float
    total_seller_amount: float
    total_commission_amount: float
    status: OrderStatus
    payment_status: PaymentStatus
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    id: str
    customer_id: str
    total_customer_amount: float
    total_items: int
    status: OrderStatus
    payment_status: PaymentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    admin_notes: Optional[str] = None


class PaymentStatusUpdate(BaseModel):
    payment_status: PaymentStatus
    admin_notes: Optional[str] = None


class OrderStats(BaseModel):
    total_orders: int
    pending_orders: int
    processing_orders: int
    shipped_orders: int
    delivered_orders: int
    cancelled_orders: int
    total_revenue: float
    total_commission: float 