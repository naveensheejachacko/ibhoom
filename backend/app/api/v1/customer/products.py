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
from ....services import product_service
from ....utils.location import is_within_radius, get_city_coordinates

router = APIRouter()


def get_customer_location(
    latitude: Optional[float],
    longitude: Optional[float],
    city: Optional[str],
    current_user: User
) -> tuple[Optional[float], Optional[float]]:
    """
    Get customer location from multiple sources in priority order:
    1. Provided latitude/longitude (most accurate)
    2. Provided city name (geocoded)
    3. Customer's stored pincode (auto-geocoded)
    
    Returns:
        Tuple of (latitude, longitude) or (None, None) if location cannot be determined
    """
    # Priority 1: Use provided coordinates
    if latitude and longitude:
        return latitude, longitude
    
    # Priority 2: Geocode city name
    if city:
        from ....utils.location import get_city_coordinates
        coords = get_city_coordinates(city)
        if coords:
            return coords
    
    # Priority 3: Use customer's stored pincode
    if current_user.pincode:
        from ....utils.location import geocode_pincode_kerala
        coords = geocode_pincode_kerala(current_user.pincode, db_session=None)
        if coords:
            return coords
    
    return None, None


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


@router.get("/", response_model=List[ProductListResponse])
async def get_all_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_id: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at", regex="^(created_at|price|name)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    # Location filtering parameters
    latitude: Optional[float] = Query(None, description="Customer's latitude"),
    longitude: Optional[float] = Query(None, description="Customer's longitude"),
    city: Optional[str] = Query(None, description="Customer's city name"),
    radius_km: Optional[float] = Query(5, ge=1, le=500, description="Search radius in kilometers (default: 5km)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get all products with location-based filtering (within 5km radius) (Customer only)"""
    # Get customer location - auto-uses stored pincode if available
    customer_lat, customer_lon = get_customer_location(latitude, longitude, city, current_user)
    
    # Enforce location requirement for 5km filtering
    if not customer_lat or not customer_lon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location is required. Please provide either (latitude, longitude) or city parameter, or set your pincode in your profile to see products within 5km radius."
        )
    
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
    
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    ratings_map = get_rating_stats_for_products(db, [product.id for product in products])
    
    # Add seller information to each product
    result = []
    for product in products:
        # Skip products without sellers (location filtering requires seller)
        if not product.seller:
            continue
            
        # Get seller information
        seller_name = f"{product.seller.user.first_name} {product.seller.user.last_name}"
        seller_email = product.seller.user.email
        
        # Apply location filtering (required - 5km radius)
        # Skip products from sellers without location data
        if not product.seller.latitude or not product.seller.longitude:
            continue
        
        # Check if seller is within radius (enforced 5km)
        if not is_within_radius(
            product.seller.latitude, product.seller.longitude,
            customer_lat, customer_lon,
            radius_km
        ):
            continue
        
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
            "created_at": product.created_at,
            "images": product.images,
            "seller_name": seller_name,
            "seller_email": seller_email,
            "average_rating": product_stats.get("average_rating"),
            "total_reviews": product_stats.get("total_reviews", 0)
        }
        result.append(product_dict)
    
    # Apply sorting
    if sort_by == "price":
        result.sort(key=lambda x: x["customer_price"], reverse=(sort_order == "desc"))
    elif sort_by == "name":
        result.sort(key=lambda x: x["name"], reverse=(sort_order == "desc"))
    else:  # created_at
        result.sort(key=lambda x: x["created_at"], reverse=(sort_order == "desc"))
    
    return result


@router.get("/newly-arrived", response_model=List[ProductListResponse])
async def get_newly_arrived_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    # Location filtering parameters
    latitude: Optional[float] = Query(None, description="Customer's latitude"),
    longitude: Optional[float] = Query(None, description="Customer's longitude"),
    city: Optional[str] = Query(None, description="Customer's city name"),
    radius_km: Optional[float] = Query(5, ge=1, le=500, description="Search radius in kilometers (default: 5km)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get newly arrived products (Customer only) - Products added in last 7 days within 5km radius"""
    # Get customer location - auto-uses stored pincode if available
    customer_lat, customer_lon = get_customer_location(latitude, longitude, city, current_user)
    
    # Enforce location requirement for 5km filtering
    if not customer_lat or not customer_lon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location is required. Please provide either (latitude, longitude) or city parameter, or set your pincode in your profile to see products within 5km radius."
        )
    
    from datetime import datetime, timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # Query products with eager loading of seller and user relationships
    query = db.query(Product).options(
        joinedload(Product.seller).joinedload(Seller.user)
    ).filter(
        Product.status == ProductStatus.APPROVED,
        Product.created_at >= seven_days_ago
    )
    
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    ratings_map = get_rating_stats_for_products(db, [product.id for product in products])
    
    # Add seller information to each product
    result = []
    for product in products:
        # Skip products without sellers (location filtering requires seller)
        if not product.seller:
            continue
            
        # Get seller information
        seller_name = f"{product.seller.user.first_name} {product.seller.user.last_name}"
        seller_email = product.seller.user.email
        
        # Apply location filtering (required - 5km radius)
        # Skip products from sellers without location data
        if not product.seller.latitude or not product.seller.longitude:
            continue
        
        # Check if seller is within radius (enforced 5km)
        if not is_within_radius(
            product.seller.latitude, product.seller.longitude,
            customer_lat, customer_lon,
            radius_km
        ):
            continue
        
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
            "created_at": product.created_at,
            "images": product.images,
            "seller_name": seller_name,
            "seller_email": seller_email,
            "average_rating": product_stats.get("average_rating"),
            "total_reviews": product_stats.get("total_reviews", 0)
        }
        result.append(product_dict)
    
    return result


