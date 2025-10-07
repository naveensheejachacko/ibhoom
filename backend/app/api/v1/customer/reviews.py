from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from ....core.database import get_db
from ....core.dependencies import get_customer_user
from ....models.user import User
from ....models.review import ProductReview
from ....models.product import Product
from ....schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, ReviewStats

router = APIRouter()


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Create a product review (Customer only)"""
    # Check if product exists and is approved
    product = db.query(Product).filter(Product.id == review.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    # Check if customer already reviewed this product
    existing_review = db.query(ProductReview).filter(
        and_(
            ProductReview.product_id == review.product_id,
            ProductReview.customer_id == current_user.id
        )
    ).first()
    
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="You have already reviewed this product"
        )
    
    # Create review
    db_review = ProductReview(
        product_id=review.product_id,
        customer_id=current_user.id,
        rating=review.rating,
        comment=review.comment
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    # Add customer name to response
    review_response = ReviewResponse(
        id=db_review.id,
        product_id=db_review.product_id,
        customer_id=db_review.customer_id,
        customer_name=f"{current_user.first_name} {current_user.last_name}",
        rating=db_review.rating,
        comment=db_review.comment,
        is_approved=db_review.is_approved,
        created_at=db_review.created_at,
        updated_at=db_review.updated_at
    )
    
    return review_response


@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get reviews for a specific product (Customer only)"""
    reviews = db.query(ProductReview).filter(
        ProductReview.product_id == product_id,
        ProductReview.is_approved == True
    ).order_by(ProductReview.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add customer names to responses
    result = []
    for review in reviews:
        review_response = ReviewResponse(
            id=review.id,
            product_id=review.product_id,
            customer_id=review.customer_id,
            customer_name=f"{review.customer.first_name} {review.customer.last_name}",
            rating=review.rating,
            comment=review.comment,
            is_approved=review.is_approved,
            created_at=review.created_at,
            updated_at=review.updated_at
        )
        result.append(review_response)
    
    return result


@router.get("/product/{product_id}/stats", response_model=ReviewStats)
async def get_product_review_stats(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get review statistics for a product (Customer only)"""
    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    # Get approved reviews
    reviews = db.query(ProductReview).filter(
        ProductReview.product_id == product_id,
        ProductReview.is_approved == True
    ).all()
    
    if not reviews:
        return ReviewStats(
            average_rating=0.0,
            total_reviews=0,
            rating_breakdown={1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        )
    
    # Calculate statistics
    total_reviews = len(reviews)
    average_rating = sum(review.rating for review in reviews) / total_reviews
    
    # Rating breakdown
    rating_breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        rating_breakdown[review.rating] += 1
    
    return ReviewStats(
        average_rating=round(average_rating, 1),
        total_reviews=total_reviews,
        rating_breakdown=rating_breakdown
    )


@router.get("/my-reviews", response_model=List[ReviewResponse])
async def get_my_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get current customer's reviews (Customer only)"""
    reviews = db.query(ProductReview).filter(
        ProductReview.customer_id == current_user.id
    ).order_by(ProductReview.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add customer names to responses
    result = []
    for review in reviews:
        review_response = ReviewResponse(
            id=review.id,
            product_id=review.product_id,
            customer_id=review.customer_id,
            customer_name=f"{current_user.first_name} {current_user.last_name}",
            rating=review.rating,
            comment=review.comment,
            is_approved=review.is_approved,
            created_at=review.created_at,
            updated_at=review.updated_at
        )
        result.append(review_response)
    
    return result


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: str,
    review_update: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Update a review (Customer only)"""
    review = db.query(ProductReview).filter(
        ProductReview.id == review_id,
        ProductReview.customer_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    # Update review fields
    if review_update.rating is not None:
        review.rating = review_update.rating
    if review_update.comment is not None:
        review.comment = review_update.comment
    
    db.commit()
    db.refresh(review)
    
    # Add customer name to response
    review_response = ReviewResponse(
        id=review.id,
        product_id=review.product_id,
        customer_id=review.customer_id,
        customer_name=f"{current_user.first_name} {current_user.last_name}",
        rating=review.rating,
        comment=review.comment,
        is_approved=review.is_approved,
        created_at=review.created_at,
        updated_at=review.updated_at
    )
    
    return review_response


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Delete a review (Customer only)"""
    review = db.query(ProductReview).filter(
        ProductReview.id == review_id,
        ProductReview.customer_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    db.delete(review)
    db.commit()
    
    return None



