from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....core.dependencies import get_admin_user
from ....models.user import User
from ....models.product import ProductStatus
from ....schemas.product import ProductResponse, ProductListResponse, ProductApprovalUpdate, ProductFilters
from ....services import product_service

router = APIRouter()


@router.get("/", response_model=List[ProductListResponse])
async def get_all_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_id: Optional[str] = Query(None),
    seller_id: Optional[str] = Query(None),
    status: Optional[ProductStatus] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all products with filtering (Admin only)"""
    products = product_service.get_products(
        db, skip=skip, limit=limit,
        category_id=category_id, seller_id=seller_id, status=status,
        min_price=min_price, max_price=max_price, search=search
    )
    return products


@router.get("/pending", response_model=List[ProductListResponse])
async def get_pending_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get products pending approval (Admin only)"""
    products = product_service.get_pending_products(db, skip=skip, limit=limit)
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get product by ID (Admin only)"""
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.put("/{product_id}/approve", response_model=ProductResponse)
async def approve_product(
    product_id: str,
    approval: ProductApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Approve or reject product (Admin only)"""
    updated_product = product_service.approve_product(db, product_id, approval)
    if not updated_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return updated_product


@router.post("/{product_id}/recalculate-commission", response_model=ProductResponse)
async def recalculate_product_commission(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Recalculate commission for a product (Admin only)"""
    updated_product = product_service.recalculate_product_commission(db, product_id)
    if not updated_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return updated_product


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete product (Admin only)"""
    try:
        deleted = product_service.delete_product(db, product_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return {"message": "Product deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/slug/{slug}", response_model=ProductResponse)
async def get_product_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get product by slug (Admin only)"""
    product = product_service.get_product_by_slug(db, slug)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product 