from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class ReviewBase(BaseModel):
    rating: int
    comment: Optional[str] = None

    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class ReviewCreate(ReviewBase):
    product_id: str

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v

class ReviewResponse(ReviewBase):
    id: str
    product_id: str
    customer_id: str
    customer_name: Optional[str] = None
    is_approved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReviewStats(BaseModel):
    average_rating: float
    total_reviews: int
    rating_breakdown: dict  # {1: count, 2: count, 3: count, 4: count, 5: count}



