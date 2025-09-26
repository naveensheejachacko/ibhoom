from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: str
    slug: str
    level: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CategoryWithChildren(CategoryResponse):
    children: List['CategoryWithChildren'] = []
    
    class Config:
        from_attributes = True


class CategoryTree(BaseModel):
    categories: List[CategoryWithChildren]


# Update forward references
CategoryWithChildren.model_rebuild() 