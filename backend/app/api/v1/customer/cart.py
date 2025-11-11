from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from decimal import Decimal
from ....core.database import get_db
from ....core.dependencies import get_customer_user
from ....models.user import User
from ....models.cart import Cart
from ....models.product import ProductImage, ProductVariant
from ....schemas.cart import (
    CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse
)
from ....services import cart_service

router = APIRouter()


@router.post("/", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    cart_item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Add item to cart (Customer only)"""
    try:
        cart = cart_service.add_to_cart(db, current_user.id, cart_item)
        
        # Build response with product details
        product = cart.product
        # Get variant if product_variant_id exists
        variant = None
        variant_name = None
        if cart.product_variant_id:
            variant = cart.variant
            if not variant:
                # If variant not loaded, query it explicitly
                variant = db.query(ProductVariant).filter(
                    ProductVariant.id == cart.product_variant_id
                ).first()
            if variant:
                variant_name = variant.variant_name
        
        # Get product image - try primary first, then any image, then None
        primary_image = db.query(ProductImage).filter(
            ProductImage.product_id == product.id,
            ProductImage.is_primary == True
        ).first()
        
        if not primary_image:
            # Fallback to any image if no primary image
            any_image = db.query(ProductImage).filter(
                ProductImage.product_id == product.id
            ).order_by(ProductImage.sort_order.asc()).first()
            product_image = any_image.image_url if any_image else None
        else:
            product_image = primary_image.image_url
        
        # Calculate prices
        unit_price = variant.customer_price if variant else product.customer_price
        total_price = unit_price * cart.quantity
        stock_available = variant.stock_quantity if variant else product.stock_quantity
        in_stock = stock_available > 0
        
        return CartItemResponse(
            id=cart.id,
            product_id=cart.product_id,
            product_name=product.name,
            product_variant_id=cart.product_variant_id,
            variant_name=variant_name,
            quantity=cart.quantity,
            unit_price=unit_price,
            total_price=total_price,
            product_image=product_image,
            stock_available=stock_available,
            in_stock=in_stock,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=CartResponse)
async def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get all items in cart (Customer only)"""
    # Get cart items with eager loading
    cart_items = db.query(Cart).options(
        joinedload(Cart.product),
        joinedload(Cart.variant)
    ).filter(Cart.customer_id == current_user.id).all()
    
    # Build response with product details
    items = []
    total_amount = Decimal('0.00')
    
    for cart_item in cart_items:
        
        product = cart_item.product
        # Get variant if product_variant_id exists
        variant = None
        variant_name = None
        if cart_item.product_variant_id:
            variant = cart_item.variant
            if not variant:
                # If variant not loaded, query it explicitly
                variant = db.query(ProductVariant).filter(
                    ProductVariant.id == cart_item.product_variant_id
                ).first()
            if variant:
                variant_name = variant.variant_name
        
        # Get product image - try primary first, then any image, then None
        primary_image = db.query(ProductImage).filter(
            ProductImage.product_id == product.id,
            ProductImage.is_primary == True
        ).first()
        
        if not primary_image:
            # Fallback to any image if no primary image
            any_image = db.query(ProductImage).filter(
                ProductImage.product_id == product.id
            ).order_by(ProductImage.sort_order.asc()).first()
            product_image = any_image.image_url if any_image else None
        else:
            product_image = primary_image.image_url
        
        # Calculate prices
        unit_price = variant.customer_price if variant else product.customer_price
        total_price = unit_price * cart_item.quantity
        total_amount += total_price
        stock_available = variant.stock_quantity if variant else product.stock_quantity
        in_stock = stock_available > 0
        
        items.append(CartItemResponse(
            id=cart_item.id,
            product_id=cart_item.product_id,
            product_name=product.name,
            product_variant_id=cart_item.product_variant_id,
            variant_name=variant_name,
            quantity=cart_item.quantity,
            unit_price=unit_price,
            total_price=total_price,
            product_image=product_image,
            stock_available=stock_available,
            in_stock=in_stock,
            created_at=cart_item.created_at,
            updated_at=cart_item.updated_at
        ))
    
    total_items = sum(item.quantity for item in cart_items)
    
    return CartResponse(
        items=items,
        total_items=total_items,
        total_amount=total_amount,
        item_count=len(items)
    )


@router.put("/{cart_item_id}", response_model=CartItemResponse)
async def update_cart_item(
    cart_item_id: str,
    quantity_update: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Update cart item quantity (Customer only)"""
    try:
        cart_item = cart_service.update_cart_item_quantity(
            db, current_user.id, cart_item_id, quantity_update
        )
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        
        # Build response with product details
        cart_item = db.query(Cart).options(
            joinedload(Cart.product),
            joinedload(Cart.variant)
        ).filter(Cart.id == cart_item.id).first()
        
        product = cart_item.product
        # Get variant if product_variant_id exists
        variant = None
        variant_name = None
        if cart_item.product_variant_id:
            variant = cart_item.variant
            if not variant:
                # If variant not loaded, query it explicitly
                variant = db.query(ProductVariant).filter(
                    ProductVariant.id == cart_item.product_variant_id
                ).first()
            if variant:
                variant_name = variant.variant_name
        
        # Get product image - try primary first, then any image, then None
        primary_image = db.query(ProductImage).filter(
            ProductImage.product_id == product.id,
            ProductImage.is_primary == True
        ).first()
        
        if not primary_image:
            # Fallback to any image if no primary image
            any_image = db.query(ProductImage).filter(
                ProductImage.product_id == product.id
            ).order_by(ProductImage.sort_order.asc()).first()
            product_image = any_image.image_url if any_image else None
        else:
            product_image = primary_image.image_url
        
        # Calculate prices
        unit_price = variant.customer_price if variant else product.customer_price
        total_price = unit_price * cart_item.quantity
        stock_available = variant.stock_quantity if variant else product.stock_quantity
        in_stock = stock_available > 0
        
        return CartItemResponse(
            id=cart_item.id,
            product_id=cart_item.product_id,
            product_name=product.name,
            product_variant_id=cart_item.product_variant_id,
            variant_name=variant_name,
            quantity=cart_item.quantity,
            unit_price=unit_price,
            total_price=total_price,
            product_image=product_image,
            stock_available=stock_available,
            in_stock=in_stock,
            created_at=cart_item.created_at,
            updated_at=cart_item.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    cart_item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Remove item from cart (Customer only)"""
    success = cart_service.remove_from_cart(db, current_user.id, cart_item_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )


@router.delete("/", status_code=status.HTTP_200_OK)
async def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Clear all items from cart (Customer only)"""
    deleted_count = cart_service.clear_cart(db, current_user.id)
    return {"message": f"Cart cleared. {deleted_count} item(s) removed."}


@router.get("/{cart_item_id}", response_model=CartItemResponse)
async def get_cart_item(
    cart_item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get specific cart item (Customer only)"""
    cart_item = cart_service.get_cart_item(db, current_user.id, cart_item_id)
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Eagerly load product and variant
    cart_item = db.query(Cart).options(
        joinedload(Cart.product),
        joinedload(Cart.variant)
    ).filter(Cart.id == cart_item.id).first()
    
    product = cart_item.product
    # Get variant if product_variant_id exists
    variant = None
    variant_name = None
    if cart_item.product_variant_id:
        variant = cart_item.variant
        if not variant:
            # If variant not loaded, query it explicitly
            from ....models.product import ProductVariant
            variant = db.query(ProductVariant).filter(
                ProductVariant.id == cart_item.product_variant_id
            ).first()
        if variant:
            variant_name = variant.variant_name
    
    # Get product image - try primary first, then any image, then None
    primary_image = db.query(ProductImage).filter(
        ProductImage.product_id == product.id,
        ProductImage.is_primary == True
    ).first()
    
    if not primary_image:
        # Fallback to any image if no primary image
        any_image = db.query(ProductImage).filter(
            ProductImage.product_id == product.id
        ).order_by(ProductImage.sort_order.asc()).first()
        product_image = any_image.image_url if any_image else None
    else:
        product_image = primary_image.image_url
    
    # Calculate prices
    unit_price = variant.customer_price if variant else product.customer_price
    total_price = unit_price * cart_item.quantity
    stock_available = variant.stock_quantity if variant else product.stock_quantity
    in_stock = stock_available > 0
    
    return CartItemResponse(
        id=cart_item.id,
        product_id=cart_item.product_id,
        product_name=product.name,
        product_variant_id=cart_item.product_variant_id,
        variant_name=variant_name,
        quantity=cart_item.quantity,
        unit_price=unit_price,
        total_price=total_price,
        product_image=product_image,
        stock_available=stock_available,
        in_stock=in_stock,
        created_at=cart_item.created_at,
        updated_at=cart_item.updated_at
    )

