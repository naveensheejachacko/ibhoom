from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from ..models.cart import Wishlist
from ..models.product import Product, ProductStatus
import uuid


def add_to_wishlist(
    db: Session,
    customer_id: str,
    product_id: str
) -> Wishlist:
    """Add product to wishlist"""
    
    # Verify product exists and is approved
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.status == ProductStatus.APPROVED
    ).first()
    
    if not product:
        raise ValueError("Product not found or not available")
    
    # Check if already in wishlist
    existing_item = db.query(Wishlist).filter(
        and_(
            Wishlist.customer_id == customer_id,
            Wishlist.product_id == product_id
        )
    ).first()
    
    if existing_item:
        return existing_item
    
    # Create new wishlist item
    wishlist_item = Wishlist(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        product_id=product_id
    )
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    return wishlist_item


def remove_from_wishlist(
    db: Session,
    customer_id: str,
    wishlist_item_id: str
) -> bool:
    """Remove item from wishlist"""
    
    wishlist_item = db.query(Wishlist).filter(
        and_(
            Wishlist.id == wishlist_item_id,
            Wishlist.customer_id == customer_id
        )
    ).first()
    
    if not wishlist_item:
        return False
    
    db.delete(wishlist_item)
    db.commit()
    return True


def remove_product_from_wishlist(
    db: Session,
    customer_id: str,
    product_id: str
) -> bool:
    """Remove product from wishlist by product_id"""
    
    wishlist_item = db.query(Wishlist).filter(
        and_(
            Wishlist.customer_id == customer_id,
            Wishlist.product_id == product_id
        )
    ).first()
    
    if not wishlist_item:
        return False
    
    db.delete(wishlist_item)
    db.commit()
    return True


def get_wishlist(
    db: Session,
    customer_id: str
) -> List[Wishlist]:
    """Get all items in customer's wishlist"""
    
    return db.query(Wishlist).filter(
        Wishlist.customer_id == customer_id
    ).all()


def is_in_wishlist(
    db: Session,
    customer_id: str,
    product_id: str
) -> bool:
    """Check if product is in customer's wishlist"""
    
    item = db.query(Wishlist).filter(
        and_(
            Wishlist.customer_id == customer_id,
            Wishlist.product_id == product_id
        )
    ).first()
    
    return item is not None

