from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from decimal import Decimal
from ..models.cart import Cart
from ..models.product import Product, ProductVariant, ProductStatus
from ..schemas.cart import CartItemCreate, CartItemUpdate
import uuid


def add_to_cart(
    db: Session,
    customer_id: str,
    cart_item: CartItemCreate
) -> Cart:
    """Add item to cart or update quantity if already exists"""
    
    # Verify product exists and is approved
    product = db.query(Product).filter(
        Product.id == cart_item.product_id,
        Product.status == ProductStatus.APPROVED
    ).first()
    
    if not product:
        raise ValueError("Product not found or not available")
    
    # Check if variant is provided
    variant = None
    if cart_item.product_variant_id:
        variant = db.query(ProductVariant).filter(
            ProductVariant.id == cart_item.product_variant_id,
            ProductVariant.product_id == cart_item.product_id,
            ProductVariant.is_active == True
        ).first()
        
        if not variant:
            raise ValueError("Product variant not found or not available")
        
        # Check stock availability for variant
        if variant.stock_quantity < cart_item.quantity:
            raise ValueError(f"Insufficient stock. Only {variant.stock_quantity} available.")
    else:
        # Check stock availability for base product
        if product.stock_quantity < cart_item.quantity:
            raise ValueError(f"Insufficient stock. Only {product.stock_quantity} available.")
    
    # Check if item already exists in cart
    # Handle both NULL and non-NULL variant_id cases
    if cart_item.product_variant_id:
        existing_cart_item = db.query(Cart).filter(
            and_(
                Cart.customer_id == customer_id,
                Cart.product_id == cart_item.product_id,
                Cart.product_variant_id == cart_item.product_variant_id
            )
        ).first()
    else:
        existing_cart_item = db.query(Cart).filter(
            and_(
                Cart.customer_id == customer_id,
                Cart.product_id == cart_item.product_id,
                Cart.product_variant_id.is_(None)
            )
        ).first()
    
    if existing_cart_item:
        # Update quantity
        new_quantity = existing_cart_item.quantity + cart_item.quantity
        
        # Check stock again with new quantity
        available_stock = variant.stock_quantity if variant else product.stock_quantity
        if available_stock < new_quantity:
            raise ValueError(f"Insufficient stock. Only {available_stock} available. You already have {existing_cart_item.quantity} in cart.")
        
        existing_cart_item.quantity = new_quantity
        db.commit()
        db.refresh(existing_cart_item)
        return existing_cart_item
    else:
        # Create new cart item
        cart = Cart(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            product_id=cart_item.product_id,
            product_variant_id=cart_item.product_variant_id,
            quantity=cart_item.quantity
        )
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart


def update_cart_item_quantity(
    db: Session,
    customer_id: str,
    cart_item_id: str,
    quantity_update: CartItemUpdate
) -> Optional[Cart]:
    """Update cart item quantity"""
    
    cart_item = db.query(Cart).filter(
        and_(
            Cart.id == cart_item_id,
            Cart.customer_id == customer_id
        )
    ).first()
    
    if not cart_item:
        return None
    
    # Get product and variant for stock check
    product = cart_item.product
    variant = cart_item.variant if cart_item.product_variant_id else None
    
    # Check stock availability
    available_stock = variant.stock_quantity if variant else product.stock_quantity
    
    if available_stock < quantity_update.quantity:
        raise ValueError(f"Insufficient stock. Only {available_stock} available.")
    
    cart_item.quantity = quantity_update.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


def remove_from_cart(
    db: Session,
    customer_id: str,
    cart_item_id: str
) -> bool:
    """Remove item from cart"""
    
    cart_item = db.query(Cart).filter(
        and_(
            Cart.id == cart_item_id,
            Cart.customer_id == customer_id
        )
    ).first()
    
    if not cart_item:
        return False
    
    db.delete(cart_item)
    db.commit()
    return True


def get_cart(
    db: Session,
    customer_id: str
) -> List[Cart]:
    """Get all items in customer's cart"""
    
    return db.query(Cart).filter(
        Cart.customer_id == customer_id
    ).all()


def clear_cart(
    db: Session,
    customer_id: str
) -> int:
    """Clear all items from customer's cart"""
    
    deleted_count = db.query(Cart).filter(
        Cart.customer_id == customer_id
    ).delete()
    
    db.commit()
    return deleted_count


def get_cart_item(
    db: Session,
    customer_id: str,
    cart_item_id: str
) -> Optional[Cart]:
    """Get specific cart item"""
    
    return db.query(Cart).filter(
        and_(
            Cart.id == cart_item_id,
            Cart.customer_id == customer_id
        )
    ).first()

