from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from typing import Any, Dict, List, Optional
from ....core.database import get_db
from ....core.dependencies import get_customer_user
from ....models.user import User
from ....models.product import Product, ProductStatus
from ....models.seller import Seller
from ....models.review import ProductReview
from ....schemas.product import ProductResponse, ProductListResponse
from ....schemas.pagination import PaginatedResponse
from ....services import product_service
router = APIRouter()


def get_rating_stats_for_products(db: Session, product_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Fetch average rating and review count for the provided product IDs.
    Returns a mapping of product_id -> {"average_rating": float | None, "total_reviews": int}
    """
    if not product_ids:
        return {}

    stats = (
        db.query(
            ProductReview.product_id,
            func.avg(ProductReview.rating).label("avg_rating"),
            func.count(ProductReview.id).label("review_count")
        )
        .filter(
            ProductReview.product_id.in_(product_ids),
            ProductReview.is_approved == True
        )
        .group_by(ProductReview.product_id)
        .all()
    )

    ratings_map: Dict[str, Dict[str, Any]] = {}
    for stat in stats:
        avg_rating = float(stat.avg_rating) if stat.avg_rating is not None else None
        ratings_map[stat.product_id] = {
            "average_rating": round(avg_rating, 1) if avg_rating is not None else None,
            "total_reviews": int(stat.review_count)
        }

    return ratings_map


@router.get("/", response_model=PaginatedResponse[ProductListResponse])
async def get_all_products(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=1000, description="Items per page"),
    skip: Optional[int] = Query(None, ge=0, description="Skip items (alternative to page, deprecated)"),
    category_id: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at", regex="^(created_at|price|name)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get all products (Customer only)"""
    # Calculate skip from page if not provided
    if skip is None:
        skip = (page - 1) * limit
    
    # Query products with eager loading of seller and user relationships
    query = db.query(Product).options(
        joinedload(Product.seller).joinedload(Seller.user)
    ).filter(Product.status == ProductStatus.APPROVED)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if min_price:
        query = query.filter(Product.customer_price >= min_price)
    
    if max_price:
        query = query.filter(Product.customer_price <= max_price)
    
    if search:
        # Case-insensitive search across name, description, and tags
        search_term = f"%{search}%"
        query = query.filter(
            Product.name.ilike(search_term) | 
            Product.description.ilike(search_term) |
            Product.tags.ilike(search_term)
        )
    
    # Get total count before pagination
    total = query.count()
    
    # Apply sorting
    if sort_by == "price":
        if sort_order == "asc":
            query = query.order_by(Product.customer_price.asc())
        else:
            query = query.order_by(Product.customer_price.desc())
    elif sort_by == "name":
        if sort_order == "asc":
            query = query.order_by(Product.name.asc())
        else:
            query = query.order_by(Product.name.desc())
    else:  # created_at
        if sort_order == "asc":
            query = query.order_by(Product.created_at.asc())
        else:
            query = query.order_by(Product.created_at.desc())
    
    products = query.offset(skip).limit(limit).all()
    ratings_map = get_rating_stats_for_products(db, [product.id for product in products])
    
    # Add seller information to each product
    result = []
    for product in products:
        # Skip products without sellers
        if not product.seller:
            continue
            
        # Get seller information
        seller_name = f"{product.seller.user.first_name} {product.seller.user.last_name}"
        seller_email = product.seller.user.email
        
        product_stats = ratings_map.get(product.id, {})
        
        product_dict = {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "seller_id": product.seller_id,
            "category_id": product.category_id,
            "seller_price": float(product.seller_price),
            "customer_price": float(product.customer_price),
            "commission_rate": float(product.commission_rate),
            "stock_quantity": product.stock_quantity,
            "status": product.status,
            "is_newly_arrived": product.is_newly_arrived,
            "created_at": product.created_at,
            "images": product.images,
            "seller_name": seller_name,
            "seller_email": seller_email,
            "average_rating": product_stats.get("average_rating"),
            "total_reviews": product_stats.get("total_reviews", 0)
        }
        result.append(product_dict)
    
    # Calculate pagination metadata
    current_page = page
    pages = (total + limit - 1) // limit if total > 0 else 1
    
    return PaginatedResponse(
        items=result,
        total=total,
        page=current_page,
        size=limit,
        pages=pages
    )


@router.get("/newly-arrived", response_model=PaginatedResponse[ProductListResponse])
async def get_newly_arrived_products(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    skip: Optional[int] = Query(None, ge=0, description="Skip items (alternative to page, deprecated)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get newly arrived products (Customer only) - Products marked as newly arrived by sellers"""
    # Calculate skip from page if not provided
    if skip is None:
        skip = (page - 1) * limit
    
    # Query products with eager loading of seller and user relationships
    # Filter by is_newly_arrived flag set by sellers
    query = db.query(Product).options(
        joinedload(Product.seller).joinedload(Seller.user)
    ).filter(
        Product.status == ProductStatus.APPROVED,
        Product.is_newly_arrived == True
    )
    
    # Get total count before pagination
    total = query.count()
    
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    ratings_map = get_rating_stats_for_products(db, [product.id for product in products])
    
    # Add seller information to each product
    result = []
    for product in products:
        # Skip products without sellers
        if not product.seller:
            continue
            
        # Get seller information
        seller_name = f"{product.seller.user.first_name} {product.seller.user.last_name}"
        seller_email = product.seller.user.email
        
        product_stats = ratings_map.get(product.id, {})
        
        product_dict = {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "seller_id": product.seller_id,
            "category_id": product.category_id,
            "seller_price": float(product.seller_price),
            "customer_price": float(product.customer_price),
            "commission_rate": float(product.commission_rate),
            "stock_quantity": product.stock_quantity,
            "status": product.status,
            "is_newly_arrived": product.is_newly_arrived,
            "created_at": product.created_at,
            "images": product.images,
            "seller_name": seller_name,
            "seller_email": seller_email,
            "average_rating": product_stats.get("average_rating"),
            "total_reviews": product_stats.get("total_reviews", 0)
        }
        result.append(product_dict)
    
    # Calculate pagination metadata
    current_page = page
    pages = (total + limit - 1) // limit if total > 0 else 1
    
    return PaginatedResponse(
        items=result,
        total=total,
        page=current_page,
        size=limit,
        pages=pages
    )


@router.get("/category/{category_id}", response_model=PaginatedResponse[ProductListResponse])
async def get_products_by_category(
    category_id: str,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=1000, description="Items per page"),
    skip: Optional[int] = Query(None, ge=0, description="Skip items (alternative to page, deprecated)"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at", regex="^(created_at|price|name)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get products by category (Customer only)"""
    # Calculate skip from page if not provided
    if skip is None:
        skip = (page - 1) * limit
    
    # Query products with eager loading of seller and user relationships
    query = db.query(Product).options(
        joinedload(Product.seller).joinedload(Seller.user)
    ).filter(Product.status == ProductStatus.APPROVED)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if min_price:
        query = query.filter(Product.customer_price >= min_price)
    
    if max_price:
        query = query.filter(Product.customer_price <= max_price)
    
    if search:
        # Case-insensitive search across name, description, and tags
        search_term = f"%{search}%"
        query = query.filter(
            Product.name.ilike(search_term) | 
            Product.description.ilike(search_term) |
            Product.tags.ilike(search_term)
        )
    
    # Get total count before pagination
    total = query.count()
    
    # Apply sorting
    if sort_by == "price":
        if sort_order == "asc":
            query = query.order_by(Product.customer_price.asc())
        else:
            query = query.order_by(Product.customer_price.desc())
    elif sort_by == "name":
        if sort_order == "asc":
            query = query.order_by(Product.name.asc())
        else:
            query = query.order_by(Product.name.desc())
    else:  # created_at
        if sort_order == "asc":
            query = query.order_by(Product.created_at.asc())
        else:
            query = query.order_by(Product.created_at.desc())
    
    products = query.offset(skip).limit(limit).all()
    ratings_map = get_rating_stats_for_products(db, [product.id for product in products])
    
    # Add seller information to each product
    result = []
    for product in products:
        # Skip products without sellers
        if not product.seller:
            continue
        
        # Get seller information
        seller_name = f"{product.seller.user.first_name} {product.seller.user.last_name}"
        seller_email = product.seller.user.email
        
        product_stats = ratings_map.get(product.id, {})
        
        product_dict = {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "seller_id": product.seller_id,
            "category_id": product.category_id,
            "seller_price": float(product.seller_price),
            "customer_price": float(product.customer_price),
            "commission_rate": float(product.commission_rate),
            "stock_quantity": product.stock_quantity,
            "status": product.status,
            "is_newly_arrived": product.is_newly_arrived,
            "created_at": product.created_at,
            "images": product.images,
            "seller_name": seller_name,
            "seller_email": seller_email,
            "average_rating": product_stats.get("average_rating"),
            "total_reviews": product_stats.get("total_reviews", 0)
        }
        result.append(product_dict)
    
    # Calculate pagination metadata
    current_page = page
    pages = (total + limit - 1) // limit if total > 0 else 1
    
    return PaginatedResponse(
        items=result,
        total=total,
        page=current_page,
        size=limit,
        pages=pages
    )


@router.get("/seller/{seller_id}", response_model=PaginatedResponse[ProductListResponse])
async def get_products_by_seller(
    seller_id: str,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=1000, description="Items per page"),
    skip: Optional[int] = Query(None, ge=0, description="Skip items (alternative to page, deprecated)"),
    category_id: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at", regex="^(created_at|price|name)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get all products from a specific seller (Customer only)"""
    # Calculate skip from page if not provided
    if skip is None:
        skip = (page - 1) * limit
    
    # Verify seller exists (no approval check - consistent with general product listing)
    seller = db.query(Seller).options(
        joinedload(Seller.user)
    ).filter(Seller.id == seller_id).first()
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")
    
    # Get products by seller
    query = db.query(Product).filter(
        Product.seller_id == seller_id,
        Product.status == ProductStatus.APPROVED
    )
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if min_price:
        query = query.filter(Product.customer_price >= min_price)
    
    if max_price:
        query = query.filter(Product.customer_price <= max_price)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Product.name.ilike(search_term) | 
            Product.description.ilike(search_term) |
            Product.tags.ilike(search_term)
        )
    
    # Apply sorting
    if sort_by == "price":
        if sort_order == "asc":
            query = query.order_by(Product.customer_price.asc())
        else:
            query = query.order_by(Product.customer_price.desc())
    elif sort_by == "name":
        if sort_order == "asc":
            query = query.order_by(Product.name.asc())
        else:
            query = query.order_by(Product.name.desc())
    else:  # created_at
        if sort_order == "asc":
            query = query.order_by(Product.created_at.asc())
        else:
            query = query.order_by(Product.created_at.desc())
    
    # Get total count before pagination
    total = query.count()
    
    products = query.offset(skip).limit(limit).all()
    ratings_map = get_rating_stats_for_products(db, [product.id for product in products])
    
    # Build response with seller information
    result = []
    for product in products:
        product_stats = ratings_map.get(product.id, {})
        
        product_dict = {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "seller_id": product.seller_id,
            "category_id": product.category_id,
            "seller_price": float(product.seller_price),
            "customer_price": float(product.customer_price),
            "commission_rate": float(product.commission_rate),
            "stock_quantity": product.stock_quantity,
            "status": product.status,
            "is_newly_arrived": product.is_newly_arrived,
            "created_at": product.created_at,
            "images": product.images,
            "seller_name": seller.business_name,
            "seller_email": seller.user.email if seller.user else None,
            "average_rating": product_stats.get("average_rating"),
            "total_reviews": product_stats.get("total_reviews", 0)
        }
        result.append(product_dict)
    
    # Calculate pagination metadata
    current_page = page  # Use the provided page parameter
    pages = (total + limit - 1) // limit if total > 0 else 1
    
    return PaginatedResponse(
        items=result,
        total=total,
        page=current_page,
        size=limit,
        pages=pages
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_details(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get product details with seller information (Customer only)"""
    # Get product with eager loading of seller and user relationships
    product = db.query(Product).options(
        joinedload(Product.seller).joinedload(Seller.user)
    ).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if product.status != ProductStatus.APPROVED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not available")
    
    # Build seller basic info
    seller_info = None
    if product.seller:
        from ....schemas.product import SellerBasicInfo
        seller_info = SellerBasicInfo(
            id=product.seller.id,
            business_name=product.seller.business_name,
            business_type=product.seller.business_type,
            city=product.seller.city,
            state=product.seller.state,
            pincode=product.seller.pincode,
            email=product.seller.user.email if product.seller.user else None,
            phone=product.seller.user.phone if product.seller.user else None
        )
    
    # Calculate tax and final price for product
    tax_rate = float(product.tax_rate) if product.tax_rate is not None else 18.0
    customer_price = float(product.customer_price)
    tax_amount = customer_price * (tax_rate / 100)
    final_unit_price = customer_price + tax_amount
    
    # Process variants with calculated pricing
    variants_with_pricing = []
    for variant in product.variants:
        variant_tax_rate = float(variant.tax_rate) if variant.tax_rate is not None else tax_rate
        variant_customer_price = float(variant.customer_price)
        variant_tax_amount = variant_customer_price * (variant_tax_rate / 100)
        variant_final_price = variant_customer_price + variant_tax_amount
        
        variant_dict = {
            "id": variant.id,
            "variant_name": variant.variant_name,
            "sku": variant.sku,
            "stock_quantity": variant.stock_quantity,
            "customer_price": variant_customer_price,
            "tax_rate": variant_tax_rate,  # Percentage (e.g., 18.0 means 18%)
            "tax_amount": round(variant_tax_amount, 2),  # Amount in currency
            "final_unit_price": round(variant_final_price, 2),
            "is_active": variant.is_active
        }
        variants_with_pricing.append(variant_dict)
    
    # Get product response and add seller info
    product_dict = {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "description": product.description,
        "category_id": product.category_id,
        "seller_id": product.seller_id,
        "customer_price": customer_price,
        "tax_rate": tax_rate,  # Percentage (e.g., 18.0 means 18%)
        "tax_amount": round(tax_amount, 2),  # Amount in currency
        "final_unit_price": round(final_unit_price, 2),
        "stock_quantity": product.stock_quantity,
        "status": product.status,
        "tags": product.tags,
        "meta_title": product.meta_title,
        "meta_description": product.meta_description,
        "admin_notes": None,  # Admin notes not exposed to customers (stored in rejection_reason field)
        "has_return_policy": product.has_return_policy,
        "return_period_days": product.return_period_days,
        "return_policy_description": product.return_policy_description,
        "is_newly_arrived": product.is_newly_arrived,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "images": product.images,
        "variants": variants_with_pricing,
        "reviews": [],  # Will be populated if needed
        "average_rating": None,
        "total_reviews": 0,
        "seller": seller_info
    }
    
    return ProductResponse(**product_dict)
