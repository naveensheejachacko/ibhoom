from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from ..models.attribute import AttributeType


class AttributeValueBase(BaseModel):
    value: str
    sort_order: int = 0


class AttributeValueCreate(AttributeValueBase):
    attribute_id: str


class AttributeValueUpdate(BaseModel):
    value: Optional[str] = None
    sort_order: Optional[int] = None


class AttributeValueResponse(AttributeValueBase):
    id: str
    attribute_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AttributeBase(BaseModel):
    name: str
    type: AttributeType
    is_required: bool = False
    sort_order: int = 0


class AttributeCreate(AttributeBase):
    pass


class AttributeUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[AttributeType] = None
    is_required: Optional[bool] = None
    sort_order: Optional[int] = None


class AttributeResponse(AttributeBase):
    id: str
    created_at: datetime
    attribute_values: List[AttributeValueResponse] = []
    
    class Config:
        from_attributes = True


class CategoryAttributeBase(BaseModel):
    category_id: str
    attribute_id: str
    is_required: bool = False
    is_variant: bool = False  # True if this attribute affects pricing/inventory


class CategoryAttributeCreate(CategoryAttributeBase):
    pass


class CategoryAttributeUpdate(BaseModel):
    is_required: Optional[bool] = None
    is_variant: Optional[bool] = None


class CategoryAttributeResponse(CategoryAttributeBase):
    id: str
    created_at: datetime
    attribute: Optional[AttributeResponse] = None
    
    class Config:
        from_attributes = True


class CategoryAttributesResponse(BaseModel):
    category_id: str
    attributes: List[AttributeResponse] = []

