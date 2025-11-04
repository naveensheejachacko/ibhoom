from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from ....core.database import get_db
from ....core.dependencies import get_customer_user
from ....models.user import User
from ....models.cart import Wishlist
from ....models.product import ProductImage, ProductStatus
from ....schemas.cart import WishlistItemResponse, WishlistResponse
from ....services import wishlist_service

router = APIRouter()


@router.post("/{product_id}", response_model=WishlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Add product to wishlist (Customer only)"""
    try:
        wishlist_item = wishlist_service.add_to_wishlist(db, current_user.id, product_id)
        
        # Build response with product details
        product = wishlist_item.product
        
        # Get product image
        primary_image = db.query(ProductImage).filter(
            ProductImage.product_id == product.id,
            ProductImage.is_primary == True
        ).first()
        
        product_image = primary_image.image_url if primary_image else None
        
        return WishlistItemResponse(
            id=wishlist_item.id,
            product_id=wishlist_item.product_id,
            product_name=product.name,
            product_image=product_image,
            customer_price=product.customer_price,
            stock_quantity=product.stock_quantity,
            created_at=wishlist_item.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=WishlistResponse)
async def get_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get all items in wishlist (Customer only)"""
    wishlist_items = wishlist_service.get_wishlist(db, current_user.id)
    
    # Build response with product details
    items = []
    
    for wishlist_item in wishlist_items:
        # Eagerly load product
        wishlist_item = db.query(Wishlist).options(
            joinedload(Wishlist.product)
        ).filter(Wishlist.id == wishlist_item.id).first()
        
        product = wishlist_item.product
        
        # Get product image
        primary_image = db.query(ProductImage).filter(
            ProductImage.product_id == product.id,
            ProductImage.is_primary == True
        ).first()
        
        product_image = primary_image.image_url if primary_image else None
        
        items.append(WishlistItemResponse(
            id=wishlist_item.id,
            product_id=wishlist_item.product_id,
            product_name=product.name,
            product_image=product_image,
            customer_price=product.customer_price,
            stock_quantity=product.stock_quantity,
            created_at=wishlist_item.created_at
        ))
    
    return WishlistResponse(
        items=items,
        total_items=len(items)
    )


@router.delete("/{wishlist_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    wishlist_item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Remove item from wishlist by ID (Customer only)"""
    success = wishlist_service.remove_from_wishlist(db, current_user.id, wishlist_item_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found"
        )


@router.delete("/product/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_product_from_wishlist(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Remove product from wishlist by product_id (Customer only)"""
    success = wishlist_service.remove_product_from_wishlist(db, current_user.id, product_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found in wishlist"
        )


@router.get("/check/{product_id}")
async def check_wishlist_status(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Check if product is in wishlist (Customer only)"""
    is_in_wishlist = wishlist_service.is_in_wishlist(db, current_user.id, product_id)
    return {"is_in_wishlist": is_in_wishlist, "product_id": product_id}

