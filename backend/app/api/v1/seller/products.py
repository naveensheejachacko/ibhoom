from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....core.dependencies import get_seller_user
from ....models.user import User
from ....models.product import ProductStatus
from ....schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from ....services import product_service

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Create a new product (Seller only)"""
    try:
        db_product = product_service.create_product(db, product, current_user.seller.id)
        return db_product
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[ProductListResponse])
async def get_my_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ProductStatus] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Get seller's own products (Seller only)"""
    products = product_service.get_products(
        db, skip=skip, limit=limit,
        seller_id=current_user.seller.id,
        status=status, search=search
    )
    
    # Add seller information to each product
    result = []
    for product in products:
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
            "seller_name": f"{current_user.first_name} {current_user.last_name}",
            "seller_email": current_user.email
        }
        result.append(product_dict)
    
    return result


@router.get("/{product_id}", response_model=ProductResponse)
async def get_my_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Get seller's own product by ID (Seller only)"""
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    # Check if seller owns the product
    if product.seller_id != current_user.seller.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this product")
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_my_product(
    product_id: str,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Update seller's own product (Seller only)"""
    try:
        updated_product = product_service.update_product(db, product_id, product_update, current_user.seller.id)
        if not updated_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return updated_product
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{product_id}")
async def delete_my_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Delete seller's own product (Seller only)"""
    try:
        deleted = product_service.delete_product(db, product_id, current_user.seller.id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return {"message": "Product deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/pending/count")
async def get_pending_products_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Get count of seller's pending products (Seller only)"""
    products = product_service.get_products(
        db, seller_id=current_user.seller.id, status=ProductStatus.PENDING, limit=1000
    )
    return {"count": len(products)}


@router.get("/approved/count")
async def get_approved_products_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Get count of seller's approved products (Seller only)"""
    products = product_service.get_products(
        db, seller_id=current_user.seller.id, status=ProductStatus.APPROVED, limit=1000
    )
    return {"count": len(products)} 