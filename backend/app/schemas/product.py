from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.product import ProductStatus
from decimal import Decimal


class ProductImageBase(BaseModel):
    image_url: str
    alt_text: Optional[str] = None
    sort_order: int = 0


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageResponse(ProductImageBase):
    id: str
    
    class Config:
        from_attributes = True


class ProductVariantAttributeBase(BaseModel):
    attribute_id: str
    attribute_value_id: str


class ProductVariantAttributeCreate(ProductVariantAttributeBase):
    pass


class ProductVariantAttributeResponse(ProductVariantAttributeBase):
    id: str
    attribute_name: str
    attribute_value: str
    
    class Config:
        from_attributes = True


class ProductVariantBase(BaseModel):
    sku: Optional[str] = None
    seller_price: float
    stock_quantity: int = 0
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    
    @validator('seller_price')
    def validate_seller_price(cls, v):
        if v <= 0:
            raise ValueError('Seller price must be positive')
        return v

    @validator('stock_quantity')
    def validate_stock_quantity(cls, v):
        if v < 0:
            raise ValueError('Stock quantity cannot be negative')
        return v


class ProductVariantCreate(ProductVariantBase):
    attributes: List[ProductVariantAttributeCreate] = []


class ProductVariantUpdate(BaseModel):
    sku: Optional[str] = None
    seller_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    
    @validator('seller_price')
    def validate_seller_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Seller price must be positive')
        return v


class ProductVariantResponse(ProductVariantBase):
    id: str
    commission_rate: float
    commission_amount: float
    customer_price: float
    attributes: List[ProductVariantAttributeResponse] = []
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: str
    seller_price: float
    stock_quantity: int = 0
    tags: Optional[str] = None  # JSON string for SQLite compatibility
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    
    @validator('seller_price')
    def validate_seller_price(cls, v):
        if v <= 0:
            raise ValueError('Seller price must be positive')
        return v

    @validator('stock_quantity')
    def validate_stock_quantity(cls, v):
        if v < 0:
            raise ValueError('Stock quantity cannot be negative')
        return v


class ProductCreate(ProductBase):
    images: List[ProductImageCreate] = []
    variants: List[ProductVariantCreate] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    seller_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    tags: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    
    @validator('seller_price')
    def validate_seller_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Seller price must be positive')
        return v


class ProductResponse(ProductBase):
    id: str
    slug: str
    seller_id: str
    commission_rate: float
    commission_amount: float
    customer_price: float
    status: ProductStatus
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    images: List[ProductImageResponse] = []
    variants: List[ProductVariantResponse] = []
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    id: str
    name: str
    slug: str
    seller_id: str
    category_id: str
    seller_price: float
    customer_price: float
    commission_rate: float
    stock_quantity: int
    status: ProductStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductApprovalUpdate(BaseModel):
    status: ProductStatus
    admin_notes: Optional[str] = None


class ProductFilters(BaseModel):
    category_id: Optional[str] = None
    seller_id: Optional[str] = None
    status: Optional[ProductStatus] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    search: Optional[str] = None 