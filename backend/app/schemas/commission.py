from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from ..models.commission import CommissionType


class CommissionSettingBase(BaseModel):
    type: CommissionType
    entity_id: Optional[str] = None  # category_id or product_id
    commission_rate: float
    min_seller_price: float = 0.0
    max_seller_price: Optional[float] = None
    is_active: bool = True
    effective_from: Optional[datetime] = None
    effective_until: Optional[datetime] = None

    @validator('commission_rate')
    def validate_commission_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Commission rate must be between 0 and 100')
        return v

    @validator('min_seller_price')
    def validate_min_price(cls, v):
        if v < 0:
            raise ValueError('Minimum seller price cannot be negative')
        return v

    @validator('max_seller_price')
    def validate_max_price(cls, v, values):
        if v is not None:
            if v < 0:
                raise ValueError('Maximum seller price cannot be negative')
            if 'min_seller_price' in values and v < values['min_seller_price']:
                raise ValueError('Maximum price cannot be less than minimum price')
        return v


class CommissionSettingCreate(CommissionSettingBase):
    pass


class CommissionSettingUpdate(BaseModel):
    commission_rate: Optional[float] = None
    min_seller_price: Optional[float] = None
    max_seller_price: Optional[float] = None
    is_active: Optional[bool] = None
    effective_from: Optional[datetime] = None
    effective_until: Optional[datetime] = None

    @validator('commission_rate')
    def validate_commission_rate(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Commission rate must be between 0 and 100')
        return v


class CommissionSettingResponse(CommissionSettingBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class CommissionCalculation(BaseModel):
    seller_price: float
    commission_rate: float
    commission_amount: float
    customer_price: float 