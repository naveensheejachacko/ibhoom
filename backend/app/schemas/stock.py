from pydantic import BaseModel, validator
from typing import Optional


class StockUpdateRequest(BaseModel):
    """Request to update stock for a product"""
    stock_quantity: int
    notes: Optional[str] = None
    
    @validator('stock_quantity')
    def validate_stock(cls, v):
        if v < 0:
            raise ValueError('Stock quantity cannot be negative')
        return v


class VariantStockUpdateRequest(BaseModel):
    """Request to update stock for a product variant"""
    variant_id: str
    stock_quantity: int
    notes: Optional[str] = None
    
    @validator('stock_quantity')
    def validate_stock(cls, v):
        if v < 0:
            raise ValueError('Stock quantity cannot be negative')
        return v


class BulkStockUpdateRequest(BaseModel):
    """Request to update stock for multiple items"""
    updates: list[VariantStockUpdateRequest]


class StockItemResponse(BaseModel):
    """Response for stock item details"""
    product_id: str
    product_name: str
    product_slug: str
    sku: Optional[str] = None
    variant_id: Optional[str] = None
    variant_name: Optional[str] = None
    variant_sku: Optional[str] = None
    stock_quantity: int
    low_stock_threshold: int = 10  # Default threshold
    is_low_stock: bool = False
    status: str
    
    class Config:
        from_attributes = True

