from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.product import Product, ProductVariant, ProductImage, ProductVariantAttribute, ProductStatus
from ..models.category import Category
from ..models.seller import Seller
from ..schemas.product import ProductCreate, ProductUpdate, ProductApprovalUpdate
import uuid
import re
from datetime import datetime


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from product name"""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def create_product(db: Session, product: ProductCreate, seller_id: str) -> Product:
    """Create a new product"""
    # Validate category exists
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise ValueError("Category not found")
    
    # Validate seller exists
    seller = db.query(Seller).filter(Seller.id == seller_id).first()
    if not seller:
        raise ValueError("Seller not found")
    
    # Generate unique slug
    base_slug = generate_slug(product.name)
    slug = base_slug
    counter = 1
    
    while db.query(Product).filter(Product.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Calculate commission
    commission_rate = get_commission_rate(db, product.category_id, seller_price=product.seller_price)
    commission_calc = calculate_commission(product.seller_price, commission_rate)
    
    # Create product
    db_product = Product(
        id=str(uuid.uuid4()),
        name=product.name,
        slug=slug,
        description=product.description,
        category_id=product.category_id,
        seller_id=seller_id,
        seller_price=product.seller_price,
        commission_rate=commission_calc.commission_rate,
        commission_amount=commission_calc.commission_amount,
        customer_price=commission_calc.customer_price,
        stock_quantity=product.stock_quantity,
        tags=product.tags,
        weight=product.weight,
        dimensions=product.dimensions,
        meta_title=product.meta_title,
        meta_description=product.meta_description,
        status=ProductStatus.PENDING
    )
    
    db.add(db_product)
    db.flush()  # Get the ID
    
    # Add images
    for img_data in product.images:
        image = ProductImage(
            id=str(uuid.uuid4()),
            product_id=db_product.id,
            image_url=img_data.image_url,
            alt_text=img_data.alt_text,
            sort_order=img_data.sort_order
        )
        db.add(image)
    
    # Add variants
    for variant_data in product.variants:
        variant_commission_calc = calculate_commission(variant_data.seller_price, commission_rate)
        
        variant = ProductVariant(
            id=str(uuid.uuid4()),
            product_id=db_product.id,
            sku=variant_data.sku,
            seller_price=variant_data.seller_price,
            commission_rate=variant_commission_calc.commission_rate,
            commission_amount=variant_commission_calc.commission_amount,
            customer_price=variant_commission_calc.customer_price,
            stock_quantity=variant_data.stock_quantity,
            weight=variant_data.weight,
            dimensions=variant_data.dimensions
        )
        db.add(variant)
        db.flush()
        
        # Add variant attributes
        for attr_data in variant_data.attributes:
            variant_attr = ProductVariantAttribute(
                id=str(uuid.uuid4()),
                product_variant_id=variant.id,
                attribute_id=attr_data.attribute_id,
                attribute_value_id=attr_data.attribute_value_id
            )
            db.add(variant_attr)
    
    db.commit()
    db.refresh(db_product)
    
    return db_product


def get_product(db: Session, product_id: str) -> Optional[Product]:
    """Get product by ID"""
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_slug(db: Session, slug: str) -> Optional[Product]:
    """Get product by slug"""
    return db.query(Product).filter(Product.slug == slug).first()


def get_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category_id: Optional[str] = None,
    seller_id: Optional[str] = None,
    status: Optional[ProductStatus] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None
) -> List[Product]:
    """Get products with filtering"""
    query = db.query(Product)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if seller_id:
        query = query.filter(Product.seller_id == seller_id)
    
    if status:
        query = query.filter(Product.status == status)
    
    if min_price:
        query = query.filter(Product.customer_price >= min_price)
    
    if max_price:
        query = query.filter(Product.customer_price <= max_price)
    
    if search:
        query = query.filter(
            Product.name.contains(search) | 
            Product.description.contains(search) |
            Product.tags.contains(search)
        )
    
    return query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()


def update_product(db: Session, product_id: str, product_update: ProductUpdate, seller_id: Optional[str] = None) -> Optional[Product]:
    """Update product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        return None
    
    # If seller_id is provided, ensure the seller owns the product
    if seller_id and db_product.seller_id != seller_id:
        raise ValueError("Not authorized to update this product")
    
    update_data = product_update.dict(exclude_unset=True)
    
    # Handle slug regeneration if name changed
    if "name" in update_data:
        base_slug = generate_slug(update_data["name"])
        slug = base_slug
        counter = 1
        
        while db.query(Product).filter(Product.slug == slug, Product.id != product_id).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        update_data["slug"] = slug
    
    # Recalculate commission if price or category changed
    if "seller_price" in update_data or "category_id" in update_data:
        category_id = update_data.get("category_id", db_product.category_id)
        seller_price = update_data.get("seller_price", db_product.seller_price)
        
        commission_rate = get_commission_rate(db, category_id, product_id, seller_price)
        commission_calc = calculate_commission(seller_price, commission_rate)
        
        update_data["commission_rate"] = commission_calc.commission_rate
        update_data["commission_amount"] = commission_calc.commission_amount
        update_data["customer_price"] = commission_calc.customer_price
    
    # Reset status to pending if product details changed (except for admin updates)
    if seller_id and any(key in update_data for key in ["name", "description", "category_id", "seller_price"]):
        update_data["status"] = ProductStatus.PENDING
    
    update_data["updated_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    
    return db_product


def approve_product(db: Session, product_id: str, approval: ProductApprovalUpdate) -> Optional[Product]:
    """Approve or reject product (Admin only)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        return None
    
    db_product.status = approval.status
    db_product.admin_notes = approval.admin_notes
    db_product.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_product)
    
    return db_product


def delete_product(db: Session, product_id: str, seller_id: Optional[str] = None) -> bool:
    """Delete product (soft delete by setting status to inactive)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        return False
    
    # If seller_id is provided, ensure the seller owns the product
    if seller_id and db_product.seller_id != seller_id:
        raise ValueError("Not authorized to delete this product")
    
    # Check if product has orders (implement when order model is ready)
    
    # Soft delete
    db_product.status = ProductStatus.INACTIVE
    db_product.updated_at = datetime.utcnow()
    db.commit()
    
    return True


def get_pending_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """Get products pending approval (Admin only)"""
    return db.query(Product).filter(
        Product.status == ProductStatus.PENDING
    ).order_by(Product.created_at.asc()).offset(skip).limit(limit).all()


def recalculate_product_commission(db: Session, product_id: str) -> Optional[Product]:
    """Recalculate commission for a product (Admin only)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        return None
    
    # Recalculate main product commission
    commission_rate = get_commission_rate(db, db_product.category_id, product_id, db_product.seller_price)
    commission_calc = calculate_commission(db_product.seller_price, commission_rate)
    
    db_product.commission_rate = commission_calc.commission_rate
    db_product.commission_amount = commission_calc.commission_amount
    db_product.customer_price = commission_calc.customer_price
    db_product.updated_at = datetime.utcnow()
    
    # Recalculate variant commissions
    for variant in db_product.variants:
        variant_calc = calculate_commission(variant.seller_price, commission_rate)
        variant.commission_rate = variant_calc.commission_rate
        variant.commission_amount = variant_calc.commission_amount
        variant.customer_price = variant_calc.customer_price
    
    db.commit()
    db.refresh(db_product)
    
    return db_product 