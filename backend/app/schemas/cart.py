from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class CartItemBase(BaseModel):
    product_id: str
    product_variant_id: Optional[str] = None
    quantity: int
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class CartItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    product_variant_id: Optional[str] = None
    variant_name: Optional[str] = None
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    tax_rate: Decimal  # Tax percentage
    tax_unit_amount: Decimal  # Tax on one unit
    tax_total_amount: Decimal  # Tax on total quantity
    final_unit_price: Decimal  # unit_price + tax_unit_amount
    final_total_price: Decimal  # total_price + tax_total_amount
    product_image: Optional[str] = None
    stock_available: int
    in_stock: bool  # True if stock_available > 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    total_amount: Decimal
    total_tax_amount: Decimal  # Total tax for all items
    grand_total: Decimal  # total_amount + total_tax_amount
    item_count: int  # Number of distinct items


class WishlistItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    product_image: Optional[str] = None
    customer_price: Decimal
    stock_quantity: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class WishlistResponse(BaseModel):
    items: List[WishlistItemResponse]
    total_items: int

