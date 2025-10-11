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
    
    class Config:
        from_attributes = True


class ProductVariantBase(BaseModel):
    variant_name: Optional[str] = None
    sku: Optional[str] = None
    seller_price: float
    stock_quantity: int = 0
    
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
    is_active: bool = True
    # Don't include attributes in response to avoid validation issues
    # attributes: List[ProductVariantAttributeResponse] = []
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: str
    seller_price: float
    stock_quantity: int = 0
    tags: Optional[str] = None  # JSON string for SQLite compatibility
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
    reviews: List[dict] = []  # Will contain review stats
    average_rating: Optional[float] = None
    total_reviews: int = 0
    
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
    images: List[ProductImageResponse] = []
    seller_name: Optional[str] = None
    seller_email: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProductApprovalUpdate(BaseModel):
    status: ProductStatus
    admin_notes: Optional[str] = None  # This will be stored in rejection_reason field
    commission_rate: Optional[float] = None


class ProductFilters(BaseModel):
    category_id: Optional[str] = None
    seller_id: Optional[str] = None
    status: Optional[ProductStatus] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    search: Optional[str] = None 