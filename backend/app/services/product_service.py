from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.product import Product, ProductVariant, ProductImage, ProductVariantAttribute, ProductStatus
from ..models.category import Category
from ..models.seller import Seller
from ..schemas.product import ProductCreate, ProductUpdate, ProductApprovalUpdate
from .commission_service import get_commission_rate, calculate_commission
import uuid
import re
from datetime import datetime
from decimal import Decimal


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from product name"""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def generate_sku(seller_id: str, product_name: str) -> str:
    """Auto-generate unique SKU for product
    Format: SELLER-{short_seller_id}-{timestamp}-{random}
    Example: SELLER-ABC123-1702045678-X9K2
    """
    from time import time
    import random
    import string
    
    # Get short seller ID (first 6 chars)
    short_seller_id = seller_id[:6].upper()
    
    # Get timestamp (last 4 digits)
    timestamp = str(int(time()))[-4:]
    
    # Generate random suffix (4 chars)
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    # Create SKU
    sku = f"SELLER-{short_seller_id}-{timestamp}-{random_suffix}"
    
    return sku


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
    
    # Auto-generate SKU
    auto_sku = generate_sku(seller_id, product.name)
    
    # Calculate commission
    commission_rate = get_commission_rate(db, product.category_id, seller_price=product.seller_price)
    commission_calc = calculate_commission(product.seller_price, commission_rate)
    
    # Create product
    default_tax_rate = Decimal('18.00')
    
    db_product = Product(
        id=str(uuid.uuid4()),
        name=product.name,
        slug=slug,
        sku=auto_sku,  # Auto-generated SKU
        description=product.description,
        category_id=product.category_id,
        seller_id=seller_id,
        seller_price=product.seller_price,
        commission_rate=commission_calc.commission_rate,
        commission_amount=commission_calc.commission_amount,
        customer_price=commission_calc.customer_price,
        stock_quantity=product.stock_quantity,
        tags=product.tags,
        meta_title=product.meta_title,
        meta_description=product.meta_description,
        status=ProductStatus.PENDING,
        tax_rate=default_tax_rate,
        has_return_policy=product.has_return_policy,  # Set return policy from request
        return_period_days=product.return_period_days,  # Set return period from request
        return_policy_description=product.return_policy_description,  # Set return policy description from request
        is_newly_arrived=False  # Always False on creation - only admin can set during approval
    )
    
    db.add(db_product)
    db.flush()  # Get the ID
    
    # Add images
    from ..core.config import settings
    from ..utils.cloudinary_service import upload_base64_image
    
    for img_data in product.images:
        image_url = img_data.image_url
        
        # If image_url is a base64 string, upload to Cloudinary
        if image_url:
            # Check if Cloudinary is configured
            if not settings.CLOUDINARY_URL:
                print("⚠️  WARNING: CLOUDINARY_URL not set! Images will be stored as base64 in database.")
                # Continue with base64 - no upload
            # Check if it's a base64 image (starts with data:image or is a long base64 string)
            elif image_url.startswith('data:image') or (len(image_url) > 100 and not image_url.startswith('http')):
                try:
                    print(f"📤 Uploading image to Cloudinary for product {db_product.id}...")
                    print(f"   Base64 length: {len(image_url)} characters")
                    result = upload_base64_image(
                        base64_string=image_url,
                        folder=f"products/{seller_id}"
                    )
                    image_url = result["image_url"]
                    print(f"✅ Image uploaded successfully: {image_url[:50]}...")
                except ValueError as e:
                    # ValueError means validation or upload error - show full error
                    error_msg = str(e)
                    print(f"❌ ERROR: {error_msg}")
                    import traceback
                    print(f"   Full traceback:\n{traceback.format_exc()}")
                    raise ValueError(error_msg)
                except Exception as e:
                    # Catch any other unexpected errors
                    error_msg = f"Unexpected error uploading image: {str(e)}"
                    print(f"❌ ERROR: {error_msg}")
                    import traceback
                    print(f"   Full traceback:\n{traceback.format_exc()}")
                    raise ValueError(error_msg)
            # If it's already a Cloudinary URL, use it as is
            elif "cloudinary.com" in image_url:
                print(f"✅ Using existing Cloudinary URL: {image_url[:50]}...")
                image_url = image_url  # Already a Cloudinary URL
            # If it's already an HTTP URL (not Cloudinary), use it as is
            elif image_url.startswith('http'):
                print(f"ℹ️  Using existing HTTP URL: {image_url[:50]}...")
                image_url = image_url
        
        image = ProductImage(
            id=str(uuid.uuid4()),
            product_id=db_product.id,
            image_url=image_url,
            alt_text=img_data.alt_text,
            sort_order=img_data.sort_order
        )
        db.add(image)
    
    # Add variants
    for idx, variant_data in enumerate(product.variants, 1):
        variant_commission_calc = calculate_commission(variant_data.seller_price, commission_rate)
        
        # Generate variant SKU if not provided
        # Format: {product_sku}-V{number}
        variant_sku = variant_data.sku if variant_data.sku else f"{auto_sku}-V{idx:03d}"
        
        variant = ProductVariant(
            id=str(uuid.uuid4()),
            product_id=db_product.id,
            variant_name=getattr(variant_data, 'variant_name', None),
            sku=variant_sku,
            seller_price=variant_data.seller_price,
            commission_rate=variant_commission_calc.commission_rate,
            commission_amount=variant_commission_calc.commission_amount,
            customer_price=variant_commission_calc.customer_price,
            stock_quantity=variant_data.stock_quantity,
            is_active=True,  # Set variants as active by default
            tax_rate=default_tax_rate
        )
        db.add(variant)
        db.flush()
        
        # Add variant attributes
        for attr_data in variant_data.attributes:
            variant_attr = ProductVariantAttribute(
                id=str(uuid.uuid4()),
                variant_id=variant.id,
                attribute_id=attr_data.attribute_id,
                attribute_value_id=attr_data.attribute_value_id
            )
            db.add(variant_attr)
    
    db.commit()
    db.refresh(db_product)
    
    return db_product


def get_product(db: Session, product_id: str) -> Optional[Product]:
    """Get product by ID with variants and their attributes"""
    from sqlalchemy.orm import joinedload
    return db.query(Product).options(
        joinedload(Product.variants).joinedload(ProductVariant.attributes)
    ).filter(Product.id == product_id).first()


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
    search: Optional[str] = None,
    include_hidden: bool = False
) -> List[Product]:
    """Get products with filtering"""
    query = db.query(Product)
    
    # By default, exclude hidden (soft-deleted) products
    if not include_hidden:
        query = query.filter(Product.status != ProductStatus.HIDDEN)
    
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
    
    # Prevent sellers from setting is_newly_arrived (admin only)
    if seller_id and "is_newly_arrived" in update_data:
        raise ValueError("Sellers cannot mark products as newly arrived. Only admins can set this during approval.")
    
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
    
    # Handle variants update if provided
    variants_data = update_data.pop("variants", None)
    if variants_data is not None:
        # Delete all existing variants and their attributes
        for existing_variant in db_product.variants:
            # Delete variant attributes first
            db.query(ProductVariantAttribute).filter(
                ProductVariantAttribute.variant_id == existing_variant.id
            ).delete()
            # Delete the variant
            db.delete(existing_variant)
        
        # Flush deletions to ensure they're committed before creating new variants
        db.flush()
        
        # Get commission rate for variants (use product's category and commission rate)
        category_id = update_data.get("category_id", db_product.category_id)
        base_commission_rate = get_commission_rate(db, category_id, product_id, db_product.seller_price)
        
        # Import ProductVariantCreate to convert dicts to models
        from ..schemas.product import ProductVariantCreate
        
        # Create new variants
        for idx, variant_dict in enumerate(variants_data, 1):
            # Convert dict to Pydantic model for validation
            variant_data = ProductVariantCreate(**variant_dict)
            
            variant_commission_calc = calculate_commission(variant_data.seller_price, base_commission_rate)
            
            # Generate variant SKU if not provided, or ensure uniqueness if provided
            product_sku = update_data.get("sku", db_product.sku)
            if variant_data.sku:
                # Check if SKU already exists for other products (we already deleted variants from this product)
                variant_sku = variant_data.sku
                existing_variant_with_sku = db.query(ProductVariant).filter(
                    ProductVariant.sku == variant_sku
                ).first()
                if existing_variant_with_sku:
                    # SKU exists for another product/variant, generate a new one
                    base_sku = f"{product_sku}-V{idx:03d}"
                    variant_sku = base_sku
                    counter = 1
                    while db.query(ProductVariant).filter(ProductVariant.sku == variant_sku).first():
                        variant_sku = f"{base_sku}-{counter}"
                        counter += 1
            else:
                # Generate new SKU
                base_sku = f"{product_sku}-V{idx:03d}"
                variant_sku = base_sku
                counter = 1
                while db.query(ProductVariant).filter(ProductVariant.sku == variant_sku).first():
                    variant_sku = f"{base_sku}-{counter}"
                    counter += 1
            
            variant = ProductVariant(
                id=str(uuid.uuid4()),
                product_id=db_product.id,
                variant_name=variant_data.variant_name,
                sku=variant_sku,
                seller_price=variant_data.seller_price,
                commission_rate=variant_commission_calc.commission_rate,
                commission_amount=variant_commission_calc.commission_amount,
                customer_price=variant_commission_calc.customer_price,
                stock_quantity=variant_data.stock_quantity,
                is_active=True,
                tax_rate=db_product.tax_rate or Decimal('18.00')
            )
            db.add(variant)
            db.flush()
            
            # Add variant attributes
            for attr_data in variant_data.attributes:
                variant_attr = ProductVariantAttribute(
                    id=str(uuid.uuid4()),
                    variant_id=variant.id,
                    attribute_id=attr_data.attribute_id,
                    attribute_value_id=attr_data.attribute_value_id
                )
                db.add(variant_attr)
        
        # If variants were added/updated, reset status to pending (variants are significant changes)
        if seller_id:
            update_data["status"] = ProductStatus.PENDING
    
    # Reset status to pending if product details changed (except for admin updates)
    # Don't reset status for metadata-only updates like tags, meta fields
    # Note: is_newly_arrived is admin-only, so it's not in metadata_fields for sellers
    metadata_fields = {"tags", "meta_title", "meta_description", "has_return_policy", "return_period_days", "return_policy_description"}
    if seller_id and any(key in update_data for key in ["name", "description", "category_id", "seller_price"]):
        # Only reset if non-metadata fields changed
        if not all(key in metadata_fields for key in update_data.keys()):
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
    db_product.rejection_reason = approval.admin_notes
    db_product.updated_at = datetime.utcnow()
    
    # Update is_newly_arrived if provided
    if approval.is_newly_arrived is not None:
        db_product.is_newly_arrived = approval.is_newly_arrived
    
    # Ensure tax rate is set during approval
    tax_rate_value = approval.tax_rate
    if tax_rate_value is None:
        tax_rate_decimal = db_product.tax_rate or Decimal('18.00')
    else:
        tax_rate_decimal = Decimal(str(tax_rate_value))
    db_product.tax_rate = tax_rate_decimal
    for variant in db_product.variants:
        variant.tax_rate = tax_rate_decimal
    
    # Update commission rate if provided
    if approval.commission_rate is not None:
        db_product.commission_rate = approval.commission_rate
        # Recalculate commission amount and customer price for main product
        from .commission_service import calculate_commission
        commission_calc = calculate_commission(
            db_product.seller_price, 
            approval.commission_rate
        )
        db_product.commission_amount = commission_calc.commission_amount
        db_product.customer_price = commission_calc.customer_price
        
        # Update commission for all variants as well
        for variant in db_product.variants:
            variant_calc = calculate_commission(variant.seller_price, approval.commission_rate)
            variant.commission_rate = variant_calc.commission_rate
            variant.commission_amount = variant_calc.commission_amount
            variant.customer_price = variant_calc.customer_price
    
    db.commit()
    db.refresh(db_product)
    
    return db_product


def delete_product(db: Session, product_id: str, seller_id: Optional[str] = None) -> bool:
    """Delete product (soft delete by setting status to hidden)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        return False
    
    # If seller_id is provided, ensure the seller owns the product
    if seller_id and db_product.seller_id != seller_id:
        raise ValueError("Not authorized to delete this product")
    
    # Check if product has orders (implement when order model is ready)
    
    # Soft delete
    db_product.status = ProductStatus.HIDDEN
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