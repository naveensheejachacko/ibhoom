from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....core.dependencies import get_customer_user
from ....models.user import User
from ....models.product import Product, ProductStatus
from ....schemas.product import ProductResponse, ProductListResponse
from ....services import product_service
from ....utils.location import is_within_radius, get_city_coordinates

router = APIRouter()


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
    """Get all approved products for customers with location-based filtering (within 5km radius) (Customer only)"""
    # Require location to enforce 5km radius rule
    customer_lat, customer_lon = None, None
    if latitude and longitude:
        customer_lat, customer_lon = latitude, longitude
    elif city:
        # Geocode city to get coordinates
        coords = get_city_coordinates(city)
        if coords:
            customer_lat, customer_lon = coords
    
    # Enforce location requirement for 5km filtering
    if not customer_lat or not customer_lon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location is required. Please provide either (latitude, longitude) or city parameter to see products within 5km radius."
        )
    
    products = product_service.get_products(
        db, skip=skip, limit=limit,
        category_id=category_id, status=ProductStatus.APPROVED,
        min_price=min_price, max_price=max_price, search=search
    )
    
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
            "seller_email": seller_email
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
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100),
    # Location filtering parameters
    latitude: Optional[float] = Query(None, description="Customer's latitude"),
    longitude: Optional[float] = Query(None, description="Customer's longitude"),
    city: Optional[str] = Query(None, description="Customer's city name"),
    radius_km: Optional[float] = Query(5, ge=1, le=500, description="Search radius in kilometers (default: 5km)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get newly arrived products with location-based filtering (within 5km radius) (Customer only)"""
    from datetime import datetime, timedelta
    
    # Require location to enforce 5km radius rule
    customer_lat, customer_lon = None, None
    if latitude and longitude:
        customer_lat, customer_lon = latitude, longitude
    elif city:
        # Geocode city to get coordinates
        coords = get_city_coordinates(city)
        if coords:
            customer_lat, customer_lon = coords
    
    # Enforce location requirement for 5km filtering
    if not customer_lat or not customer_lon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location is required. Please provide either (latitude, longitude) or city parameter to see products within 5km radius."
        )
    
    # Calculate date threshold
    threshold_date = datetime.utcnow() - timedelta(days=days)
    
    products = db.query(Product).filter(
        Product.status == ProductStatus.APPROVED,
        Product.created_at >= threshold_date
    ).order_by(Product.created_at.desc()).limit(limit).all()
    
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
            "seller_email": seller_email
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
    # Require location to enforce 5km radius rule
    customer_lat, customer_lon = None, None
    if latitude and longitude:
        customer_lat, customer_lon = latitude, longitude
    elif city:
        # Geocode city to get coordinates
        coords = get_city_coordinates(city)
        if coords:
            customer_lat, customer_lon = coords
    
    # Enforce location requirement for 5km filtering
    if not customer_lat or not customer_lon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location is required. Please provide either (latitude, longitude) or city parameter to see products within 5km radius."
        )
    
    products = product_service.get_products(
        db, skip=skip, limit=limit,
        category_id=category_id, status=ProductStatus.APPROVED,
        min_price=min_price, max_price=max_price, search=search
    )
    
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
            "seller_email": seller_email
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


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_details(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get product details (Customer only)"""
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    if product.status != ProductStatus.APPROVED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not available")
    
    return product