@router.get("/category/{category_id}", response_model=List[ProductListResponse])
async def get_products_by_category(
    category_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at", regex="^(created_at|price|name)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    # Location filtering parameters
    latitude: Optional[float] = Query(None, description="Customer's latitude"),
    longitude: Optional[float] = Query(None, description="Customer's longitude"),
    city: Optional[str] = Query(None, description="Customer's city name"),
    radius_km: Optional[float] = Query(5, ge=1, le=500, description="Search radius in kilometers (default: 5km)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get products by category with location-based filtering (within 5km radius) (Customer only)"""
    # Get customer location - auto-uses stored pincode if available
    customer_lat, customer_lon = get_customer_location(latitude, longitude, city, current_user)
    
    # Enforce location requirement for 5km filtering
    if not customer_lat or not customer_lon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location is required. Please provide either (latitude, longitude) or city parameter, or set your pincode in your profile to see products within 5km radius."
        )
    
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
    
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    ratings_map = get_rating_stats_for_products(db, [product.id for product in products])
    
    # Add seller information to each product
    result = []
    for product in products:
        # Skip products without sellers (location filtering requires seller)
        if not product.seller:
            continue
        
        # Get seller information
        seller_name = f"{product.seller.user.first_name} {product.seller.user.last_name}"
        seller_email = product.seller.user.email
        
        # Apply location filtering (required - 5km radius)
        # Skip products from sellers without location data
        if not product.seller.latitude or not product.seller.longitude:
            continue
        
        # Check if seller is within radius (enforced 5km)
        if not is_within_radius(
            product.seller.latitude, product.seller.longitude,
            customer_lat, customer_lon,
            radius_km
        ):
            continue
        
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
            "created_at": product.created_at,
            "images": product.images,
            "seller_name": seller_name,
            "seller_email": seller_email,
            "average_rating": product_stats.get("average_rating"),
            "total_reviews": product_stats.get("total_reviews", 0)
        }
        result.append(product_dict)
    
    # Apply sorting
    if sort_by == "price":
        result.sort(key=lambda x: x["customer_price"], reverse=(sort_order == "desc"))
    elif sort_by == "name":
        result.sort(key=lambda x: x["name"], reverse=(sort_order == "desc"))
    else:  # created_at
        result.sort(key=lambda x: x["created_at"], reverse=(sort_order == "desc"))
    
    return result


@router.get("/seller/{seller_id}", response_model=List[ProductListResponse])
async def get_products_by_seller(
    seller_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_id: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at", regex="^(created_at|price|name)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    # Location filtering parameters
    latitude: Optional[float] = Query(None, description="Customer's latitude"),
    longitude: Optional[float] = Query(None, description="Customer's longitude"),
    city: Optional[str] = Query(None, description="Customer's city name"),
    radius_km: Optional[float] = Query(5, ge=1, le=500, description="Search radius in kilometers (default: 5km)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get all products from a specific seller (Customer only)"""
    # Verify seller exists and is approved
    seller = db.query(Seller).options(
        joinedload(Seller.user)
    ).filter(Seller.id == seller_id).first()
    if not seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")
    
    if not seller.is_approved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not available")
    
    # Get customer location (optional - if provided, filter by radius)
    customer_lat, customer_lon = get_customer_location(latitude, longitude, city, current_user)
    
    # If location is provided, check if seller is within radius
    if customer_lat and customer_lon and seller.latitude and seller.longitude:
        if not is_within_radius(seller.latitude, seller.longitude, customer_lat, customer_lon, radius_km):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Seller is outside your delivery area (beyond {radius_km}km radius)"
            )
    
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
            "created_at": product.created_at,
            "images": product.images,
            "seller_name": seller.business_name,
            "seller_email": seller.user.email if seller.user else None,
            "average_rating": product_stats.get("average_rating"),
            "total_reviews": product_stats.get("total_reviews", 0)
        }
        result.append(product_dict)
    
    return result


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
    
    # Get product response and add seller info
    product_dict = {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "description": product.description,
        "category_id": product.category_id,
        "seller_id": product.seller_id,
        "seller_price": float(product.seller_price),
        "commission_rate": float(product.commission_rate),
        "commission_amount": float(product.commission_amount),
        "customer_price": float(product.customer_price),
        "stock_quantity": product.stock_quantity,
        "status": product.status,
        "tags": product.tags,
        "meta_title": product.meta_title,
        "meta_description": product.meta_description,
        "admin_notes": product.admin_notes,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "images": product.images,
        "variants": product.variants,
        "reviews": [],  # Will be populated if needed
        "average_rating": None,
        "total_reviews": 0,
        "seller": seller_info
    }
    
    return ProductResponse(**product_dict)
